import pytest
from services.rag_copilot import ClinicalRAGCopilotEngine


@pytest.fixture(autouse=True)
def no_live_gemini_calls(monkeypatch):
    """Keeps this test hermetic: force the template fallback path instead of making a
    real network call to Gemini on every test run."""
    monkeypatch.setattr("services.rag_copilot.generate_text", lambda *a, **k: None)


def test_rag_query():
    text = "I feel so hopeless and I bought pills to end my life tonight."
    res = ClinicalRAGCopilotEngine.query_rag_knowledge(text, 0.85, "hopelessness")

    assert "rag_citations" in res
    assert "dsm5_matches" in res
    assert "cssrs_protocol" in res
    assert res["cssrs_protocol"]["level"].startswith("C-SSRS")
    assert res["narrative_source"] == "template"
    assert res["grounded_summary"]


def test_rag_query_uses_gemini_narrative_when_available(monkeypatch):
    monkeypatch.setattr(
        "services.rag_copilot.generate_text",
        lambda *a, **k: "Clinician-facing rationale grounded in the retrieved criteria.",
    )
    text = "I feel so hopeless and I bought pills to end my life tonight."
    res = ClinicalRAGCopilotEngine.query_rag_knowledge(text, 0.85, "hopelessness")

    assert res["narrative_source"] == "gemini"
    assert res["grounded_summary"] == "Clinician-facing rationale grounded in the retrieved criteria."
