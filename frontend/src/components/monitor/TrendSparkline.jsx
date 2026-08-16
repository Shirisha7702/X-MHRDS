import React from 'react';

const WIDTH = 120;
const HEIGHT = 32;
const PAD = 5;

const ACCENT_BY_TREND = {
  Escalating: 'var(--color-danger)',
  Stable: 'var(--color-brand)',
  'De-escalating': 'var(--color-success)',
};

export default function TrendSparkline({ history, trendLabel, changePointIndex }) {
  if (!history || history.length < 2) {
    return <span style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>Not enough data yet</span>;
  }

  const accent = ACCENT_BY_TREND[trendLabel] || 'var(--text-secondary)';
  const usableHeight = HEIGHT - PAD * 2;
  const stepX = WIDTH / (history.length - 1);

  const points = history.map((value, idx) => {
    const x = idx * stepX;
    const y = PAD + (1 - value) * usableHeight;
    return [x, y];
  });

  const polylinePoints = points.map(([x, y]) => `${x},${y}`).join(' ');
  const [lastX, lastY] = points[points.length - 1];

  const hasChangePoint = typeof changePointIndex === 'number' && changePointIndex >= 0 && changePointIndex < history.length;
  const changePointX = hasChangePoint ? changePointIndex * stepX : null;

  const summary = `Risk trend: ${trendLabel}, from ${(history[0] * 100).toFixed(0)}% to ${(history[history.length - 1] * 100).toFixed(0)}% over ${history.length} posts`
    + (hasChangePoint ? `; sharp shift detected at post ${changePointIndex + 1}` : '');

  return (
    <svg
      width={WIDTH}
      height={HEIGHT}
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      role="img"
      aria-label={summary}
    >
      {hasChangePoint && (
        <line
          x1={changePointX}
          y1={0}
          x2={changePointX}
          y2={HEIGHT}
          style={{ stroke: 'var(--color-warning)', strokeWidth: 1, opacity: 0.7 }}
        />
      )}
      <polyline
        points={polylinePoints}
        style={{ fill: 'none', stroke: 'var(--text-muted)', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round' }}
      />
      {/* Surface-color ring so the end-marker stays legible where it meets the line. */}
      <circle cx={lastX} cy={lastY} r={6} style={{ fill: 'var(--bg-card)' }} />
      <circle cx={lastX} cy={lastY} r={4} style={{ fill: accent }} />
    </svg>
  );
}
