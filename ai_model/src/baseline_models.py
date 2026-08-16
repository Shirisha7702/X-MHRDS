import os
import sys
# Add backend src dir to PYTHONPATH for config, anonymizer, etc.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend/src')))

import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
from config import settings as config
from calibration import compute_ece, fit_temperature, apply_temperature

def load_data():
    """Loads the preprocessed train, validation, and test sets."""
    if not (os.path.exists(config.TRAIN_DATA_PATH) and 
            os.path.exists(config.VAL_DATA_PATH) and 
            os.path.exists(config.TEST_DATA_PATH)):
        raise FileNotFoundError("Processed datasets not found. Please run preprocessing.py first.")
        
    train_df = pd.read_csv(config.TRAIN_DATA_PATH)
    val_df = pd.read_csv(config.VAL_DATA_PATH)
    test_df = pd.read_csv(config.TEST_DATA_PATH)
    
    # Fill any empty values
    train_df["cleaned_text"] = train_df["cleaned_text"].fillna("")
    val_df["cleaned_text"] = val_df["cleaned_text"].fillna("")
    test_df["cleaned_text"] = test_df["cleaned_text"].fillna("")
    
    return train_df, val_df, test_df

def train_baselines():
    # Load splits
    train_df, val_df, test_df = load_data()
    
    X_train, y_train = train_df["cleaned_text"], train_df["label"]
    X_val, y_val = val_df["cleaned_text"], val_df["label"]
    X_test, y_test = test_df["cleaned_text"], test_df["label"]
    
    print("Fitting TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(max_features=config.TFIDF_MAX_FEATURES, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_val_vec = vectorizer.transform(X_val)
    X_test_vec = vectorizer.transform(X_test)
    
    # 1. Train Logistic Regression
    print("Training Logistic Regression...")
    lr_model = LogisticRegression(max_iter=config.LR_MAX_ITER, random_state=config.RANDOM_STATE)
    lr_model.fit(X_train_vec, y_train)
    
    # 2. Train SVM (LinearSVC) wrapped in CalibratedClassifierCV to get predict_proba support
    print("Training SVM (Calibrated LinearSVC)...")
    base_svm = LinearSVC(C=config.SVM_C, random_state=config.RANDOM_STATE)
    svm_model = CalibratedClassifierCV(base_svm, cv=3)
    svm_model.fit(X_train_vec, y_train)
    
    # Evaluate Logistic Regression
    print("\n" + "="*30)
    print("Evaluating Logistic Regression")
    print("="*30)
    evaluate_model(lr_model, X_test_vec, y_test, "Logistic Regression")
    fit_and_save_calibration(lr_model, X_val_vec, y_val, "Logistic Regression")

    # Evaluate SVM
    print("\n" + "="*30)
    print("Evaluating SVM")
    print("="*30)
    evaluate_model(svm_model, X_test_vec, y_test, "SVM")
    fit_and_save_calibration(svm_model, X_val_vec, y_val, "SVM")
    
    # Save the models and vectorizer
    print("\nSaving baseline model artifacts...")
    with open(os.path.join(config.MODELS_DIR, "tfidf_vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)
    with open(os.path.join(config.MODELS_DIR, "logistic_regression.pkl"), "wb") as f:
        pickle.dump(lr_model, f)
    with open(os.path.join(config.MODELS_DIR, "svm_classifier.pkl"), "wb") as f:
        pickle.dump(svm_model, f)
        
    print("Baseline models trained and saved successfully.")

def evaluate_model(model, X_test, y_test, model_name):
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, preds, average="binary")
    cm = confusion_matrix(y_test, preds)
    
    print(classification_report(y_test, preds, target_names=["Non-Suicide", "Suicide"]))
    print("Confusion Matrix:")
    print(cm)
    print(f"Metrics summary for {model_name}:")
    print(f"Accuracy: {acc:.4f} | Precision: {precision:.4f} | Recall: {recall:.4f} | F1: {f1:.4f}")
    
    # Save metrics data to a file for comparison dashboard
    metrics_path = os.path.join(config.MODELS_DIR, f"{model_name.lower().replace(' ', '_')}_metrics.pkl")
    with open(metrics_path, "wb") as f:
        pickle.dump({
            "model_name": model_name,
            "accuracy": acc,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "confusion_matrix": cm
        }, f)

def fit_and_save_calibration(model, X_val, y_val, model_name):
    """Fits a temperature-scaling calibrator on validation predictions and saves it,
    along with ECE before/after, for use at inference time and in the analytics dashboard."""
    val_probs = model.predict_proba(X_val)[:, 1]
    ece_before = compute_ece(val_probs, y_val)
    temperature = fit_temperature(val_probs, y_val)
    ece_after = compute_ece(apply_temperature(val_probs, temperature), y_val)

    print(f"Calibration for {model_name}: T={temperature:.4f} | ECE {ece_before:.4f} -> {ece_after:.4f}")

    calibration_path = os.path.join(config.MODELS_DIR, f"{model_name.lower().replace(' ', '_')}_calibration.pkl")
    with open(calibration_path, "wb") as f:
        pickle.dump({
            "temperature": temperature,
            "ece_before": ece_before,
            "ece_after": ece_after,
        }, f)

class BaselineClassifier:
    """Wrapper class for prediction/inference using TF-IDF baseline models."""
    def __init__(self, model_path, vectorizer_path):
        print(f"Loading baseline classifier from {model_path}...")
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)
        with open(vectorizer_path, "rb") as f:
            self.vectorizer = pickle.load(f)
            
    def predict_proba(self, text):
        """Returns predictions and class probabilities for a given string."""
        if not text:
            text = ""
        vec = self.vectorizer.transform([text])
        prediction = int(self.model.predict(vec)[0])
        probs = self.model.predict_proba(vec)[0]
        return {
            "prediction": prediction, # 0 = Non-suicide, 1 = Suicide
            "probabilities": [float(p) for p in probs] # [prob_0, prob_1]
        }

if __name__ == "__main__":
    train_baselines()
