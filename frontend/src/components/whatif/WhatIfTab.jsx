import React from 'react';
import { GitCompare, Zap, BarChart3, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function WhatIfTab(props) {
  const whatIfText = props.whatIfText ?? '';
  const setWhatIfText = props.setWhatIfText ?? (() => {});
  const targetWord = props.targetWord ?? '';
  const setTargetWord = props.setTargetWord ?? (() => {});
  const replacementWord = props.replacementWord ?? '';
  const setReplacementWord = props.setReplacementWord ?? (() => {});
  const modelChoice = props.modelChoice ?? '';
  const whatIfLoading = props.whatIfLoading ?? false;
  const executeWhatIf = props.executeWhatIf ?? (() => {});
  const whatIfResult = props.whatIfResult ?? null;

  return (
    <div className="glass-grid">
      {/* Left Substitution Panel */}
      <div className="glass-card">
        <div className="card-title-group">
          <h2 className="card-title">
            <GitCompare size={18} />
            <span>Counterfactual Substitution</span>
          </h2>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Model: <strong>{modelChoice}</strong>
          </span>
        </div>

        <div className="form-group">
          <label className="form-label">Baseline Input Post</label>
          <textarea
            className="text-area"
            value={whatIfText}
            onChange={(e) => setWhatIfText(e.target.value)}
            placeholder="Type baseline sentence..."
          />
        </div>

        <div className="form-group" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div>
            <label className="form-label">Target Phrase to Swap</label>
            <input
              className="text-input"
              type="text"
              value={targetWord}
              onChange={(e) => setTargetWord(e.target.value)}
              placeholder="e.g., end my life"
            />
          </div>
          <div>
            <label className="form-label">Replacement Phrase</label>
            <input
              className="text-input"
              type="text"
              value={replacementWord}
              onChange={(e) => setReplacementWord(e.target.value)}
              placeholder="e.g., get help"
            />
          </div>
        </div>

        <button className="btn-primary" disabled={whatIfLoading} onClick={executeWhatIf}>
          {whatIfLoading ? (
            <>
              <div className="spinner-sm" />
              <span>Simulating Perturbation...</span>
            </>
          ) : (
            <>
              <Zap size={16} />
              <span>Evaluate Wording Substitution</span>
            </>
          )}
        </button>
      </div>

      {/* Right Output Panel */}
      <div className="glass-card">
        <div className="card-title-group">
          <h2 className="card-title">
            <BarChart3 size={18} />
            <span>Perturbation Sensitivity Assessment</span>
          </h2>
        </div>

        {whatIfResult ? (
          <>
            <div style={{ marginBottom: '1.25rem' }}>
              <span className="form-label">Modified Text Payload</span>
              <div
                style={{
                  background: 'var(--bg-surface-2)',
                  border: '1px solid var(--border-card)',
                  padding: '1rem',
                  borderRadius: 'var(--radius-md)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.9rem',
                  lineHeight: 1.5,
                  marginTop: '6px',
                }}
              >
                {whatIfResult.modified_text || whatIfResult.text}
              </div>
            </div>

            <div className="metrics-hero-grid">
              <div className="hero-metric-card">
                <span className="metric-label">Original Risk</span>
                <span className="metric-value-huge" style={{ color: 'var(--color-danger)' }}>
                  {((whatIfResult.original_probability ?? whatIfResult.original_prob ?? 0) * 100).toFixed(1)}%
                </span>
              </div>

              <div className="hero-metric-card">
                <span className="metric-label">Modified Risk</span>
                <span
                  className="metric-value-huge"
                  style={{
                    color:
                      (whatIfResult.modified_probability ?? whatIfResult.modified_prob ?? 0) > 0.5
                        ? 'var(--color-danger)'
                        : 'var(--color-success)',
                  }}
                >
                  {((whatIfResult.modified_probability ?? whatIfResult.modified_prob ?? 0) * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            <div
              style={{
                display: 'flex',
                justify: 'space-between',
                alignItems: 'center',
                padding: '12px 16px',
                background: 'var(--bg-surface-2)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-card)',
              }}
            >
              <div>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', fontWeight: '700', textTransform: 'uppercase' }}>Probability Delta</span>
                <div style={{ fontSize: '1.1rem', fontWeight: '800', fontFamily: 'var(--font-mono)', marginTop: '2px', color: 'var(--color-brand)' }}>
                  {(whatIfResult.probability_delta ?? whatIfResult.delta_prob ?? 0) > 0 ? '+' : ''}
                  {((whatIfResult.probability_delta ?? whatIfResult.delta_prob ?? 0) * 100).toFixed(2)}%
                </div>
              </div>

              <span
                className={`metric-badge ${
                  (whatIfResult.probability_delta ?? whatIfResult.delta_prob ?? 0) < 0
                    ? 'metric-badge-success'
                    : 'metric-badge-danger'
                }`}
                style={{ fontSize: '0.85rem', padding: '6px 14px', gap: '6px' }}
              >
                {(whatIfResult.probability_delta ?? whatIfResult.delta_prob ?? 0) < 0 ? (
                  <>
                    <CheckCircle2 size={14} />
                    <span>Risk De-escalated</span>
                  </>
                ) : (
                  <>
                    <AlertTriangle size={14} />
                    <span>Risk Escalated</span>
                  </>
                )}
              </span>
            </div>
          </>
        ) : (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '3.5rem 1rem' }}>
            <GitCompare size={36} style={{ opacity: 0.4, marginBottom: '0.75rem' }} />
            <p style={{ margin: 0, fontWeight: 500 }}>No counterfactual simulation evaluated yet.</p>
            <p style={{ fontSize: '0.85rem', margin: '6px 0 0 0' }}>Substitute target phrasing on the left to measure sensitivity delta.</p>
          </div>
        )}
      </div>
    </div>
  );
}
