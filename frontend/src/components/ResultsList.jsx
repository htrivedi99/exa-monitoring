import { useState } from 'react';

function ResultsList({ results }) {
  const [expandedId, setExpandedId] = useState(null);

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div>
      {results.map((result) => (
        <div key={result.id} className="result-item">
          <div className="result-header">
            <div>
              <strong>{formatDate(result.run_at)}</strong>
              <span style={{ marginLeft: '12px', color: '#666' }}>
                {result.new_urls_count} new item{result.new_urls_count !== 1 ? 's' : ''}
              </span>
            </div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              {result.llm_analysis && result.llm_analysis.is_significant && (
                <span className="badge badge-warning">Significant</span>
              )}
              <span className={`badge ${
                result.status === 'completed' ? 'badge-success' :
                result.status === 'failed' ? 'badge-danger' :
                'badge-info'
              }`}>
                {result.status}
              </span>
              {result.webhook_sent && (
                <span className="badge badge-info">Webhook Sent</span>
              )}
            </div>
          </div>

          {result.llm_analysis && (
            <div style={{ marginTop: '12px', padding: '12px', background: '#f9fafb', borderRadius: '4px' }}>
              <strong style={{ display: 'block', marginBottom: '8px', color: '#667eea' }}>
                AI Analysis:
              </strong>
              <p style={{ margin: '0 0 8px 0' }}>{result.llm_analysis.summary}</p>

              {result.llm_analysis.key_changes && result.llm_analysis.key_changes.length > 0 && (
                <div style={{ marginTop: '8px' }}>
                  <strong style={{ fontSize: '0.9rem', color: '#666' }}>Key Changes:</strong>
                  <ul style={{ marginTop: '4px', marginLeft: '20px', fontSize: '0.9rem' }}>
                    {result.llm_analysis.key_changes.map((change, idx) => (
                      <li key={idx}>{change}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {result.new_urls_count > 0 && (
            <div style={{ marginTop: '12px' }}>
              <button
                className="btn btn-secondary"
                style={{ padding: '8px 16px', fontSize: '0.9rem' }}
                onClick={() => toggleExpand(result.id)}
              >
                {expandedId === result.id ? 'Hide URLs' : `Show ${result.new_urls_count} URL${result.new_urls_count !== 1 ? 's' : ''}`}
              </button>

              {expandedId === result.id && (
                <ul className="url-list">
                  {result.urls.map((url, idx) => (
                    <li key={idx} className="url-item">
                      <div className="url-item-title">{url.title}</div>
                      <a href={url.url} target="_blank" rel="noopener noreferrer">
                        {url.url}
                      </a>
                      {url.published_date && (
                        <div style={{ fontSize: '0.85rem', color: '#999', marginTop: '4px' }}>
                          Published: {new Date(url.published_date).toLocaleDateString()}
                        </div>
                      )}
                      {url.summary && (
                        <div className="url-item-summary">{url.summary}</div>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {result.status === 'failed' && result.error_message && (
            <div className="error" style={{ marginTop: '12px' }}>
              Error: {result.error_message}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default ResultsList;
