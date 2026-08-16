import React, { createContext, useState, useCallback } from 'react';
import {
  analyzeText, analyzeMultilingualText, runWhatIf, searchCases, fetchRobustness, fetchFairness, fetchTemporal, fetchModelMetrics, fetchConstructAudit, createReport
} from '../services/apiClient';
import { useNotification } from '../hooks/useNotification';
import { useAppContext } from '../hooks/useAppContext';

export const AnalysisContext = createContext();

const DEFAULT_CLINICAL_TEXT = "Over the last six months, everything in my life has collapsed. I lost my job, my relationship ended, and the constant unbearable weight in my chest never goes away even for a second. Every single morning I wake up wishing I hadn't. I have written letters to my family and cleared out my apartment. I bought a bottle of sleeping pills yesterday and I have made up my mind to end my life tonight when everyone is asleep. I cannot carry this exhausting agony anymore.";

export function AnalysisProvider({ children }) {
  const { addNotification } = useNotification();
  const { modelChoice, anonymizeActive, explanationMethod } = useAppContext();

  // Sandbox state - pre-loaded with sample long clinical text payload for instant testing
  const [rawText, setRawText] = useState(DEFAULT_CLINICAL_TEXT);
  const [analyzing, setAnalyzing] = useState(false);
  const [sandboxResult, setSandboxResult] = useState(null);

  // What-If state
  const [whatIfText, setWhatIfText] = useState('I am feeling so hopeless and tired. I want to end my life tonight.');
  const [targetWord, setTargetWord] = useState('end my life');
  const [replacementWord, setReplacementWord] = useState('get help for my pain');
  const [whatIfLoading, setWhatIfLoading] = useState(false);
  const [whatIfResult, setWhatIfResult] = useState(null);

  // Case search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchResults, setSearchResults] = useState([]);

  // Analytics & Audits cached data
  const [fairnessResults, setFairnessResults] = useState(null);
  const [fairnessLoading, setFairnessLoading] = useState(false);
  const [temporalResults, setTemporalResults] = useState([]);
  const [temporalLoading, setTemporalLoading] = useState(false);
  const [modelMetrics, setModelMetrics] = useState([]);
  const [modelMetricsLoading, setModelMetricsLoading] = useState(false);
  const [robustnessMetrics, setRobustnessMetrics] = useState(null);
  const [robustnessLoading, setRobustnessLoading] = useState(false);
  const [constructAudit, setConstructAudit] = useState(null);
  const [constructAuditLoading, setConstructAuditLoading] = useState(false);

  const runAnalysis = useCallback(async () => {
    if (!rawText.trim()) return;
    setAnalyzing(true);
    try {
      // Check if text has non-ascii or non-english keywords
      const isNonEnglish = /[^\x00-\x7F]/.test(rawText) || /el|la|le|die|que|por|siento|seul|traurig|ich/i.test(rawText);
      let data;
      if (isNonEnglish) {
        data = await analyzeMultilingualText({
          text: rawText,
          model_choice: modelChoice,
          anonymize_active: anonymizeActive,
        });
      } else {
        data = await analyzeText({
          text: rawText,
          model_choice: modelChoice,
          anonymize_active: anonymizeActive,
          explanation_method: explanationMethod,
        });
      }
      setSandboxResult(data);
      addNotification(`Analysis complete: ${data.tier_label}`, data.prob_suicide > 0.5 ? 'warning' : 'success');
    } catch (err) {
      addNotification(err.message || 'Error executing text analysis.', 'error');
    } finally {
      setAnalyzing(false);
    }
  }, [rawText, modelChoice, anonymizeActive, explanationMethod, addNotification]);

  const generateDiagnosticReport = useCallback(async (resultObj) => {
    const resObj = resultObj || sandboxResult;
    if (!resObj) return;
    try {
      const res = await createReport({
        raw_text: rawText,
        processed_text: resObj.processed_text || rawText,
        model_choice: modelChoice,
        tier_label: resObj.tier_label,
        prob_suicide: resObj.prob_suicide,
        tier_num: resObj.tier_num,
        dominant_emotion: resObj.dominant_emotion || 'distress',
        draft_response: resObj.draft_response || '',
      });
      const blob = new Blob([res.html], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const win = window.open(url, '_blank');
      if (!win) {
        addNotification('Report generated! (Please allow popups to view)', 'warning');
      } else {
        addNotification('Diagnostic Report opened in new tab', 'success');
      }
    } catch (err) {
      addNotification(err.message || 'Failed to generate diagnostic report.', 'error');
    }
  }, [sandboxResult, rawText, modelChoice, addNotification]);

  const executeWhatIf = useCallback(async () => {
    if (!whatIfText.trim() || !targetWord.trim()) {
      addNotification('Please specify original text and target word to swap.', 'warning');
      return;
    }
    setWhatIfLoading(true);
    try {
      const data = await runWhatIf({
        text: whatIfText,
        target_word: targetWord,
        replacement_word: replacementWord,
        model_choice: modelChoice,
      });
      setWhatIfResult(data);
      addNotification('What-if perturbation completed', 'info');
    } catch (err) {
      addNotification(err.message || 'Failed to run what-if simulation.', 'error');
    } finally {
      setWhatIfLoading(false);
    }
  }, [whatIfText, targetWord, replacementWord, modelChoice, addNotification]);

  const executeSearch = useCallback(async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearchLoading(true);
    try {
      const results = await searchCases(searchQuery, 4);
      setSearchResults(results);
      addNotification(`Found ${results.length} similar historical cases`, 'info');
    } catch (err) {
      addNotification(err.message || 'Error performing case search.', 'error');
    } finally {
      setSearchLoading(false);
    }
  }, [searchQuery, addNotification]);

  const loadFairness = useCallback(async (force = false) => {
    if (!force && fairnessResults && fairnessResults._modelChoice === modelChoice) return;
    setFairnessLoading(true);
    try {
      const data = await fetchFairness(modelChoice);
      if (data && typeof data === 'object') {
        data._modelChoice = modelChoice;
      }
      setFairnessResults(data);
    } catch (err) {
      addNotification('Error fetching fairness metrics.', 'error');
    } finally {
      setFairnessLoading(false);
    }
  }, [modelChoice, fairnessResults, addNotification]);

  const loadTemporal = useCallback(async (force = false) => {
    if (!force && temporalResults && temporalResults._modelChoice === modelChoice) return;
    setTemporalLoading(true);
    try {
      const data = await fetchTemporal(modelChoice);
      if (data) {
        data._modelChoice = modelChoice;
      }
      setTemporalResults(data);
    } catch (err) {
      addNotification('Error fetching temporal trajectory data.', 'error');
    } finally {
      setTemporalLoading(false);
    }
  }, [modelChoice, temporalResults, addNotification]);

  const loadModelMetrics = useCallback(async (force = false) => {
    if (!force && modelMetrics && modelMetrics.length > 0) return;
    setModelMetricsLoading(true);
    try {
      const data = await fetchModelMetrics();
      setModelMetrics(data);
    } catch (err) {
      addNotification('Error fetching model metrics.', 'error');
    } finally {
      setModelMetricsLoading(false);
    }
  }, [modelMetrics, addNotification]);

  const loadRobustness = useCallback(async (force = false) => {
    if (!force && robustnessMetrics) return;
    setRobustnessLoading(true);
    try {
      const data = await fetchRobustness();
      setRobustnessMetrics(data);
    } catch (err) {
      addNotification('Error fetching robustness metrics.', 'error');
    } finally {
      setRobustnessLoading(false);
    }
  }, [robustnessMetrics, addNotification]);

  const loadConstructAudit = useCallback(async (force = false) => {
    if (!force && constructAudit) return;
    setConstructAuditLoading(true);
    try {
      const data = await fetchConstructAudit();
      setConstructAudit(data);
    } catch (err) {
      addNotification('Error fetching construct audit metrics.', 'error');
    } finally {
      setConstructAuditLoading(false);
    }
  }, [constructAudit, addNotification]);


  const value = {
    rawText, setRawText, analyzing, sandboxResult, runAnalysis, generateDiagnosticReport,
    whatIfText, setWhatIfText, targetWord, setTargetWord, replacementWord, setReplacementWord, whatIfLoading, whatIfResult, executeWhatIf,
    searchQuery, setSearchQuery, searchLoading, searchResults, executeSearch,
    fairnessResults, fairnessLoading, loadFairness,
    temporalResults, temporalLoading, loadTemporal,
    modelMetrics, modelMetricsLoading, loadModelMetrics,
    robustnessMetrics, robustnessLoading, loadRobustness,
    constructAudit, constructAuditLoading, loadConstructAudit,
  };

  return <AnalysisContext.Provider value={value}>{children}</AnalysisContext.Provider>;
}
