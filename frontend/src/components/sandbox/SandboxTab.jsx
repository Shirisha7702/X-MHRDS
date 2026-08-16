import React, { useState } from 'react';
import WordImportance from './WordImportance';
import MultilingualHeatmap from './MultilingualHeatmap';
import { Zap, Activity, AlertTriangle, FileText, Edit3, Bookmark, Clipboard, Trash2 } from 'lucide-react';

const PRESET_EXAMPLES = [
  {
    label: 'High Risk (Active Ideation)',
    text: 'I feel so completely hopeless. Every day is a struggle and I just want to end my life tonight.',
  },
  {
    label: 'Multilingual High Risk (Spanish)',
    text: 'me siento solo y sin esperanza quiero morir',
  },
  {
    label: 'Multilingual High Risk (French)',
    text: 'je me sens tellement seul et triste je veux mourir',
  },
  {
    label: 'Long Clinical Narrative: Severe Active Risk (Tier 3)',
    text: 'Over the last six months, everything in my life has collapsed. I lost my job, my relationship ended, and the constant unbearable weight in my chest never goes away even for a second. Every single morning I wake up wishing I hadn\'t. I have written letters to my family and cleared out my apartment. I bought a bottle of sleeping pills yesterday and I have made up my mind to end my life tonight when everyone is asleep. I cannot carry this exhausting agony anymore.',
  },
  {
    label: 'Low Risk (Protective)',
    text: 'Had a really tough week at work, but spending time with family and talking to my therapist helped me feel better.',
  },
];

