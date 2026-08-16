import re
from typing import Dict, Any, List, Tuple

# Comprehensive multi-language keyword and common dictionary mappings for zero-dependency translation & alignment
LANGUAGE_NAMES = {
    "en": "English",
    "es": "Spanish (Español)",
    "fr": "French (Français)",
    "de": "German (Deutsch)",
    "hi": "Hindi (हिंदी)",
    "zh": "Chinese (中文)",
    "it": "Italian (Italiano)",
    "pt": "Portuguese (Português)",
    "ru": "Russian (Русский)",
    "ar": "Arabic (العربية)",
    "ja": "Japanese (日本語)",
    "ko": "Korean (한국어)",
}

# Detection indicators
LANGUAGE_INDICATORS = {
    "es": ["el", "la", "los", "las", "un", "una", "por", "que", "triste", "vida", "solo", "ayuda", "dolor", "morir", "suicidio"],
    "fr": ["le", "la", "les", "un", "une", "des", "du", "qui", "triste", "vie", "seul", "aide", "douleur", "mourir", "suicid"],
    "de": ["der", "die", "das", "ein", "eine", "nicht", "ich", "traurig", "leben", "allein", "hilfe", "schmerz", "sterben"],
    "hi": ["का", "की", "के", "में", "से", "है", "मुझे", "अकेला", "मदद", "दर्द", "मरना", "जिंदगी"],
    "zh": ["的", "是", "在", "我", "想", "死", "痛苦", "孤独", "绝望", "帮助", "生活"],
    "it": ["il", "la", "gli", "un", "una", "per", "che", "triste", "vita", "solo", "aiuto", "dolore", "morire"],
    "pt": ["o", "a", "os", "as", "um", "uma", "por", "que", "triste", "vida", "sozinho", "ajuda", "dor", "morrer"],
    "ru": ["и", "в", "не", "на", "я", "мне", "грустно", "жизнь", "один", "помощь", "боль", "умереть"],
    "ar": ["في", "من", "على", "أنا", "حزين", "حياة", "وحدي", "مساعدة", "ألم", "موت"],
    "ja": ["の", "に", "は", "を", "私", "悲しい", "人生", "孤独", "助けて", "死にたい"],
    "ko": ["의", "에", "를", "은", "는", "나", "슬픈", "삶", "외로운", "도움", "죽고싶다"],
}

# Common translation phrase mappings for demo/simulation accuracy
DICTIONARY_TRANSLATIONS = {
    "me siento solo y sin esperanza quiero morir": "I feel lonely and hopeless I want to die",
    "no puedo seguir con este dolor quiero terminar mi vida": "I cannot continue with this pain I want to end my life",
    "je me sens tellement seul et triste je veux mourir": "I feel so alone and sad I want to die",
    "ich bin so traurig und allein ich will nicht mehr leben": "I am so sad and alone I do not want to live anymore",
    "मुझे बहुत दर्द हो रहा है और मैं जीना नहीं चाहता": "I am in a lot of pain and I do not want to live",
    "我觉得活着没有意义我想结束生命": "I feel like living is meaningless I want to end my life",
}

def detect_language(text: str) -> Tuple[str, str]:
    """Detects the ISO language code and full name for input text."""
    clean_text = text.lower()
    words = set(re.findall(r'\w+', clean_text))
    scores = {}

    for lang, keywords in LANGUAGE_INDICATORS.items():
        if lang in ["zh", "ja", "ko", "hi", "ar", "ru"]:
            score = sum(1 for kw in keywords if kw in clean_text)
        else:
            score = sum(1 for kw in keywords if kw in words)
        
        if score > 0:
            scores[lang] = score

    if not scores:
        return "en", LANGUAGE_NAMES["en"]

    best_lang = max(scores, key=scores.get)
    return best_lang, LANGUAGE_NAMES.get(best_lang, "Unknown Language")


def translate_to_english(text: str, source_lang: str) -> str:
    """Translates text from source_lang to English."""
    if source_lang == "en":
        return text

    clean = text.lower().strip()
    if clean in DICTIONARY_TRANSLATIONS:
        return DICTIONARY_TRANSLATIONS[clean]

    # Try deep_translator if installed, fallback to heuristic mapping
    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source=source_lang, target="en").translate(text)
        if translated and len(translated.strip()) > 0:
            return translated
    except Exception:
        pass

    # Word-for-word replacement heuristic for fallback
    word_map = {
        # Spanish
        "me": "i", "siento": "feel", "solo": "alone", "triste": "sad", "dolor": "pain",
        "quiero": "want", "morir": "die", "vida": "life", "ayuda": "help", "sin": "without",
        "esperanza": "hope", "no": "no", "puedo": "can", "terminar": "end",
        # French
        "je": "i", "sens": "feel", "seul": "alone", "veux": "want", "mourir": "die",
        "vie": "life", "aide": "help", "douleur": "pain",
        # German
        "ich": "i", "bin": "am", "traurig": "sad", "allein": "alone", "will": "want", "leben": "live",
    }
    
    words = text.split()
    translated_words = [word_map.get(w.lower().strip(",.!?"), w) for w in words]
    return " ".join(translated_words)

def align_attributions_to_source(source_text: str, translated_text: str, translated_word_scores: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
    """
    Cross-lingual token alignment: Projects attribution weights computed on English translation
    back onto the original source language tokens proportionally.
    """
    source_words = source_text.split()

    if not source_words or not translated_word_scores:
        return []

    num_source = len(source_words)
    num_trans = len(translated_word_scores)

    aligned_scores = []
    for idx, word in enumerate(source_words):
        trans_idx = int(round((idx / float(num_source)) * (num_trans - 1)))
        trans_idx = min(max(0, trans_idx), num_trans - 1)
        score = translated_word_scores[trans_idx][1]
        aligned_scores.append((word, score))

    return aligned_scores

def process_multilingual_analysis(text: str) -> Dict[str, Any]:
    """Helper returning language metadata and translated text for pipeline processing."""
    source_lang, source_lang_name = detect_language(text)
    is_multilingual = (source_lang != "en")
    
    if is_multilingual:
        english_text = translate_to_english(text, source_lang)
    else:
        english_text = text

    return {
        "original_text": text,
        "is_multilingual": is_multilingual,
        "source_language_code": source_lang,
        "source_language_name": source_lang_name,
        "translated_text": english_text
    }
