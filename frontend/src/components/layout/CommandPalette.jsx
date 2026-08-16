import React, { useState, useEffect, useRef } from 'react';
import {
  Zap,
  BookOpen,
  GitCompare,
  BarChart3,
  Scale,
  TrendingUp,
  Radio,
  HeartPulse,
  Cpu,
  Activity,
  Sun,
  Search,
} from 'lucide-react';

export default function CommandPalette({ isOpen, onOpen, onClose, onSelectTab, onSelectModel, toggleTheme, onOpenCopilot }) {
  const [query, setQuery] = useState('');
  const inputRef = useRef(null);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
        else onOpen();
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose, onOpen]);

  if (!isOpen) return null;

  const actions = [
    { label: 'Go to Analysis Sandbox', icon: Zap, category: 'Navigation', run: () => onSelectTab('sandbox') },
    { label: 'Go to Cases Library', icon: BookOpen, category: 'Navigation', run: () => onSelectTab('cases') },
    { label: 'Go to What-If Simulator', icon: GitCompare, category: 'Navigation', run: () => onSelectTab('whatif') },
    { label: 'Go to Model & Construct Analytics', icon: BarChart3, category: 'Navigation', run: () => onSelectTab('analytics') },
    { label: 'Go to Fairness & Demographic Audit', icon: Scale, category: 'Navigation', run: () => onSelectTab('fairness') },
    { label: 'Go to Temporal Trajectories', icon: TrendingUp, category: 'Navigation', run: () => onSelectTab('temporal') },
    { label: 'Go to Live Monitor Feed', icon: Radio, category: 'Navigation', run: () => onSelectTab('monitor') },
    { label: 'Open Clinical Safety Copilot', icon: HeartPulse, category: 'Copilot', run: () => onOpenCopilot() },
    { label: 'Switch Model to Logistic Regression', icon: Cpu, category: 'Model', run: () => onSelectModel('Logistic Regression') },
    { label: 'Switch Model to SVM (Calibrated)', icon: Cpu, category: 'Model', run: () => onSelectModel('SVM (Calibrated LinearSVC)') },
    { label: 'Switch Model to BERT (Fine-tuned)', icon: Activity, category: 'Model', run: () => onSelectModel('BERT (Fine-tuned)') },
    { label: 'Switch Model to RoBERTa (Fine-tuned)', icon: Activity, category: 'Model', run: () => onSelectModel('RoBERTa (Fine-tuned)') },
    { label: 'Toggle Light / Dark Theme', icon: Sun, category: 'Theme', run: () => toggleTheme() },
  ];

  const filtered = actions.filter((a) =>
    a.label.toLowerCase().includes(query.toLowerCase()) ||
    a.category.toLowerCase().includes(query.toLowerCase())
  );

  const handleRun = (action) => {
    action.run();
    onClose();
  };

  return (
    <div className="cmd-overlay" onClick={onClose}>
      <div className="cmd-modal" onClick={(e) => e.stopPropagation()}>
        <div className="cmd-header">
          <Search size={16} style={{ color: 'var(--text-secondary)' }} />
          <input
            ref={inputRef}
            type="text"
            className="cmd-input"
            placeholder="Type a command or search... (Esc to exit)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <kbd className="cmd-kbd">ESC</kbd>
        </div>
        <div className="cmd-body">
          {filtered.length === 0 ? (
            <div className="cmd-empty" style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              No matching commands found.
            </div>
          ) : (
            filtered.map((item, idx) => {
              const IconComp = item.icon;
              return (
                <button key={idx} className="cmd-item" onClick={() => handleRun(item)}>
                  <IconComp size={16} style={{ color: 'var(--color-brand)' }} />
                  <span className="cmd-item-label">{item.label}</span>
                  <span className="cmd-item-badge">{item.category}</span>
                </button>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
