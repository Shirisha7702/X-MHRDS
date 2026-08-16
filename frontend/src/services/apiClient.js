const API_BASE = "http://localhost:8000/api";
const WS_BASE = "ws://localhost:8000/api";

async function fetchJson(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || response.statusText || 'Request failed');
  }

  return response.json();
}

export async function analyzeText(payload) {
  return fetchJson('/analyze', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function runWhatIf(payload) {
  return fetchJson('/what-if', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function searchCases(query, topN = 3) {
  return fetchJson('/search', {
    method: 'POST',
    body: JSON.stringify({ query, top_n: topN }),
  });
}

export async function fetchRobustness() {
  return fetchJson('/robustness');
}

export async function fetchModelMetrics() {
  return fetchJson('/metrics');
}

export async function fetchConstructAudit() {
  return fetchJson('/construct-audit');
}

export async function fetchFairness(modelChoice) {
  const encoded = encodeURIComponent(modelChoice);
  return fetchJson(`/fairness?model_choice=${encoded}`);
}

export async function fetchTemporal(modelChoice) {
  const encoded = encodeURIComponent(modelChoice);
  return fetchJson(`/temporal?model_choice=${encoded}`);
}

export async function createReport(payload) {
  return fetchJson('/report', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function startMonitor(modelChoice) {
  return fetchJson('/monitor/start', {
    method: 'POST',
    body: JSON.stringify({ model_choice: modelChoice }),
  });
}

export async function stopMonitor() {
  return fetchJson('/monitor/stop', { method: 'POST' });
}

export async function fetchMonitorStatus() {
  return fetchJson('/monitor/status');
}

export async function fetchMonitorUserTrends() {
  return fetchJson('/monitor/users');
}

export async function fetchCopilotAudit(payload) {
  return fetchJson('/copilot/audit', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function dispatchCopilotProtocol(payload) {
  return fetchJson('/copilot/dispatch-protocol', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function fetchExplainComparison(payload) {
  return fetchJson('/explain-comparison', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function analyzeMultilingualText(payload) {
  return fetchJson('/multilingual-analyze', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function fetchRagCopilotQuery(payload) {
  return fetchJson('/copilot/rag-query', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function fetchDriftMetrics() {
  return fetchJson('/drift-metrics');
}

export function connectMonitorSocket(onMessage) {
  const socket = new WebSocket(`${WS_BASE}/ws/monitor`);
  socket.onmessage = (event) => {
    try {
      onMessage(JSON.parse(event.data));
    } catch (err) {
      console.error('Failed to parse monitor event', err);
    }
  };
  return socket;
}

