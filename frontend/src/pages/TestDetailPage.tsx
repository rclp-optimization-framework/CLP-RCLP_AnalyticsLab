import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "sonner";
import { api } from "../services/api";
import type { Result, Test } from "../types";
import { formatStationVector } from "../utils/cache-format";

const arrayToPills = (value: unknown) => {
  if (!Array.isArray(value))
    return <span className="text-slate-500">No data</span>;
  return (
    <div className="flex flex-wrap gap-2">
      {value.map((item, index) => (
        <span
          key={`${index}-${String(item)}`}
          className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-slate-700 ring-1 ring-slate-200"
        >
          {Array.isArray(item) ? `[${item.join(", ")}]` : String(item)}
        </span>
      ))}
    </div>
  );
};

export function TestDetailPage() {
  const navigate = useNavigate();
  const { testId } = useParams();
  const [test, setTest] = useState<Test | null>(null);
  const [results, setResults] = useState<Result[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const id = Number(testId);
    if (!Number.isFinite(id)) return;

    void (async () => {
      try {
        setLoading(true);
        const [testData, resultData] = await Promise.all([
          api.getTestById(id),
          api.getCacheByTest(id).catch(() => []),
        ]);
        setTest(testData);
        setResults(resultData);
      } catch (error) {
        toast.error(
          error instanceof Error ? error.message : "Could not load test detail",
        );
      } finally {
        setLoading(false);
      }
    })();
  }, [testId]);

  if (loading) {
    return (
      <div className="glass-panel rounded-[2rem] p-6 shadow-panel">
        Loading test detail...
      </div>
    );
  }

  if (!test) {
    return (
      <div className="rounded-3xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700 ring-1 ring-rose-200">
        Test not found.
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <section className="glass-panel rounded-[2rem] p-6 shadow-panel">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
              Test detail
            </p>
            <h1 className="mt-3 text-4xl font-bold text-slate-950">
              Test #{test.id}
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600">
              Structured view of the routing inputs, solver-ready matrices, and
              the cache entries generated for this test.
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
            Buses
          </p>
          <p className="mt-2 text-2xl font-semibold">{test.num_buses}</p>
        </div>
        <div className="rounded-3xl bg-slate-100 p-5">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
            Stations
          </p>
          <p className="mt-2 text-2xl font-semibold text-slate-950">
            {test.num_stations}
          </p>
        </div>
        <div className="rounded-3xl bg-slate-100 p-5">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
            Max stops
          </p>
          <p className="mt-2 text-2xl font-semibold text-slate-950">
            {test.max_stops}
          </p>
        </div>
        <div className="rounded-3xl bg-slate-100 p-5">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
            Cache
          </p>
          <p className="mt-2 text-2xl font-semibold text-slate-950">
            {results.length}
          </p>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <article className="glass-panel rounded-[2rem] p-6 shadow-panel">
          <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
            Route inputs
          </p>
          <div className="mt-5 space-y-4">
            <div className="rounded-3xl bg-white p-4 ring-1 ring-slate-200">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                st_bi
              </p>
              <div className="mt-3">{arrayToPills(test.st_bi)}</div>
            </div>
            <div className="rounded-3xl bg-white p-4 ring-1 ring-slate-200">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                d
              </p>
              <div className="mt-3">{arrayToPills(test.d)}</div>
            </div>
            <div className="rounded-3xl bg-white p-4 ring-1 ring-slate-200">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                t
              </p>
              <div className="mt-3">{arrayToPills(test.t)}</div>
            </div>
            <div className="rounded-3xl bg-white p-4 ring-1 ring-slate-200">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                tau_bi
              </p>
              <div className="mt-3">{arrayToPills(test.tau_bi)}</div>
            </div>
          </div>
        </article>

        <article className="glass-panel rounded-[2rem] p-6 shadow-panel">
          <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
            Scalar values
          </p>
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            {[
              ["Consumption max", test.consumo_max],
              ["Consumption min", test.consumo_min],
              ["Alpha", test.alpha],
              ["Mu", test.mu],
              ["Sm", test.sm],
              ["Psi", test.psi],
              ["Beta", test.beta],
              ["M", test.m],
            ].map(([label, value]) => (
              <div
                key={label as string}
                className="rounded-3xl bg-white p-4 ring-1 ring-slate-200"
              >
                <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                  {label}
                </p>
                <p className="mt-2 text-lg font-semibold text-slate-950">
                  {String(value)}
                </p>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="glass-panel rounded-[2rem] p-6 shadow-panel">
        <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
          Solver outputs
        </p>
        {results.length === 0 ? (
          <p className="mt-4 text-sm text-slate-600">
            No cache stored for this test yet.
          </p>
        ) : (
          <div className="mt-5 grid gap-4 lg:grid-cols-2">
            {results.map((result) => (
              <article
                key={result.id}
                className="rounded-[1.75rem] border border-slate-200 bg-white p-5"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs uppercase tracking-[0.24em] text-blue-700">
                      Solver {result.solver}
                    </p>
                    <h3 className="mt-2 text-xl font-semibold text-slate-950">
                      Cache #{result.id}
                    </h3>
                  </div>
                  <div className="rounded-full bg-slate-950 px-3 py-1 text-xs font-semibold text-white">
                    {result.execution_time_seconds.toFixed(2)} s
                  </div>
                </div>
                <div className="mt-4 grid gap-3 sm:grid-cols-3">
                  <div className="rounded-2xl bg-slate-50 p-3">
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                      Deviation
                    </p>
                    <p className="mt-1 text-sm font-semibold text-slate-950">
                      {result.time_deviation_minutes.toFixed(2)} min
                    </p>
                  </div>
                  <div className="rounded-2xl bg-slate-50 p-3">
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                      Charging stations
                    </p>
                    <p className="mt-1 text-sm font-semibold text-slate-950">
                      {result.charged_stations}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-slate-50 p-3">
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                      Station vector
                    </p>
                    <p className="mt-1 text-sm font-semibold text-slate-950">
                      {formatStationVector(result)}
                    </p>
                  </div>
                </div>
                {result.comment ? (
                  <p className="mt-4 rounded-2xl bg-blue-50 p-3 text-sm text-slate-700 ring-1 ring-blue-100">
                    {result.comment}
                  </p>
                ) : null}
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
