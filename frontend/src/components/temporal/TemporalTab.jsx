import React from 'react';
import { Calendar, TrendingUp } from 'lucide-react';

export default function TemporalTab(props) {
  const temporalResults = props.temporalResults ?? [];
  const modelChoice = props.modelChoice ?? '';

  return (
    <div className="glass-grid">
      {/* Left Timeline Panel */}
      <div className="glass-card">
        <div className="card-title-group">
          <h2 className="card-title">
            <Calendar size={18} />
            <span>Simulated Post Timeline</span>
          </h2>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Model: <strong>{modelChoice}</strong>
          </span>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '-0.5rem', marginBottom: '1.25rem' }}>
          Chronological simulation of user posts tracking progressive distress trajectory.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', marginBottom: '1.25rem' }}>
          {temporalResults.length > 0 ? (
            temporalResults.map((ev, idx) => (
              <div
                key={idx}
                style={{
                  background: 'var(--bg-surface-2)',
                  border: '1px solid var(--border-card)',
                  padding: '1rem',
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Calendar size={13} />
                    <span>{ev.date}</span>
                  </span>
                  <span
                    className="metric-badge"
                    style={{
                      backgroundColor: ev.probability > 60 ? 'var(--color-danger-bg)' : ev.probability > 30 ? 'var(--color-warning-bg)' : 'var(--color-success-bg)',
                      color: ev.probability > 60 ? 'var(--color-danger)' : ev.probability > 30 ? 'var(--color-warning)' : 'var(--color-success)',
                    }}
                  >
                    Risk: {ev.probability.toFixed(1)}%
                  </span>
                </div>
                <div style={{ fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: 1.4 }}>
                  "{ev.post}"
                </div>
              </div>
            ))
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2.5rem 1rem' }}>
              <p>No temporal post events available.</p>
            </div>
          )}
        </div>
      </div>

      {/* Right Distress Escalation Plot Panel */}
      <div className="glass-card">
        <div className="card-title-group">
          <h2 className="card-title">
            <TrendingUp size={18} />
            <span>Distress Escalation Trajectory</span>
          </h2>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '-0.5rem', marginBottom: '1.25rem' }}>
          Suicide risk probability trajectory mapped chronologically across user timeline.
        </p>

        {temporalResults.length > 0 ? (
          <div style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border-card)', borderRadius: 'var(--radius-md)', padding: '1.25rem' }}>
            <svg className="chart-svg" viewBox="0 0 400 200">
              <defs>
                <linearGradient id="area-gradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--color-brand)" stopOpacity="0.35" />
                  <stop offset="100%" stopColor="var(--color-brand)" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {/* Axis Gridlines */}
              <line x1="45" y1="30" x2="375" y2="30" className="chart-grid-line" />
              <line x1="45" y1="75" x2="375" y2="75" className="chart-grid-line" />
              <line x1="45" y1="120" x2="375" y2="120" className="chart-grid-line" />
              <line x1="45" y1="165" x2="375" y2="165" className="chart-grid-line" />

              {/* Y Axis Labels */}
              <text x="10" y="34" fill="var(--text-muted)" fontSize="9" fontFamily="var(--font-mono)">100%</text>
              <text x="10" y="79" fill="var(--text-muted)" fontSize="9" fontFamily="var(--font-mono)">65%</text>
              <text x="10" y="124" fill="var(--text-muted)" fontSize="9" fontFamily="var(--font-mono)">35%</text>
              <text x="10" y="169" fill="var(--text-muted)" fontSize="9" fontFamily="var(--font-mono)">0%</text>

              {(() => {
                const step = (375 - 60) / Math.max(temporalResults.length - 1, 1);
                const points = temporalResults.map((res, idx) => ({
                  x: 60 + idx * step,
                  y: 165 - (res.probability / 100) * 135,
                  prob: res.probability,
                  date: res.date.slice(5),
                }));

                const lineD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
                const areaD = `${lineD} L ${points[points.length - 1].x} 165 L ${points[0].x} 165 Z`;

                return (
                  <g>
                    {/* Shaded Area */}
                    <path d={areaD} className="chart-area-path" />

                    {/* Glowing Stroke Line */}
                    <path d={lineD} className="chart-stroke-line" />

                    {/* Data Points & Tooltip Labels */}
                    {points.map((p, idx) => (
                      <g key={idx}>
                        <circle cx={p.x} cy={p.y} r="5" className="chart-dot-handle" />
                        <text
                          x={p.x}
                          y={p.y - 12}
                          fill="var(--text-primary)"
                          fontSize="9"
                          fontWeight="700"
                          fontFamily="var(--font-mono)"
                          textAnchor="middle"
                        >
                          {p.prob.toFixed(0)}%
                        </text>
                        <text
                          x={p.x}
                          y="185"
                          fill="var(--text-secondary)"
                          fontSize="9"
                          fontFamily="var(--font-sans)"
                          textAnchor="middle"
                        >
                          {p.date}
                        </text>
                      </g>
                    ))}
                  </g>
                );
              })()}
            </svg>
          </div>
        ) : (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '3rem 1rem' }}>
            <p>No temporal trajectory data loaded.</p>
          </div>
        )}
      </div>
    </div>
  );
}
