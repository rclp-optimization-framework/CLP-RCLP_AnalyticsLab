import {
  ArrowRight,
  BarChart3,
  Clock3,
  DatabaseZap,
  Layers3,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { mockBatteries, mockCaches, mockTests } from "../data/mockData";

const featureCards = [
  {
    icon: ShieldCheck,
    title: "Controlled execution",
    copy: "Each battery encapsulates one or many solver-ready test cases with consistent validation.",
  },
  {
    icon: DatabaseZap,
    title: "Research persistence",
    copy: "When storage is enabled, cache entries are routed through the transactional backend into the statistics layer",
  },
  {
    icon: BarChart3,
    title: "Analytics-ready output",
    copy: "Cache values feed ranking tables, deviation charts, and battery comparisons without manual processing.",
  },
];

export function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="space-y-12">
      <section className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
        <div className="space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-white/80 px-4 py-2 text-sm font-semibold text-blue-700 shadow-sm">
            <Sparkles className="h-4 w-4" />
            AVISPA research platform
          </div>
          <div className="space-y-4">
            <h1 className="max-w-3xl text-5xl font-bold leading-tight text-slate-950 sm:text-6xl">
              Execute test batteries, store solver outcomes, and turn them into
              decision-grade statistics.
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-slate-600">
              R-CLP Analytics centralizes the experimentation flow for bus
              charging-location studies, from JSON payload creation to cache-backed
              analytics and comparison dashboards.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => navigate("/execution")}
              className="inline-flex items-center gap-2 rounded-full bg-slate-950 px-6 py-3 text-sm font-semibold text-white shadow-glow transition hover:-translate-y-0.5"
            >
              Start execution
              <ArrowRight className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={() => navigate("/statistics")}
              className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-700 transition hover:border-blue-300 hover:text-blue-700"
            >
              Open analytics
            </button>
          </div>
        </div>

        <div className="glass-panel rounded-[2rem] p-6 shadow-panel">
          <div className="grid gap-4 sm:grid-cols-2">
            {mockBatteries.map((battery) => (
              <article
                key={battery.id}
                className="rounded-3xl bg-slate-950 p-5 text-white shadow-glow"
              >
                <p className="text-xs uppercase tracking-[0.35em] text-blue-300">
                  Battery {battery.id}
                </p>
                <h2 className="mt-3 text-2xl font-semibold">
                  {battery.nombre}
                </h2>
                <p className="mt-2 text-sm text-slate-300">
                  Solver selected at execution
                </p>
                <div className="mt-6 flex items-center gap-2 text-sm text-slate-300">
                  <Clock3 className="h-4 w-4" />
                  {battery.timestamp}
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-5 md:grid-cols-3">
        {featureCards.map((card) => {
          const Icon = card.icon;
          return (
            <article
              key={card.title}
              className="glass-panel rounded-3xl p-6 shadow-panel transition hover:-translate-y-1"
            >
              <Icon className="h-6 w-6 text-blue-700" />
              <h3 className="mt-4 text-xl font-semibold text-slate-950">
                {card.title}
              </h3>
              <p className="mt-3 text-sm leading-7 text-slate-600">
                {card.copy}
              </p>
            </article>
          );
        })}
      </section>

      <section className="grid gap-8 lg:grid-cols-[0.85fr_1.15fr]">
        <article className="glass-panel rounded-[2rem] p-6 shadow-panel">
          <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
            Recent activity
          </p>
          <div className="mt-6 space-y-4">
            {mockCaches.map((cache) => (
              <div
                key={cache.id}
                className="rounded-2xl bg-white/80 p-4 ring-1 ring-slate-200"
              >
                <p className="text-sm font-semibold text-slate-950">
                  Cache #{cache.id}
                </p>
                <p className="mt-1 text-sm text-slate-600">
                  Execution time {cache.execution_time_seconds.toFixed(2)} s and
                  deviation {cache.time_deviation_minutes.toFixed(2)} min
                </p>
              </div>
            ))}
          </div>
        </article>

        <article className="glass-panel overflow-hidden rounded-[2rem] p-6 shadow-panel">
          <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
            Examples used
          </p>
          <div className="mt-6 flex gap-4 overflow-x-auto pb-3 snap-x">
            {mockTests.map((test) => (
              <div
                key={test.id}
                className="min-w-[280px] snap-start rounded-3xl bg-slate-950 p-5 text-white shadow-glow"
              >
                <p className="text-xs uppercase tracking-[0.3em] text-blue-300">
                  Test {test.id}
                </p>
                <h3 className="mt-3 text-xl font-semibold">
                  {test.num_buses} buses / {test.num_stations} stations
                </h3>
                <p className="mt-2 text-sm text-slate-300">
                  Max stops {test.max_stops} and solver-ready matrices included.
                </p>
              </div>
            ))}
          </div>
          <div className="mt-5 flex items-center gap-2 text-sm text-slate-600">
            <Layers3 className="h-4 w-4 text-blue-700" />
            Scroll the cards to review documented sample payloads.
          </div>
        </article>
      </section>
    </div>
  );
}
