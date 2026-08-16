import os
import sys
import random
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from config import settings as config

# Needed for the lazy `from baseline_models import ...` / `from transformer_models import
# ...` imports below when this module is run standalone (python -m services.robustness)
# rather than imported through routes.py/main.py, which already add this path themselves.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../ai_model/src')))

# Set random seed for consistency
random.seed(config.RANDOM_STATE)
np.random.seed(config.RANDOM_STATE)

def inject_typos(text, rate=0.15):
    """
    Randomly injects typos into the text by swapping adjacent characters
    or dropping characters.
    """
    if not isinstance(text, str) or not text:
        return text
        
    words = text.split()
    perturbed_words = []
    
    for word in words:
        if len(word) > 3 and random.random() < rate:
            # Choose typo type: 0 = swap adjacent, 1 = drop char, 2 = double char
            typo_type = random.choice([0, 1, 2])
            idx = random.randint(1, len(word) - 2)
            
            if typo_type == 0:
                # Swap adjacent chars
                word_list = list(word)
                word_list[idx], word_list[idx+1] = word_list[idx+1], word_list[idx]
                word = "".join(word_list)
            elif typo_type == 1:
                # Drop char
                word = word[:idx] + word[idx+1:]
            elif typo_type == 2:
                # Double char
                word = word[:idx] + word[idx] + word[idx:]
                
        perturbed_words.append(word)
        
    return " ".join(perturbed_words)

def add_distracting_text(text):
    """
    Appends a positive/distracting statement to the end of the text to test
    if the classifier is vulnerable to distracting context.
    """
    distractions = [
        "Anyway, I'm going to watch a comedy movie now and eat pizza.",
        "I hope tomorrow is a sunny day for my run.",
        "By the way, my dog learned a new trick today!",
        "On the bright side, I had a very delicious lunch.",
        "I will just study for my computer science test now."
    ]
    distraction = random.choice(distractions)
    return f"{text} {distraction}"

def evaluate_robustness_on_dataset(test_df, classifier):
    """
    Evaluates the model on:
    1. Original test data
    2. Test data with typos
    3. Test data with distracting text
    Returns a dictionary of performance metrics.
    """
    texts = test_df["cleaned_text"].fillna("").tolist()
    labels = test_df["label"].tolist()
    
    # 1. Generate perturbed texts
    typo_texts = [inject_typos(t) for t in texts]
    distracted_texts = [add_distracting_text(t) for t in texts]
    
    # 2. Get predictions using unified predict_proba interface
    preds_orig = [classifier.predict_proba(t)["prediction"] for t in texts]
    preds_typo = [classifier.predict_proba(t)["prediction"] for t in typo_texts]
    preds_distracted = [classifier.predict_proba(t)["prediction"] for t in distracted_texts]
        
    # 3. Calculate metrics
    def get_metrics(y_true, y_pred):
        acc = accuracy_score(y_true, y_pred)
        p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)
        return {"accuracy": acc, "precision": p, "recall": r, "f1_score": f1}
        
    results = {
        "original": get_metrics(labels, preds_orig),
        "typos": get_metrics(labels, preds_typo),
        "distracted": get_metrics(labels, preds_distracted)
    }
    
    return results

def run_robustness_suite():
    """Runs robustness suite across all available trained models and saves the results."""
    # Load test set
    if not os.path.exists(config.TEST_DATA_PATH):
        print("Test data splits not found. Run preprocessing.py first.")
        return
        
    test_df = pd.read_csv(config.TEST_DATA_PATH)
    
    results = {}
    
    # Check baseline models
    lr_path = os.path.join(config.MODELS_DIR, "logistic_regression.pkl")
    svm_path = os.path.join(config.MODELS_DIR, "svm_classifier.pkl")
    vec_path = os.path.join(config.MODELS_DIR, "tfidf_vectorizer.pkl")
    
    if os.path.exists(lr_path) and os.path.exists(vec_path):
        print("Running robustness evaluation on Logistic Regression...")
        from baseline_models import BaselineClassifier
        classifier = BaselineClassifier(lr_path, vec_path)
        results["logistic_regression"] = evaluate_robustness_on_dataset(test_df, classifier)
        
    if os.path.exists(svm_path) and os.path.exists(vec_path):
        print("Running robustness evaluation on SVM...")
        from baseline_models import BaselineClassifier
        classifier = BaselineClassifier(svm_path, vec_path)
        results["svm"] = evaluate_robustness_on_dataset(test_df, classifier)
        
    # Check Transformer models
    bert_dir = os.path.join(config.MODELS_DIR, "bert_model")
    if os.path.exists(os.path.join(bert_dir, "config.json")):
        print("Running robustness evaluation on BERT...")
        from transformer_models import TransformerClassifier
        classifier = TransformerClassifier(bert_dir)
        results["bert"] = evaluate_robustness_on_dataset(test_df, classifier)
        
    roberta_dir = os.path.join(config.MODELS_DIR, "roberta_model")
    if not os.path.exists(roberta_dir):
        roberta_dir = os.path.join(config.MODELS_DIR, "roberta-base")
        
    if os.path.exists(os.path.join(roberta_dir, "config.json")):
        print("Running robustness evaluation on RoBERTa...")
        from transformer_models import TransformerClassifier
        classifier = TransformerClassifier(roberta_dir)
        results["roberta"] = evaluate_robustness_on_dataset(test_df, classifier)
        
    # Save results to disk
    robustness_metrics_path = os.path.join(config.MODELS_DIR, "robustness_metrics.pkl")
    with open(robustness_metrics_path, "wb") as f:
        pickle.dump(results, f)
        
    print(f"Robustness results successfully saved to {robustness_metrics_path}")
    
    # Print summary
    for model_name, res in results.items():
        print(f"\nModel: {model_name}")
        print(f"  Original   F1: {res['original']['f1_score']:.4f} | Recall: {res['original']['recall']:.4f}")
        print(f"  With Typos F1: {res['typos']['f1_score']:.4f} | Recall: {res['typos']['recall']:.4f}")
        print(f"  Distracted F1: {res['distracted']['f1_score']:.4f} | Recall: {res['distracted']['recall']:.4f}")

if __name__ == "__main__":
    run_robustness_suite()
