import numpy as np
from scipy.optimize import minimize_scalar

EPS = 1e-7


def _logit(probs):
    p = np.clip(np.asarray(probs, dtype=float), EPS, 1 - EPS)
    return np.log(p / (1 - p))


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def compute_ece(probs, labels, n_bins=10):
    """
    Computes the binned Expected Calibration Error: the weighted average gap
    between predicted confidence and observed accuracy across confidence bins.
    """
    probs = np.asarray(probs, dtype=float)
    labels = np.asarray(labels, dtype=float)
    preds = (probs >= 0.5).astype(float)
    correct = (preds == labels).astype(float)

    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    confidences = np.where(probs >= 0.5, probs, 1 - probs)

    ece = 0.0
    n = len(probs)
    for i in range(n_bins):
        lo, hi = bin_edges[i], bin_edges[i + 1]
        in_bin = (confidences > lo) & (confidences <= hi) if i > 0 else (confidences >= lo) & (confidences <= hi)
        bin_count = in_bin.sum()
        if bin_count == 0:
            continue
        bin_acc = correct[in_bin].mean()
        bin_conf = confidences[in_bin].mean()
        ece += (bin_count / n) * abs(bin_acc - bin_conf)

    return float(ece)


def fit_temperature(probs, labels):
    """
    Fits a scalar temperature T minimizing negative log-likelihood of
    sigmoid(logit(probs) / T) against the true binary labels.
    """
    logits = _logit(probs)
    labels = np.asarray(labels, dtype=float)

    def nll(T):
        T = max(T, EPS)
        calibrated = _sigmoid(logits / T)
        calibrated = np.clip(calibrated, EPS, 1 - EPS)
        return -np.mean(labels * np.log(calibrated) + (1 - labels) * np.log(1 - calibrated))

    result = minimize_scalar(nll, bounds=(0.05, 10.0), method="bounded")
    return float(result.x)


def apply_temperature(probs, temperature):
    """Rescales probabilities by dividing their logit-transform by a fitted temperature."""
    logits = _logit(probs)
    calibrated = _sigmoid(logits / max(temperature, EPS))
    return float(calibrated) if np.isscalar(probs) else calibrated
