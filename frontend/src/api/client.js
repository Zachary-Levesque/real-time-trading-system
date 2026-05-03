const fallbackBaseUrl = "http://localhost:8000/api/v1";

export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? fallbackBaseUrl;

async function readJson(path, options = undefined) {
  let response;

  try {
    response = await fetch(`${apiBaseUrl}${path}`, options);
  } catch {
    throw new Error(
      `Cannot reach the backend API at ${apiBaseUrl}. Make sure the backend service is running on port 8000.`,
    );
  }

  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    if (typeof payload === "object" && payload !== null && "detail" in payload) {
      throw new Error(payload.detail);
    }
    throw new Error(typeof payload === "string" && payload ? payload : `Request failed for ${path}`);
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

export function getRecommendationHistory(ticker, limit = 6) {
  return readJson(`/recommendation/${ticker}/history?limit=${limit}`);
}

export function getSystemStatus() {
  return readJson("/system/status");
}

export function getTickerCatalog() {
  return readJson("/tickers");
}

export function refreshAnalysis(ticker) {
  return readJson(`/analysis/${ticker}/refresh`, {
    method: "POST",
  });
}
