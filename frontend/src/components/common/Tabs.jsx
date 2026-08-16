import React from 'react';
import {
  Zap,
  BarChart3,
  GitCompare,
  BookOpen,
  Scale,
  TrendingUp,
  Radio,
  Cpu,
  Activity,
} from 'lucide-react';

const TABS = [
  { id: 'sandbox', label: 'Diagnostic Assessment', icon: Zap },
  { id: 'multixai', label: 'Multi-XAI Studio', icon: Cpu },
  { id: 'analytics', label: 'Clinical Analytics', icon: BarChart3 },
  { id: 'drift', label: 'Model Drift & PSI', icon: Activity },
  { id: 'whatif', label: 'What-If Perturbation', icon: GitCompare },
  { id: 'cases', label: 'Historical Retrieval', icon: BookOpen },
  { id: 'fairness', label: 'Demographic Audit', icon: Scale },
  { id: 'temporal', label: 'Temporal Trajectory', icon: TrendingUp },
  { id: 'monitor', label: 'Live Stream Monitor', icon: Radio },
];


export default function Tabs(props) {
  const activeTab = props.activeTab ?? 'sandbox';
  const handleTabChange = props.setActiveTab ?? props.onChange ?? props.onTabChange ?? (() => {});

  return (
    <nav className="tabs-nav-bar">
      {TABS.map((tab) => {
        const IconComponent = tab.icon;
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            type="button"
            className={`tab-pill-btn ${isActive ? 'active' : ''}`}
            onClick={() => handleTabChange(tab.id)}
          >
            <IconComponent className="tab-icon" size={16} />
            <span>{tab.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
