import React from 'react';
import { Globe, ArrowRight } from 'lucide-react';

export default function MultilingualHeatmap({ multilingualMeta }) {
  if (!multilingualMeta || !multilingualMeta.is_multilingual) {
    return null;
  }

  const { source_language_name, translated_text, source_word_scores } = multilingualMeta;

  return (
    <div className="glass-card multilingual-heatmap-card" style={{ padding: '1.25rem', marginTop: '1rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
        <Globe size={20} style={{ color: 'var(--color-brand)' }} />
        <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
          Multilingual Analysis & Cross-Lingual Attribution Alignment
        </h4>
        <span style={{ marginLeft: 'auto', background: 'var(--color-info-bg)', color: 'var(--color-info)', padding: '0.2rem 0.6rem', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 600 }}>
          Detected: {source_language_name}
        </span>
      </div>

      <div style={{ display: 'grid', gap: '1rem' }}>
        {/* Source Language Heatmap */}
        <div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.4rem', fontWeight: 500 }}>
            Native Source Text ({source_language_name} Heatmap):
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', background: 'var(--bg-surface-2)', border: '1px solid var(--border-card)', padding: '0.75rem', borderRadius: '6px' }}>
            {source_word_scores.map(([word, score], idx) => {
              const normScore = Math.min(Math.abs(score) * 2.5, 1.0);
              const isRisk = score > 0;
              return (
                <span
                  key={idx}
                  title={`Projected attribution: ${score.toFixed(4)}`}
                  style={{
                    backgroundColor: isRisk ? 'var(--color-danger-bg)' : 'var(--color-success-bg)',
                    color: isRisk ? 'var(--color-danger)' : 'var(--color-success)',
                    border: `1px solid ${isRisk ? 'var(--color-danger)' : 'var(--color-success)'}`,
                    opacity: 0.55 + 0.45 * normScore,
                    padding: '0.2rem 0.5rem',
                    borderRadius: '4px',
                    fontSize: '0.85rem',
                    fontWeight: Math.abs(score) > 0.1 ? 600 : 400
                  }}
                >
                  {word}
                </span>
              );
            })}
          </div>
        </div>

        {/* English Translation */}
        <div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.4rem', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span>English Translation</span>
            <ArrowRight size={14} />
          </div>
          <div style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border-card)', color: 'var(--text-primary)', padding: '0.75rem', borderRadius: '6px', fontSize: '0.85rem', fontStyle: 'italic' }}>
            "{translated_text}"
          </div>
        </div>
      </div>
    </div>
  );
}
