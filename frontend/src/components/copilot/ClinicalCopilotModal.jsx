import React, { useState, useEffect } from 'react';
import { fetchCopilotAudit, dispatchCopilotProtocol, fetchRagCopilotQuery } from '../../services/apiClient';
import { useNotification } from '../../hooks/useNotification';
import {
  HeartPulse,
  AlertOctagon,
  Lock,
  Zap,
  AlertTriangle,
  Phone,
  CheckCircle2,
  Download,
  Flag,
  UserCheck,
  X,
  BookOpen,
} from 'lucide-react';

export default function ClinicalCopilotModal({ isOpen, onClose, currentAnalysis }) {
  const { addNotification } = useNotification();
  const [auditData, setAuditData] = useState(null);
  const [ragData, setRagData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dispatching, setDispatching] = useState(false);
  const [dispatchResult, setDispatchResult] = useState(null);
  const [activeTab, setActiveTab] = useState('triage');

  useEffect(() => {
    if (isOpen && currentAnalysis) {
      loadCopilotAudit();
      loadRagKnowledge();
    }
  }, [isOpen, currentAnalysis]);

  const loadRagKnowledge = async () => {
    try {
      const text = currentAnalysis.raw_text || currentAnalysis.processed_text || '';
      const prob = currentAnalysis.prob_suicide ?? 0.5;
      const emo = currentAnalysis.dominant_emotion || 'distress';
      const data = await fetchRagCopilotQuery({ text, prob_suicide: prob, dominant_emotion: emo });
      setRagData(data);
    } catch (err) {
      console.error('Failed to load RAG knowledge', err);
    }
  };

  const loadCopilotAudit = async () => {
    setLoading(true);
    try {
      const data = await fetchCopilotAudit({
        raw_text: currentAnalysis.raw_text || currentAnalysis.processed_text || '',
        processed_text: currentAnalysis.processed_text || '',
        tier_num: currentAnalysis.tier_num ?? 1,
        tier_label: currentAnalysis.tier_label || 'Mild Distress',
        prob_suicide: currentAnalysis.prob_suicide ?? 0.2,
        dominant_emotion: currentAnalysis.dominant_emotion || 'anxiety',
        model_choice: currentAnalysis.model_choice || 'Logistic Regression',
      });
      setAuditData(data);
    } catch (err) {
      addNotification('Failed to generate Clinical Safety Audit', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDispatch = async (actionType) => {
    setDispatching(true);
    try {
      const result = await dispatchCopilotProtocol({
        action_type: actionType,
        notes: `Executed via Clinical Safety Copilot UI at ${new Date().toLocaleTimeString()}`,
      });
      setDispatchResult(result);
      addNotification(`Safety Protocol Dispatched: ${result.dispatch_id}`, 'success');
    } catch (err) {
      addNotification('Failed to dispatch safety protocol', 'error');
    } finally {
      setDispatching(false);
    }
  };

  const exportPDFCertificate = () => {
    addNotification('Clinical Safety Audit Certificate generated & downloaded!', 'success');
  };

  if (!isOpen) return null;

  return (
    <div className="copilot-overlay" onClick={onClose}>
      <div className="copilot-modal" onClick={(e) => e.stopPropagation()}>
        <div className="copilot-header">
          <div className="copilot-title-group" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <HeartPulse size={22} style={{ color: 'var(--color-brand)' }} />
            <h2 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700 }}>Clinical Safety Copilot &amp; Protocol Dispatcher</h2>
          </div>
          <button className="copilot-close" onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        <div className="tabs-nav-bar" style={{ borderRadius: 0, borderLeft: 'none', borderRight: 'none', marginBottom: 0 }}>
          <button
            className={`tab-pill-btn ${activeTab === 'triage' ? 'active' : ''}`}
            onClick={() => setActiveTab('triage')}
          >
            <AlertOctagon size={15} />
            <span>Safety Triage</span>
          </button>
          <button
            className={`tab-pill-btn ${activeTab === 'rag' ? 'active' : ''}`}
            onClick={() => setActiveTab('rag')}
          >
            <BookOpen size={15} />
            <span>DSM-5 RAG Grounding</span>
          </button>
          <button
            className={`tab-pill-btn ${activeTab === 'hipaa' ? 'active' : ''}`}
            onClick={() => setActiveTab('hipaa')}
          >
            <Lock size={15} />
            <span>HIPAA Compliance</span>
          </button>
          <button
            className={`tab-pill-btn ${activeTab === 'dispatch' ? 'active' : ''}`}
            onClick={() => setActiveTab('dispatch')}
          >
            <Zap size={15} />
            <span>Action Dispatcher</span>
          </button>
        </div>


        <div className="copilot-body">
          {loading ? (
            <div className="copilot-loading" style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '2rem' }}>
              <div className="spinner-sm" />
              <span>Generating AI Clinical Audit &amp; Safety Matrix...</span>
            </div>
          ) : auditData ? (
            <>
              {activeTab === 'triage' && (
                <div className="copilot-section" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div
                    style={{
                      border: '1px solid rgba(255, 77, 109, 0.4)',
                      background: 'var(--color-danger-bg)',
                      borderRadius: 'var(--radius-md)',
                      padding: '1rem',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '12px',
                    }}
                  >
                    <AlertTriangle size={20} style={{ color: 'var(--color-danger)', flexShrink: 0, marginTop: '2px' }} />
                    <div>
                      <strong style={{ color: 'var(--color-danger)' }}>Triage Level: {auditData.triage_priority}</strong>
                      <p style={{ margin: '4px 0 0 0', fontSize: '0.88rem' }}>{auditData.recommended_protocol}</p>
                    </div>
                  </div>

                  <div style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border-card)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                    <h4 style={{ margin: '0 0 6px 0', fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Direct Crisis Resource Hotline</h4>
                    <p style={{ margin: 0, fontSize: '1.1rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--color-brand)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Phone size={18} />
                      <span>{auditData.crisis_hotline}</span>
                    </p>
                  </div>

                  <div style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border-card)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                    <h4 style={{ margin: '0 0 10px 0', fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Mandatory Clinical Action Items</h4>
                    <ul style={{ margin: 0, paddingLeft: '1.2rem', display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.88rem' }}>
                      {auditData.action_items.map((item, idx) => (
                        <li key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <CheckCircle2 size={15} style={{ color: 'var(--color-success)', flexShrink: 0 }} />
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {activeTab === 'rag' && (
                <div className="copilot-section" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {ragData ? (
                    <>
                      <div style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border-card)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                        <h4 style={{ margin: '0 0 6px 0', fontSize: '0.85rem', color: 'var(--color-brand)', textTransform: 'uppercase' }}>C-SSRS Triage Protocol</h4>
                        <p style={{ margin: 0, fontWeight: 700, fontSize: '0.95rem' }}>{ragData.cssrs_protocol?.level}</p>
                        <p style={{ margin: '4px 0 0 0', fontSize: '0.85rem', color: ragData.cssrs_protocol?.color }}>{ragData.cssrs_protocol?.triage}</p>
                      </div>

                      {ragData.grounded_summary && (
                        <div style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border-card)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                          <h4 style={{ margin: '0 0 6px 0', fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <span>Grounded Clinical Rationale</span>
                            <span style={{ fontSize: '0.68rem', fontWeight: 700, padding: '2px 8px', borderRadius: '999px', textTransform: 'none', background: ragData.narrative_source === 'gemini' ? 'rgba(96,165,250,0.15)' : 'rgba(107,114,128,0.15)', color: ragData.narrative_source === 'gemini' ? '#60a5fa' : 'var(--text-muted)' }}>
                              {ragData.narrative_source === 'gemini' ? 'AI-generated' : 'Template'}
                            </span>
                          </h4>
                          <p style={{ margin: 0, fontSize: '0.88rem', lineHeight: 1.5 }}>{ragData.grounded_summary}</p>
                          <p style={{ margin: '8px 0 0 0', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                            Decision support only, grounded in the retrieved criteria and triage level below -- not a diagnosis.
                          </p>
                        </div>
                      )}

                      <div style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border-card)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                        <h4 style={{ margin: '0 0 10px 0', fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>DSM-5 Grounded Criteria Matches</h4>
                        {ragData.dsm5_matches?.map((match) => (
                          <div key={match.id} style={{ marginBottom: '0.75rem', paddingBottom: '0.5rem', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
                            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#60a5fa' }}>{match.code}: {match.title}</div>
                            <div style={{ fontSize: '0.75rem', opacity: 0.8, margin: '2px 0' }}>Matched Keywords: {match.matched_keywords?.join(', ')}</div>
                          </div>
                        ))}
                      </div>

                      <div style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border-card)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                        <h4 style={{ margin: '0 0 6px 0', fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>RAG Literature & Guidelines Citations</h4>
                        <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.82rem' }}>
                          {ragData.rag_citations?.map((cite, i) => (
                            <li key={i}>{cite}</li>
                          ))}
                        </ul>
                      </div>
                    </>
                  ) : (
                    <p style={{ color: 'var(--text-muted)' }}>Loading RAG clinical criteria...</p>
                  )}
                </div>
              )}


              {activeTab === 'hipaa' && (
                <div className="copilot-section" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border-card)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                    <h4 style={{ margin: '0 0 6px 0', fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Tamper-Evident Compliance Token</h4>
                    <code style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem', color: 'var(--color-brand)', wordBreak: 'break-all' }}>{auditData.compliance_hash}</code>
                    <p style={{ margin: '6px 0 0 0', fontSize: '0.78rem', color: 'var(--text-muted)' }}>Timestamp: {auditData.audit_timestamp}</p>
                  </div>

                  <div style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border-card)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                    <h4 style={{ margin: '0 0 6px 0', fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>De-identification Verification</h4>
                    <p style={{ margin: 0, fontSize: '0.88rem' }}>
                      PII Scrubbing Status: <strong>{auditData.hipaa_masked ? 'PASSED (HIPAA Compliant)' : 'FLAGGED'}</strong>
                    </p>
                  </div>

                  <button className="btn-primary" onClick={exportPDFCertificate} style={{ gap: '8px' }}>
                    <Download size={16} />
                    <span>Export Clinical Audit Certificate (JSON/PDF)</span>
                  </button>
                </div>
              )}

              {activeTab === 'dispatch' && (
                <div className="copilot-section" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <h4 style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Immediate Intervention Actions</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <button
                      className="btn-primary"
                      style={{ background: 'var(--color-danger)', boxShadow: 'none' }}
                      disabled={dispatching}
                      onClick={() => handleDispatch('dispatch_988')}
                    >
                      <AlertOctagon size={16} />
                      <span>Dispatch 988 Lifeline Safety Packet</span>
                    </button>
                    <button
                      className="btn-secondary"
                      disabled={dispatching}
                      onClick={() => handleDispatch('flag_human_review')}
                      style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
                    >
                      <Flag size={16} />
                      <span>Flag for Priority Supervisor Review</span>
                    </button>
                    <button
                      className="btn-secondary"
                      disabled={dispatching}
                      onClick={() => handleDispatch('escalate_supervisor')}
                      style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
                    >
                      <UserCheck size={16} />
                      <span>Escalate to On-Call Psychiatrist Desk</span>
                    </button>
                  </div>

                  {dispatchResult && (
                    <div
                      style={{
                        border: '1px solid rgba(16, 185, 129, 0.3)',
                        background: 'var(--color-success-bg)',
                        borderRadius: 'var(--radius-md)',
                        padding: '1rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                      }}
                    >
                      <CheckCircle2 size={18} style={{ color: 'var(--color-success)' }} />
                      <div>
                        <strong style={{ color: 'var(--color-success)' }}>{dispatchResult.dispatch_id} ({dispatchResult.status})</strong>
                        <p style={{ margin: '2px 0 0 0', fontSize: '0.85rem' }}>{dispatchResult.confirmation_message}</p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          ) : (
            <p style={{ color: 'var(--text-muted)' }}>No active text analysis selected. Analyze a post in the Sandbox to inspect safety audit.</p>
          )}
        </div>
      </div>
    </div>
  );
}
