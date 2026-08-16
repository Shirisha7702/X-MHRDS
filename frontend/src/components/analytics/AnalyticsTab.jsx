import React from 'react';
import { BarChart3, Shield, Cpu } from 'lucide-react';

const pct = (value) => (value === null || value === undefined ? '—' : `${(value * 100).toFixed(1)}%`);

export default function AnalyticsTab(props) {
  const robustnessMetrics = props.robustnessMetrics ?? null;
  const robustnessLoading = props.robustnessLoading ?? false;
  const modelMetrics = props.modelMetrics ?? [];
  const modelMetricsLoading = props.modelMetricsLoading ?? false;

  return (
    <div className="glass-grid">
      {/* Left Model Performance Comparison Panel */}
      <div className="glass-card">
        <div className="card-title-group">
          <h2 className="card-title">
            <BarChart3 size={18} />
            <span>Model Performance Comparison</span>
          </h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '-0.5rem', marginBottom: '1rem' }}>
          Test-set evaluation metrics across baseline ML and fine-tuned Transformer classification engines.
        </p>

        {modelMetricsLoading ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', padding: '2rem 0' }}>
            <div className="spinner-sm" />
            <span>Loading evaluation benchmarks...</span>
          </div>
        ) : modelMetrics.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', padding: '2rem 0' }}>No trained model metrics found.</p>
        ) : (
          <div className="ui-table-container">
            <table className="ui-table">
              <thead>
                <tr>
                  <th>Classification Engine</th>
                  <th>Accuracy</th>
                  <th>Precision</th>
                  <th>Recall</th>
                  <th>F1 Score</th>
                </tr>
              </thead>
              <tbody>
                {modelMetrics.map((row) => (
                  <tr key={row.label || row.model || Math.random()}>
                    <td style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{row.label || row.model}</td>
                    <td><span className="metric-badge metric-badge-primary">{pct(row.accuracy)}</span></td>
                    <td><span className="metric-badge metric-badge-success">{pct(row.precision)}</span></td>
                    <td><span className="metric-badge metric-badge-warning">{pct(row.recall)}</span></td>
                    <td><span className="metric-badge metric-badge-success">{pct(row.f1_score)}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Right Perturbation Robustness Metrics Panel */}
      <div className="glass-card">
        <div className="card-title-group">
          <h2 className="card-title">
            <Shield size={18} />
            <span>Perturbation Robustness Metrics</span>
          </h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '-0.5rem', marginBottom: '1rem' }}>
          Model stability metrics evaluated against typo injections and distracting text perturbations.
        </p>

        {robustnessMetrics ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {Object.keys(robustnessMetrics).map((modelKey) => {
              const metrics = robustnessMetrics[modelKey];
              if (!metrics) return null;
              return (
                <div key={modelKey} style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border-card)', borderRadius: 'var(--radius-md)', padding: '1rem' }}>
                  <div style={{ fontWeight: '700', fontSize: '0.85rem', color: 'var(--color-brand)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.5px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Cpu size={15} />
                    <span>{modelKey.replace('_', ' ')}</span>
                  </div>
                  <div className="ui-table-container" style={{ marginTop: 0 }}>
                    <table className="ui-table">
                      <thead>
                        <tr>
                          <th>Scenario</th>
                          <th>Accuracy</th>
                          <th>Precision</th>
                          <th>Recall</th>
                          <th>F1 Score</th>
                        </tr>
                      </thead>
                      <tbody>
                        {['original', 'typos', 'distracted'].map((scenario) => {
                          const sec = metrics[scenario];
                          if (!sec) return null;
                          return (
                            <tr key={scenario}>
                              <td style={{ textTransform: 'capitalize', fontWeight: '600' }}>{scenario.replace('_', ' ')}</td>
                              <td><span className="cell-mono">{(sec.accuracy * 100).toFixed(1)}%</span></td>
                              <td><span className="cell-mono">{(sec.precision * 100).toFixed(1)}%</span></td>
                              <td><span className="cell-mono">{(sec.recall * 100).toFixed(1)}%</span></td>
                              <td><span className="cell-mono">{(sec.f1_score * 100).toFixed(1)}%</span></td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p style={{ color: 'var(--text-muted)', padding: '2rem 0' }}>Robustness metrics loaded.</p>
        )}
      </div>
    </div>
  );
}
