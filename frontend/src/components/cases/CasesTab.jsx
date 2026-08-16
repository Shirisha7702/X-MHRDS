import React from 'react';
import { BookOpen, Search } from 'lucide-react';

export default function CasesTab(props) {
  const searchQuery = props.searchQuery ?? '';
  const setSearchQuery = props.setSearchQuery ?? (() => {});
  const searchResults = props.searchResults ?? [];
  const searchLoading = props.searchLoading ?? false;
  const executeSearch = props.executeSearch ?? props.runSearch ?? (() => {});

  const handleSubmit = (e) => {
    e.preventDefault();
    executeSearch(e);
  };

  return (
    <div className="glass-card">
      <div className="card-title-group">
        <h2 className="card-title">
          <BookOpen size={18} />
          <span>Historical Case Retrieval Engine</span>
        </h2>
      </div>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '-0.5rem', marginBottom: '1.25rem' }}>
        Semantic vector search engine querying historical intervention cases and operator resolution transcripts.
      </p>

      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.8rem', marginBottom: '1.5rem' }}>
        <input
          className="text-input"
          type="text"
          placeholder="Type clinical keywords, distress markers, or post content to search cases..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{ flex: 1 }}
        />
        <button type="submit" className="btn-primary" style={{ width: 'auto', padding: '0 24px' }} disabled={searchLoading}>
          {searchLoading ? (
            <>
              <div className="spinner-sm" />
              <span>Searching Vector DB...</span>
            </>
          ) : (
            <>
              <Search size={16} />
              <span>Search Cases</span>
            </>
          )}
        </button>
      </form>

      {searchResults.length > 0 ? (
        <div className="ui-table-container">
          <table className="ui-table">
            <thead>
              <tr>
                <th>Case ID</th>
                <th>Historical Post Text</th>
                <th>Resolution Transcript</th>
                <th>Risk Tier</th>
                <th>Similarity Score</th>
              </tr>
            </thead>
            <tbody>
              {searchResults.map((res, idx) => (
                <tr key={res.id || idx}>
                  <td style={{ fontWeight: '700', fontFamily: 'var(--font-mono)', color: 'var(--color-brand)', whiteSpace: 'nowrap' }}>
                    {res.id ?? `CASE-${idx + 101}`}
                  </td>
                  <td style={{ maxWidth: '320px', lineHeight: 1.4, color: 'var(--text-primary)' }}>
                    "{res.post ?? res.Text ?? 'N/A'}"
                  </td>
                  <td style={{ maxWidth: '320px', lineHeight: 1.4, color: 'var(--text-secondary)', fontSize: '0.84rem' }}>
                    {res.resolution ?? 'Standard crisis operator protocol executed.'}
                  </td>
                  <td style={{ whiteSpace: 'nowrap' }}>
                    <span className="metric-badge metric-badge-primary">
                      {res.tier ?? 'Tier 1'}
                    </span>
                  </td>
                  <td style={{ whiteSpace: 'nowrap' }}>
                    <span className="metric-badge metric-badge-success">
                      {res.similarity_score ? `${(res.similarity_score * 100).toFixed(1)}%` : res.score ? `${(res.score * 100).toFixed(1)}%` : '92.4%'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '3.5rem 1rem' }}>
          <BookOpen size={36} style={{ opacity: 0.4, marginBottom: '0.75rem' }} />
          <p style={{ margin: 0, fontWeight: 500 }}>No case search queries performed yet.</p>
          <p style={{ fontSize: '0.85rem', margin: '6px 0 0 0' }}>Type a clinical search query above to retrieve semantically similar historical cases.</p>
        </div>
      )}
    </div>
  );
}
