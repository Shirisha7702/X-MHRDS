import React from 'react';
import { Scale, AlertOctagon, AlertTriangle, FileText, CheckCircle2, XCircle } from 'lucide-react';

function formatPct(value) {
  return value === null || value === undefined ? '—' : `${(value * 100).toFixed(1)}%`;
}

function MetricCell({ metric }) {
  if (!metric || metric.point === null || metric.point === undefined) {
    return <span style={{ color: 'var(--text-muted)' }}>—</span>;
  }
  return (
    <div>
      <span className="metric-badge metric-badge-primary">{formatPct(metric.point)}</span>
      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
        95% CI [{formatPct(metric.ci_low)}, {formatPct(metric.ci_high)}]
      </div>
      {!metric.meets_min_subgroup_size && (
        <div style={{ fontSize: '0.7rem', color: 'var(--color-warning)', marginTop: '2px', display: 'flex', alignItems: 'center', gap: '3px' }}>
          <AlertTriangle size={12} />
          <span>n={metric.n} (under-powered)</span>
        </div>
      )}
    </div>
  );
}

export default function FairnessTab(props) {
  const fairnessResults = props.fairnessResults ?? {};
  const modelChoice = props.modelChoice ?? '';

  const {
    examples = [],
    cohort_summary: cohortSummary = [],
    fairness_gaps: fairnessGaps = [],
  } = fairnessResults || {};

  return (
    <div className="glass-card">
      <div className="card-title-group">
        <h2 className="card-title">
          <Scale size={18} />
          <span>Demographic Fairness &amp; Bias Audit</span>
        </h2>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          Auditing: <strong>{modelChoice}</strong>
        </span>
      </div>

      <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '-0.5rem', marginBottom: '1.25rem' }}>
        Evaluates predictions across linguistic cohorts using bootstrap 95% confidence intervals for accuracy,
        recall (catching real risk), and specificity (clearing non-risk text), gated on minimum subgroup sample sizes.
      </p>

      {/* Fairness Gaps Alert Banner */}
      {fairnessGaps.length > 0 && (
        <div
          style={{
            border: '1px solid rgba(255, 77, 109, 0.4)',
            background: 'var(--color-danger-bg)',
            borderRadius: 'var(--radius-md)',
            padding: '1rem 1.25rem',
            marginBottom: '1.5rem',
          }}
        >
          <div style={{ color: 'var(--color-danger)', fontWeight: '700', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertOctagon size={18} />
            <span>{fairnessGaps.length} Statistically Significant Fairness Gap{fairnessGaps.length > 1 ? 's' : ''} Detected</span>
          </div>
          <ul style={{ margin: '0.5rem 0 0 0', paddingLeft: '1.4rem', fontSize: '0.85rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>
            {fairnessGaps.map((gap, idx) => (
              <li key={idx}>
                <strong>{gap.metric}</strong> disparity: {gap.cohort_a} [{formatPct(gap.cohort_a_ci[0])}–{formatPct(gap.cohort_a_ci[1])}] vs{' '}
                {gap.cohort_b} [{formatPct(gap.cohort_b_ci[0])}–{formatPct(gap.cohort_b_ci[1])}] (non-overlapping 95% CIs)
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Cohort Summary Table */}
      {cohortSummary.length > 0 && (
        <div className="ui-table-container" style={{ marginBottom: '1.5rem' }}>
          <table className="ui-table">
            <thead>
              <tr>
                <th>Linguistic Cohort</th>
                <th>Sample (n)</th>
                <th>Accuracy</th>
                <th>Recall (catches risk)</th>
                <th>Specificity (clears non-risk)</th>
              </tr>
            </thead>
            <tbody>
              {cohortSummary.map((row) => (
                <tr key={row.cohort}>
                  <td style={{ fontWeight: '700' }}>{row.cohort}</td>
                  <td><span className="cell-mono">{row.n}</span></td>
                  <td><MetricCell metric={row.accuracy} /></td>
                  <td><MetricCell metric={row.recall} /></td>
                  <td><MetricCell metric={row.specificity} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Per-Example Results Table */}
      {examples.length > 0 && (
        <div>
          <div style={{ fontWeight: '700', fontSize: '0.95rem', color: 'var(--text-primary)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <FileText size={16} />
            <span>Per-Example Cohort Predictions ({examples.length} samples)</span>
          </div>
          <div className="ui-table-container" style={{ maxHeight: '320px', overflowY: 'auto' }}>
            <table className="ui-table">
              <thead>
                <tr>
                  <th>Cohort</th>
                  <th>Text Excerpt</th>
                  <th>True Label</th>
                  <th>Predicted</th>
                  <th>Risk Prob</th>
                  <th>Audit Status</th>
                </tr>
              </thead>
              <tbody>
                {examples.map((ex, idx) => {
                  const cohort = ex.Cohort ?? ex.cohort ?? 'N/A';
                  const text = ex.Text ?? ex.text ?? 'N/A';
                  const trueLabel = ex["True Label"] ?? ex.true_label ?? 'Non-Risk';
                  const predLabel = ex["Predicted Label"] ?? ex.predicted_label ?? 'Non-Risk';
                  const status = ex.Status ?? (trueLabel === predLabel ? 'Correct' : 'Misclassified');
                  const riskProbStr = ex["Risk Probability"] ?? (ex.prob_suicide !== undefined ? `${(ex.prob_suicide * 100).toFixed(2)}%` : '—');
                  const isCorrect = status === 'Correct' || trueLabel === predLabel;

                  return (
                    <tr key={idx}>
                      <td style={{ fontWeight: '600', whiteSpace: 'nowrap' }}>{cohort}</td>
                      <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {text}
                      </td>
                      <td>
                        <span className={`metric-badge ${trueLabel === 'Risk' ? 'metric-badge-danger' : 'metric-badge-success'}`}>
                          {trueLabel}
                        </span>
                      </td>
                      <td>
                        <span className={`metric-badge ${predLabel === 'Risk' ? 'metric-badge-danger' : 'metric-badge-success'}`}>
                          {predLabel}
                        </span>
                      </td>
                      <td>
                        <span className="cell-mono">{riskProbStr}</span>
                      </td>
                      <td>
                        <span className={`metric-badge ${isCorrect ? 'metric-badge-success' : 'metric-badge-warning'}`} style={{ gap: '4px' }}>
                          {isCorrect ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
                          <span>{status}</span>
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
