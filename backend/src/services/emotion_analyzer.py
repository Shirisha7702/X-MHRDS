import re
import numpy as np
from logging_config import get_logger

logger = get_logger("emotion_analyzer")

# Emotion lexical terms
EMOTION_LEXICON = {
    "sadness": [
        "sad", "depressed", "unhappy", "cry", "crying", "tears", "grief", "pain", "hurt", 
        "lonely", "broken", "empty", "miserable", "sorrow", "alone"
    ],
    "anger": [
        "angry", "hate", "mad", "pissed", "furious", "annoyed", "frustrated", "rage", 
        "stupid", "idiot", "damn", "worst", "hate", "disgust"
    ],
    "fear": [
        "scared", "afraid", "terrified", "fear", "panic", "dread", "nightmare", "worry", 
        "worried", "shaking", "horror", "scary", "threatened"
    ],
    "hopelessness": [
        "hopeless", "useless", "worthless", "tired", "give up", "never", "pointless", 
        "stuck", "trapped", "fail", "failed", "failure", "burden", "care anymore"
    ],
    "anxiety": [
        "anxious", "stress", "stressed", "overwhelm", "overwhelmed", "nervous", "tension", 
        "panic attack", "breathless", "racing thoughts", "uneasy", "jittery"
    ],
    "joy": [
        "happy", "joy", "excited", "good", "great", "wonderful", "love", "smile", 
        "laugh", "fun", "glad", "blessed", "cheerful", "positive", "nice"
    ]
}

class EmotionAnalyzer:
    """Extracts fine-grained emotional distributions using lexical profiling."""
    def __init__(self, use_transformer=False):
        self.use_transformer = use_transformer
        self.classifier = None
        
        if use_transformer:
            try:
                from transformers import pipeline
                logger.info("Loading Hugging Face emotion classifier...")
                self.classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", top_k=None)
            except Exception:
                logger.exception("Failed to load HF emotion pipeline. Falling back to lexical profiling.")
                self.classifier = None
                
    def analyze_emotions(self, text):
        """
        Returns a dictionary of emotion probabilities.
        """
        if not isinstance(text, str) or not text.strip():
            return {emotion: 0.0 for emotion in EMOTION_LEXICON.keys()}
            
        # If transformer is active and loaded, run deep inference
        if self.use_transformer and self.classifier:
            try:
                # Output looks like [[{'label': 'sadness', 'score': 0.8}, {'label': 'joy', 'score': 0.1}, ...]]
                res = self.classifier(text)[0]
                emotions = {item['label']: float(item['score']) for item in res}
                
                # Check for hopelessness (often merged in sadness/fear) and map standard emotions
                if "hopelessness" not in emotions:
                    # Synthesize hopelessness score from sadness and lexical presence
                    lex_scores = self._lexical_profile(text)
                    emotions["hopelessness"] = min(emotions.get("sadness", 0.0) * 0.8, lex_scores.get("hopelessness", 0.0) * 1.5)
                return emotions
            except Exception:
                logger.exception("Transformer inference error. Falling back to lexical analysis.")
                
        # Standard Lexical profiling fallback
        return self._lexical_profile(text)
        
    def _lexical_profile(self, text):
        cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        words = cleaned_text.split()
        
        if not words:
            return {emotion: 0.0 for emotion in EMOTION_LEXICON.keys()}
            
        counts = {emotion: 0 for emotion in EMOTION_LEXICON.keys()}
        
        # Word counts checks
        for word in words:
            for emotion, keywords in EMOTION_LEXICON.items():
                if word in keywords:
                    counts[emotion] += 1
                    
        # Bigram match checks (e.g. "give up", "care anymore", "panic attack")
        for emotion, keywords in EMOTION_LEXICON.items():
            for phrase in keywords:
                if " " in phrase and phrase in cleaned_text:
                    counts[emotion] += 2
                    
        total_hits = sum(counts.values())
        
        # Normalize scores to look like probabilities
        if total_hits == 0:
            # Equal uniform distribution, or default bias towards mild neutral
            # If no matches, return very small defaults
            return {emotion: 0.05 for emotion in EMOTION_LEXICON.keys()}
            
        probs = {}
        for emotion, count in counts.items():
            probs[emotion] = float(count / total_hits)
            
        # Smooth and scale to make the visualization clean
        sum_probs = sum(probs.values())
        return {k: float(v / sum_probs) for k, v in probs.items()}

if __name__ == "__main__":
    analyzer = EmotionAnalyzer()
    
    test_1 = "I am so happy and excited today, everything is wonderful!"
    test_2 = "I feel so hopeless and sad. I am overwhelmed by anxiety and stress."
    
    print(f"Text 1: {test_1}")
    print("Emotions 1:", analyzer.analyze_emotions(test_1))
    print(f"\nText 2: {test_2}")
    print("Emotions 2:", analyzer.analyze_emotions(test_2))
