import os
import sys
import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from config import settings as config

# Needed for the lazy `from baseline_models import ...` / `from transformer_models import
# ...` imports below when this module is run standalone (python -m services.
# construct_validity_auditor) rather than imported through routes.py/main.py, which
# already add this path themselves.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../ai_model/src')))

# Generic negative-affect vocabulary, deliberately disjoint from suicide/self-harm-specific
# crisis language ("kill", "suicide", "end my life", "pills", "plan", ...). Used to check
# whether a classifier's predicted risk is substantially explained by generic negativity
# rather than crisis-specific signal -- the construct-overlap failure mode described in
# Dehghan & Ashrafi (2026, arXiv:2607.10633), where an apparently-specific predictor turns
# out to be a proxy for a broader, less specific construct (there: trait anxiety vs.
# depression; here: generic sadness/negativity vs. suicide-specific risk language).
GENERAL_NEGATIVITY_LEXICON = {
    "bad", "terrible", "awful", "horrible", "worst", "miserable", "unhappy", "sad",
    "upset", "angry", "mad", "annoyed", "frustrated", "disappointed", "hate", "dislike",
    "hurt", "stressed", "stress", "tired", "exhausted", "worried", "anxious", "nervous",
    "lonely", "alone", "difficult", "hard", "struggle", "struggling", "pain", "painful",
    "cry", "crying", "tears", "down", "low", "rough", "sick", "ill", "sorry", "regret",
    "fear", "afraid", "scared", "hopeless", "helpless", "useless", "worthless", "burden",
}


def compute_negativity_score(text):
    """Fraction of a text's words that appear in the generic negative-affect lexicon."""
    if not isinstance(text, str) or not text.strip():
        return 0.0
    words = text.lower().split()
    if not words:
        return 0.0
    hits = sum(1 for w in words if w.strip(".,!?;:\"'") in GENERAL_NEGATIVITY_LEXICON)
    return hits / len(words)


def audit_construct_overlap(predict_fn, texts, labels):
    """
    Diagnoses how much of a classifier's predicted risk probability is explained by
    generic negative sentiment alone, versus signal specific to the target construct.

    Method: regress the model's predicted probability on a confound (generic negativity
    score) and inspect the residual -- the part of the prediction the confound can't
    explain. If that residual still correlates with the true label, the model carries
    genuine construct-specific signal beyond the confound; if the residual is essentially
    uncorrelated with the label while the raw prediction is, the model's apparent accuracy
    may largely be an artifact of detecting generic negativity rather than suicide risk
    specifically. This mirrors the residualization protocol of Dehghan & Ashrafi (2026),
    applied at the model-output level so it works identically for linear baselines and
    black-box transformers alike.

    Args:
        predict_fn: text -> P(risk) in [0, 1].
        texts: sequence of input strings.
        labels: sequence of true binary labels (0/1), aligned with texts.

    Returns:
        dict with:
            negativity_r2: R^2 of model_prob ~ negativity_score (variance in the model's
                output explained by the confound alone; higher means more overlap).
            residual_label_correlation: correlation of the regression residual with the
                true label (evidence of genuine signal beyond the confound).
            raw_label_correlation: correlation of the raw model probability with the true
                label, for reference -- the audit explains part of *why* the model gets
                there, it doesn't restate headline accuracy.
            n_samples: number of texts actually audited.
    """
    negativity = np.array([compute_negativity_score(t) for t in texts]).reshape(-1, 1)
    model_probs = np.array([predict_fn(t) for t in texts], dtype=float)
    label_arr = np.array(labels, dtype=float)

    reg = LinearRegression()
    reg.fit(negativity, model_probs)
    predicted_from_negativity = reg.predict(negativity)
    residual = model_probs - predicted_from_negativity

    negativity_r2 = float(reg.score(negativity, model_probs))
    residual_label_correlation = float(np.corrcoef(residual, label_arr)[0, 1]) if np.std(residual) > 0 else 0.0
    raw_label_correlation = float(np.corrcoef(model_probs, label_arr)[0, 1]) if np.std(model_probs) > 0 else 0.0

    return {
        "negativity_r2": negativity_r2,
        "residual_label_correlation": residual_label_correlation,
        "raw_label_correlation": raw_label_correlation,
        "n_samples": len(texts),
    }


def run_construct_validity_audit():
    """
    Runs the construct-overlap audit across every available trained model on a random
    sample of the held-out test split, and saves the results for the /api/construct-audit
    route and the Analytics dashboard.
    """
    if not os.path.exists(config.TEST_DATA_PATH):
        print("Test data splits not found. Run preprocessing.py first.")
        return

    test_df = pd.read_csv(config.TEST_DATA_PATH).dropna(subset=["cleaned_text"])
    sample_size = min(config.CONSTRUCT_AUDIT_SAMPLE_SIZE, len(test_df))
    sample_df = test_df.sample(n=sample_size, random_state=config.RANDOM_STATE)
    texts = sample_df["cleaned_text"].tolist()
    labels = sample_df["label"].tolist()

    results = {}

    lr_path = os.path.join(config.MODELS_DIR, "logistic_regression.pkl")
    svm_path = os.path.join(config.MODELS_DIR, "svm_classifier.pkl")
    vec_path = os.path.join(config.MODELS_DIR, "tfidf_vectorizer.pkl")

    if os.path.exists(lr_path) and os.path.exists(vec_path):
        print("Auditing Logistic Regression...")
        from baseline_models import BaselineClassifier
        clf = BaselineClassifier(lr_path, vec_path)
        results["Logistic Regression"] = audit_construct_overlap(
            lambda t: clf.predict_proba(t)["probabilities"][1], texts, labels
        )

    if os.path.exists(svm_path) and os.path.exists(vec_path):
        print("Auditing SVM...")
        from baseline_models import BaselineClassifier
        clf = BaselineClassifier(svm_path, vec_path)
        results["SVM (Calibrated LinearSVC)"] = audit_construct_overlap(
            lambda t: clf.predict_proba(t)["probabilities"][1], texts, labels
        )

    bert_dir = os.path.join(config.MODELS_DIR, "bert_model")
    if os.path.exists(os.path.join(bert_dir, "config.json")):
        print("Auditing BERT...")
        from transformer_models import TransformerClassifier
        clf = TransformerClassifier(bert_dir)
        results["BERT (Fine-tuned)"] = audit_construct_overlap(
            lambda t: clf.predict_proba(t)["probabilities"][1], texts, labels
        )

    roberta_dir = os.path.join(config.MODELS_DIR, "roberta_model")
    if not os.path.exists(roberta_dir):
        roberta_dir = os.path.join(config.MODELS_DIR, "roberta-base")
    if os.path.exists(os.path.join(roberta_dir, "config.json")):
        print("Auditing RoBERTa...")
        from transformer_models import TransformerClassifier
        clf = TransformerClassifier(roberta_dir)
        results["RoBERTa (Fine-tuned)"] = audit_construct_overlap(
            lambda t: clf.predict_proba(t)["probabilities"][1], texts, labels
        )

    audit_path = os.path.join(config.MODELS_DIR, "construct_validity_audit.pkl")
    with open(audit_path, "wb") as f:
        pickle.dump(results, f)

    print(f"\nConstruct-validity audit saved to {audit_path}")
    for model_name, res in results.items():
        print(f"\n{model_name}:")
        print(f"  Negativity R^2:              {res['negativity_r2']:.4f}")
        print(f"  Residual-label correlation:  {res['residual_label_correlation']:.4f}")
        print(f"  Raw model-label correlation: {res['raw_label_correlation']:.4f}")


if __name__ == "__main__":
    run_construct_validity_audit()
