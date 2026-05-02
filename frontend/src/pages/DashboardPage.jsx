import { apiBaseUrl } from "../api/client";
import { SectionHeading } from "../components/SectionHeading";

const placeholders = [
  { label: "Ticker", value: "AAPL" },
  { label: "Recommendation", value: "Pending engine" },
  { label: "Confidence", value: "--" },
  { label: "Risk", value: "--" },
];

export function DashboardPage() {
  return (
    <section className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-16">
      <SectionHeading
        eyebrow="Dashboard shell"
        title="Phase 1 keeps the product interface in place without business logic."
        description="The dashboard route, layout, and API boundary are ready. Future phases will connect ticker search, charts, and recommendation data."
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

          <div className="rounded-[1.5rem] border border-dashed border-white/15 bg-slate-950/60 p-6">
            <div className="flex flex-col gap-4 sm:flex-row">
              <input
                type="text"
                placeholder="Ticker search coming in Phase 7"
                disabled
                className="w-full rounded-full border border-white/10 bg-slate-900 px-5 py-3 text-sm text-slate-400 outline-none"
              />
              <button
                type="button"
                disabled
                className="rounded-full bg-white/10 px-5 py-3 text-sm font-semibold text-slate-400"
              >
                Analyze
              </button>
            </div>

            <div className="mt-6 flex h-72 items-center justify-center rounded-[1.5rem] border border-white/10 bg-[linear-gradient(180deg,rgba(15,23,42,0.85),rgba(2,6,23,1))] text-sm text-slate-500">
              Chart area reserved for Recharts integration
            </div>
          </div>
        </div>

        <div className="space-y-6">
          {placeholders.map((item) => (
            <div key={item.label} className="rounded-[1.5rem] border border-white/10 bg-white/5 p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">{item.label}</p>
              <p className="mt-3 text-xl font-semibold text-white">{item.value}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

