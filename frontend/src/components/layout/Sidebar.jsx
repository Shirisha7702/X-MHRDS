import React, { useState } from 'react';
import {
  Zap,
  Cpu,
  BarChart3,
  Activity,
  GitCompare,
  BookOpen,
  Scale,
  TrendingUp,
  Radio,
  ChevronLeft,
  ChevronRight,
  HeartPulse,
  Search,
  Sun,
  Moon,
  ShieldAlert,
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'sandbox', label: 'Diagnostic Assessment', icon: Zap, category: 'Core Assessment', color: '#0284C7' },
  { id: 'multixai', label: 'Multi-XAI Studio', icon: Cpu, category: 'Core Assessment', color: '#7C3AED' },
  { id: 'analytics', label: 'Clinical Analytics', icon: BarChart3, category: 'Governance & Audits', color: '#2563EB' },
  { id: 'drift', label: 'Model Drift & PSI', icon: Activity, category: 'Governance & Audits', color: '#059669' },
  { id: 'whatif', label: 'What-If Perturbation', icon: GitCompare, category: 'Simulation & Search', color: '#D97706' },
  { id: 'cases', label: 'Historical Retrieval', icon: BookOpen, category: 'Simulation & Search', color: '#0284C7' },
  { id: 'fairness', label: 'Demographic Audit', icon: Scale, category: 'Bias & Trajectory', color: '#DB2777' },
  { id: 'temporal', label: 'Temporal Trajectory', icon: TrendingUp, category: 'Bias & Trajectory', color: '#EA580C' },
  { id: 'monitor', label: 'Live Stream Monitor', icon: Radio, category: 'Real-Time Monitoring', badge: 'LIVE', color: '#DC2626' },
];

export default function Sidebar({
  activeTab,
  setActiveTab,
  collapsed,
  setCollapsed,
  theme,
  toggleTheme,
  modelChoice,
  setModelChoice,
  onOpenCmd,
  onOpenCopilot,
  mobileOpen,
  setMobileOpen,
}) {
  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          className="sidebar-mobile-backdrop"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <aside className={`app-sidebar ${collapsed ? 'collapsed' : ''} ${mobileOpen ? 'mobile-open' : ''}`}>
        {/* Sidebar Header / Brand */}
        <div className="sidebar-brand-container">
          {!collapsed && (
            <div className="sidebar-brand-group">
              <div className="sidebar-logo-icon">
                <Activity size={22} />
              </div>
              <div className="sidebar-brand-info">
                <span className="sidebar-title">X-MHRDS</span>
                <span className="sidebar-subtitle">Explainable AI Risk Platform</span>
              </div>
            </div>
          )}

          <button
            className="sidebar-collapse-btn desktop-only"
            onClick={() => setCollapsed(!collapsed)}
            title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
            aria-label="Toggle Sidebar Navigation"
          >
            {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
        </div>

        {/* Clinical Alert Pill */}
        {!collapsed && (
          <div className="sidebar-alert-pill">
            <ShieldAlert size={14} style={{ color: 'var(--color-warning)' }} />
            <span>CDS Protocol 988-Ready</span>
          </div>
        )}

        {/* Navigation Items */}
        <nav className="sidebar-nav-scroll">
          <div className="sidebar-menu-list">
            {NAV_ITEMS.map((item, index) => {
              const IconComponent = item.icon;
              const isActive = activeTab === item.id;
              const showCategoryHeader =
                !collapsed &&
                (index === 0 || NAV_ITEMS[index - 1].category !== item.category);

              return (
                <React.Fragment key={item.id}>
                  {showCategoryHeader && (
                    <div className="sidebar-category-header">
                      {item.category}
                    </div>
                  )}

                  <button
                    type="button"
                    className={`sidebar-item-btn ${isActive ? 'active' : ''}`}
                    onClick={() => {
                      setActiveTab(item.id);
                      if (mobileOpen) setMobileOpen(false);
                    }}
                    title={collapsed ? item.label : undefined}
                  >
                    <div className="sidebar-item-icon">
                      <IconComponent size={18} color={isActive ? '#FFFFFF' : item.color} />
                    </div>
                    {!collapsed && (
                      <span className="sidebar-item-label">{item.label}</span>
                    )}
                    {!collapsed && item.badge && (
                      <span className="sidebar-item-badge">{item.badge}</span>
                    )}
                    {collapsed && (
                      <div className="sidebar-tooltip">{item.label}</div>
                    )}
                  </button>
                </React.Fragment>
              );
            })}
          </div>
        </nav>

        {/* Sidebar Footer Controls */}
        <div className="sidebar-footer">
          {!collapsed && (
            <div className="sidebar-model-box">
              <label className="sidebar-model-label">Architecture Model</label>
              <select
                className="sidebar-model-select"
                value={modelChoice}
                onChange={(e) => setModelChoice(e.target.value)}
              >
                <option value="Logistic Regression">Logistic Regression</option>
                <option value="SVM (Calibrated LinearSVC)">SVM (Calibrated)</option>
                <option value="BERT (Fine-tuned)">BERT (Transformer)</option>
                <option value="RoBERTa (Fine-tuned)">RoBERTa (Transformer)</option>
              </select>
            </div>
          )}

          <div className="sidebar-actions-grid">
            <button
              className="sidebar-action-btn"
              onClick={onOpenCmd}
              title="Command Palette (Ctrl+K)"
            >
              <Search size={16} />
              {!collapsed && <span>Cmd Palette</span>}
              {!collapsed && <kbd className="sidebar-kbd">Ctrl+K</kbd>}
            </button>

            <button
              className="sidebar-action-btn brand-btn"
              onClick={onOpenCopilot}
              title="Clinical Safety Copilot"
            >
              <HeartPulse size={16} />
              {!collapsed && <span>Copilot</span>}
            </button>

            <button
              className="sidebar-action-btn"
              onClick={toggleTheme}
              title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
            >
              {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
              {!collapsed && <span>{theme === 'dark' ? 'Light' : 'Dark'}</span>}
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
