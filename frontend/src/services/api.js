const rawBase = import.meta.env.VITE_API_BASE_URL;
let API_BASE = '/api/v1';

if (rawBase && rawBase !== 'undefined' && rawBase.trim() !== '') {
  const formattedBase = rawBase.startsWith('http') ? rawBase : `https://${rawBase}`;
  API_BASE = `${formattedBase.replace(/\/$/, '')}/api/v1`;
}

async function fetchJSON(url, options = {}) {
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };
  
  const token = localStorage.getItem('agentshield_token');
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || 'API Request Failed');
  }

  return response.json();
}

export const api = {
  // Auth
  login: (data) => fetchJSON('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  getMe: () => fetchJSON('/auth/me'),

  // Analytics & Executions
  getOverview: () => fetchJSON('/analytics/overview'),
  getRecentExecutions: () => fetchJSON('/analytics/recent-executions'),

  // Agents
  getAgents: () => fetchJSON('/agents'),
  createAgent: (data) => fetchJSON('/agents', { method: 'POST', body: JSON.stringify(data) }),
  toggleAgentStatus: (agentId, status) => fetchJSON(`/agents/${agentId}/status?status=${status}`, { method: 'PUT' }),
  rotateAgentKey: (agentId) => fetchJSON(`/agents/${agentId}/rotate-key`, { method: 'POST' }),

  // Tools & Permissions
  getTools: () => fetchJSON('/tools'),
  registerTool: (data) => fetchJSON('/tools', { method: 'POST', body: JSON.stringify(data) }),
  getPermissionMatrix: () => fetchJSON('/permissions/matrix'),
  updatePermission: (data) => fetchJSON('/permissions/update', { method: 'POST', body: JSON.stringify(data) }),

  // Security Gateway
  executeToolGateway: (data, apiKey) => fetchJSON('/gateway/execute', {
    method: 'POST',
    headers: apiKey ? { 'X-Agent-API-Key': apiKey } : {},
    body: JSON.stringify(data),
  }),

  // Policies
  getPolicies: () => fetchJSON('/policies'),
  createPolicy: (data) => fetchJSON('/policies', { method: 'POST', body: JSON.stringify(data) }),
  togglePolicy: (id) => fetchJSON(`/policies/${id}/toggle`, { method: 'PUT' }),

  // Approvals
  getApprovals: (statusFilter) => fetchJSON(`/approvals${statusFilter ? `?status_filter=${statusFilter}` : ''}`),
  respondApproval: (id, action, reason) => fetchJSON(`/approvals/${id}/action`, {
    method: 'POST',
    body: JSON.stringify({ action, reason }),
  }),

  // Verification & Events
  getVerifications: () => fetchJSON('/verification'),
  getSecurityEvents: () => fetchJSON('/events'),

  // Audit Logs
  getAuditLogs: () => fetchJSON('/audit'),

  // AI Agent Simulator
  simulateAgent: (data) => fetchJSON('/agents-demo/simulate', { method: 'POST', body: JSON.stringify(data) }),
};
