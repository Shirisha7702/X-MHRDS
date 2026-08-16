import React, { useState } from 'react';
import { fetchExplainComparison } from '../../services/apiClient';
import { useNotification } from '../../hooks/useNotification';
import { Cpu, GitMerge, BarChart2, ShieldCheck, RefreshCw, Zap, Bookmark } from 'lucide-react';

const PRESETS = [
  "Over the last six months, everything in my life has collapsed. I lost my job, my relationship ended, and the constant unbearable weight in my chest never goes away even for a second. Every single morning I wake up wishing I hadn't. I have written letters to my family and cleared out my apartment. I bought a bottle of sleeping pills yesterday and I have made up my mind to end my life tonight when everyone is asleep. I cannot carry this exhausting agony anymore.",
  "I've been feeling extremely stressed about my upcoming final exams and job interviews, but I am keeping up with my daily workouts, drinking plenty of water, and talking to my counselor weekly.",
  "I am deeply exhausted and isolated. Nothing seems to bring me joy anymore, but I am still trying to take things one small step at a time.",
];

const EXPLAINERS = [
  { name: 'SHAP (Kernel)', desc: 'Shapley Additive Explanations', color: '#0284C7' },
  { name: 'Integrated Gradients (IG)', desc: 'Axiomatic Attribution', color: '#7C3AED' },
  { name: 'LIME (Local Surrogates)', desc: 'Interpretable Model-Agnostic', color: '#059669' },
  { name: 'LOO (Leave-One-Out)', desc: 'Omission Perturbation', color: '#D97706' },
];