export default function SandboxTab(props) {
  // Support both prop naming conventions for total safety
  const textInput = props.rawText ?? props.textInput ?? '';
  const setTextInput = props.setRawText ?? props.setTextInput ?? (() => {});
  const analysisResult = props.sandboxResult ?? props.analysisResult ?? null;
  const analysisLoading = props.analyzing ?? props.analysisLoading ?? false;
  const executeAnalysis = props.runAnalysis ?? props.executeAnalysis ?? (() => {});
  const { onOpenCopilot, generateDiagnosticReport } = props;

  const [inputMode, setInputMode] = useState('custom'); // 'custom' | 'preset'

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      if (textInput.trim() && !analysisLoading) {
        executeAnalysis();
      }
    }
  };

  const handlePasteClipboard = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        setTextInput(text);
      }
    } catch (err) {
      // Non-critical clipboard permission fail
    }
  };

  const handleClearText = () => {
    setTextInput('');
  };

  const wordCount = textInput.trim() ? textInput.trim().split(/\s+/).length : 0;
  const charCount = textInput.length;

  return (
    <div className="glass-grid">
      {/* Left Input & Settings Panel */}
      <div className="glass-card">
        <div className="card-title-group">
          <h2 className="card-title">
            <Edit3 size={18} />
            <span>Clinical Post Assessment</span>
          </h2>
        </div>

        {/* Input Mode Selector Bar */}
        <div className="tabs-nav-bar" style={{ marginBottom: '1.15rem', padding: '3px' }}>
          <button
            type="button"
            className={`tab-pill-btn ${inputMode === 'custom' ? 'active' : ''}`}
            onClick={() => setInputMode('custom')}
            style={{ fontSize: '0.8rem', padding: '6px 12px' }}
          >
            <Edit3 size={14} />
            <span>Direct Custom Text</span>
          </button>
          <button
            type="button"
            className={`tab-pill-btn ${inputMode === 'preset' ? 'active' : ''}`}
            onClick={() => setInputMode('preset')}
            style={{ fontSize: '0.8rem', padding: '6px 12px' }}
          >
            <Bookmark size={14} />
            <span>Clinical Presets</span>
          </button>
        </div>

        {inputMode === 'preset' ? (
          <div className="form-group">
            <label className="form-label">Clinical Benchmark Presets</label>
            <select
              className="select-input"
              onChange={(e) => {
                if (e.target.value) {
                  setTextInput(e.target.value);
                  setInputMode('custom');
                }
              }}
              defaultValue=""
            >
              <option value="" disabled>-- Select a pre-configured scenario --</option>
              {PRESET_EXAMPLES.map((ex, idx) => (
                <option key={idx} value={ex.text}>
                  {ex.label}
                </option>
              ))}
            </select>
          </div>
        ) : (
          <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '0.85rem' }}>
            Enter or paste any custom social media post, interview transcript, or raw text payload to evaluate:
          </div>
        )}

        {/* Direct Custom Text Input Workspace */}
        <div className="form-group">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
            <label className="form-label">Input Text Payload</label>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                {wordCount} words | {charCount} chars
              </span>
              <button
                type="button"
                className="header-btn"
                onClick={handlePasteClipboard}
                style={{ padding: '2px 6px', fontSize: '0.72rem' }}
                title="Paste text from clipboard"
              >
                <Clipboard size={12} />
                <span>Paste</span>
              </button>
              {textInput && (
                <button
                  type="button"
                  className="header-btn"
                  onClick={handleClearText}
                  style={{ padding: '2px 6px', fontSize: '0.72rem', color: 'var(--color-danger)' }}
                  title="Clear payload"
                >
                  <Trash2 size={12} />
                  <span>Clear</span>
                </button>
              )}
            </div>
          </div>

          <textarea
            className="text-area"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type or paste social media post / clinical interview transcript... (Ctrl + Enter to run)"
          />
        </div>

        <button className="btn-primary" disabled={analysisLoading || !textInput.trim()} onClick={executeAnalysis}>
          {analysisLoading ? (
            <>
              <div className="spinner-sm" />
              <span>Analyzing Payload...</span>
            </>
          ) : (
            <>
              <Zap size={16} />
              <span>Run Diagnostic Assessment</span>
              <span className="cmd-kbd-badge" style={{ marginLeft: '6px', background: 'rgba(255,255,255,0.2)', color: '#fff' }}>Ctrl+Enter</span>
            </>
          )}
        </button>
      </div>

      {/* Right Diagnostic Result Panel */}
      <div className="glass-card">
        <div className="card-title-group">
          <h2 className="card-title">
            <Activity size={18} />
            <span>Diagnostic Inference</span>
          </h2>
          {analysisResult && (
            <div style={{ display: 'flex', gap: '8px' }}>
              {generateDiagnosticReport && (
                <button
                  className="header-btn"
                  onClick={() => generateDiagnosticReport(analysisResult)}
                  style={{ padding: '4px 10px', fontSize: '0.78rem' }}
                >
                  <FileText size={14} />
                  <span>Report</span>
                </button>
              )}
              {onOpenCopilot && (
                <button className="header-btn" onClick={onOpenCopilot} style={{ padding: '4px 10px', fontSize: '0.78rem' }}>
                  <FileText size={14} />
                  <span>Copilot</span>
                </button>
              )}
            </div>
          )}
        </div>

        {analysisResult ? (
          <>
            <div className="metrics-hero-grid">
              <div className="hero-metric-card">
                <span className="metric-label">Suicide Risk Probability</span>
                <span
                  className="metric-value-huge"
                  style={{
                    color: analysisResult.prob_suicide > 0.5 ? 'var(--color-danger)' : 'var(--color-success)',
                  }}
                >
                  {((analysisResult.prob_suicide ?? 0) * 100).toFixed(1)}%
                </span>
              </div>

              <div className="hero-metric-card">
                <span className="metric-label">Assigned Risk Severity</span>
                <div style={{ marginTop: '8px' }}>
                  <span className={`tier-status-pill tier-${analysisResult.tier_num ?? 0}`}>
                    {analysisResult.tier_label || 'Tier 0'}
                  </span>
                </div>
              </div>
            </div>

            {/* XAI Token Attribution Section */}
            <WordImportance wordScores={analysisResult.word_scores || []} />
            <MultilingualHeatmap multilingualMeta={analysisResult.multilingual_meta} />
          </>
        ) : (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '3.5rem 1rem' }}>
            <AlertTriangle size={32} style={{ opacity: 0.4, marginBottom: '0.75rem' }} />
            <p style={{ margin: 0, fontWeight: 500 }}>No diagnostic assessment performed yet.</p>
            <p style={{ fontSize: '0.85rem', margin: '6px 0 0 0' }}>Type or paste any plain text payload on the left and press <kbd style={{ background: 'var(--bg-surface-2)', padding: '2px 6px', borderRadius: '4px', border: '1px solid var(--border-card)' }}>Ctrl + Enter</kbd> or click Run Assessment.</p>
          </div>
        )}
      </div>
    </div>
  );
}
