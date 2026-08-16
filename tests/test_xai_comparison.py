import pytest
from services.explainability import compute_pearson_correlation

def test_pearson_correlation():
    vec1 = [0.1, 0.5, 0.9, 0.2]
    vec2 = [0.1, 0.5, 0.9, 0.2]
    corr = compute_pearson_correlation(vec1, vec2)
    assert abs(corr - 1.0) < 1e-4

    vec3 = [0.9, 0.5, 0.1, 0.8]
    corr_inv = compute_pearson_correlation(vec1, vec3)
    assert corr_inv < 1.0
