import numpy as np
import shap
from lime.lime_text import LimeTextExplainer
import torch
import re
from config import settings as config

def clean_and_tokenize(text):
    """Tokenizes text into words while keeping punctuation mapping if possible."""
    return re.findall(r'\w+', text.lower())

def explain_baseline(text, model, vectorizer):
    """
    Computes feature importance using a SHAP linear explainer or coefficients
    for the TF-IDF baselines. Returns a list of (word, score) tuples.
    """
    words = text.split()
    if not words:
        return []
        
    # Get vector representation
    vec = vectorizer.transform([text]).toarray()[0]
    feature_names = vectorizer.get_feature_names_out()
    
    # Calculate word importance by mapping non-zero weights
    word_scores = []
    # Logistic Regression has coef_[0]
    if hasattr(model, "coef_"):
        coef = model.coef_[0]
    elif hasattr(model, "calibrated_classifiers_"):
        # For Calibrated LinearSVC, average the coefficients of base estimators
        coefs = [clf.estimator.coef_[0] for clf in model.calibrated_classifiers_]
        coef = np.mean(coefs, axis=0)
    else:
        coef = np.zeros(len(feature_names))
        
    for word in words:
        cleaned_word = re.sub(r'[^a-zA-Z]', '', word.lower())
        if cleaned_word in feature_names:
            idx = np.where(feature_names == cleaned_word)[0][0]
            val = vec[idx]
            weight = coef[idx]
            # Score is TF-IDF value * coefficient weight
            score = val * weight
            word_scores.append((word, float(score)))
        else:
            word_scores.append((word, 0.0))
            
    return word_scores

def explain_transformer_loo(text, classifier):
    """
    Performs a fast Leave-One-Out (LOO) word-level importance explanation.
    Removes one word at a time, computes change in probability for the risk class (label 1),
    and returns a list of (word, score) tuples.
    This is extremely robust and fast compared to raw SHAP.
    """
    words = text.split()
    if not words:
        return []
        
    # Get base probability for 'Suicide' class (label 1)
    base_res = classifier.predict_proba(text)
    base_prob = base_res["probabilities"][1]
    
    word_scores = []
    
    for i in range(len(words)):
        # Construct text without current word
        perturbed_words = words[:i] + words[i+1:]
        perturbed_text = " ".join(perturbed_words)
        
        if not perturbed_text.strip():
            word_scores.append((words[i], 0.0))
            continue
            
        perturbed_res = classifier.predict_proba(perturbed_text)
        perturbed_prob = perturbed_res["probabilities"][1]
        
        # Change in probability: positive means the word contributed to suicide risk
        # (removing it decreased the probability)
        score = base_prob - perturbed_prob
        word_scores.append((words[i], float(score)))
        
    return word_scores

def explain_transformer_shap(text, model, tokenizer, device):
    """
    Uses SHAP's Partition explainer over a HF text-classification pipeline to generate
    token-level SHAP values for the transformer's risk class. Slower than the LOO method
    (explain_transformer_loo) but grounded in Shapley values rather than single-word removal.
    Can be slow on CPU.
    """
    from transformers import pipeline
    pipe = pipeline(
        "text-classification",
        model=model,
        tokenizer=tokenizer,
        device=0 if device.type == "cuda" else -1,
        return_all_scores=True
    )

    # Define explainer
    explainer = shap.Explainer(pipe)
    shap_values = explainer([text], max_evals=config.SHAP_MAX_EVALS)

    # Extract word tokens and corresponding values for the risk class (label 1)
    # shap_values[0, :, 1] corresponds to input 0, all tokens, class 1
    tokens = shap_values.data[0]
    values = shap_values.values[0, :, 1]

    return list(zip(tokens, [float(v) for v in values]))

