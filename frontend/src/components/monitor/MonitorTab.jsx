import React from 'react';
import TrendSparkline from './TrendSparkline';
import { Radio, Play, Square, TrendingUp, AlertTriangle } from 'lucide-react';

const TREND_COLOR = {
  Escalating: 'var(--color-danger)',
  Stable: 'var(--color-brand)',
  'De-escalating': 'var(--color-success)',
};

export default function MonitorTab({
  monitorRunning,
  monitorLoading,
  monitorEvents,
  modelChoice,
  handleStartMonitor,
  handleStopMonitor,
  userTrends = [],
}) {
  const alertCount = monitorEvents.filter((e) => (e.prob_suicide ?? 0) >= 0.5 || (e.tier_num ?? 0) >= 2).length;

  return (
    <div className="glass-grid">
      {/* Left Control Panel */}
      <div className="glass-card">
        <div className="card-title-group">
          <h2 className="card-title">
            <Radio size={18} />
            <span>Live Feed Stream Control</span>
          </h2>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Model: <strong>{modelChoice}</strong>
          </span>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '-0.5rem', marginBottom: '1.25rem' }}>
          Continuously monitors simulated post feeds via WebSocket connection, performing real-time risk triage.
        </p>

        <div className="metrics-hero-grid" style={{ marginBottom: '1.25rem' }}>
          <div className="hero-metric-card">
            <span className="metric-label">Monitor Status</span>
            <span className="metric-value-huge" style={{ color: monitorRunning ? 'var(--color-success)' : 'var(--text-muted)' }}>
              {monitorRunning ? 'LIVE' : 'OFFLINE'}
            </span>
          </div>

          <div className="hero-metric-card">
            <span className="metric-label">High Risk Alerts</span>
            <span className="metric-value-huge" style={{ color: alertCount > 0 ? 'var(--color-danger)' : 'var(--color-success)' }}>
              {alertCount}
            </span>
          </div>
        </div>

        {monitorRunning ? (
          <button className="btn-secondary" disabled={monitorLoading} onClick={handleStopMonitor} style={{ width: '100%', padding: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
            <Square size={16} />
            <span>{monitorLoading ? 'Stopping Monitor...' : 'Stop Live Monitoring'}</span>
          </button>
        ) : (
          <button className="btn-primary" disabled={monitorLoading} onClick={handleStartMonitor}>
            {monitorLoading ? (
              <>
                <div className="spinner-sm" />
                <span>Starting Stream...</span>
              </>
            ) : (
              <>
                <Play size={16} />
                <span>Start Live Stream ({modelChoice})</span>
              </>
            )}
          </button>
        )}
      </div>

      {/* Right Stream Feed Panel */}
      <div className="glass-card">
        <div className="card-title-group">
          <h2 className="card-title">
            <Radio size={18} />
            <span>Live Post Feed ({monitorEvents.length})</span>
          </h2>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '420px', overflowY: 'auto' }}>
          {monitorEvents.length > 0 ? (
            monitorEvents.map((ev, idx) => (
              <div
                key={idx}
                style={{
                  background: 'var(--bg-surface-2)',
                  border: ev.prob_suicide > 0.5 ? '1px solid rgba(255, 77, 109, 0.4)' : '1px solid var(--border-card)',
                  padding: '1rem',
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span
                    className="metric-badge"
                    style={{
                      backgroundColor: ev.prob_suicide > 0.5 ? 'var(--color-danger-bg)' : 'var(--color-success-bg)',
                      color: ev.prob_suicide > 0.5 ? 'var(--color-danger)' : 'var(--color-success)',
                    }}
                  >
                    {ev.tier_label || 'Analysis Event'}
                  </span>
                  <span style={{ fontSize: '0.82rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                    Risk: {((ev.prob_suicide ?? 0) * 100).toFixed(1)}%
                  </span>
                </div>
                <div style={{ fontSize: '0.88rem', color: 'var(--text-primary)', lineHeight: 1.4 }}>
                  "{ev.processed_text || ev.post || ev.raw_text}"
                </div>
                {ev.user_id && (
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                    User ID: {ev.user_id}
                  </div>
                )}
              </div>
            ))
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '3.5rem 1rem' }}>
              <Radio size={36} style={{ opacity: 0.4, marginBottom: '0.75rem' }} />
              <p style={{ margin: 0, fontWeight: 500 }}>Live monitoring stream offline.</p>
              <p style={{ fontSize: '0.85rem', margin: '6px 0 0 0' }}>Click "Start Live Stream" to begin receiving real-time posts.</p>
            </div>
          )}
        </div>
      </div>

      {/* Escalation Watch Table across full width */}
      <div className="glass-card" style={{ gridColumn: '1 / -1' }}>
        <div className="card-title-group">
          <h2 className="card-title">
            <TrendingUp size={18} />
            <span>User Escalation Watch &amp; Risk Trajectories</span>
          </h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '-0.5rem', marginBottom: '1.25rem' }}>
          Monitors user-level cumulative risk trajectories across sequential posts to detect sudden risk escalation.
        </p>

        {userTrends.length > 0 ? (
          <div className="ui-table-container">
            <table className="ui-table">
              <thead>
                <tr>
                  <th>User ID</th>
                  <th>Observed Posts</th>
                  <th>Latest Risk</th>
                  <th>Severity Tier</th>
                  <th>Trend Status</th>
                  <th>Sparkline Trajectory</th>
                </tr>
              </thead>
              <tbody>
                {userTrends.map((u) => (
                  <tr key={u.user_id}>
                    <td style={{ fontWeight: '700', fontFamily: 'var(--font-mono)', color: 'var(--color-brand)' }}>{u.user_id}</td>
                    <td><span className="cell-mono">{u.n_posts}</span></td>
                    <td>
                      <span className="cell-mono" style={{ color: u.latest_prob_suicide > 0.5 ? 'var(--color-danger)' : 'var(--color-success)' }}>
                        {(u.latest_prob_suicide * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td>
                      <span className="metric-badge metric-badge-primary">{u.latest_tier_label}</span>
                    </td>
                    <td>
                      <span
                        className="metric-badge"
                        style={{
                          backgroundColor: 'var(--bg-surface-2)',
                          color: TREND_COLOR[u.trend_label] || 'var(--text-primary)',
                          border: '1px solid var(--border-card)',
                        }}
                      >
                        {u.trend_label}
                      </span>
                    </td>
                    <td>
                      <TrendSparkline history={u.history} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem 0' }}>
            No user escalation history recorded yet.
          </p>
        )}
      </div>
    </div>
  );
}
