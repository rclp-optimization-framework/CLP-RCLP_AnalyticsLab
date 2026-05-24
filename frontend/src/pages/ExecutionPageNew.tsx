import { useState, useEffect } from "react";
import { Play, RotateCcw } from "lucide-react";
import { toast } from "sonner";
import { api } from "../services/api";
import type { Battery, Test, SolverName } from "../types";

export function ExecutionPageNew() {
  const [batteries, setBatteries] = useState<Battery[]>([]);
  const [selectedBattery, setSelectedBattery] = useState<number | null>(null);
  const [tests, setTests] = useState<Test[]>([]);
  const [selectedTests, setSelectedTests] = useState<Set<number>>(new Set());
  const [availableSolvers, setAvailableSolvers] = useState<SolverName[]>([]);
  const [selectedSolvers, setSelectedSolvers] = useState<Set<SolverName>>(
    new Set(),
  );
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<any>(null);

  useEffect(() => {
    loadBatteries();
    loadSolvers();
  }, []);

  useEffect(() => {
    if (selectedBattery) {
      loadTests(selectedBattery);
    }
  }, [selectedBattery]);

  const loadBatteries = async () => {
    try {
      const data = await api.getBatteries();
      setBatteries(data);
      if (data.length > 0) {
        setSelectedBattery(data[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error loading batteries");
    }
  };

  const loadTests = async (batteryId: number) => {
    try {
      setLoading(true);
      const data = await api.getBatteryTests(batteryId);
      setTests(data);
      setSelectedTests(new Set()); // Reset selection
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error loading tests");
    } finally {
      setLoading(false);
    }
  };

  const loadSolvers = async () => {
    try {
      const data = await api.getAvailableSolversForExecution();
      setAvailableSolvers(data.solvers);
      if (data.solvers.length > 0) {
        setSelectedSolvers(new Set([data.solvers[0]]));
      }
    } catch (err) {
      console.error("Error loading solvers:", err);
      toast.error("Error loading solvers");
    }
  };

  const toggleTestSelection = (testId: number) => {
    const newSet = new Set(selectedTests);
    if (newSet.has(testId)) {
      newSet.delete(testId);
    } else {
      newSet.add(testId);
    }
    setSelectedTests(newSet);
  };

  const toggleSolverSelection = (solver: SolverName) => {
    const newSet = new Set(selectedSolvers);
    if (newSet.has(solver)) {
      newSet.delete(solver);
    } else {
      newSet.add(solver);
    }
    setSelectedSolvers(newSet);
  };

  const selectAllTests = () => {
    if (selectedTests.size === tests.length) {
      setSelectedTests(new Set());
    } else {
      setSelectedTests(new Set(tests.map((t) => t.id)));
    }
  };

  const handleExecute = async () => {
    if (
      !selectedBattery ||
      selectedTests.size === 0 ||
      selectedSolvers.size === 0
    ) {
      setError("Please select battery, tests, and at least one solver");
      return;
    }

    try {
      setExecuting(true);
      setError(null);
      const result = await api.executeBatteryTests(
        selectedBattery,
        Array.from(selectedTests),
        Array.from(selectedSolvers),
      );
      setResults(result);
      toast.success("Execution completed (see cache)");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Execution failed");
      toast.error(err instanceof Error ? err.message : "Execution failed");
    } finally {
      setExecuting(false);
    }
  };

  const resetExecution = () => {
    setResults(null);
    setError(null);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Execution</h1>
        <p className="text-slate-600">
          Select battery, tests, and solvers to execute
        </p>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 p-4 text-red-700">{error}</div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Battery selection */}
        <div className="lg:col-span-1">
          <div className="rounded-lg border border-slate-200 p-4">
            <h2 className="font-semibold text-slate-900 mb-4">
              Select Battery
            </h2>
            <div className="space-y-2">
              {batteries.map((battery) => (
                <button
                  key={battery.id}
                  onClick={() => setSelectedBattery(battery.id)}
                  className={`w-full text-left px-4 py-2 rounded-lg transition ${
                    selectedBattery === battery.id
                      ? "bg-blue-600 text-white"
                      : "bg-slate-100 text-slate-900 hover:bg-slate-200"
                  }`}
                >
                  {battery.nombre}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Tests selection */}
        <div className="lg:col-span-1">
          <div className="rounded-lg border border-slate-200 p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold text-slate-900">Select Tests</h2>
              <button
                onClick={selectAllTests}
                className="text-xs text-blue-600 hover:underline"
              >
                {selectedTests.size === tests.length
                  ? "Deselect all"
                  : "Select all"}
              </button>
            </div>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {loading ? (
                <p className="text-slate-600 text-sm">Loading tests...</p>
              ) : tests.length === 0 ? (
                <p className="text-slate-600 text-sm">
                  No tests in this battery
                </p>
              ) : (
                tests.map((test) => (
                  <label
                    key={test.id}
                    className="flex items-center gap-3 p-2 hover:bg-slate-50 rounded cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedTests.has(test.id)}
                      onChange={() => toggleTestSelection(test.id)}
                      className="rounded"
                    />
                    <div className="text-sm">
                      <div className="font-medium">Test {test.id}</div>
                      <div className="text-xs text-slate-600">
                        {test.num_buses} buses, {test.num_stations} stations
                      </div>
                    </div>
                  </label>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Solver selection */}
        <div className="lg:col-span-1">
          <div className="rounded-lg border border-slate-200 p-4">
            <h2 className="font-semibold text-slate-900 mb-4">
              Select Solvers
            </h2>
            <div className="space-y-2">
              {availableSolvers.map((solver) => (
                <label
                  key={solver}
                  className="flex items-center gap-3 p-2 hover:bg-slate-50 rounded cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedSolvers.has(solver)}
                    onChange={() => toggleSolverSelection(solver)}
                    className="rounded"
                  />
                  <span className="text-sm font-medium">{solver}</span>
                </label>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Execution controls */}
      <div className="flex gap-4">
        <button
          onClick={handleExecute}
          disabled={
            executing ||
            !selectedBattery ||
            selectedTests.size === 0 ||
            selectedSolvers.size === 0
          }
          title="Execute selected tests with chosen solvers"
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Play className="h-4 w-4" />
          {executing ? "Executing..." : "Execute"}
        </button>
        <button
          onClick={resetExecution}
          title="Reset execution cache"
          className="flex items-center gap-2 rounded-lg bg-slate-200 px-6 py-3 text-slate-900 hover:bg-slate-300"
        >
          <RotateCcw className="h-4 w-4" />
          Reset
        </button>
      </div>

      {/* Cache */}
      {results && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-6">
          <h2 className="font-semibold text-green-900 mb-4">
            Execution Cache
          </h2>
          <div className="space-y-4">
            {results.map((result: any, idx: number) => (
              <div
                key={idx}
                className={`p-4 rounded-lg border ${
                  result.success
                    ? "border-green-300 bg-white"
                    : "border-red-300 bg-red-50"
                }`}
              >
                <div className="font-medium">
                  Test {result.prueba_id} - {result.solver}
                </div>
                {result.success ? (
                  <div className="text-sm text-green-700">
                    ✓ Execution successful (Result ID: {result.result_id})
                  </div>
                ) : (
                  <div className="text-sm text-red-700">✗ {result.error}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
