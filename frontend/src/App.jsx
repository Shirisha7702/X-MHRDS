import React, { useEffect, useState, lazy, Suspense } from 'react';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import SkeletonLoader from './components/common/SkeletonLoader';
import Toast from './components/common/Toast';
import CommandPalette from './components/layout/CommandPalette';
import ClinicalCopilotModal from './components/copilot/ClinicalCopilotModal';
import LandingPage from './components/landing/LandingPage';

import { ThemeProvider } from './context/ThemeContext';
import { NotificationProvider } from './context/NotificationContext';
import { AppProvider } from './context/AppContext';
import { AnalysisProvider } from './context/AnalysisContext';
import { MonitorProvider } from './context/MonitorContext';

import { useTheme } from './hooks/useTheme';
import { useAppContext } from './hooks/useAppContext';
import { useAnalysis } from './hooks/useAnalysis';
import { useMonitor } from './hooks/useMonitor';
import './App.css';

// FAANG-Grade Code Splitting: Lazy loaded tab components
const SandboxTab = lazy(() => import('./components/sandbox/SandboxTab'));
const MultiXAIComparisonStudio = lazy(() => import('./components/sandbox/MultiXAIComparisonStudio'));
const AnalyticsTab = lazy(() => import('./components/analytics/AnalyticsTab'));
const DriftDashboard = lazy(() => import('./components/analytics/DriftDashboard'));
const WhatIfTab = lazy(() => import('./components/whatif/WhatIfTab'));
const CasesTab = lazy(() => import('./components/cases/CasesTab'));
const FairnessTab = lazy(() => import('./components/fairness/FairnessTab'));
const TemporalTab = lazy(() => import('./components/temporal/TemporalTab'));
const MonitorTab = lazy(() => import('./components/monitor/MonitorTab'));

