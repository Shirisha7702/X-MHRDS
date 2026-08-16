import pytest
from services.translation import detect_language, translate_to_english, align_attributions_to_source

def test_language_detection():
    lang_es, name_es = detect_language("me siento triste y solo quiero morir")
    assert lang_es == "es"

    lang_en, name_en = detect_language("I feel hopeless and tired")
    assert lang_en == "en"

def test_translation():
    translated = translate_to_english("me siento solo y sin esperanza quiero morir", "es")
    assert "feel" in translated.lower() or "die" in translated.lower()

def test_token_alignment():
    source = "me siento solo"
    translated = "I feel alone"
    trans_scores = [("I", 0.1), ("feel", 0.4), ("alone", 0.8)]

    aligned = align_attributions_to_source(source, translated, trans_scores)
    assert len(aligned) == 3
    assert aligned[0][0] == "me"
