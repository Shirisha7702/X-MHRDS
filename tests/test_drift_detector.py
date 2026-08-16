import pytest
from services.drift_detector import calculate_psi, compute_model_drift_metrics

def test_psi_calculation():
    baseline = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    stream = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    psi = calculate_psi(baseline, stream)
    assert psi < 0.1

def test_drift_metrics_structure():
    metrics = compute_model_drift_metrics()
    assert "psi_score" in metrics
    assert "drift_status" in metrics
    assert "histogram" in metrics
