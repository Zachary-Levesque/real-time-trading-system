const fallbackBaseUrl = "http://localhost:8000/api/v1";

export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? fallbackBaseUrl;

async function readJson(path) {
  const response = await fetch(`${apiBaseUrl}${path}`);
  const payload = await response.json();

  if (!response.ok) {
    throw new Error(payload.detail ?? `Request failed for ${path}`);
  }

  return payload;
}

export function getPriceSnapshot(ticker) {
  return readJson(`/price/${ticker}`);
}

export function getSignals(ticker) {
  return readJson(`/signals/${ticker}`);
}

export function getRecommendation(ticker) {
  return readJson(`/recommendation/${ticker}`);
}

export function getSystemStatus() {
  return readJson("/system/status");
}
