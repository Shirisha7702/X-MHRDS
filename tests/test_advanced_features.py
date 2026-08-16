import os
import sys
import pytest

# Add backend src, backend services, and ai_model src dirs to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/src/services')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../ai_model/src')))

from anonymizer import mask_pii
from multi_tier_classifier import MultiTierClassifier
from emotion_analyzer import EmotionAnalyzer
from clinical_helper import ClinicalResponseHelper
from semantic_search import CaseSearchEngine
from report_generator import ReportGenerator
from fairness_auditor import FairnessAuditor
from explainability import what_if_swap
from cognitive_distortion_analyzer import analyze_distortions, get_dominant_distortions
from construct_validity_auditor import compute_negativity_score, audit_construct_overlap

def test_anonymizer():
    """Verify that usernames, subreddits, emails, phone numbers, and names are correctly masked."""
    text = "Contact u/helper at test@email.com or r/help desk. Call 1-800-273-8255. I am John."
    anonymized = mask_pii(text)
    
    assert "[USER]" in anonymized
    assert "[EMAIL]" in anonymized
    assert "[SUBREDDIT]" in anonymized
    assert "[PHONE]" in anonymized
    assert "[NAME]" in anonymized

def test_multi_tier_classifier_rules():
    """Test manual rule tier assignments based on binary probabilities."""
    clf = MultiTierClassifier()
    
    # Check Tier 0
    res_0 = clf.predict_tier("nothing special", binary_prob=0.1)
    assert res_0["tier"] == 0
    assert res_0["label"] == "No Risk"
    
    # Check Tier 1
    res_1 = clf.predict_tier("feeling down", binary_prob=0.3)
    assert res_1["tier"] == 1
    assert res_1["label"] == "Mild Distress"

    # Check Tier 2
    res_2 = clf.predict_tier("wish I was gone", binary_prob=0.6)
    assert res_2["tier"] == 2
    assert res_2["label"] == "Moderate Risk"

    # Check Tier 3 escalation
    res_3 = clf.predict_tier("I am planning my suicide tonight, goodbye", binary_prob=0.85)
    assert res_3["tier"] == 3
    assert res_3["label"] == "Severe Active Risk"

def test_emotion_lexicon_analyzer():
    """Verify lexical emotion counts and normalization profiling."""
    analyzer = EmotionAnalyzer()
    
    # Joy sentence
    res_joy = analyzer.analyze_emotions("This is wonderful, I am happy and smiling!")
    assert res_joy["joy"] > res_joy["sadness"]
    
    # Sadness/Hopelessness sentence: sadness/hopelessness should dominate over joy within this text
    res_sad = analyzer.analyze_emotions("I feel sad and hopeless and tired.")
    assert res_sad["sadness"] + res_sad["hopelessness"] > res_sad["joy"]

def test_clinical_helper_drafts():
    """Check clinical guideline attachments and draft responses matches tiers."""
    helper = ClinicalResponseHelper()
    
    res_1 = helper.generate_draft(1, "anxiety")
    assert "stressed" in res_1["draft"] or "anxious" in res_1["draft"]
    
    res_3 = helper.generate_draft(3, "hopelessness")
    assert "988" in res_3["draft"]
    assert "emergency" in res_3["draft"]

def test_semantic_case_search():
    """Verify TF-IDF case similarity search index lookup."""
    engine = CaseSearchEngine()
    matches = engine.find_similar_cases("failing college exams and parent pressure")
    
    # CASE-101 is academic failure
    assert len(matches) > 0
    assert matches[0]["id"] == "CASE-101"

