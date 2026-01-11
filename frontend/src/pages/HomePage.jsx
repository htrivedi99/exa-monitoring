import { useNavigate } from 'react-router-dom';
import { useMonitors } from '../hooks/useMonitors';
import MonitorCard from '../components/MonitorCard';

function HomePage() {
  const navigate = useNavigate();
  const { data: monitors, isLoading, error } = useMonitors();

  if (isLoading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading monitors...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error">
        Error loading monitors: {error.message}
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">My Monitors</h2>
        <button
          className="btn btn-primary"
          onClick={() => navigate('/monitors/new')}
        >
          + Create New Monitor
        </button>
      </div>

      {monitors && monitors.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px 24px' }}>
          <h3 style={{ marginBottom: '16px', color: '#666' }}>No monitors yet</h3>
          <p style={{ color: '#999', marginBottom: '24px' }}>
            Create your first monitor to start tracking changes on the internet
          </p>
          <button
            className="btn btn-primary"
            onClick={() => navigate('/monitors/new')}
          >
            Create Your First Monitor
          </button>
        </div>
      ) : (
        <div className="grid">
          {monitors && monitors.map((monitor) => (
            <MonitorCard key={monitor.id} monitor={monitor} />
          ))}
        </div>
      )}
    </div>
  );
}

export default HomePage;
