import os
import sys
# Add backend src dir to PYTHONPATH for config, anonymizer, etc.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend/src')))

import argparse
import pickle
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_cosine_schedule_with_warmup
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from config import settings as config
from calibration import compute_ece, fit_temperature, apply_temperature


class EMA:
    """
    Exponential Moving Average of model parameters (Polyak averaging). Maintaining a
    running average of weights across training steps and evaluating/deploying that
    average rather than the raw final-step weights measurably stabilizes fine-tuning
    against noisy late-training updates, at the cost of one shadow copy of the
    trainable parameters in memory.
    """
    def __init__(self, model, decay):
        self.decay = decay
        self.shadow = {
            name: param.detach().clone()
            for name, param in model.named_parameters() if param.requires_grad
        }

    def update(self, model):
        for name, param in model.named_parameters():
            if param.requires_grad:
                self.shadow[name].mul_(self.decay).add_(param.detach(), alpha=1 - self.decay)

    def apply_to(self, model):
        """Copies the EMA shadow weights into the given model's parameters, in-place."""
        with torch.no_grad():
            for name, param in model.named_parameters():
                if name in self.shadow:
                    param.copy_(self.shadow[name])

class MentalHealthDataset(Dataset):
    """Custom PyTorch Dataset for Mental Health Text Classification."""
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]

        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )

        return {
            'text': text,
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(label, dtype=torch.long)
        }

def train_epoch(model, data_loader, optimizer, scheduler, device, scaler=None, ema=None):
    """Performs one training epoch, optionally under mixed precision (when `scaler` is a
    live GradScaler) and updating an EMA shadow of the weights after every step."""
    model.train()
    total_loss = 0
    use_amp = scaler is not None and scaler.is_enabled()

    for d in data_loader:
        input_ids = d['input_ids'].to(device)
        attention_mask = d['attention_mask'].to(device)
        labels = d['label'].to(device)

        optimizer.zero_grad()

        with torch.autocast(device_type=device.type, enabled=use_amp):
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            loss = outputs.loss

        if use_amp:
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

        scheduler.step()
        total_loss += loss.item()

        if ema is not None:
            ema.update(model)

    return total_loss / len(data_loader)


def evaluate_with_ema(model, ema, data_loader, device):
    """Evaluates using the EMA-averaged weights without disturbing the live training
    weights: stash the raw state, swap in the EMA shadow, evaluate, restore the raw
    state so training can continue from where it left off."""
    raw_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
    ema.apply_to(model)
    metrics = evaluate_model(model, data_loader, device)
    model.load_state_dict(raw_state)
    return metrics


def save_with_ema_weights(model, ema, tokenizer, save_dir):
    """Saves the EMA-averaged weights as the checkpoint, then restores the model's live
    training weights so the caller can keep training uninterrupted."""
    raw_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
    ema.apply_to(model)
    model.save_pretrained(save_dir)
    tokenizer.save_pretrained(save_dir)
    model.load_state_dict(raw_state)


def collect_energies(model, data_loader, device, temperature):
    """Energy-based OOD score (Liu et al., 2020) for every example in a data loader:
    E(x) = -T * logsumexp(logits / T). Lower energy indicates a more in-distribution,
    confident prediction; higher energy indicates a more anomalous input."""
    model.eval()
    energies = []
    with torch.no_grad():
        for d in data_loader:
            input_ids = d['input_ids'].to(device)
            attention_mask = d['attention_mask'].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            batch_energy = -temperature * torch.logsumexp(outputs.logits / temperature, dim=1)
            energies.extend(batch_energy.cpu().tolist())
    return np.array(energies)