export default function MultiXAIComparisonStudio({ modelChoice, defaultText }) {
  const { addNotification } = useNotification();
  const [text, setText] = useState(defaultText || PRESETS[0]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
  const charCount = text.length;

  const handleRunComparison = async () => {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const data = await fetchExplainComparison({ text, model_choice: modelChoice });
      setResult(data);
      addNotification('Multi-XAI comparison completed across 4 explainers', 'success');
    } catch (err) {
      addNotification(err.message || 'Failed to generate multi-XAI comparison', 'error');
    } finally {
      setLoading(false);
    }
  };

  const getCorrColors = (val) => {
    if (val >= 0.7) return { bg: 'var(--color-success-bg)', text: 'var(--color-success)', border: 'rgba(16, 185, 129, 0.3)' };
    if (val >= 0.4) return { bg: 'var(--color-warning-bg)', text: 'var(--color-warning)', border: 'rgba(255, 183, 3, 0.3)' };
    return { bg: 'var(--color-danger-bg)', text: 'var(--color-danger)', border: 'rgba(255, 77, 109, 0.35)' };
  };

  return (
    <div className="glass-card multi-xai-studio" style={{ marginBottom: '1.5rem' }}>
      {/* Header Bar */}
      <div className="card-title-group" style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div style={{ width: '42px', height: '42px', borderRadius: 'var(--radius-md)', background: 'linear-gradient(135deg, #7C3AED, #9333EA)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#FFF', boxShadow: '0 4px 12px rgba(124, 58, 237, 0.3)' }}>
            <Cpu size={22} />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.3px' }}>
              Multi-XAI Attribution Comparison Studio
            </h3>
            <p style={{ margin: '2px 0 0 0', fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
              Compare attributions side-by-side across SHAP, Integrated Gradients, LIME, and LOO explainers.
            </p>
          </div>
        </div>

        <button
          className="btn-primary"
          onClick={handleRunComparison}
          disabled={loading}
          style={{ width: 'auto', padding: '10px 20px', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: '0.5rem', flexShrink: 0 }}
        >
          {loading ? <RefreshCw className="spin" size={16} /> : <GitMerge size={16} />}
          <span>{loading ? 'Computing Attributions...' : 'Run 4-Explainer Comparison'}</span>
        </button>
      </div>

      {/* Explainer Architecture Badges */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '1.25rem' }}>
        {EXPLAINERS.map((ex) => (
          <div
            key={ex.name}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '4px 10px',
              borderRadius: 'var(--radius-full)',
              background: 'var(--bg-surface-2)',
              border: `1px solid ${ex.color}40`,
              fontSize: '0.74rem',
              fontWeight: 700,
              color: 'var(--text-primary)'
            }}
          >
            <span style={{ width: '7px', height: '7px', borderRadius: '50%', background: ex.color }} />
            <span>{ex.name}</span>
          </div>
        ))}
      </div>

      {/* Textarea Payload Input Workspace */}
      <div className="form-group" style={{ marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
          <label className="form-label">Input Clinical Post Payload</label>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              {wordCount} words | {charCount} chars
            </span>
            <select
              className="select-input"
              style={{ width: 'auto', padding: '3px 8px', fontSize: '0.76rem' }}
              onChange={(e) => {
                if (e.target.value) setText(e.target.value);
              }}
              defaultValue=""
            >
              <option value="" disabled>Load Preset Scenario...</option>
              {PRESETS.map((p, idx) => (
                <option key={idx} value={p}>
                  Preset Scenario #{idx + 1}
                </option>
              ))}
            </select>
          </div>
        </div>

        <textarea
          className="text-area"
          rows={4}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste or type any social post text to compute multi-XAI explainability attributions..."
          style={{ fontSize: '0.9rem', lineHeight: '1.5', minHeight: '100px' }}
        />
      </div>

      {/* Comparison Results Area */}
      {result && (
        <div className="xai-comparison-results" style={{ display: 'grid', gap: '1.25rem', marginTop: '1.5rem' }}>
          {/* Convergence Correlation Matrix */}
          <div className="sub-card" style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border-card)', padding: '1.15rem', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
              <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-primary)' }}>
                <BarChart2 size={18} style={{ color: 'var(--color-brand)' }} />
                <span>Explainer Convergence Matrix (Pearson Correlation)</span>
              </h4>
              <span className="metric-badge metric-badge-primary">
                {result.overall_agreement || 'High Agreement'}
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '0.75rem' }}>
              {Object.entries(result.correlation_matrix || {}).map(([pair, corr]) => {
                const corrColors = getCorrColors(corr);
                return (
                  <div
                    key={pair}
                    style={{
                      padding: '0.7rem 0.9rem',
                      borderRadius: 'var(--radius-sm)',
                      backgroundColor: corrColors.bg,
                      color: corrColors.text,
                      border: `1px solid ${corrColors.border}`,
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <span style={{ fontSize: '0.82rem', fontWeight: 600 }}>{pair}</span>
                    <span style={{ fontSize: '0.95rem', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>{corr.toFixed(3)}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Side-by-Side Word Heatmap Rows */}
          <div className="sub-card" style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border-card)', padding: '1.15rem', borderRadius: 'var(--radius-md)' }}>
            <h4 style={{ margin: '0 0 1rem 0', fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Side-by-Side Explainer Word Attributions
            </h4>
            <div style={{ display: 'grid', gap: '1.15rem' }}>
              {Object.entries(result.methods || {}).map(([methodName, wordScores]) => (
                <div key={methodName} style={{ borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.86rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                      {methodName}
                    </span>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      (Feature Attribution Heatmap)
                    </span>
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                    {wordScores.map(([word, score], idx) => {
                      const normScore = Math.min(Math.abs(score) * 2.5, 1.0);
                      const isRisk = score > 0;
                      return (
                        <span
                          key={idx}
                          title={`${word}: ${score.toFixed(4)}`}
                          style={{
                            backgroundColor: isRisk ? 'var(--color-danger-bg)' : 'var(--color-success-bg)',
                            color: isRisk ? 'var(--color-danger)' : 'var(--color-success)',
                            border: `1px solid ${isRisk ? 'rgba(255, 77, 109, 0.35)' : 'rgba(16, 185, 129, 0.3)'}`,
                            opacity: 0.65 + 0.35 * normScore,
                            padding: '3px 7px',
                            borderRadius: 'var(--radius-sm)',
                            fontSize: '0.84rem',
                            fontFamily: 'var(--font-mono)',
                            fontWeight: Math.abs(score) > 0.1 ? 700 : 500,
                            cursor: 'help'
                          }}
                        >
                          {word}
                        </span>
                      );
                    })}
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

