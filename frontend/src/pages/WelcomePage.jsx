import { Link } from "react-router-dom";

import { SectionHeading } from "../components/SectionHeading";

const systemPillars = [
  {
    title: "Market Intake",
    text: "Recent market data is pulled, normalized, and saved into stable contracts that later services can trust.",
  },
  {
    title: "Signal Engine",
    text: "The platform converts price movement, trend, volatility, and volume into deterministic market signals.",
  },
  {
    title: "Recommendation Layer",
    text: "Signals are scored into explainable BUY, HOLD, or SELL outputs with confidence, risk, and reasoning.",
  },
];

const proofPoints = [
  "FastAPI backend with explicit API contracts",
  "Deterministic scoring with explicit signal weighting and bounded outputs",
  "Modular pipeline structure ready for storage and real-time updates",
];

export function WelcomePage() {
  return (
    <div className="relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(56,189,248,0.18),_transparent_28%),radial-gradient(circle_at_80%_10%,_rgba(244,114,182,0.14),_transparent_24%),linear-gradient(160deg,_rgba(15,23,42,0.2),_transparent_40%)]" />
      <div className="absolute inset-0 bg-grid opacity-30" />
      <div className="absolute left-1/2 top-24 h-80 w-80 -translate-x-1/2 rounded-full bg-cyan-400/10 blur-3xl" />

      <section className="relative mx-auto flex min-h-[calc(100vh-73px)] max-w-6xl flex-col gap-20 px-6 py-16 sm:py-20">
        <div className="grid gap-14 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div className="space-y-8">
            <div className="space-y-4">
              <p className="inline-flex rounded-full border border-cyan-300/25 bg-cyan-300/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.32em] text-cyan-100">
                Systems-first trading product
              </p>
              <h1 className="max-w-4xl text-5xl font-semibold leading-[1.02] text-white sm:text-6xl lg:text-7xl">
                See recent market moves translated into clear, explainable trade signals.
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-slate-300">
                Real-Time Trading System helps you explore recent stock activity, understand the signals behind it,
                and view a simple buy, hold, or sell recommendation with supporting context.
              </p>
            </div>

            <div className="flex flex-wrap gap-4">
              <Link
                to="/dashboard"
                className="rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
              >
                Start with dashboard
              </Link>
              <a
                href="http://localhost:8000/docs"
                className="rounded-full border border-white/15 px-6 py-3 text-sm font-semibold text-white transition hover:border-white/30 hover:bg-white/5"
              >
                Inspect API docs
              </a>
            </div>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-slate-950/60 p-6 shadow-panel backdrop-blur">
            <div className="rounded-[1.6rem] border border-white/10 bg-[linear-gradient(180deg,rgba(8,15,29,0.92),rgba(10,18,34,0.78))] p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.3em] text-sky-300">Current system state</p>
                  <p className="mt-2 text-2xl font-semibold text-white">Phase-based build</p>
                </div>
                <div className="rounded-full border border-emerald-300/20 bg-emerald-300/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-emerald-200">
                  Active
                </div>
              </div>

              <div className="mt-8 space-y-4">
                {systemPillars.map((pillar, index) => (
                  <div key={pillar.title} className="grid grid-cols-[auto_1fr] gap-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/10 text-sm font-semibold text-white">
                      0{index + 1}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-white">{pillar.title}</p>
                      <p className="mt-2 text-sm leading-6 text-slate-300">{pillar.text}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="grid gap-8 lg:grid-cols-[0.8fr_1.2fr]">
          <SectionHeading
            eyebrow="Why this matters"
            title="More than a trading model."
            description="The point of the project is not prediction theater. It is to show clean service boundaries, usable interfaces, explainable logic, and the discipline to ship a complete system."
          />

          <div className="grid gap-4 sm:grid-cols-3">
            {proofPoints.map((item) => (
              <div key={item} className="rounded-[1.7rem] border border-white/10 bg-slate-900/70 p-6">
                <p className="text-sm leading-7 text-slate-200">{item}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="grid gap-8 rounded-[2rem] border border-white/10 bg-white/[0.04] p-8 lg:grid-cols-[1fr_auto] lg:items-center">
          <div className="space-y-4">
            <h2 className="text-3xl font-semibold text-white sm:text-4xl">Ready to explore the dashboard?</h2>
          </div>
          <Link
            to="/dashboard"
            className="inline-flex items-center justify-center rounded-full border border-cyan-300/30 bg-cyan-300/10 px-6 py-3 text-sm font-semibold text-cyan-100 transition hover:border-cyan-200/50 hover:bg-cyan-300/15"
          >
            Continue to dashboard
          </Link>
        </div>
      </section>
    </div>
  );
}
