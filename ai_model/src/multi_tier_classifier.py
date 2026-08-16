import os
import sys
# Add backend src dir to PYTHONPATH for config, anonymizer, etc.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend/src')))

import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from config import settings as config

class MultiTierClassifier:
    """
    Classifies mental health risk into 4 clinical levels:
    - Tier 0: No Risk
    - Tier 1: Mild Distress
    - Tier 2: Moderate Risk (Passive Ideation)
    - Tier 3: Severe Active Risk (Active Intent)
    """
    def __init__(self, model_path=None, binary_model=None, vectorizer=None):
        self.model_path = model_path
        self.model = None
        self.vectorizer = vectorizer
        self.binary_model = binary_model
        
        # Load trained multi-class model if it exists
        if model_path and os.path.exists(model_path):
            try:
                with open(model_path, "rb") as f:
                    data = pickle.load(f)
                    self.model = data["model"]
                    self.vectorizer = data["vectorizer"]
                print(f"Successfully loaded trained multi-class model from {model_path}")
            except Exception as e:
                print(f"Error loading multi-class model: {e}. Falling back to threshold rules.")
                
    def train_multi_class_baseline(self, train_df, val_df):
        """
        Trains a baseline TF-IDF multi-class classifier using synthetic annotations
        for demonstration purposes, since Suicide Watch is binary.
        """
        print("Synthesizing multi-tier labels based on heuristics for training...")
        
        # Heuristic rules to assign Tiers 0-3 based on text search
        def assign_tier(row):
            text = str(row["cleaned_text"]).lower()
            label = row["label"]
            
            if label == 0:
                if any(w in text for w in ["stressed", "anxious", "sad", "exams", "crying", "lonely", "hate myself"]):
                    return 1 # Tier 1: Mild Distress
                return 0 # Tier 0: No Risk
            else:
                if any(w in text for w in ["goodbye", "tonight", "end it", "pills", "kill myself", "hanging", "plan"]):
                    return 3 # Tier 3: Severe Active Risk
                return 2 # Tier 2: Moderate Risk (Passive Ideation)
                
        train_df["tier"] = train_df.apply(assign_tier, axis=1)
        val_df["tier"] = val_df.apply(assign_tier, axis=1)
        
        print("Training multi-class vectorizer and model...")
        vec = TfidfVectorizer(max_features=config.TFIDF_MAX_FEATURES, ngram_range=(1, 2))
        X_train = vec.fit_transform(train_df["cleaned_text"].fillna(""))
        y_train = train_df["tier"]
        
        clf = LogisticRegression(max_iter=config.LR_MAX_ITER, random_state=config.RANDOM_STATE)
        clf.fit(X_train, y_train)
        
        self.model = clf
        self.vectorizer = vec
        
        # Save multi-class state
        if self.model_path:
            with open(self.model_path, "wb") as f:
                pickle.dump({"model": clf, "vectorizer": vec}, f)
            print(f"Multi-class model saved to {self.model_path}")
            
    def predict_tier(self, text, binary_prob=None):
        """
        Predicts the risk tier for a given text.
        Falls back to rule-based thresholding on the binary probability if no multi-class model is available.
        """
        text_lower = text.lower()
        
        # If multi-class model is loaded, use it
        if self.model and self.vectorizer:
            vec_text = self.vectorizer.transform([text])
            tier = int(self.model.predict(vec_text)[0])
            probs = self.model.predict_proba(vec_text)[0]
            
            tier_labels = ["No Risk", "Mild Distress", "Moderate Risk", "Severe Active Risk"]
            return {
                "tier": tier,
                "label": tier_labels[tier],
                "probabilities": [float(p) for p in probs]
            }
            
        # Fallback: Dynamic threshold rules on binary suicide probability
        if binary_prob is None:
            # Try to run binary inference if model is provided
            if self.binary_model and self.vectorizer:
                vec_text = self.vectorizer.transform([text])
                binary_prob = self.binary_model.predict_proba(vec_text)[0, 1]
            else:
                binary_prob = 0.0
                
        # Heuristics + thresholds
        if binary_prob < 0.2:
            tier = 0
            label = "No Risk"
        elif binary_prob < 0.5:
            tier = 1
            label = "Mild Distress"
        elif binary_prob < 0.8:
            tier = 2
            label = "Moderate Risk"
        else:
            # If high probability and contains active verbs, escalate to Tier 3
            if any(w in text_lower for w in ["goodbye", "hanging", "overdose", "pills", "tonight", "end it", "plan"]):
                tier = 3
                label = "Severe Active Risk"
            else:
                tier = 2
                label = "Moderate Risk"
                
        # Generate simulated multi-class probabilities based on tier position
        simulated_probs = [0.0] * 4
        simulated_probs[tier] = 0.7
        simulated_probs[(tier + 1) % 4] = 0.15
        simulated_probs[(tier - 1) % 4] = 0.15
        
        return {
            "tier": tier,
            "label": label,
            "probabilities": simulated_probs
        }

if __name__ == "__main__":
    # Test execution
    train_path = config.TRAIN_DATA_PATH
    val_path = config.VAL_DATA_PATH
    model_save_path = os.path.join(config.MODELS_DIR, "multi_tier_classifier.pkl")
    
    if os.path.exists(train_path) and os.path.exists(val_path):
        train_df = pd.read_csv(train_path)
        val_df = pd.read_csv(val_path)
        
        mt_clf = MultiTierClassifier(model_path=model_save_path)
        mt_clf.train_multi_class_baseline(train_df, val_df)
        
        # Test predict
        test_post = "I feel hopeless. I have a plan to end it all tonight."
        print(f"Text: {test_post}")
        print("Prediction:", mt_clf.predict_tier(test_post))
    else:
        print("Train/val splits not found. Run preprocessing.py first.")
