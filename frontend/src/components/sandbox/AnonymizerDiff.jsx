import React from 'react';

function highlightText(txt) {
  if (!txt) return '';
  const parts = txt.split(/(\[NAME\]|\[EMAIL\]|\[PHONE\]|\[USER\]|\[SUBREDDIT\])/i);
  return parts.map((part, idx) => {
    const token = part.toLowerCase();
    if (['[name]', '[email]', '[phone]', '[user]', '[subreddit]'].includes(token)) {
      return (
        <span key={idx} style={{ backgroundColor: 'var(--color-brand-glow)', color: 'var(--color-brand)', padding: '0.15rem 0.35rem', borderRadius: '4px', marginRight: '0.1rem', display: 'inline-block' }}>
          {part}
        </span>
      );
    }
    return part;
  });
}

export default function AnonymizerDiff({ text, showDiff, onToggle }) {
  if (!text) return null;

  const scrubbed = text
    .replace(/\b[rR]\/\w+\b/g, '[SUBREDDIT]')
    .replace(/\b[uU]\/\w+\b/g, '[USER]');

  return (
    <div className="diff-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div className="diff-title">Privacy Scrubbed Output Preview</div>
        <button className="btn-secondary" onClick={onToggle}>
          {showDiff ? 'Hide Preview' : 'Show Preview'}
        </button>
      </div>
      {showDiff && <div className="diff-content">{highlightText(scrubbed)}</div>}
    </div>
  );
}