function MainAppContent() {
  const { theme, toggleTheme } = useTheme();
  const {
    activeTab, setActiveTab, modelChoice, setModelChoice,
    isCmdOpen, setIsCmdOpen, isCopilotOpen, setIsCopilotOpen,
  } = useAppContext();

  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const {
    rawText, setRawText, analyzing, sandboxResult, runAnalysis, generateDiagnosticReport,
    whatIfText, setWhatIfText, targetWord, setTargetWord, replacementWord, setReplacementWord, whatIfLoading, whatIfResult, executeWhatIf,
    searchQuery, setSearchQuery, searchLoading, searchResults, executeSearch,
    fairnessResults, fairnessLoading, loadFairness,
    temporalResults, temporalLoading, loadTemporal,
    modelMetrics, modelMetricsLoading, loadModelMetrics,
    robustnessMetrics, robustnessLoading, loadRobustness,
    constructAudit, constructAuditLoading, loadConstructAudit,
  } = useAnalysis();

  const {
    monitorRunning, monitorLoading, monitorEvents, userTrends,
    handleStartMonitor, handleStopMonitor, refreshUserTrends,
  } = useMonitor();

  // Tab change & model change data loading side-effects
  useEffect(() => {
    if (activeTab === 'fairness') {
      loadFairness();
    } else if (activeTab === 'analytics') {
      loadConstructAudit();
      loadModelMetrics();
      loadRobustness();
    } else if (activeTab === 'temporal') {
      loadTemporal();
    } else if (activeTab === 'monitor') {
      refreshUserTrends();
    }
  }, [activeTab, loadFairness, loadConstructAudit, loadModelMetrics, loadRobustness, loadTemporal, refreshUserTrends]);

  // When model architecture changes, force reload for model-dependent tabs
  useEffect(() => {
    if (activeTab === 'fairness') {
      loadFairness(true);
    } else if (activeTab === 'temporal') {
      loadTemporal(true);
    }
  }, [modelChoice, activeTab, loadFairness, loadTemporal]);

  return (
    <div className="app-layout">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        collapsed={sidebarCollapsed}
        setCollapsed={setSidebarCollapsed}
        theme={theme}
        toggleTheme={toggleTheme}
        modelChoice={modelChoice}
        setModelChoice={setModelChoice}
        onOpenCmd={() => setIsCmdOpen(true)}
        onOpenCopilot={() => setIsCopilotOpen(true)}
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
      />

      <div className={`main-viewport ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <Header
          activeTab={activeTab}
          theme={theme}
          toggleTheme={toggleTheme}
          modelChoice={modelChoice}
          setModelChoice={setModelChoice}
          onOpenCmd={() => setIsCmdOpen(true)}
          onOpenCopilot={() => setIsCopilotOpen(true)}
          setMobileOpen={setMobileOpen}
        />

        <main className="content">
          <Suspense fallback={<SkeletonLoader tabName={activeTab} />}>
            <div style={{ display: activeTab === 'sandbox' ? 'block' : 'none' }}>
              <SandboxTab
                rawText={rawText}
                setRawText={setRawText}
                modelChoice={modelChoice}
                analyzing={analyzing}
                runAnalysis={runAnalysis}
                sandboxResult={sandboxResult}
                generateDiagnosticReport={generateDiagnosticReport}
                onOpenCopilot={() => setIsCopilotOpen(true)}
              />
            </div>

            <div style={{ display: activeTab === 'multixai' ? 'block' : 'none' }}>
              <MultiXAIComparisonStudio
                modelChoice={modelChoice}
                defaultText={rawText}
              />
            </div>

            <div style={{ display: activeTab === 'analytics' ? 'block' : 'none' }}>
              <AnalyticsTab
                constructAudit={constructAudit}
                constructAuditLoading={constructAuditLoading}
                modelMetrics={modelMetrics}
                modelMetricsLoading={modelMetricsLoading}
                robustnessMetrics={robustnessMetrics}
                robustnessLoading={robustnessLoading}
              />
            </div>

            <div style={{ display: activeTab === 'drift' ? 'block' : 'none' }}>
              <DriftDashboard />
            </div>

            <div style={{ display: activeTab === 'whatif' ? 'block' : 'none' }}>
              <WhatIfTab
                whatIfText={whatIfText}
                setWhatIfText={setWhatIfText}
                targetWord={targetWord}
                setTargetWord={setTargetWord}
                replacementWord={replacementWord}
                setReplacementWord={setReplacementWord}
                modelChoice={modelChoice}
                whatIfLoading={whatIfLoading}
                executeWhatIf={executeWhatIf}
                whatIfResult={whatIfResult}
              />
            </div>

            <div style={{ display: activeTab === 'cases' ? 'block' : 'none' }}>
              <CasesTab
                searchQuery={searchQuery}
                setSearchQuery={setSearchQuery}
                searchLoading={searchLoading}
                executeSearch={executeSearch}
                searchResults={searchResults}
              />
            </div>

            <div style={{ display: activeTab === 'fairness' ? 'block' : 'none' }}>
              <FairnessTab
                modelChoice={modelChoice}
                fairnessLoading={fairnessLoading}
                fairnessResults={fairnessResults}
              />
            </div>

            <div style={{ display: activeTab === 'temporal' ? 'block' : 'none' }}>
              <TemporalTab
                modelChoice={modelChoice}
                temporalLoading={temporalLoading}
                temporalResults={temporalResults}
              />
            </div>

            <div style={{ display: activeTab === 'monitor' ? 'block' : 'none' }}>
              <MonitorTab
                modelChoice={modelChoice}
                monitorRunning={monitorRunning}
                monitorLoading={monitorLoading}
                handleStartMonitor={handleStartMonitor}
                handleStopMonitor={handleStopMonitor}
                monitorEvents={monitorEvents}
                userTrends={userTrends}
              />
            </div>
          </Suspense>
        </main>
    </div>

    <Toast />

      <CommandPalette
        isOpen={isCmdOpen}
        onOpen={() => setIsCmdOpen(true)}
        onClose={() => setIsCmdOpen(false)}
        onSelectTab={setActiveTab}
        onSelectModel={setModelChoice}
        toggleTheme={toggleTheme}
        onOpenCopilot={() => {
          setIsCmdOpen(false);
          setIsCopilotOpen(true);
        }}
      />

      <ClinicalCopilotModal
        isOpen={isCopilotOpen}
        onClose={() => setIsCopilotOpen(false)}
        currentAnalysis={sandboxResult}
      />
    </div>
  );
}

function AppShell() {
  const [showLanding, setShowLanding] = useState(true);

  if (showLanding) {
    return <LandingPage onEnter={() => setShowLanding(false)} />;
  }

  return (
    <AppProvider>
      <AnalysisProvider>
        <MonitorProvider>
          <MainAppContent />
        </MonitorProvider>
      </AnalysisProvider>
    </AppProvider>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <NotificationProvider>
        <AppShell />
      </NotificationProvider>
    </ThemeProvider>
  );
}
