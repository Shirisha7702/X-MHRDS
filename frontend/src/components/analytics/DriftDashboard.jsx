import React, { useEffect, useState, useCallback } from 'react';
import { fetchDriftMetrics } from '../../services/apiClient';
import { Activity, AlertTriangle, ShieldCheck, RefreshCw, BarChart2 } from 'lucide-react';

export default function DriftDashboard() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);

  const loadMetrics = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetchDriftMetrics();
      setData(res);
    } catch (err) {
      console.error('Failed to load drift metrics', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadMetrics();
  }, [loadMetrics]);

  const getAlertBadge = (level, status) => {
    if (level === 'red') {
      return (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', background: 'var(--color-danger-bg)', color: 'var(--color-danger)', padding: '0.4rem 0.8rem', borderRadius: '20px', fontWeight: 700, fontSize: '0.85rem' }}>
          <AlertTriangle size={16} /> {status}
        </span>
      );
    }
    if (level === 'amber') {
      return (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', background: 'var(--color-warning-bg)', color: 'var(--color-warning)', padding: '0.4rem 0.8rem', borderRadius: '20px', fontWeight: 700, fontSize: '0.85rem' }}>
          <AlertTriangle size={16} /> {status}
        </span>
      );
    }
    return (
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', background: 'var(--color-success-bg)', color: 'var(--color-success)', padding: '0.4rem 0.8rem', borderRadius: '20px', fontWeight: 700, fontSize: '0.85rem' }}>
        <ShieldCheck size={16} /> {status}
      </span>
    );
  };

  const alertColor = (level) => level === 'red' ? 'var(--color-danger)' : level === 'amber' ? 'var(--color-warning)' : 'var(--color-success)';

  return (
    <div className="glass-card drift-dashboard" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Activity size={24} style={{ color: 'var(--color-brand)' }} />
          <div>
            <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-primary)' }}>Model Drift & Population Stability (PSI)</h3>
            <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Monitors statistical prediction probability drift between baseline evaluation and live streams.
            </p>
          </div>
        </div>
        <button className="btn-secondary" onClick={loadMetrics} disabled={loading} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <RefreshCw className={loading ? 'spin' : ''} size={16} />
          <span>Refresh Drift Data</span>
        </button>
      </div>

      {data && (
        <div style={{ display: 'grid', gap: '1.25rem' }}>
          {/* Top Status Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
            <div style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border-card)', padding: '1rem', borderRadius: '8px', borderLeft: `4px solid ${alertColor(data.alert_level)}` }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Population Stability Index (PSI)</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)' }}>{data.psi_score.toFixed(4)}</div>
              <div style={{ marginTop: '0.5rem' }}>{getAlertBadge(data.alert_level, data.drift_status)}</div>
            </div>

            <div style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border-card)', padding: '1rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Evaluated Sample Sizes</div>
              <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>Baseline: {data.sample_sizes?.baseline_samples || 0} posts</div>
              <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--color-brand)' }}>Live Stream: {data.sample_sizes?.stream_samples || 0} posts</div>
            </div>

            <div style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border-card)', padding: '1rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Automated Recommendation</div>
              <div style={{ fontSize: '0.85rem', lineHeight: '1.4', color: 'var(--text-primary)' }}>{data.recommendation}</div>
            </div>
          </div>

          {/* Histogram Breakdown */}
          <div style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border-card)', padding: '1rem', borderRadius: '8px' }}>
            <h4 style={{ margin: '0 0 1rem 0', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-primary)' }}>
              <BarChart2 size={16} />
              <span>Risk Probability Distribution Shift (Baseline vs Live Stream)</span>
            </h4>
            <div style={{ display: 'grid', gap: '0.6rem' }}>
              {data.histogram?.map((item) => (
                <div key={item.range} style={{ display: 'grid', gridTemplateColumns: '80px 1fr 1fr', gap: '1rem', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}>Range {item.range}</span>
                  <div style={{ background: 'var(--color-info-bg)', color: 'var(--text-primary)', padding: '0.4rem', borderRadius: '4px', fontSize: '0.75rem' }}>
                    Baseline: {item.baseline}
                  </div>
                  <div style={{ background: 'rgba(168, 85, 247, 0.16)', color: 'var(--text-primary)', padding: '0.4rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600 }}>
                    Stream: {item.stream}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
