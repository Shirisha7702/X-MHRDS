import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add backend src dir to PYTHONPATH so `import main` resolves the same way uvicorn does.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/src')))

from main import app
import db

# TestClient (without a `with` block) doesn't reliably fire FastAPI's startup lifespan
# event across starlette versions, so initialize the DB explicitly here instead of
# depending on it.
db.init_db()

client = TestClient(app)

RISKY_TEXT = "I cannot take this anymore, I have a plan to end my life tonight. Goodbye everyone."
BENIGN_TEXT = "Just finished dinner, cooking pizza. Recommend a good anime to watch tonight?"

ALL_MODEL_CHOICES = [
    "Logistic Regression",
    "SVM (Calibrated LinearSVC)",
    "BERT (Fine-tuned)",
    "RoBERTa (Fine-tuned)",
]


def test_status():
    res = client.get("/api/status")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


@pytest.mark.parametrize("model_choice", ALL_MODEL_CHOICES)
def test_analyze_risky_text_all_models(model_choice):
    res = client.post("/api/analyze", json={
        "text": RISKY_TEXT,
        "model_choice": model_choice,
        "anonymize_active": True,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["prob_suicide"] > 0.5
    assert data["tier_num"] >= 1
    assert isinstance(data["word_scores"], list) and len(data["word_scores"]) > 0
    assert data["draft_response"]


def test_analyze_benign_text():
    res = client.post("/api/analyze", json={
        "text": BENIGN_TEXT,
        "model_choice": "Logistic Regression",
        "anonymize_active": True,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["prob_suicide"] < 0.5
    assert data["tier_num"] == 0


def test_analyze_empty_text_returns_400():
    res = client.post("/api/analyze", json={
        "text": "   ",
        "model_choice": "Logistic Regression",
        "anonymize_active": True,
    })
    assert res.status_code == 400


def test_analyze_anonymizer_masks_pii():
    res = client.post("/api/analyze", json={
        "text": "My name is John and my email is john@example.com. I feel hopeless.",
        "model_choice": "Logistic Regression",
        "anonymize_active": True,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["processed_text"] != data["raw_text"]
    assert "john@example.com" not in data["processed_text"]


def test_analyze_lime_explanation_on_baseline():
    res = client.post("/api/analyze", json={
        "text": RISKY_TEXT,
        "model_choice": "Logistic Regression",
        "anonymize_active": True,
        "explanation_method": "lime",
    })
    assert res.status_code == 200
    word_scores = res.json()["word_scores"]
    assert len(word_scores) > 0
    assert all(isinstance(word, str) and isinstance(score, float) for word, score in word_scores)


def test_analyze_shap_rejected_for_baseline_model():
    res = client.post("/api/analyze", json={
        "text": RISKY_TEXT,
        "model_choice": "Logistic Regression",
        "anonymize_active": True,
        "explanation_method": "shap",
    })
    assert res.status_code == 400


def test_analyze_shap_explanation_on_transformer():
    res = client.post("/api/analyze", json={
        "text": RISKY_TEXT,
        "model_choice": "BERT (Fine-tuned)",
        "anonymize_active": True,
        "explanation_method": "shap",
    })
    assert res.status_code == 200
    word_scores = res.json()["word_scores"]
    assert len(word_scores) > 0
    assert all(isinstance(score, float) for _token, score in word_scores)


def test_analyze_invalid_explanation_method_rejected():
    res = client.post("/api/analyze", json={
        "text": RISKY_TEXT,
        "model_choice": "Logistic Regression",
        "anonymize_active": True,
        "explanation_method": "not-a-real-method",
    })
    assert res.status_code == 422


def test_bert_and_roberta_give_different_predictions():
    """Regression test: 'RoBERTa' contains the substring 'BERT', which previously caused
    both model choices to silently route to the same BERT classifier."""
    bert_res = client.post("/api/analyze", json={
        "text": BENIGN_TEXT,
        "model_choice": "BERT (Fine-tuned)",
        "anonymize_active": True,
    }).json()
    roberta_res = client.post("/api/analyze", json={
        "text": BENIGN_TEXT,
        "model_choice": "RoBERTa (Fine-tuned)",
        "anonymize_active": True,
    }).json()
    assert bert_res["prob_suicide"] != roberta_res["prob_suicide"]


def test_what_if_deescalation():
    res = client.post("/api/what-if", json={
        "text": "I am feeling so hopeless and tired. I want to end my life tonight.",
        "target_word": "end my life",
        "replacement_word": "get help for my pain",
        "model_choice": "Logistic Regression",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["deescalated"] is True
    assert data["probability_delta"] < 0


def test_search_returns_relevant_case():
    """Regression test: routes.py previously called a non-existent engine.search() method."""
    res = client.post("/api/search", json={
        "query": "failing college exams and parent pressure",
        "top_n": 3,
    })
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0
    assert data[0]["id"] == "CASE-101"


def test_search_empty_query():
    res = client.post("/api/search", json={"query": "   ", "top_n": 3})
    assert res.status_code == 200
    assert res.json() == []


def test_robustness_metrics_structure():
    res = client.get("/api/robustness")
    assert res.status_code == 200
    data = res.json()
    assert "logistic_regression" in data
    for scenario in ("original", "typos", "distracted"):
        assert scenario in data["logistic_regression"]
        assert 0.0 <= data["logistic_regression"][scenario]["accuracy"] <= 1.0


def test_construct_validity_audit_structure():
    res = client.get("/api/construct-audit")
    assert res.status_code == 200
    data = res.json()
    assert "Logistic Regression" in data
    for model_name, result in data.items():
        assert 0.0 <= result["negativity_r2"] <= 1.0
        assert -1.0 <= result["residual_label_correlation"] <= 1.0
        assert result["n_samples"] > 0


def test_analyze_response_includes_cognitive_distortions():
    res = client.post("/api/analyze", json={
        "text": "I always fail at everything, it's all my fault and I'm such a failure.",
        "model_choice": "Logistic Regression",
        "anonymize_active": True,
    })
    assert res.status_code == 200
    data = res.json()
    assert "cognitive_distortions" in data
    assert "dominant_distortions" in data
    assert len(data["dominant_distortions"]) > 0
    assert "Overgeneralization" in data["cognitive_distortions"]


@pytest.mark.parametrize("model_choice", ["Logistic Regression", "SVM (Calibrated LinearSVC)"])
def test_fairness_audit(model_choice):
    res = client.get("/api/fairness", params={"model_choice": model_choice})
    assert res.status_code == 200
    data = res.json()

    assert data["min_subgroup_size"] == 30

    examples = data["examples"]
    assert len(examples) == 96
    assert all(
        row["Status"] in ("Correct", "False Negative (MISS)", "False Positive (FALSE ALARM)")
        for row in examples
    )

    cohort_summary = data["cohort_summary"]
    assert {row["cohort"] for row in cohort_summary} == {"Youth Slang", "Formal Language", "Literal / Direct"}
    for row in cohort_summary:
        assert row["n"] == 32
        for metric in ("accuracy", "recall", "specificity"):
            stats = row[metric]
            assert 0.0 <= stats["point"] <= 1.0
            assert stats["ci_low"] <= stats["point"] <= stats["ci_high"]
            # accuracy is computed over the full 32-example cohort (meets the n>=30 gate);
            # recall/specificity are each computed over a 16-example class subset (below it).
            assert stats["meets_min_subgroup_size"] == (metric == "accuracy")

    # fairness_gaps only ever cites cohorts/metrics that both meet the subgroup-size gate.
    for gap in data["fairness_gaps"]:
        assert gap["metric"] == "accuracy"


def test_model_comparison_metrics():
    res = client.get("/api/metrics")
    assert res.status_code == 200
    data = res.json()
    labels = {row["label"] for row in data}
    assert labels == set(ALL_MODEL_CHOICES)
    for row in data:
        for key in ("accuracy", "precision", "recall", "f1_score"):
            assert 0.0 <= row[key] <= 1.0


def test_temporal_trend_increases_toward_crisis():
    res = client.get("/api/temporal", params={"model_choice": "Logistic Regression"})
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 4
    # The timeline goes from a clearly benign post to clearly severe ones; the model isn't
    # perfect so we don't assert strict monotonicity, but the overall trend must be upward.
    assert data[0]["probability"] < data[-1]["probability"]
    assert data[0]["probability"] < 10
    assert data[-1]["probability"] > 40


def test_report_generation():
    res = client.post("/api/report", json={
        "raw_text": RISKY_TEXT,
        "processed_text": RISKY_TEXT,
        "model_choice": "Logistic Regression",
        "tier_label": "Severe Active Risk",
        "prob_suicide": 0.93,
        "tier_num": 3,
        "dominant_emotion": "sadness",
        "draft_response": "I hear how much pain you are in.",
    })
    assert res.status_code == 200
    assert "<html" in res.json()["html"].lower()
