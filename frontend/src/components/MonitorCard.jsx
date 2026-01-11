import { useNavigate } from 'react-router-dom';

function MonitorCard({ monitor }) {
  const navigate = useNavigate();

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  const getCadenceLabel = (cadence) => {
    const labels = {
      'hourly': 'Hourly',
      '6hours': '6 Hours',
      '12hours': '12 Hours',
      'daily': 'Daily',
      'weekly': 'Weekly'
    };
    return labels[cadence] || cadence;
  };

  return (
    <div
      className="card monitor-card"
      onClick={() => navigate(`/monitors/${monitor.id}`)}
    >
      <div className="monitor-card-header">
        <h3 className="monitor-card-title">{monitor.query}</h3>

        <div className="monitor-card-meta">
          <span className="badge badge-info">
            {getCadenceLabel(monitor.cadence)}
          </span>
          <span className={`badge ${monitor.status === 'active' ? 'badge-success' : 'badge-warning'}`}>
            {monitor.status}
          </span>
        </div>
      </div>

      <div style={{ fontSize: '0.9rem', color: '#666' }}>
        <div style={{ marginBottom: '8px' }}>
          <strong>Last run:</strong> {formatDate(monitor.last_run_at)}
        </div>
        <div style={{ marginBottom: '8px' }}>
          <strong>Next run:</strong> {formatDate(monitor.next_run_at)}
        </div>
        <div>
          <strong>Tracked URLs:</strong> {monitor.seen_urls_count}
        </div>
      </div>
    </div>
  );
}

export default MonitorCard;
