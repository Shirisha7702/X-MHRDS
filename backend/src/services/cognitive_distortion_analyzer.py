import re
from config import settings as config

# The ten cognitive distortions catalogued in Beck's cognitive therapy and popularized by
# Burns ("Feeling Good"). Each category is a list of case-insensitive regex patterns mixing
# single trigger words and short phrases -- phrases are more precise than lone words, so
# they're preferred wherever the distortion has a recognizable multi-word form.
COGNITIVE_DISTORTIONS = {
    "All-or-Nothing Thinking": [
        r"\bcomplete(?:ly)? (?:failure|disaster|worthless)\b",
        r"\btotal(?:ly)? (?:failure|disaster|worthless|ruined)\b",
        r"\butterly (?:worthless|hopeless|useless)\b",
        r"\ball or nothing\b",
        r"\bperfect(?:ly)?\b",
        r"\bruined everything\b",
    ],
    "Overgeneralization": [
        r"\balways\b",
        r"\bnever\b",
        r"\bevery (?:single )?time\b",
        r"\ball the time\b",
        r"\bconstantly\b",
        r"\bagain and again\b",
        r"\bas usual\b",
        r"\btypical\b",
    ],
    "Mental Filter": [
        r"\bonly thing (?:i can think|that matters)\b",
        r"\ball i can think about\b",
        r"\bcan'?t stop thinking about\b",
        r"\bnothing good\b",
        r"\bnothing ever goes right\b",
    ],
    "Disqualifying the Positive": [
        r"\bdoesn'?t count\b",
        r"\bnot a big deal\b",
        r"\bjust (?:luck|lucky)\b",
        r"\bwasn'?t (?:really|actually)\b",
        r"\banyone (?:could|would) have\b",
        r"\bit was nothing\b",
    ],
    "Jumping to Conclusions": [
        r"\b(?:he|she|they|everyone) (?:thinks?|knows?) (?:i'?m|i am)\b",
        r"\bmust think i'?m\b",
        r"\bprobably thinks?\b",
        r"\bi just know\b",
        r"\bbound to (?:fail|happen)\b",
        r"\bgoing to (?:fail|go wrong|end badly)\b",
        r"\bwill never\b",
    ],
    "Magnification / Catastrophizing": [
        r"\bdisaster\b",
        r"\bcatastrophe\b",
        r"\bworst thing\b",
        r"\bend of the world\b",
        r"\bruined my life\b",
        r"\bcan'?t handle this\b",
        r"\bunbearable\b",
        r"\bfalling apart\b",
        r"\bit'?s all over\b",
    ],
    "Emotional Reasoning": [
        r"\bi feel like (?:i'?m|i am) (?:worthless|stupid|useless|a failure|a burden)\b",
        r"\bit feels? true\b",
        r"\bmust be true because i feel\b",
        r"\bmy feelings? prove\b",
    ],
    "Should Statements": [
        r"\bshould(?:n'?t)?\b",
        r"\bmust\b",
        r"\bhave to\b",
        r"\bought to\b",
        r"\bsupposed to\b",
    ],
    "Labeling": [
        r"\bi'?m (?:such )?(?:a |an )?(?:failure|loser|idiot|stupid|worthless|burden|broken|mess|pathetic|useless)\b",
        r"\bi am (?:such )?(?:a |an )?(?:failure|loser|idiot|stupid|worthless|burden|broken|mess|pathetic|useless)\b",
        r"\bsuch an? (?:idiot|loser|failure|mess)\b",
    ],
    "Personalization": [
        r"\bmy fault\b",
        r"\bbecause of me\b",
        r"\bi caused\b",
        r"\bi ruined\b",
        r"\bif only i had\b",
        r"\bi'?m to blame\b",
        r"\bbetter off without me\b",
    ],
}


def analyze_distortions(text):
    """
    Detects cognitive-distortion patterns (Beck/Burns taxonomy) present in a piece of text.

    Args:
        text: raw or cleaned text to scan.

    Returns:
        dict[str, dict]: category name -> {"score": float, "matches": list[str]}, for every
        category with at least one match. "score" is the match count normalized by word
        count, in the same style as EmotionAnalyzer, so scores are comparable across texts
        of different lengths.
    """
    if not isinstance(text, str) or not text.strip():
        return {}

    word_count = max(len(text.split()), 1)
    results = {}

    for category, patterns in COGNITIVE_DISTORTIONS.items():
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text, flags=re.IGNORECASE))
        if matches:
            results[category] = {
                "score": len(matches) / word_count,
                "matches": matches,
            }

    return results


def get_dominant_distortions(text, top_n=None, min_score=None):
    """
    Ranks detected distortions by score and returns the top N category names that clear
    the reporting threshold, for use in downstream clinical-response drafting.
    """
    top_n = config.DISTORTION_TOP_N if top_n is None else top_n
    min_score = config.DISTORTION_MIN_SCORE_TO_REPORT if min_score is None else min_score

    scored = analyze_distortions(text)
    ranked = sorted(scored.items(), key=lambda kv: kv[1]["score"], reverse=True)
    return [category for category, data in ranked if data["score"] >= min_score][:top_n]


if __name__ == "__main__":
    samples = [
        "I always fail at everything, I'm such a failure and it's all my fault.",
        "He must think I'm pathetic. This is a complete disaster and I can't handle it.",
        "I should have known better. I'm to blame for ruining everything.",
        "Just finished dinner, cooking pizza. Recommend a good anime to watch tonight?",
    ]
    for sample in samples:
        print(f"\nText: {sample}")
        print("Dominant distortions:", get_dominant_distortions(sample))