def test_what_if_swap():
    """Check probability change calculations when words are swapped."""
    # Mock classifier matching the BaselineClassifier/TransformerClassifier interface:
    # a single object exposing predict_proba(text) -> {"prediction": int, "probabilities": [p0, p1]}
    class MockClassifier:
        def predict_proba(self, text):
            if "end my life" in text:
                return {"prediction": 1, "probabilities": [0.1, 0.9]}
            return {"prediction": 0, "probabilities": [0.9, 0.1]}

    classifier = MockClassifier()

    res = what_if_swap(
        text="I want to end my life.",
        target_word="end my life",
        replacement_word="get help",
        classifier=classifier
    )

    assert res["deescalated"] is True
    assert res["probability_delta"] < 0


@pytest.mark.parametrize("text,expected_category", [
    ("I always fail at everything and it never gets better.", "Overgeneralization"),
    ("It's all my fault, I'm to blame for ruining everything.", "Personalization"),
    ("He must think I'm pathetic and everyone thinks I'm a joke.", "Jumping to Conclusions"),
    ("This is a complete disaster, I can't handle this catastrophe.", "Magnification / Catastrophizing"),
    ("I should have known better, I really must be more careful.", "Should Statements"),
    ("I'm such a failure, I'm a total loser.", "Labeling"),
])
def test_distortion_categories_detected(text, expected_category):
    """Each canonical distortion example should trigger its own named category."""
    results = analyze_distortions(text)
    assert expected_category in results
    assert results[expected_category]["score"] > 0
    assert len(results[expected_category]["matches"]) > 0


def test_distortion_analyzer_benign_text_returns_empty():
    results = analyze_distortions("Just finished dinner, cooking pizza tonight.")
    assert results == {}


def test_dominant_distortions_ranked_and_thresholded():
    text = "I always fail. I always mess up. It's my fault."
    dominant = get_dominant_distortions(text, top_n=1)
    # "always" appears twice (Overgeneralization) vs. one "my fault" (Personalization),
    # so Overgeneralization should outrank Personalization for the top-1 slot.
    assert dominant == ["Overgeneralization"]


def test_clinical_helper_reflects_dominant_distortion():
    """The draft response should weave in a gentle, non-diagnostic reflection of the
    top-ranked distortion, and stay unchanged when none is provided (backward compatible)."""
    helper = ClinicalResponseHelper()

    with_distortion = helper.generate_draft(2, "sadness", dominant_distortions=["Personalization"])
    assert "blame" in with_distortion["draft"].lower()

    without_distortion = helper.generate_draft(2, "sadness")
    assert "blame" not in without_distortion["draft"].lower()


def test_compute_negativity_score():
    assert compute_negativity_score("I feel sad and terrible and hopeless") > 0
    assert compute_negativity_score("Just finished dinner, cooking pizza tonight") == 0.0
    assert compute_negativity_score("") == 0.0


def test_construct_audit_detects_pure_confound_model():
    """A model whose output is purely a function of generic negativity (no real signal
    beyond it) should show near-total negativity R^2 and ~zero residual-label correlation."""
    texts = ["i feel sad and bad"] * 20 + ["this is fine and great"] * 20
    labels = ([1] * 10 + [0] * 10) * 2  # negativity uncorrelated with label by construction

    def pure_negativity_model(text):
        return compute_negativity_score(text)

    res = audit_construct_overlap(pure_negativity_model, texts, labels)
    assert res["negativity_r2"] > 0.9
    assert abs(res["residual_label_correlation"]) < 0.1
    assert res["n_samples"] == 40


def test_construct_audit_detects_genuine_signal_beyond_confound():
    """A model that only fires on crisis-specific wording (not just negativity) should
    show a real residual-label correlation surviving after the negativity confound is
    regressed out."""
    texts = (
        ["i feel sad and bad, i have a plan to end my life"] * 15  # negative + crisis -> label 1
        + ["i feel sad and bad about my exam"] * 15                 # negative only -> label 0
    )
    labels = [1] * 15 + [0] * 15

    def crisis_specific_model(text):
        crisis = 1.0 if "plan to end my life" in text else 0.0
        return crisis

    res = audit_construct_overlap(crisis_specific_model, texts, labels)
    assert res["residual_label_correlation"] > 0.5
