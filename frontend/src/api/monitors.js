import { api } from './client';

export const monitorsAPI = {
  // Get all monitors
  getAll: () => api.get('/monitors'),

  // Get single monitor
  getById: (monitorId) => api.get(`/monitors/${monitorId}`),

  // Create new monitor
  create: (data) => api.post('/monitors', data),

  // Update monitor
  update: (monitorId, data) => api.put(`/monitors/${monitorId}`, data),

  // Delete monitor
  delete: (monitorId) => api.delete(`/monitors/${monitorId}`),

  // Manually trigger run
  triggerRun: (monitorId) => api.post(`/monitors/${monitorId}/run`, {}),

  // Get results for a monitor
  getResults: (monitorId, limit = 10, offset = 0) =>
    api.get(`/monitors/${monitorId}/results?limit=${limit}&offset=${offset}`),

  // Get single result
  getResult: (monitorId, resultId) =>
    api.get(`/monitors/${monitorId}/results/${resultId}`),
};
