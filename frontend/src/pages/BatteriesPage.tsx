import { Eye, Plus, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { api } from "../services/api";
import type { Battery, Result, Test } from "../types";

interface BatteryPreview {
  summary: {
    id: number;
    nombre: string;
    timestamp?: string;
    test_count: number;
    result_count: number;
  } | null;
  tests: Test[];
  results: Result[];
}

export function BatteriesPage() {
  const [batteries, setBatteries] = useState<Battery[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newBatteryName, setNewBatteryName] = useState("");
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [previewBattery, setPreviewBattery] = useState<Battery | null>(null);
  const [previewData, setPreviewData] = useState<BatteryPreview>({
    summary: null,
    tests: [],
    results: [],
  });
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteCandidate, setDeleteCandidate] = useState<Battery | null>(null);

  useEffect(() => {
    void loadBatteries();
  }, []);

  const loadBatteries = async () => {
    try {
      setLoading(true);
      const data = await api.getBatteries();
      setBatteries(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error loading batteries");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBattery = async () => {
    const trimmedName = newBatteryName.trim();
    if (!trimmedName) {
      toast.error("Type a battery name first");
      return;
    }

    try {
      await api.createBattery({ nombre: trimmedName, pruebas: undefined });
      setNewBatteryName("");
      setShowCreateModal(false);
      await loadBatteries();
      toast.success("Battery created");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Error creating battery";
      setError(message);
      toast.error(message);
    }
  };

  const handlePreviewBattery = async (battery: Battery) => {
    setPreviewBattery(battery);
    setShowPreviewModal(true);
    try {
      const [summary, tests, results] = await Promise.all([
        api.getBatterySummary(battery.id).catch(() => null),
        api.getBatteryTests(battery.id).catch(() => [] as Test[]),
        api.getCacheByBattery(battery.id).catch(() => [] as Result[]),
      ]);
      setPreviewData({ summary, tests, results });
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Could not load battery preview",
      );
    }
  };

  const confirmDeleteBattery = (battery: Battery) => {
    setDeleteCandidate(battery);
    setShowDeleteModal(true);
  };

  const handleDeleteBattery = async () => {
    if (!deleteCandidate) return;
    try {
      await api.deleteBattery(deleteCandidate.id);
      setShowDeleteModal(false);
      setDeleteCandidate(null);
      await loadBatteries();
      toast.success("Battery and associated tests/cache deleted");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Error deleting battery";
      setError(message);
      toast.error(message);
    }
  };

  return (
    <div className="space-y-8">
      <section className="glass-panel rounded-[2rem] p-6 shadow-panel">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
              Batteries
            </p>
            <h1 className="mt-3 text-4xl font-bold text-slate-950">
              Battery collections and previews
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600">
              Inspect how many tests and cache entries each battery contains before
              moving to execution or statistics.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center gap-2 rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-panel transition hover:bg-slate-800"
            title="Create battery"
          >
            <Plus className="h-4 w-4" />
            Create battery
          </button>
        </div>
      </section>

      {error ? (
        <div className="rounded-3xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700 ring-1 ring-rose-200">
          {error}
        </div>
      ) : null}

      <section className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-panel">
        {loading ? (
          <div className="p-10 text-center text-slate-500">
            Loading batteries...
          </div>
        ) : batteries.length === 0 ? (
          <div className="p-10 text-center text-slate-500">
            No batteries yet. Create one to get started.
          </div>
        ) : (
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-950 text-white">
              <tr>
                <th className="px-6 py-3 text-left font-semibold">ID</th>
                <th className="px-6 py-3 text-left font-semibold">Name</th>
                <th className="px-6 py-3 text-left font-semibold">Created</th>
                <th className="px-6 py-3 text-right font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {batteries.map((battery) => (
                <tr key={battery.id} className="hover:bg-slate-50/80">
                  <td className="px-6 py-4 font-semibold text-slate-900">
                    #{battery.id}
                  </td>
                  <td className="px-6 py-4 text-slate-700">{battery.nombre}</td>
                  <td className="px-6 py-4 text-slate-600">
                    {battery.timestamp
                      ? new Date(battery.timestamp).toLocaleString()
                      : "-"}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex justify-end gap-2">
                      <button
                        type="button"
                        onClick={() => handlePreviewBattery(battery)}
                        className="inline-flex items-center rounded-full border border-slate-200 p-2 text-slate-700 transition hover:border-blue-300 hover:text-blue-700"
                        title="Preview battery"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        type="button"
                        onClick={() => confirmDeleteBattery(battery)}
                        className="inline-flex items-center rounded-full border border-rose-200 p-2 text-rose-600 transition hover:border-rose-300 hover:bg-rose-50"
                        title="Delete battery"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {showCreateModal ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 py-8 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-[2rem] bg-white p-6 shadow-glow">
            <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
              Create battery
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-950">
              New battery name
            </h2>
            <input
              type="text"
              placeholder="Battery name"
              value={newBatteryName}
              onChange={(event) => setNewBatteryName(event.target.value)}
              className="mt-5 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none ring-0 transition focus:border-blue-400"
            />
            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700"
                title="Cancel create battery"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleCreateBattery}
                className="rounded-full bg-slate-950 px-4 py-2 text-sm font-semibold text-white"
                title="Confirm create battery"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {showPreviewModal && previewBattery ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 py-8 backdrop-blur-sm">
          <div className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-[2rem] bg-white p-6 shadow-glow">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
                  Battery preview
                </p>
                <h2 className="mt-2 text-3xl font-semibold text-slate-950">
                  {previewBattery.nombre}
                </h2>
              </div>
              <button
                type="button"
                onClick={() => setShowPreviewModal(false)}
                className="rounded-full bg-slate-950 px-4 py-2 text-sm font-semibold text-white"
                title="Close preview"
              >
                Close
              </button>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-3">
              <div className="rounded-3xl bg-slate-950 p-5 text-white">
                <p className="text-xs uppercase tracking-[0.25em] text-blue-300">
                  Battery ID
                </p>
                <p className="mt-2 text-2xl font-semibold">
                  #{previewBattery.id}
                </p>
              </div>
              <div className="rounded-3xl bg-slate-100 p-5">
                <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
                  Tests
                </p>
                <p className="mt-2 text-2xl font-semibold text-slate-950">
                  {previewData.summary?.test_count ?? previewData.tests.length}
                </p>
              </div>
              <div className="rounded-3xl bg-slate-100 p-5">
                <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
                  Cache
                </p>
                <p className="mt-2 text-2xl font-semibold text-slate-950">
                  {previewData.summary?.result_count ??
                    previewData.results.length}
                </p>
              </div>
            </div>

            <div className="mt-6 grid gap-6 lg:grid-cols-2">
              <section className="rounded-[1.75rem] border border-slate-200 bg-slate-50 p-5">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">
                  Basic info
                </p>
                <div className="mt-4 space-y-3 text-sm text-slate-700">
                  <div className="flex items-center justify-between rounded-2xl bg-white px-4 py-3 ring-1 ring-slate-200">
                    <span>Name</span>
                    <span className="font-semibold">
                      {previewBattery.nombre}
                    </span>
                  </div>
                  <div className="flex items-center justify-between rounded-2xl bg-white px-4 py-3 ring-1 ring-slate-200">
                    <span>Created</span>
                    <span className="font-semibold">
                      {previewBattery.timestamp
                        ? new Date(previewBattery.timestamp).toLocaleString()
                        : "-"}
                    </span>
                  </div>
                  <div className="flex items-center justify-between rounded-2xl bg-white px-4 py-3 ring-1 ring-slate-200">
                    <span>Tests</span>
                    <span className="font-semibold">
                      {previewData.tests.length}
                    </span>
                  </div>
                  <div className="flex items-center justify-between rounded-2xl bg-white px-4 py-3 ring-1 ring-slate-200">
                    <span>Cache</span>
                    <span className="font-semibold">
                      {previewData.results.length}
                    </span>
                  </div>
                </div>
              </section>

              <section className="rounded-[1.75rem] border border-slate-200 bg-slate-50 p-5">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">
                  Contained tests
                </p>
                <div className="mt-4 space-y-3">
                  {previewData.tests.length > 0 ? (
                    previewData.tests.map((test) => (
                      <div
                        key={test.id}
                        className="rounded-2xl bg-white p-4 ring-1 ring-slate-200"
                      >
                        <p className="text-xs uppercase tracking-[0.25em] text-blue-700">
                          Test #{test.id}
                        </p>
                        <p className="mt-2 text-sm font-semibold text-slate-950">
                          {test.num_buses} buses / {test.num_stations} stations
                        </p>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-slate-600">No tests found.</p>
                  )}
                </div>
              </section>
            </div>
          </div>
        </div>
      ) : null}

      {showDeleteModal && deleteCandidate ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 py-8 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-[2rem] bg-white p-6 shadow-glow">
            <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
              Delete battery
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-950">
              Confirm deletion
            </h2>
            <p className="mt-4 text-sm leading-7 text-slate-600">
              Are you sure you want to delete{" "}
              <span className="font-semibold text-slate-950">
                {deleteCandidate.nombre}
              </span>
              ? This will remove its tests and cache entries.
            </p>
            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowDeleteModal(false)}
                className="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700"
                title="Cancel delete battery"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleDeleteBattery}
                className="rounded-full bg-rose-600 px-4 py-2 text-sm font-semibold text-white"
                title="Confirm delete battery"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
