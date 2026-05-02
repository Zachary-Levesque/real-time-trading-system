import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { apiBaseUrl, getPriceSnapshot, getRecommendation, getSignals } from "../api/client";
import { SectionHeading } from "../components/SectionHeading";

const defaultTicker = "AAPL";

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

export function DashboardPage() {
  const [tickerInput, setTickerInput] = useState(defaultTicker);
  const [activeTicker, setActiveTicker] = useState(defaultTicker);
  const [priceSnapshot, setPriceSnapshot] = useState(null);
  const [signalResult, setSignalResult] = useState(null);
  const [recommendationResult, setRecommendationResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      setLoading(true);
      setError("");

      try {
        const normalizedTicker = activeTicker.trim().toUpperCase();
        const [pricePayload, signalPayload, recommendationPayload] = await Promise.all([
          getPriceSnapshot(normalizedTicker),
          getSignals(normalizedTicker),
          getRecommendation(normalizedTicker),
        ]);

        if (cancelled) {
          return;
        }

        setPriceSnapshot(pricePayload);
        setSignalResult(signalPayload);
        setRecommendationResult(recommendationPayload);
      } catch (loadError) {
        if (cancelled) {
          return;
        }

        setPriceSnapshot(null);
        setSignalResult(null);
        setRecommendationResult(null);
        setError(loadError.message);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadDashboard();

    return () => {
      cancelled = true;
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

    setActiveTicker(normalizedTicker);
  }

  return (
    <section className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-16">
      <SectionHeading
        eyebrow="Product dashboard"
        title="Search a ticker and inspect the system output end to end."
        description="This view reads the current file-backed API for price history, signal breakdown, and recommendation logic. Phase 7 focuses on making the data usable, not just available."
      />

      <div className="grid gap-6 lg:grid-cols-[1.4fr_0.6fr]">
        <div className="rounded-[2rem] border border-white/10 bg-slate-900/70 p-6">
          <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-sky-300">API boundary</p>
              <p className="mt-2 text-sm text-slate-300">Frontend expects backend routes under:</p>
            </div>
            <code className="rounded-full border border-white/10 bg-slate-950 px-4 py-2 text-xs text-emerald-200">
              {apiBaseUrl}
            </code>
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
                {loading ? "Loading..." : "Analyze"}
              </button>
            </form>

            {error ? (
              <div className="mt-6 rounded-[1.5rem] border border-rose-400/20 bg-rose-400/10 p-5 text-sm text-rose-100">
                {error}
              </div>
            ) : null}

            <div className="mt-6 grid gap-4 rounded-[1.5rem] border border-white/10 bg-[linear-gradient(180deg,rgba(15,23,42,0.85),rgba(2,6,23,1))] p-5">
              <div className="flex flex-wrap items-end justify-between gap-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-300">Price snapshot</p>
                  <p className="mt-2 text-3xl font-semibold text-white">
                    {priceSnapshot ? formatCurrency(priceSnapshot.data.current_price, priceSnapshot.data.currency ?? "USD") : "--"}
                  </p>
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
                    {loading ? "Loading chart data..." : "Price history unavailable."}
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
            </div>
            <div className={`rounded-full border border-white/10 px-4 py-2 text-sm font-semibold ${riskTone(recommendationResult?.risk)}`}>
              Risk: {recommendationResult?.risk ?? "--"}
            </div>
          </div>

          <p className="mt-6 max-w-3xl text-base leading-8 text-slate-300">
            {recommendationResult?.reason ??
              "Run an analysis to see how current market signals translate into an explainable recommendation."}
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
        </div>
      </div>
    </section>
  );
}
