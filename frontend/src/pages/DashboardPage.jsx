import { useEffect, useRef, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  getPriceSnapshot,
  getRecommendation,
  getRecommendationHistory,
  getSignals,
  refreshAnalysis,
  getSystemStatus,
} from "../api/client";
import { SectionHeading } from "../components/SectionHeading";

const defaultTicker = "AAPL";
const quickTickers = ["AAPL", "MSFT", "NVDA", "SPY"];
const refreshIntervalMs = 60000;

function formatCurrency(value, currency = "USD") {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(value);
}

function formatPercent(value) {
  if (value === null || value === undefined) {
    return "--";
  }

  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

function formatChartLabel(timestamp) {
  return new Date(timestamp).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
  });
}

function riskTone(risk) {
  if (risk === "low") {
    return "text-emerald-300";
  }
  if (risk === "medium") {
    return "text-amber-300";
  }
  return "text-rose-300";
}

function recommendationTone(recommendation) {
  if (recommendation === "BUY") {
    return "text-emerald-300";
  }
  if (recommendation === "SELL") {
    return "text-rose-300";
  }
  return "text-amber-300";
}

function formatTimestamp(timestamp) {
  if (!timestamp) {
    return "--";
  }

  return new Date(timestamp).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function freshnessStatus(timestamp) {
  if (!timestamp) {
    return { label: "Unavailable", tone: "text-slate-400" };
  }

  const ageMinutes = (Date.now() - new Date(timestamp).getTime()) / 60000;

  if (ageMinutes <= 10) {
    return { label: "Fresh", tone: "text-emerald-300" };
  }
  if (ageMinutes <= 30) {
    return { label: "Aging", tone: "text-amber-300" };
  }
  return { label: "Stale", tone: "text-rose-300" };
}

export function DashboardPage() {
  const [tickerInput, setTickerInput] = useState(defaultTicker);
  const [activeTicker, setActiveTicker] = useState(defaultTicker);
  const [priceSnapshot, setPriceSnapshot] = useState(null);
  const [signalResult, setSignalResult] = useState(null);
  const [recommendationResult, setRecommendationResult] = useState(null);
  const [recommendationHistory, setRecommendationHistory] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [warning, setWarning] = useState("");
  const refreshOnNextLoadRef = useRef(false);

  async function loadDashboard(normalizedTicker, { triggerRefresh = false } = {}) {
    setLoading(true);
    setError("");
    setWarning("");
    let refreshError = null;

    if (triggerRefresh) {
      setRefreshing(true);
      try {
        await refreshAnalysis(normalizedTicker);
      } catch (error) {
        refreshError = error;
      } finally {
        setRefreshing(false);
      }
    }

    const [
      priceResult,
      signalResultResponse,
      recommendationResultResponse,
      recommendationHistoryResponse,
      systemStatusResponse,
    ] = await Promise.allSettled([
      getPriceSnapshot(normalizedTicker),
      getSignals(normalizedTicker),
      getRecommendation(normalizedTicker),
      getRecommendationHistory(normalizedTicker),
      getSystemStatus(),
    ]);

    const failures = [];
    const auxiliaryFailures = [];

    if (priceResult.status === "fulfilled") {
      setPriceSnapshot(priceResult.value);
    } else {
      setPriceSnapshot(null);
      failures.push("price");
    }

    if (signalResultResponse.status === "fulfilled") {
      setSignalResult(signalResultResponse.value);
    } else {
      setSignalResult(null);
      failures.push("signals");
    }

    if (recommendationResultResponse.status === "fulfilled") {
      setRecommendationResult(recommendationResultResponse.value);
    } else {
      setRecommendationResult(null);
      failures.push("recommendation");
    }

    if (recommendationHistoryResponse.status === "fulfilled") {
      setRecommendationHistory(recommendationHistoryResponse.value);
    } else {
      setRecommendationHistory(null);
      auxiliaryFailures.push("recommendation history");
    }

    if (systemStatusResponse.status === "fulfilled") {
      setSystemStatus(systemStatusResponse.value);
    } else {
      setSystemStatus(null);
      auxiliaryFailures.push("system status");
    }

    if (failures.length === 3) {
      const firstFailure =
        priceResult.status === "rejected"
          ? priceResult.reason
          : signalResultResponse.status === "rejected"
            ? signalResultResponse.reason
            : recommendationResultResponse.status === "rejected"
              ? recommendationResultResponse.reason
              : null;

      throw new Error(
        refreshError?.message ??
        firstFailure?.message ??
          `No analysis is available for ${normalizedTicker} yet. Run a live refresh or try AAPL, MSFT, NVDA, or SPY.`,
      );
    }

    const unavailableSections = [...failures, ...auxiliaryFailures];
    if (refreshError && unavailableSections.length > 0) {
      setWarning(
        `Live refresh failed: ${refreshError.message} Showing the latest saved data instead, and some sections are unavailable: ${unavailableSections.join(", ")}.`,
      );
    } else if (refreshError) {
      setWarning(`Live refresh failed: ${refreshError.message} Showing the latest saved analysis instead.`);
    } else if (unavailableSections.length > 0) {
      setWarning(`Some data is unavailable right now: ${unavailableSections.join(", ")}.`);
    }

    setLoading(false);
  }

  useEffect(() => {
    let cancelled = false;

    async function executeLoad() {
      try {
        const normalizedTicker = activeTicker.trim().toUpperCase();
        const triggerRefresh = refreshOnNextLoadRef.current;
        refreshOnNextLoadRef.current = false;
        await loadDashboard(normalizedTicker, { triggerRefresh });
      } catch (loadError) {
        if (cancelled) {
          return;
        }
        setPriceSnapshot(null);
        setSignalResult(null);
        setRecommendationResult(null);
        setRecommendationHistory(null);
        setError(loadError.message);
        setLoading(false);
      }
    }

    executeLoad();
    const intervalId = window.setInterval(executeLoad, refreshIntervalMs);

    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, [activeTicker]);

  const chartData =
    priceSnapshot?.data.points.map((point) => ({
      timestamp: point.timestamp,
      label: formatChartLabel(point.timestamp),
      close: Number(point.close.toFixed(2)),
      volume: point.volume,
    })) ?? [];

  const signalValues = signalResult?.data.values;
  const priceFreshness = freshnessStatus(priceSnapshot?.timestamp);
  const signalFreshness = freshnessStatus(signalResult?.timestamp);
  const recommendationFreshness = freshnessStatus(recommendationResult?.timestamp);
  const recommendationHistoryItems = recommendationHistory?.data ?? [];
  const latestHistoryEntry = recommendationHistoryItems[0] ?? null;
  const previousHistoryEntry = recommendationHistoryItems[1] ?? null;
  const recommendationShift =
    latestHistoryEntry && previousHistoryEntry
      ? latestHistoryEntry.recommendation === previousHistoryEntry.recommendation
        ? `Holding the same ${latestHistoryEntry.recommendation} posture as the previous run.`
        : `Shifted from ${previousHistoryEntry.recommendation} to ${latestHistoryEntry.recommendation} on the most recent run.`
      : "Recommendation history will appear as more background cycles complete.";
  const summaryCards = [
    { label: "Ticker", value: activeTicker },
    {
      label: "Recommendation",
      value: recommendationResult?.recommendation ?? "--",
      tone: recommendationTone(recommendationResult?.recommendation),
    },
    {
      label: "Confidence",
      value: recommendationResult ? `${Math.round(recommendationResult.confidence * 100)}%` : "--",
    },
    {
      label: "Risk",
      value: recommendationResult?.risk ?? "--",
      tone: riskTone(recommendationResult?.risk),
    },
  ];

  function handleSubmit(event) {
    event.preventDefault();
    const normalizedTicker = tickerInput.trim().toUpperCase();

    if (!normalizedTicker) {
      setError("Enter a ticker symbol to analyze.");
      return;
    }

    if (normalizedTicker === activeTicker) {
      void loadDashboard(normalizedTicker, { triggerRefresh: true }).catch((loadError) => {
        setPriceSnapshot(null);
        setSignalResult(null);
        setRecommendationResult(null);
        setRecommendationHistory(null);
        setError(loadError.message);
        setLoading(false);
      });
      return;
    }

    refreshOnNextLoadRef.current = true;
    setActiveTicker(normalizedTicker);
  }

  return (
    <section className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-16">
      <SectionHeading
        eyebrow="Dashboard"
        title="Search a ticker to see recent price action, market signals, and a recommendation."
        description="Run a live analysis for a ticker, then review the latest price action, signal breakdown, and recommendation history."
      />

      <div className="grid gap-6 lg:grid-cols-[1.4fr_0.6fr]">
        <div className="rounded-[2rem] border border-white/10 bg-slate-900/70 p-6">
          <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-sky-300">Live market analysis</p>
              <p className="mt-2 text-sm text-slate-300">Analyze can run the full pipeline on demand, then the dashboard keeps polling the saved result every minute.</p>
            </div>
            <p className="rounded-full border border-white/10 bg-slate-950 px-4 py-2 text-xs text-emerald-200">
              Auto-refreshes every minute
            </p>
          </div>

          <div className="rounded-[1.5rem] border border-white/10 bg-slate-950/60 p-6">
            <form className="flex flex-col gap-4 sm:flex-row" onSubmit={handleSubmit}>
              <input
                type="text"
                placeholder="Search ticker, e.g. AAPL"
                value={tickerInput}
                onChange={(event) => setTickerInput(event.target.value.toUpperCase())}
                className="w-full rounded-full border border-white/10 bg-slate-900 px-5 py-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-300/40"
              />
              <button
                type="submit"
                className="rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
              >
                {refreshing ? "Running live refresh..." : loading ? "Loading..." : "Analyze"}
              </button>
            </form>

            <div className="mt-4 flex flex-wrap gap-3">
              {quickTickers.map((ticker) => (
                <button
                  key={ticker}
                  type="button"
                  onClick={() => {
                    setTickerInput(ticker);
                    if (ticker === activeTicker) {
                      void loadDashboard(ticker, { triggerRefresh: true }).catch((loadError) => {
                        setPriceSnapshot(null);
                        setSignalResult(null);
                        setRecommendationResult(null);
                        setRecommendationHistory(null);
                        setError(loadError.message);
                        setLoading(false);
                      });
                      return;
                    }
                    refreshOnNextLoadRef.current = true;
                    setActiveTicker(ticker);
                  }}
                  className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-200 transition hover:border-cyan-300/40 hover:text-white"
                >
                  {ticker}
                </button>
              ))}
            </div>

            {error ? (
              <div className="mt-6 rounded-[1.5rem] border border-rose-400/20 bg-rose-400/10 p-5 text-sm text-rose-100">
                {error}
              </div>
            ) : null}
            {warning ? (
              <div className="mt-4 rounded-[1.5rem] border border-amber-400/20 bg-amber-400/10 p-5 text-sm text-amber-100">
                {warning}
              </div>
            ) : null}

            <div className="mt-6 grid gap-4 rounded-[1.5rem] border border-white/10 bg-[linear-gradient(180deg,rgba(15,23,42,0.85),rgba(2,6,23,1))] p-5">
              <div className="flex flex-wrap items-end justify-between gap-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-300">Price snapshot</p>
                  <p className="mt-2 text-3xl font-semibold text-white">
                    {priceSnapshot ? formatCurrency(priceSnapshot.data.current_price, priceSnapshot.data.currency ?? "USD") : "--"}
                  </p>
                  <div className="mt-2 flex items-center gap-3 text-xs text-slate-400">
                    <span>Updated {formatTimestamp(priceSnapshot?.timestamp)}</span>
                    <span className={priceFreshness.tone}>{priceFreshness.label}</span>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-slate-400">Latest move</p>
                  <p
                    className={`mt-2 text-lg font-semibold ${
                      (priceSnapshot?.data.change ?? 0) >= 0 ? "text-emerald-300" : "text-rose-300"
                    }`}
                  >
                    {priceSnapshot ? formatPercent(priceSnapshot.data.change_percent) : "--"}
                  </p>
                </div>
              </div>

              <div className="h-72">
                {chartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <defs>
                        <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.45} />
                          <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.02} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid stroke="rgba(148, 163, 184, 0.12)" vertical={false} />
                      <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 12 }} tickLine={false} axisLine={false} minTickGap={24} />
                      <YAxis
                        tick={{ fill: "#94a3b8", fontSize: 12 }}
                        tickLine={false}
                        axisLine={false}
                        domain={["dataMin - 1", "dataMax + 1"]}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#020617",
                          border: "1px solid rgba(148, 163, 184, 0.18)",
                          borderRadius: "16px",
                          color: "#e2e8f0",
                        }}
                      />
                      <Area type="monotone" dataKey="close" stroke="#38bdf8" strokeWidth={2.5} fill="url(#priceFill)" />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex h-full items-center justify-center text-sm text-slate-500">
                    {loading ? "Loading chart data..." : `No saved price history is available for ${activeTicker}.`}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          {summaryCards.map((item) => (
            <div key={item.label} className="rounded-[1.5rem] border border-white/10 bg-white/5 p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">{item.label}</p>
              <p className={`mt-3 text-xl font-semibold ${item.tone ?? "text-white"}`}>{item.value}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <div className="rounded-[1.8rem] border border-white/10 bg-white/5 p-6">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-300">Signal breakdown</p>
          <div className="mt-2 flex items-center gap-3 text-xs text-slate-400">
            <span>Updated {formatTimestamp(signalResult?.timestamp)}</span>
            <span className={signalFreshness.tone}>{signalFreshness.label}</span>
          </div>
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {[
              ["Momentum", signalValues?.momentum ?? "--"],
              ["Trend", signalValues?.trend ?? "--"],
              ["Volatility", signalValues?.volatility ?? "--"],
              ["Volume", signalValues?.volume ?? "--"],
            ].map(([label, value]) => (
              <div key={label} className="rounded-[1.3rem] border border-white/10 bg-slate-900/70 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{label}</p>
                <p className="mt-3 text-lg font-semibold text-white">{value}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-[1.8rem] border border-white/10 bg-slate-900/70 p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-300">Recommendation rationale</p>
              <h3 className="mt-3 text-2xl font-semibold text-white">
                {recommendationResult?.recommendation ?? "--"} with{" "}
                {recommendationResult ? `${Math.round(recommendationResult.confidence * 100)}%` : "--"} confidence
              </h3>
              <div className="mt-2 flex items-center gap-3 text-xs text-slate-400">
                <span>Updated {formatTimestamp(recommendationResult?.timestamp)}</span>
                <span className={recommendationFreshness.tone}>{recommendationFreshness.label}</span>
              </div>
            </div>
            <div className={`rounded-full border border-white/10 px-4 py-2 text-sm font-semibold ${riskTone(recommendationResult?.risk)}`}>
              Risk: {recommendationResult?.risk ?? "--"}
            </div>
          </div>

          <p className="mt-6 max-w-3xl text-base leading-8 text-slate-300">
            {recommendationResult?.reason ?? `No saved recommendation is available for ${activeTicker} yet.`}
          </p>

          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            <div className="rounded-[1.3rem] border border-white/10 bg-white/[0.04] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Data source</p>
              <p className="mt-3 text-sm text-white">{priceSnapshot?.data.source ?? "--"}</p>
            </div>
            <div className="rounded-[1.3rem] border border-white/10 bg-white/[0.04] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Interval</p>
              <p className="mt-3 text-sm text-white">{priceSnapshot?.data.interval ?? "--"}</p>
            </div>
            <div className="rounded-[1.3rem] border border-white/10 bg-white/[0.04] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Points loaded</p>
              <p className="mt-3 text-sm text-white">{signalResult?.data.data_points_used ?? "--"}</p>
            </div>
          </div>

          <div className="mt-8 rounded-[1.3rem] border border-white/10 bg-white/[0.04] p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Worker status</p>
            <p className="mt-3 text-sm text-white">
              {systemStatus === null
                ? "System status is unavailable right now"
                : systemStatus.worker.enabled
                ? `Background refresh every ${systemStatus.worker.interval_seconds}s for ${systemStatus.worker.tickers.join(", ")}`
                : "Automatic refresh is currently turned off"}
            </p>
            <p className="mt-2 text-xs text-slate-400">
              Last completed: {formatTimestamp(systemStatus?.worker?.last_completed_at)}
            </p>
          </div>

          <div className="mt-8 rounded-[1.3rem] border border-white/10 bg-white/[0.04] p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Recommendation history</p>
                <p className="mt-2 text-sm text-slate-300">{recommendationShift}</p>
              </div>
              <p className="text-xs text-slate-400">Updated {formatTimestamp(recommendationHistory?.timestamp)}</p>
            </div>

            <div className="mt-5 space-y-3">
              {recommendationHistoryItems.length > 0 ? (
                recommendationHistoryItems.map((entry) => (
                  <div
                    key={entry.timestamp}
                    className="flex flex-wrap items-center justify-between gap-3 rounded-[1rem] border border-white/10 bg-slate-950/50 px-4 py-3"
                  >
                    <div>
                      <p className={`text-sm font-semibold ${recommendationTone(entry.recommendation)}`}>
                        {entry.recommendation}
                      </p>
                      <p className="mt-1 text-xs text-slate-400">{formatTimestamp(entry.timestamp)}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-white">{Math.round(entry.confidence * 100)}% confidence</p>
                      <p className={`mt-1 text-xs ${riskTone(entry.risk)}`}>Risk: {entry.risk}</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">
                  {loading ? "Loading recommendation history..." : `No saved recommendation history is available for ${activeTicker} yet.`}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
