import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { api } from "../services/api";
import type { Battery, Result, Test } from "../types";
import { StatsCharts } from "../components/charts/StatsCharts";

interface TestStats {
  best_deviation: number;
  worst_deviation: number;
  avg_deviation: number;
  avg_execution: number;
  num_solvers: number;
  solvers: string[];
  cache_count: number;
}

interface SolverStationsData {
  [solver: string]: {
    charged_stations: number;
    charging_locations: any;
    station_vector: number[] | null;
    execution_time_seconds: number;
    time_deviation_minutes: number;
  };
}

export function StatisticsPage() {
  const [batteries, setBatteries] = useState<Battery[]>([]);
  const [tests, setTests] = useState<Test[]>([]);
  const [results, setResults] = useState<Result[]>([]);
  const [testStats, setTestStats] = useState<TestStats | null>(null);
  const [stationsInfo, setStationsInfo] = useState<SolverStationsData | null>(null);
  const [activeBatteryId, setActiveBatteryId] = useState<number | null>(null);
  const [activeTestId, setActiveTestId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void loadBatteries();
  }, []);

  const loadBatteries = async () => {
    try {
      setLoading(true);
      const batteryList = await api.getBatteries().catch(() => []);
      setBatteries(batteryList);
      const firstBattery = batteryList[0]?.id ?? null;
      setActiveBatteryId(firstBattery);
      if (firstBattery) {
        await loadBatteryData(firstBattery, batteryList);
      } else {
        setTests([]);
        setResults([]);
        setTestStats(null);
        setStationsInfo(null);
      }
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Could not load statistics",
      );
    } finally {
      setLoading(false);
    }
  };

  const loadBatteryData = async (
    batteryId: number,
    batterySource = batteries,
  ) => {
    const battery =
      batterySource.find((item) => item.id === batteryId) ??
      batteries.find((item) => item.id === batteryId);
    if (!battery) return;

    try {
      setLoading(true);
      const testList = await api.getBatteryTests(batteryId).catch(() => [] as Test[]);
      setTests(testList);
      const firstTest = testList[0]?.id ?? null;
      setActiveTestId(firstTest);
      if (firstTest) {
        await loadTestResults(firstTest, testList);
      } else {
        setResults([]);
        setTestStats(null);
        setStationsInfo(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const loadTestResults = async (testId: number, testSource = tests) => {
    const test =
      testSource.find((item) => item.id === testId) ??
      tests.find((item) => item.id === testId);
    if (!test) return;

    try {
      setLoading(true);
      
      // Cargar TODOS los solvers para esta prueba
      const resultList = await api
        .getAllSolversForTest(testId)
        .catch(() => [] as Result[]);
      
      // Cargar estadísticas específicas de la prueba
      const stats = await api
        .getTestStatistics(testId)
        .catch(() => null);
      
      // Cargar información de estaciones
      const stations = await api
        .getTestStationsInfo(testId)
        .catch(() => null);
      
      setResults(
        [...resultList].sort(
          (left, right) =>
            left.time_deviation_minutes - right.time_deviation_minutes,
        ),
      );
      
      setTestStats(stats);
      setStationsInfo(stations);
    } finally {
      setLoading(false);
    }
  };

  const selectedTest = useMemo(
    () => tests.find((test) => test.id === activeTestId) ?? null,
    [tests, activeTestId],
  );
  
  const bestDeviation = useMemo(
    () => testStats?.best_deviation ?? null,
    [testStats],
  );

  // Datos para gráficos - todos los solvers
  const chartData = useMemo(() => {
    return results.map((result) => ({
      label: result.solver,
      deviation: result.time_deviation_minutes,
      executionTime: result.execution_time_seconds,
      stations: result.charged_stations,
    }));
  }, [results]);

  return (
    <div className="space-y-8">
      <section className="glass-panel rounded-[2rem] p-6 shadow-panel">
        <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
          Statistics
        </p>
        <h1 className="mt-3 text-4xl font-bold text-slate-950">
          Per-test solver ranking
        </h1>
        <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-600">
          Pick a battery, then pick a single test inside that battery. The
          ranking below compares solvers only for that test, ordered by the
          lowest deviation first.
        </p>
      </section>

      <section className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <aside className="glass-panel rounded-[2rem] p-6 shadow-panel">
          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">
            Filters
          </p>
          <div className="mt-4 space-y-4">
            <label className="block">
              <span className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
                Battery
              </span>
              <select
                value={activeBatteryId ?? ""}
                onChange={async (event) => {
                  const nextBatteryId = Number(event.target.value) || null;
                  setActiveBatteryId(nextBatteryId);
                  if (nextBatteryId) {
                    await loadBatteryData(nextBatteryId, batteries);
                  }
                }}
                className="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm"
                title="Select battery"
              >
                {batteries.map((battery) => (
                  <option key={battery.id} value={battery.id}>
                    {battery.nombre}
                  </option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
                Test
              </span>
              <select
                value={activeTestId ?? ""}
                onChange={async (event) => {
                  const nextTestId = Number(event.target.value) || null;
                  setActiveTestId(nextTestId);
                  if (nextTestId) {
                    await loadTestResults(nextTestId, tests);
                  }
                }}
                className="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm"
                title="Select test"
              >
                {tests.map((test) => (
                  <option key={test.id} value={test.id}>
                    Test #{test.id} - {test.num_buses} buses /{" "}
                    {test.num_stations} stations
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="mt-6 grid gap-3">
            <div className="rounded-3xl bg-slate-950 p-5 text-white">
              <p className="text-xs uppercase tracking-[0.24em] text-blue-300">
                Selected test
              </p>
              <p className="mt-2 text-xl font-semibold">
                {selectedTest ? `Test #${selectedTest.id}` : "No test selected"}
              </p>
            </div>
            <div className="rounded-3xl bg-slate-100 p-5">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                Cache entries loaded
              </p>
              <p className="mt-2 text-xl font-semibold text-slate-950">
                {testStats?.cache_count ?? 0}
              </p>
            </div>
            <div className="rounded-3xl bg-slate-100 p-5">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                Best deviation
              </p>
              <p className="mt-2 text-xl font-semibold text-slate-950">
                {bestDeviation !== null
                  ? `${bestDeviation.toFixed(2)} min`
                  : "N/A"}
              </p>
            </div>

            {testStats ? (
              <div className="grid gap-3">
                <div className="rounded-3xl bg-white p-5 ring-1 ring-slate-200">
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                    Avg execution
                  </p>
                  <p className="mt-2 text-lg font-semibold text-slate-950">
                    {testStats.avg_execution.toFixed(2)} s
                  </p>
                </div>
                <div className="rounded-3xl bg-white p-5 ring-1 ring-slate-200">
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                    Avg deviation
                  </p>
                  <p className="mt-2 text-lg font-semibold text-slate-950">
                    {testStats.avg_deviation.toFixed(2)} min
                  </p>
                </div>
              </div>
            ) : null}
          </div>
        </aside>

        <section className="glass-panel rounded-[2rem] p-6 shadow-panel">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="brand-type text-sm font-semibold uppercase tracking-[0.25em] text-blue-700">
                Ranking
              </p>
              <h2 className="text-2xl font-semibold text-slate-950">
                Solvers for the selected test
              </h2>
            </div>
            <button
              type="button"
              onClick={() => activeTestId && void loadTestResults(activeTestId)}
              className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700"
              title="Reload ranking"
            >
              Reload
            </button>
          </div>

          {loading ? (
            <div className="mt-6 rounded-3xl bg-slate-50 p-8 text-center text-slate-600 ring-1 ring-slate-200">
              Loading statistics...
            </div>
          ) : results.length === 0 ? (
            <div className="mt-6 rounded-3xl bg-slate-50 p-8 text-center text-slate-600 ring-1 ring-slate-200">
              No cache entries found for this test.
            </div>
          ) : (
            <div className="mt-6 overflow-hidden rounded-[1.75rem] border border-slate-200 bg-white">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-950 text-white">
                  <tr>
                    <th className="px-6 py-3 text-left font-semibold">
                      Solver
                    </th>
                    <th className="px-6 py-3 text-left font-semibold">
                      Deviation
                    </th>
                    <th className="px-6 py-3 text-left font-semibold">
                      Execution Time
                    </th>
                    <th className="px-6 py-3 text-left font-semibold">
                      Stations
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {results.map((result, index) => (
                    <tr key={result.id} className={index % 2 === 0 ? "bg-slate-50" : ""}>
                      <td className="px-6 py-4 font-semibold text-slate-950">
                        {result.solver}
                      </td>
                      <td className="px-6 py-4 text-slate-700">
                        {result.time_deviation_minutes.toFixed(2)} min
                      </td>
                      <td className="px-6 py-4 text-slate-700">
                        {result.execution_time_seconds.toFixed(2)} s
                      </td>
                      <td className="px-6 py-4 text-slate-700">
                        {result.charged_stations}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </section>

      {/* Gráficos */}
      {chartData.length > 0 && (
        <StatsCharts points={chartData} summary={null} />
      )}

      {/* Tabla de estaciones */}
      {stationsInfo && Object.keys(stationsInfo).length > 0 && (
        <section className="glass-panel rounded-[2rem] p-6 shadow-panel">
          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-blue-700">
            Station Positioning
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            Charging stations by solver
          </h2>

          <div className="mt-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {Object.entries(stationsInfo).map(([solver, data]) => (
              <div key={solver} className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                <h3 className="text-lg font-semibold text-slate-950 capitalize">
                  {solver}
                </h3>
                <div className="mt-3 space-y-2 text-sm">
                  <div>
                    <p className="font-semibold text-slate-700">Stations:</p>
                    <p className="text-slate-600">{data.charged_stations}</p>
                  </div>
                  <div>
                    <p className="font-semibold text-slate-700">Vector:</p>
                    <p className="font-mono text-xs text-slate-600">
                      [{data.station_vector?.join(", ") ?? "N/A"}]
                    </p>
                  </div>
                  <div>
                    <p className="font-semibold text-slate-700">Exec Time:</p>
                    <p className="text-slate-600">{data.execution_time_seconds.toFixed(2)} s</p>
                  </div>
                  <div>
                    <p className="font-semibold text-slate-700">Deviation:</p>
                    <p className="text-slate-600">{data.time_deviation_minutes.toFixed(2)} min</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
