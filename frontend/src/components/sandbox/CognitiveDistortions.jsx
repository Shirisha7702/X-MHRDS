import React from 'react';

export default function CognitiveDistortions({ distortions }) {
  const entries = Object.entries(distortions || {}).sort((a, b) => b[1].score - a[1].score);

  if (entries.length === 0) {
    return <em style={{ color: 'var(--text-muted)' }}>No cognitive distortion patterns detected.</em>;
  }

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
      {entries.map(([category, data]) => (
        <span
          key={category}
          title={`Matched: ${[...new Set(data.matches)].join(', ')}`}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.35rem 0.7rem',
            borderRadius: '999px',
            fontSize: '0.78rem',
            background: 'var(--color-warning-bg)',
            color: 'var(--color-warning)',
            border: '1px solid var(--color-warning)',
            cursor: 'help',
          }}
        >
          {category}
          <span style={{ color: 'var(--text-muted)', fontSize: '0.72rem' }}>&times;{data.matches.length}</span>
        </span>
      ))}
    </div>
  );
}
