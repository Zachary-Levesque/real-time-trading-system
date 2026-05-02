import { Link } from "react-router-dom";

import { SectionHeading } from "../components/SectionHeading";

const highlights = [
  "FastAPI backend for low-latency recommendation serving",
  "Streaming-style signal processing for market data workflows",
  "Explainable Buy / Sell / Hold outputs with confidence and risk",
];

export function WelcomePage() {
  return (
    <div className="relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(34,197,94,0.18),_transparent_30%),linear-gradient(135deg,_rgba(59,130,246,0.12),_transparent_35%)]" />
      <div className="absolute inset-0 bg-grid opacity-40" />

      <section className="relative mx-auto flex min-h-[calc(100vh-73px)] max-w-6xl flex-col justify-center gap-14 px-6 py-20">
        <div className="grid gap-14 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
          <div className="space-y-8">
            <p className="inline-flex rounded-full border border-emerald-400/30 bg-emerald-400/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.3em] text-emerald-200">
              Production-style engineering project
            </p>
            <div className="space-y-6">
              <h1 className="max-w-4xl text-5xl font-semibold leading-tight text-white sm:text-6xl">
                Build a trading platform that proves backend and systems depth.
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-slate-300">
                Turn live market data into explainable trade recommendations through a modular backend, API-first
                contracts, and a dashboard that feels like a real internal product.
              </p>
            </div>
            <div className="flex flex-wrap gap-4">
              <Link
                to="/dashboard"
                className="rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
              >
                Open dashboard
              </Link>
              <a
                href="http://localhost:8000/docs"
                className="rounded-full border border-white/15 px-6 py-3 text-sm font-semibold text-white transition hover:border-white/30 hover:bg-white/5"
              >
                API docs
              </a>
            </div>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-panel backdrop-blur">
            <div className="space-y-5">
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-sky-300">Phase 1 foundation</p>
              <div className="grid gap-4">
                {highlights.map((item) => (
                  <div key={item} className="rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-slate-200">
                    {item}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="grid gap-10 rounded-[2rem] border border-white/10 bg-slate-900/60 p-8 lg:grid-cols-3">
          <SectionHeading
            eyebrow="What this project proves"
            title="Useful as a product, credible in interviews."
            description="The system is intentionally scoped around real engineering concerns: service boundaries, data flow, explainability, and deployability."
          />
          <div className="space-y-4 rounded-2xl border border-white/10 bg-white/5 p-6">
            <p className="text-sm font-semibold text-white">Current focus</p>
            <p className="text-sm leading-7 text-slate-300">
              Establish the backend and frontend shells so future phases can add ingestion, signal processing,
              recommendations, storage, and real-time updates without reworking the structure.
            </p>
          </div>
          <div className="space-y-4 rounded-2xl border border-white/10 bg-white/5 p-6">
            <p className="text-sm font-semibold text-white">Next phases</p>
            <p className="text-sm leading-7 text-slate-300">
              Data contracts, market data ingestion, signal logic, recommendation scoring, persistence, and background
              workers will layer into this foundation incrementally.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

