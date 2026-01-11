import { useParams, useNavigate, Link } from 'react-router-dom';
import { useMonitor, useDeleteMonitor, useTriggerRun } from '../hooks/useMonitors';
import { useResults } from '../hooks/useResults';
import ResultsList from '../components/ResultsList';

function MonitorDetailPage() {
  const { monitorId } = useParams();
  const navigate = useNavigate();

  const { data: monitor, isLoading: monitorLoading } = useMonitor(monitorId);
  const { data: resultsData, isLoading: resultsLoading } = useResults(monitorId, 20);
  const deleteMonitor = useDeleteMonitor();
  const triggerRun = useTriggerRun();

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this monitor? All results will be lost.')) {
      try {
        await deleteMonitor.mutateAsync(monitorId);
        navigate('/');
      } catch (error) {
        console.error('Error deleting monitor:', error);
      }
    }
  };

  const handleRunNow = async () => {
    try {
      await triggerRun.mutateAsync(monitorId);
      alert('Monitor run triggered! Results will appear shortly.');
    } catch (error) {
      console.error('Error triggering run:', error);
      alert('Error triggering run: ' + error.message);
    }
  };

  if (monitorLoading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading monitor...</p>
      </div>
    );
  }

  if (!monitor) {
    return (
      <div className="error">
        Monitor not found
      </div>
    );
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  const getCadenceLabel = (cadence) => {
    const labels = {
      'hourly': 'Every Hour',
      '6hours': 'Every 6 Hours',
      '12hours': 'Every 12 Hours',
      'daily': 'Daily',
      'weekly': 'Weekly'
    };
    return labels[cadence] || cadence;
  };

  return (
    <div>
      <Link to="/" className="back-link">
        ← Back to Monitors
      </Link>

      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
          <div style={{ flex: 1 }}>
            <h2 style={{ color: '#667eea', marginBottom: '16px', fontSize: '1.5rem' }}>
              {monitor.query}
            </h2>

            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', marginBottom: '16px' }}>
              <div>
                <strong style={{ color: '#666' }}>Frequency:</strong>{' '}
                <span className="badge badge-info">{getCadenceLabel(monitor.cadence)}</span>
              </div>
              <div>
                <strong style={{ color: '#666' }}>Status:</strong>{' '}
                <span className={`badge ${monitor.status === 'active' ? 'badge-success' : 'badge-warning'}`}>
                  {monitor.status}
                </span>
              </div>
              <div>
                <strong style={{ color: '#666' }}>Tracked URLs:</strong> {monitor.seen_urls_count}
              </div>
            </div>

            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', fontSize: '0.9rem', color: '#666' }}>
              <div>
                <strong>Created:</strong> {formatDate(monitor.created_at)}
              </div>
              <div>
                <strong>Last Run:</strong> {formatDate(monitor.last_run_at)}
              </div>
              <div>
                <strong>Next Run:</strong> {formatDate(monitor.next_run_at)}
              </div>
            </div>

            {monitor.webhook_url && (
              <div style={{ marginTop: '12px', fontSize: '0.9rem', color: '#666' }}>
                <strong>Webhook:</strong> {monitor.webhook_url}
              </div>
            )}
          </div>

          <div style={{ display: 'flex', gap: '8px', flexDirection: 'column' }}>
            <button
              className="btn btn-primary"
              onClick={handleRunNow}
              disabled={triggerRun.isPending}
            >
              {triggerRun.isPending ? 'Running...' : 'Run Now'}
            </button>
            <button
              className="btn btn-danger"
              onClick={handleDelete}
              disabled={deleteMonitor.isPending}
            >
              {deleteMonitor.isPending ? 'Deleting...' : 'Delete'}
            </button>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: '20px', fontSize: '1.3rem' }}>Results History</h3>

        {resultsLoading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Loading results...</p>
          </div>
        ) : resultsData && resultsData.results && resultsData.results.length > 0 ? (
          <ResultsList results={resultsData.results} />
        ) : (
          <p style={{ color: '#999', textAlign: 'center', padding: '40px' }}>
            No results yet. Click "Run Now" to execute the first check.
          </p>
        )}
      </div>
    </div>
  );
}

export default MonitorDetailPage;