def evaluate_model(model, data_loader, device):
    """Evaluates the model and returns loss, accuracy, precision, recall, and f1 score."""
    model.eval()
    losses = []
    predictions = []
    real_values = []

    with torch.no_grad():
        for d in data_loader:
            input_ids = d['input_ids'].to(device)
            attention_mask = d['attention_mask'].to(device)
            labels = d['label'].to(device)

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )

            loss = outputs.loss
            losses.append(loss.item())

            _, preds = torch.max(outputs.logits, dim=1)
            predictions.extend(preds.cpu().tolist())
            real_values.extend(labels.cpu().tolist())

    acc = accuracy_score(real_values, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(real_values, predictions, average='binary')
    cm = confusion_matrix(real_values, predictions)

    return np.mean(losses), acc, precision, recall, f1, cm

def collect_probabilities(model, data_loader, device):
    """Runs the model over a data loader and returns (prob_of_class_1, true_labels) arrays,
    used for fitting temperature-scaling calibration."""
    model.eval()
    probs = []
    real_values = []

    with torch.no_grad():
        for d in data_loader:
            input_ids = d['input_ids'].to(device)
            attention_mask = d['attention_mask'].to(device)
            labels = d['label'].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            batch_probs = torch.softmax(outputs.logits, dim=1)[:, 1]

            probs.extend(batch_probs.cpu().tolist())
            real_values.extend(labels.cpu().tolist())

    return np.array(probs), np.array(real_values)

def train_transformer(model_type, quick_mode=False):
    # Setup Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Configure model metadata
    if model_type == "bert":
        model_name = config.BERT_MODEL_NAME
        save_dir = os.path.join(config.MODELS_DIR, "bert_model")
        metrics_key = "bert_metrics"
    else:
        model_name = config.ROBERTA_MODEL_NAME
        save_dir = os.path.join(config.MODELS_DIR, "roberta-base" if "roberta" in model_name else "roberta_model")
        metrics_key = "roberta_metrics"
        
    print(f"Fine-tuning model: {model_name}")
    os.makedirs(save_dir, exist_ok=True)

    # Load splits
    train_df = pd.read_csv(config.TRAIN_DATA_PATH)
    val_df = pd.read_csv(config.VAL_DATA_PATH)
    test_df = pd.read_csv(config.TEST_DATA_PATH)

    # Subsample data if quick mode
    if quick_mode:
        print("Quick mode active. Limiting datasets to 100 train, 30 val, 30 test samples...")
        train_df = train_df.sample(min(100, len(train_df)), random_state=42).reset_index(drop=True)
        val_df = val_df.sample(min(30, len(val_df)), random_state=42).reset_index(drop=True)
        test_df = test_df.sample(min(30, len(test_df)), random_state=42).reset_index(drop=True)

    # Initialize tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    train_dataset = MentalHealthDataset(
        texts=train_df['cleaned_text'].values,
        labels=train_df['label'].values,
        tokenizer=tokenizer,
        max_len=config.MAX_LEN
    )
    val_dataset = MentalHealthDataset(
        texts=val_df['cleaned_text'].values,
        labels=val_df['label'].values,
        tokenizer=tokenizer,
        max_len=config.MAX_LEN
    )
    test_dataset = MentalHealthDataset(
        texts=test_df['cleaned_text'].values,
        labels=test_df['label'].values,
        tokenizer=tokenizer,
        max_len=config.MAX_LEN
    )

    train_loader = DataLoader(train_dataset, batch_size=config.BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config.BATCH_SIZE, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=config.BATCH_SIZE, shuffle=False)

    # Initialize model
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    model = model.to(device)

    # Training Setup
    epochs = 1 if quick_mode else config.EPOCHS
    optimizer = AdamW(model.parameters(), lr=config.LEARNING_RATE)
    total_steps = len(train_loader) * epochs
    warmup_steps = int(config.WARMUP_RATIO * total_steps)
    scheduler = get_cosine_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_steps
    )
    use_amp = device.type == "cuda" and config.USE_MIXED_PRECISION
    scaler = torch.amp.GradScaler(device.type, enabled=use_amp)
    ema = EMA(model, config.EMA_DECAY)

    print(f"Warmup steps: {warmup_steps}/{total_steps} | Mixed precision: {use_amp} | EMA decay: {config.EMA_DECAY}")

    best_f1 = 0

    for epoch in range(epochs):
        print(f"Epoch {epoch + 1}/{epochs}")
        print("-" * 10)

        train_loss = train_epoch(model, train_loader, optimizer, scheduler, device, scaler=scaler, ema=ema)
        print(f"Train loss {train_loss:.4f}")

        # Evaluate using the EMA-averaged weights, since those (not the raw noisy
        # current-step weights) are what gets saved and deployed.
        val_loss, val_acc, val_precision, val_recall, val_f1, _ = evaluate_with_ema(model, ema, val_loader, device)
        print(f"Val (EMA) loss {val_loss:.4f} | Accuracy {val_acc:.4f} | F1 {val_f1:.4f}")

        # Select the checkpoint by validation F1 rather than accuracy: F1 penalizes a
        # model that leans on the majority class, which plain accuracy can mask.
        if val_f1 > best_f1:
            print("New best validation F1 (EMA weights)! Saving model weights...")
            save_with_ema_weights(model, ema, tokenizer, save_dir)
            best_f1 = val_f1

    # Test final evaluation
    print("\nRunning final evaluation on test set...")
    # Load best weights
    best_model = AutoModelForSequenceClassification.from_pretrained(save_dir)
    best_model = best_model.to(device)
    
    test_loss, test_acc, test_precision, test_recall, test_f1, test_cm = evaluate_model(best_model, test_loader, device)
    
    print("\n" + "="*30)
    print(f"Final Test Evaluation for {model_type.upper()}")
    print("="*30)
    print(f"Accuracy: {test_acc:.4f}")
    print(f"Precision: {test_precision:.4f}")
    print(f"Recall: {test_recall:.4f}")
    print(f"F1-Score: {test_f1:.4f}")
    print("Confusion Matrix:")
    print(test_cm)
    
    # Save metrics
    metrics_path = os.path.join(config.MODELS_DIR, f"{metrics_key}.pkl")
    with open(metrics_path, "wb") as f:
        pickle.dump({
            "model_name": model_type.upper(),
            "accuracy": test_acc,
            "precision": test_precision,
            "recall": test_recall,
            "f1_score": test_f1,
            "confusion_matrix": test_cm
        }, f)

    # Fit temperature-scaling calibration on validation predictions (never test, to avoid
    # overfitting the calibrator to the same split used for the final reported metrics).
    val_probs, val_labels = collect_probabilities(best_model, val_loader, device)
    ece_before = compute_ece(val_probs, val_labels)
    temperature = fit_temperature(val_probs, val_labels)
    ece_after = compute_ece(apply_temperature(val_probs, temperature), val_labels)
    print(f"Calibration for {model_type.upper()}: T={temperature:.4f} | ECE {ece_before:.4f} -> {ece_after:.4f}")

    calibration_path = os.path.join(config.MODELS_DIR, f"{metrics_key}_calibration.pkl")
    with open(calibration_path, "wb") as f:
        pickle.dump({
            "temperature": temperature,
            "ece_before": ece_before,
            "ece_after": ece_after,
        }, f)

    # Calibrate an energy-based OOD threshold (Liu et al., 2020) from the in-distribution
    # validation set: at inference, an input whose energy exceeds this threshold is flagged
    # as anomalous/off-domain rather than scored as if it were a normal post.
    val_energies = collect_energies(best_model, val_loader, device, config.OOD_ENERGY_TEMPERATURE)
    ood_threshold = float(np.percentile(val_energies, config.OOD_PERCENTILE_THRESHOLD))
    print(f"OOD energy threshold ({config.OOD_PERCENTILE_THRESHOLD}th pct of val energies): {ood_threshold:.4f}")

    ood_path = os.path.join(config.MODELS_DIR, f"{metrics_key}_ood.pkl")
    with open(ood_path, "wb") as f:
        pickle.dump({
            "temperature": config.OOD_ENERGY_TEMPERATURE,
            "threshold": ood_threshold,
            "val_energy_mean": float(val_energies.mean()),
            "val_energy_std": float(val_energies.std()),
        }, f)

