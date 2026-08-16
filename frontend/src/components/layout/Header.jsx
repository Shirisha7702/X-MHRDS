import React from 'react';
import { Menu, Search, HeartPulse, Sun, Moon, Shield, Activity } from 'lucide-react';

const TAB_TITLES = {
  sandbox: 'Diagnostic Assessment Sandbox',
  multixai: 'Multi-XAI Attribution Studio',
  analytics: 'Clinical Model Analytics & Audits',
  drift: 'Model Drift & Population Stability (PSI)',
  whatif: 'What-If Counterfactual Perturbation',
  cases: 'Historical Semantic Case Search',
  fairness: 'Demographic Fairness Audit',
  temporal: 'Temporal Trajectory Tracker',
  monitor: 'Real-Time Stream Live Monitor',
};

export default function Header({
  activeTab,
  theme,
  toggleTheme,
  modelChoice,
  setModelChoice,
  onOpenCmd,
  onOpenCopilot,
  setMobileOpen,
}) {
  return (
    <header className="app-header">
      <div className="header-top-nav">
        <div className="header-left-group">
          <button
            className="mobile-menu-btn mobile-only"
            onClick={() => setMobileOpen(true)}
            aria-label="Open Sidebar Navigation"
          >
            <Menu size={20} />
          </button>

          <div className="header-title-wrapper">
            <h2 className="header-page-title">{TAB_TITLES[activeTab] || 'Clinical Assessment'}</h2>
            <div className="status-dot-indicator">
              <span className="pulse-dot" />
              <span>System Operational</span>
            </div>
          </div>
        </div>

        <div className="header-right-actions">
          <select
            className="header-model-select desktop-only"
            value={modelChoice}
            onChange={(e) => setModelChoice(e.target.value)}
            title="Active Model Architecture"
          >
            <option value="Logistic Regression">Logistic Regression</option>
            <option value="SVM (Calibrated LinearSVC)">SVM (Calibrated)</option>
            <option value="BERT (Fine-tuned)">BERT (Transformer)</option>
            <option value="RoBERTa (Fine-tuned)">RoBERTa (Transformer)</option>
          </select>

          <button className="header-btn desktop-only" onClick={onOpenCmd} title="Command Palette (Ctrl+K)">
            <Search size={15} />
            <span className="cmd-kbd-badge">Ctrl+K</span>
          </button>

          <button className="header-btn brand-btn-header" onClick={onOpenCopilot} title="Clinical Safety Copilot">
            <HeartPulse size={15} />
            <span>Copilot</span>
          </button>

          <button className="header-btn icon-only" onClick={toggleTheme} title="Toggle Light/Dark Theme">
            {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
          </button>
        </div>
      </div>

      <div className="clinical-alert-banner">
        <div className="clinical-alert-text">
          <span className="emergency-pill">RESEARCH &amp; CDS ONLY</span>
          <span>Clinical decision support engine. For immediate safety crisis support, contact <strong>988 Crisis Lifeline (Call/Text 988)</strong>.</span>
        </div>
      </div>
    </header>
  );
}
