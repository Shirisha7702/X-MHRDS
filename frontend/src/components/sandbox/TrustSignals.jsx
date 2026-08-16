import React from 'react';

// ln(2), the max possible entropy for a 2-class predictive distribution -- used to
// normalize predictive entropy onto a 0-100% "how much do the dropout passes disagree" scale.
const MAX_BINARY_ENTROPY = Math.log(2);

function uncertaintyLabel(normalized) {
  if (normalized >= 0.66) return { text: 'High', color: 'var(--color-danger)' };
  if (normalized >= 0.33) return { text: 'Medium', color: 'var(--color-warning)' };
  return { text: 'Low', color: 'var(--color-success)' };
}

export default function TrustSignals({ ood, uncertainty }) {
  if (!ood && !uncertainty) return null;

  return (
    <div style={{ marginBottom: '1.5rem' }}>
      <div style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
        Trust Signals (transformer models only):
      </div>
      <div className="stats-cards-container">
        {ood && (
          <div className="stat-metric-card">
            <div className="label">Domain Check</div>
            <div className="value" style={{ color: ood.is_out_of_distribution ? 'var(--color-danger)' : 'var(--color-success)' }}>
              {ood.is_out_of_distribution === null ? 'Uncalibrated' : ood.is_out_of_distribution ? 'Out-of-Distribution' : 'In-Distribution'}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
              Energy {ood.energy.toFixed(3)}{ood.threshold !== null ? ` (threshold ${ood.threshold.toFixed(3)})` : ''}
            </div>
          </div>
        )}
        {uncertainty && (() => {
          const normalized = Math.min(uncertainty.predictive_entropy / MAX_BINARY_ENTROPY, 1.0);
          const label = uncertaintyLabel(normalized);
          return (
            <div className="stat-metric-card">
              <div className="label">Predictive Uncertainty (MC-Dropout)</div>
              <div className="value" style={{ color: label.color }}>{label.text}</div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                Entropy {uncertainty.predictive_entropy.toFixed(3)} over {uncertainty.n_passes} passes
              </div>
            </div>
          );
        })()}
      </div>
    </div>
  );
}
