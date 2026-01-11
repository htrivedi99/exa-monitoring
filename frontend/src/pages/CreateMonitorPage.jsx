import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useCreateMonitor } from '../hooks/useMonitors';

function CreateMonitorPage() {
  const navigate = useNavigate();
  const createMonitor = useCreateMonitor();

  const [formData, setFormData] = useState({
    query: '',
    cadence: 'daily',
    webhook_url: '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const data = {
        query: formData.query,
        cadence: formData.cadence,
      };

      // Only include webhook_url if it's not empty
      if (formData.webhook_url) {
        data.webhook_url = formData.webhook_url;
      }

      const result = await createMonitor.mutateAsync(data);
      navigate(`/monitors/${result.id}`);
    } catch (error) {
      console.error('Error creating monitor:', error);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div>
      <Link to="/" className="back-link">
        ← Back to Monitors
      </Link>

      <div className="page-header">
        <h2 className="page-title">Create New Monitor</h2>
      </div>

      <div className="card" style={{ maxWidth: '600px' }}>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="query">
              Search Query *
            </label>
            <textarea
              id="query"
              name="query"
              placeholder="e.g., FDA approvals for diabetes drugs"
              value={formData.query}
              onChange={handleChange}
              required
            />
            <small style={{ color: '#666', fontSize: '0.9rem' }}>
              Describe what you want to monitor on the internet
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="cadence">
              Check Frequency *
            </label>
            <select
              id="cadence"
              name="cadence"
              value={formData.cadence}
              onChange={handleChange}
              required
            >
              <option value="hourly">Hourly</option>
              <option value="6hours">Every 6 Hours</option>
              <option value="12hours">Every 12 Hours</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="webhook_url">
              Webhook URL (Optional)
            </label>
            <input
              id="webhook_url"
              name="webhook_url"
              type="url"
              placeholder="https://your-webhook.com/endpoint"
              value={formData.webhook_url}
              onChange={handleChange}
            />
            <small style={{ color: '#666', fontSize: '0.9rem' }}>
              We'll send a POST request here when significant changes are detected
            </small>
          </div>

          {createMonitor.error && (
            <div className="error">
              Error: {createMonitor.error.message}
            </div>
          )}

          <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={createMonitor.isPending}
            >
              {createMonitor.isPending ? 'Creating...' : 'Create Monitor'}
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate('/')}
              disabled={createMonitor.isPending}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateMonitorPage;
