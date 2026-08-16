import React from 'react';

export default function WordImportance({ wordScores }) {
  if (!wordScores || wordScores.length === 0) {
    return <em style={{ color: 'var(--text-muted)' }}>No word attributions extracted.</em>;
  }

  return (
    <div className="xai-map-container">
      <div className="xai-header">
        <span className="form-label">XAI Local Word-Attribution Token Map</span>
        <div className="xai-legend">
          <div className="legend-item">
            <span className="legend-dot-risk" />
            <span>+ Risk Weight</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot-protective" />
            <span>- Protective Weight</span>
          </div>
        </div>
      </div>

      <div className="word-chips-flow">
        {wordScores.map(([word, score], idx) => {
          const normScore = Math.min(Math.abs(score), 1.0);
          let style = {
            backgroundColor: 'rgba(255, 255, 255, 0.04)',
            color: 'var(--text-secondary)',
            border: '1px solid var(--border-subtle)',
          };

          if (score > 0.01) {
            style = {
              backgroundColor: 'var(--color-danger-bg)',
              color: 'var(--color-danger)',
              border: '1px solid var(--color-danger)',
              opacity: 0.55 + 0.45 * normScore,
            };
          } else if (score < -0.01) {
            style = {
              backgroundColor: 'var(--color-success-bg)',
              color: 'var(--color-success)',
              border: '1px solid var(--color-success)',
              opacity: 0.55 + 0.45 * normScore,
            };
          }

          return (
            <span
              key={idx}
              className="word-chip"
              style={style}
              title={`Word: "${word}" | Attribution Weight: ${score > 0 ? '+' : ''}${score.toFixed(4)}`}
            >
              {word}
            </span>
          );
        })}
      </div>
    </div>
  );
}