def explain_lime(text, predict_proba_fn):
    """
    Uses LIME to explain a prediction.
    predict_proba_fn takes a list of strings and returns an array of shape (N, 2).
    """
    explainer = LimeTextExplainer(class_names=["Non-Suicide", "Suicide"])
    exp = explainer.explain_instance(
        text,
        predict_proba_fn,
        num_features=config.LIME_NUM_FEATURES,
        num_samples=config.LIME_NUM_SAMPLES,
    )
    return [(word, float(weight)) for word, weight in exp.as_list()]

def explain_integrated_gradients(text, classifier, steps=20):
    """
    Computes Integrated Gradients (IG) attributions for a model.
    For Transformers: Computes path integrals of embedding gradients.
    For Baselines: Computes feature attributions based on TF-IDF gradients.
    """
    words = text.split()
    if not words:
        return []

    # Check if classifier is a Transformer (has .model, .tokenizer, .device)
    if hasattr(classifier, "model") and hasattr(classifier, "tokenizer") and hasattr(classifier, "device"):
        try:
            model = classifier.model
            tokenizer = classifier.tokenizer
            device = classifier.device
            model.eval()

            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            input_ids = inputs["input_ids"].to(device)
            attention_mask = inputs["attention_mask"].to(device)

            # Get embedding layer
            if hasattr(model, "get_input_embeddings"):
                embed_layer = model.get_input_embeddings()
            elif hasattr(model, "bert"):
                embed_layer = model.bert.embeddings.word_embeddings
            elif hasattr(model, "roberta"):
                embed_layer = model.roberta.embeddings.word_embeddings
            else:
                return explain_transformer_loo(text, classifier)

            embeddings = embed_layer(input_ids).detach()
            baseline_embeddings = torch.zeros_like(embeddings)

            grads = []
            for i in range(1, steps + 1):
                alpha = i / float(steps)
                interp_embeddings = baseline_embeddings + alpha * (embeddings - baseline_embeddings)
                interp_embeddings.requires_grad_(True)

                # Forward pass with custom inputs_embeds
                outputs = model(inputs_embeds=interp_embeddings, attention_mask=attention_mask)
                logits = outputs.logits
                # Target class score (index 1 for Suicide risk)
                score = logits[0, 1] if logits.shape[1] > 1 else logits[0, 0]

                model.zero_grad()
                score.backward()
                grads.append(interp_embeddings.grad.detach())

            avg_grads = torch.stack(grads, dim=0).mean(dim=0)
            integrated_grads = (embeddings - baseline_embeddings) * avg_grads
            token_scores = integrated_grads.sum(dim=-1).squeeze(0).cpu().numpy()

            tokens = tokenizer.convert_ids_to_tokens(input_ids[0].cpu().numpy())
            
            # Map sub-tokens back to word-level scores
            word_scores = []
            for word in words:
                word_clean = re.sub(r'[^a-zA-Z0-9]', '', word.lower())
                matching_indices = []
                for idx, token in enumerate(tokens):
                    tok_clean = re.sub(r'[^a-zA-Z0-9]', '', token.lower().replace('##', '').replace('Ġ', ''))
                    if tok_clean and (tok_clean in word_clean or word_clean in tok_clean):
                        matching_indices.append(idx)
                if matching_indices:
                    val = float(np.mean([token_scores[idx] for idx in matching_indices]))
                else:
                    val = 0.0
                word_scores.append((word, val))
            return word_scores
        except Exception:
            return explain_transformer_loo(text, classifier)
    
    # Fallback for baseline models
    if hasattr(classifier, "model") and hasattr(classifier, "vectorizer"):
        return explain_baseline(text, classifier.model, classifier.vectorizer)
    return explain_transformer_loo(text, classifier)

def compute_pearson_correlation(vec1, vec2):
    """Computes Pearson correlation coefficient between two 1D numerical vectors."""
    v1 = np.array(vec1, dtype=float)
    v2 = np.array(vec2, dtype=float)
    if len(v1) == 0 or len(v2) == 0:
        return 0.0
    std1 = np.std(v1)
    std2 = np.std(v2)
    if std1 == 0 or std2 == 0:
        return 1.0 if np.allclose(v1, v2) else 0.0
    cov = np.mean((v1 - np.mean(v1)) * (v2 - np.mean(v2)))
    return float(cov / (std1 * std2))