class TransformerClassifier:
    """Wrapper class for prediction/inference using fine-tuned transformer models."""
    def __init__(self, model_dir, device=None):
        self.device = device if device else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading transformer classifier from {model_dir} on {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        self.model = self.model.to(self.device)
        self.model.eval()

    def _encode(self, text):
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=config.MAX_LEN,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )
        return encoding['input_ids'].to(self.device), encoding['attention_mask'].to(self.device)

    def _forward_logits(self, text):
        input_ids, attention_mask = self._encode(text)
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
        return outputs.logits.flatten()

    def predict_proba(self, text):
        """Returns predictions and class probabilities for a given string."""
        logits = self._forward_logits(text)
        probs = torch.softmax(logits, dim=0)
        prediction = torch.argmax(probs).item()

        # Format class probabilities
        return {
            "prediction": prediction, # 0 = Non-suicide, 1 = Suicide
            "probabilities": probs.cpu().tolist() # [prob_0, prob_1]
        }

    def compute_energy(self, text, temperature=None):
        """
        Energy-based out-of-distribution score (Liu et al., 2020):
        E(x) = -T * logsumexp(logits / T), computed from raw (pre-softmax) logits.
        Lower energy indicates a more in-distribution, confident prediction; higher
        energy indicates a more anomalous input. Compare against a threshold calibrated
        from the validation set's energy distribution (see collect_energies / the
        `{model}_ood.pkl` artifact) rather than an arbitrary cutoff.
        """
        temperature = config.OOD_ENERGY_TEMPERATURE if temperature is None else temperature
        logits = self._forward_logits(text)
        energy = -temperature * torch.logsumexp(logits / temperature, dim=0)
        return float(energy.item())

    def predict_with_uncertainty(self, text, n_passes=None):
        """
        Monte Carlo Dropout predictive uncertainty: runs n_passes stochastic forward
        passes with dropout layers kept active (everything else stays in eval mode), and
        returns the mean class-1 probability plus the predictive entropy of the averaged
        distribution as an uncertainty measure. High entropy means the model's dropout
        subnetworks disagree with each other -- a signal distinct from (and complementary
        to) calibrated confidence, which only reflects a single deterministic pass.
        """
        n_passes = config.MC_DROPOUT_PASSES if n_passes is None else n_passes
        input_ids, attention_mask = self._encode(text)

        self.model.eval()
        for module in self.model.modules():
            if isinstance(module, torch.nn.Dropout):
                module.train()

        all_probs = []
        with torch.no_grad():
            for _ in range(n_passes):
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                probs = torch.softmax(outputs.logits, dim=1).flatten()
                all_probs.append(probs.cpu().numpy())

        self.model.eval()  # restore full eval mode (dropout off) for subsequent calls

        all_probs = np.stack(all_probs)  # shape (n_passes, 2)
        mean_probs = all_probs.mean(axis=0)
        eps = 1e-12
        predictive_entropy = float(-np.sum(mean_probs * np.log(mean_probs + eps)))

        return {
            "mean_probabilities": mean_probs.tolist(),
            "predictive_entropy": predictive_entropy,
            "std_prob_class1": float(all_probs[:, 1].std()),
            "n_passes": n_passes,
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train BERT or RoBERTa for mental health risk classification.")
    parser.add_argument("--model", type=str, default="bert", choices=["bert", "roberta"], help="Model type to train.")
    parser.add_argument("--quick", action="store_true", help="Run in quick mode with limited dataset subset and epochs.")
    args = parser.parse_args()

    train_transformer(args.model, args.quick)
