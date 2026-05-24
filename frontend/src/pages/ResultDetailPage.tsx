import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "sonner";
import { api } from "../services/api";
import type { Result, Test, Battery } from "../types";
import { formatStationVector } from "../utils/cache-format";

export function CacheDetailPage() {
  const navigate = useNavigate();
  const { resultId } = useParams();
  const [result, setResult] = useState<Result | null>(null);
  const [test, setTest] = useState<Test | null>(null);
  const [battery, setBattery] = useState<Battery | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const id = Number(resultId);
    if (!Number.isFinite(id)) return;

    void (async () => {
      try {
        setLoading(true);
        const resultData = await api.getCacheById(id);
        const testData = await api.getTestById(resultData.prueba_id);
        const batteryData = await api.getBatteryById(testData.bateria_id);
        setResult(resultData);
        setTest(testData);
        setBattery(batteryData);
      } catch (error) {
        toast.error(
          error instanceof Error
            ? error.message
            : "Could not load cache detail",
        );
      } finally {
        setLoading(false);
      }
    })();
  }, [resultId]);

  if (loading) {
    return (
      <div className="glass-panel rounded-[2rem] p-6 shadow-panel">
        Loading cache detail...
      </div>
    );
  }

  if (!result || !test || !battery) {
    return (
      <div className="rounded-3xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700 ring-1 ring-rose-200">
        Cache not found.
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <section className="glass-panel rounded-[2rem] p-6 shadow-panel">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
              Cache detail
            </p>
            <h1 className="mt-3 text-4xl font-bold text-slate-950">
              Battery {battery.nombre}
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600">
              Execution summary for a single solver run, with a clean card
              layout for all key metrics and comments.
            </p>
          </div>
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="rounded-full bg-slate-950 px-4 py-2 text-sm font-semibold text-white"
            title="Go back"
          >
            Back
          </button>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-4">
        <div className="rounded-3xl bg-slate-950 p-5 text-white">
          <p className="text-xs uppercase tracking-[0.24em] text-blue-300">
            Execution
          </p>
          <p className="mt-2 text-2xl font-semibold">
            {result.execution_time_seconds.toFixed(2)} s
          </p>
        </div>
        <div className="rounded-3xl bg-slate-100 p-5">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
            Deviation
          </p>
          <p className="mt-2 text-2xl font-semibold text-slate-950">
            {result.time_deviation_minutes.toFixed(2)} min
          </p>
        </div>
        <div className="rounded-3xl bg-slate-100 p-5">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
            Charging stations
          </p>
          <p className="mt-2 text-2xl font-semibold text-slate-950">
            {result.charged_stations}
          </p>
        </div>
        <div className="rounded-3xl bg-slate-100 p-5">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
            Solver
          </p>
          <p className="mt-2 text-2xl font-semibold text-slate-950">
            {result.solver}
          </p>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <article className="glass-panel rounded-[2rem] p-6 shadow-panel">
          <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
            Summary cards
          </p>
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            <div className="rounded-3xl bg-white p-4 ring-1 ring-slate-200">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                Test
              </p>
              <p className="mt-2 text-lg font-semibold text-slate-950">
                #{test.id}
              </p>
            </div>
            <div className="rounded-3xl bg-white p-4 ring-1 ring-slate-200">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                Battery
              </p>
              <p className="mt-2 text-lg font-semibold text-slate-950">
                {battery.nombre}
              </p>
            </div>
            <div className="rounded-3xl bg-white p-4 ring-1 ring-slate-200">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                Station vector
              </p>
              <p className="mt-2 text-lg font-semibold text-slate-950">
                {formatStationVector(result)}
              </p>
            </div>
            <div className="rounded-3xl bg-white p-4 ring-1 ring-slate-200">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                Timestamp
              </p>
              <p className="mt-2 text-lg font-semibold text-slate-950">
                {result.timestamp
                  ? new Date(result.timestamp).toLocaleString()
                  : "-"}
              </p>
            </div>
          </div>
        </article>

        <article className="glass-panel rounded-[2rem] p-6 shadow-panel">
          <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
            Comments
          </p>
          <div className="mt-5 rounded-[1.75rem] bg-white p-5 ring-1 ring-slate-200">
            {result.comment ? (
              <p className="text-sm leading-7 text-slate-700">
                {result.comment}
              </p>
            ) : (
              <p className="text-sm text-slate-500">
                No comment stored for this cache entry.
              </p>
            )}
          </div>
        </article>
      </section>

      <section className="glass-panel rounded-[2rem] p-6 shadow-panel">
        <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
          Solver run
        </p>
        <div className="mt-5 grid gap-4 lg:grid-cols-3">
          <div className="rounded-3xl bg-slate-950 p-5 text-white">
            <p className="text-xs uppercase tracking-[0.24em] text-blue-300">
              Charged stations
            </p>
            <p className="mt-2 text-2xl font-semibold">
              {result.charged_stations}
            </p>
          </div>
          <div className="rounded-3xl bg-slate-100 p-5">
            <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
              Deviation vector
            </p>
            <p className="mt-2 text-sm font-semibold text-slate-950">
              {formatStationVector(result)}
            </p>
          </div>
          <div className="rounded-3xl bg-slate-100 p-5">
            <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
              Solver label
            </p>
            <p className="mt-2 text-sm font-semibold text-slate-950">
              {result.solver}
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