def compare_explainers(text, classifier, predict_proba_fn=None):
    """
    Runs multi-explainer comparison (SHAP, Integrated Gradients, LIME, LOO) for a text.
    Aligns scores across methods and computes pairwise Pearson correlation matrix.
    """
    words = text.split()
    if not words:
        return {
            "words": [],
            "methods": {},
            "correlation_matrix": {}
        }

    # Gather attributions
    loo_scores = explain_transformer_loo(text, classifier) if hasattr(classifier, "predict_proba") else explain_baseline(text, classifier.model, classifier.vectorizer)
    ig_scores = explain_integrated_gradients(text, classifier)

    # For LIME
    if predict_proba_fn is None and hasattr(classifier, "predict_proba"):
        def predict_proba_fn(texts):
            return np.array([classifier.predict_proba(t)["probabilities"] for t in texts])
    
    if predict_proba_fn:
        lime_raw = explain_lime(text, predict_proba_fn)
        lime_dict = {re.sub(r'[^a-zA-Z0-9]', '', k.lower()): v for k, v in lime_raw}
        lime_scores = []
        for w in words:
            w_clean = re.sub(r'[^a-zA-Z0-9]', '', w.lower())
            lime_scores.append((w, float(lime_dict.get(w_clean, 0.0))))
    else:
        lime_scores = loo_scores

    # For SHAP
    if hasattr(classifier, "model") and hasattr(classifier, "tokenizer") and hasattr(classifier, "device"):
        shap_raw = explain_transformer_shap(text, classifier.model, classifier.tokenizer, classifier.device)
        shap_dict = {re.sub(r'[^a-zA-Z0-9]', '', str(k).lower().replace('##', '').replace('Ġ', '')): v for k, v in shap_raw}
        shap_scores = []
        for w in words:
            w_clean = re.sub(r'[^a-zA-Z0-9]', '', w.lower())
            shap_scores.append((w, float(shap_dict.get(w_clean, 0.0))))
    else:
        shap_scores = loo_scores

    # Build vectors
    loo_vec = [s for _, s in loo_scores]
    ig_vec = [s for _, s in ig_scores]
    lime_vec = [s for _, s in lime_scores]
    shap_vec = [s for _, s in shap_scores]

    # Calculate Pearson Correlation Matrix
    methods = {
        "LOO (Leave-One-Out)": loo_scores,
        "Integrated Gradients": ig_scores,
        "LIME": lime_scores,
        "SHAP": shap_scores,
    }

    vectors = {
        "LOO": loo_vec,
        "Integrated Gradients": ig_vec,
        "LIME": lime_vec,
        "SHAP": shap_vec,
    }

    correlation_matrix = {}
    keys = list(vectors.keys())
    for i in range(len(keys)):
        for j in range(i, len(keys)):
            k1, k2 = keys[i], keys[j]
            corr = compute_pearson_correlation(vectors[k1], vectors[k2])
            pair_key = f"{k1} vs {k2}"
            correlation_matrix[pair_key] = round(corr, 4)

    return {
        "words": words,
        "methods": methods,
        "correlation_matrix": correlation_matrix,
    }

def what_if_swap(text, target_word, replacement_word, classifier):
    """
    Swaps a target word with a replacement word in the text, recalculates the suicide risk probability,
    and returns a comparison dictionary showing the de-escalation impact.
    """
    pattern = re.compile(rf'\b{re.escape(target_word)}\b', re.IGNORECASE)
    modified_text = pattern.sub(replacement_word, text)
    
    orig_prob = classifier.predict_proba(text)["probabilities"][1]
    mod_prob = classifier.predict_proba(modified_text)["probabilities"][1]
    diff = mod_prob - orig_prob
    
    return {
        "original_text": text,
        "modified_text": modified_text,
        "original_probability": float(orig_prob),
        "modified_probability": float(mod_prob),
        "probability_delta": float(diff),
        "deescalated": bool(diff < 0)
    }


