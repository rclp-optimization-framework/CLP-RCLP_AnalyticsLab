import { Edit2, Eye, Plus, Upload, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { api } from "../services/api";
import type { Battery, Test } from "../types";

const emptyEditForm = {
  num_buses: "",
  num_stations: "",
  max_stops: "",
  consumo_max: "",
  consumo_min: "",
  alpha: "",
  mu: "",
  sm: "",
  psi: "",
  beta: "",
  m: "",
};

export function TestsPage() {
  const navigate = useNavigate();
  const [batteries, setBatteries] = useState<Battery[]>([]);
  const [selectedBattery, setSelectedBattery] = useState<number | null>(null);
  const [tests, setTests] = useState<Test[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadType, setUploadType] = useState<"json" | "dzn">("json");
  const [previewTest, setPreviewTest] = useState<Test | null>(null);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [editTest, setEditTest] = useState<Test | null>(null);
  const [editForm, setEditForm] = useState(emptyEditForm);
  const [showEditModal, setShowEditModal] = useState(false);
  const [deleteCandidate, setDeleteCandidate] = useState<Test | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    void loadBatteries();
  }, []);

  useEffect(() => {
    if (selectedBattery) {
      void loadTests(selectedBattery);
    }
  }, [selectedBattery]);

  const loadBatteries = async () => {
    try {
      setLoading(true);
      const data = await api.getBatteries();
      setBatteries(data);
      if (data.length > 0) {
        setSelectedBattery(data[0].id);
      }
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error loading batteries");
    } finally {
      setLoading(false);
    }
  };

  const loadTests = async (batteryId: number) => {
    try {
      setLoading(true);
      const data = await api.getBatteryTests(batteryId);
      setTests(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error loading tests");
    } finally {
      setLoading(false);
    }
  };

  const handleUploadTests = async () => {
    if (!selectedBattery) {
      setError("Please select a battery before uploading tests");
      return;
    }

    if (!uploadFile) return;

    try {
      setLoading(true);
      const uploadedTests = await api.uploadTestsFile(
        selectedBattery,
        uploadFile,
      );
      setUploadFile(null);
      setShowUploadModal(false);
      await loadTests(selectedBattery);
      toast.success(`Successfully uploaded ${uploadedTests.length} test(s)`);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Error uploading tests";
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const openPreview = (test: Test) => {
    setPreviewTest(test);
    setShowPreviewModal(true);
  };

  const openEdit = (test: Test) => {
    setEditTest(test);
    setEditForm({
      num_buses: String(test.num_buses ?? ""),
      num_stations: String(test.num_stations ?? ""),
      max_stops: String(test.max_stops ?? ""),
      consumo_max: String(test.consumo_max ?? ""),
      consumo_min: String(test.consumo_min ?? ""),
      alpha: String(test.alpha ?? ""),
      mu: String(test.mu ?? ""),
      sm: String(test.sm ?? ""),
      psi: String(test.psi ?? ""),
      beta: String(test.beta ?? ""),
      m: String(test.m ?? ""),
    });
    setShowEditModal(true);
  };

  const handleSaveEdit = async () => {
    if (!editTest) return;

    const payload: Record<string, number> = {};
    for (const [key, value] of Object.entries(editForm)) {
      if (value !== "") {
        payload[key] = Number(value);
      }
    }

    try {
      await api.updateTest(editTest.id, payload);
      toast.success("Test updated");
      setShowEditModal(false);
      setEditTest(null);
      if (selectedBattery) {
        await loadTests(selectedBattery);
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Error updating test";
      setError(message);
      toast.error(message);
    }
  };

  const openDelete = (test: Test) => {
    setDeleteCandidate(test);
    setShowDeleteModal(true);
  };

  const handleDeleteTest = async () => {
    if (!deleteCandidate) return;
    try {
      await api.deleteTest(deleteCandidate.id);
      toast.success("Test deleted");
      setShowDeleteModal(false);
      setDeleteCandidate(null);
      if (selectedBattery) {
        await loadTests(selectedBattery);
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Error deleting test";
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
              Tests
            </p>
            <h1 className="mt-3 text-4xl font-bold text-slate-950">
              Test cases inside each battery
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600">
              Preview each test, jump to a dedicated detail page, edit its
              numeric parameters, upload JSON/DZN examples, and delete with
              confirmation.
            </p>
          </div>
          <button
            type="button"
            onClick={() => {
              if (!selectedBattery) {
                setError("Please select a battery before uploading tests");
                return;
              }
              setShowUploadModal(true);
            }}
            disabled={!selectedBattery}
            className="inline-flex items-center gap-2 rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-panel transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
            title="Upload tests"
          >
            <Upload className="h-4 w-4" />
            Upload tests
          </button>
        </div>
      </section>

      {error ? (
        <div className="rounded-3xl bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700 ring-1 ring-rose-200">
          {error}
        </div>
      ) : null}

      <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <aside className="glass-panel rounded-[2rem] p-6 shadow-panel">
          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">
            Batteries
          </p>
          <div className="mt-4 space-y-3">
            {batteries.map((battery) => (
              <button
                key={battery.id}
                type="button"
                onClick={() => setSelectedBattery(battery.id)}
                className={`w-full rounded-3xl px-4 py-4 text-left transition ${
                  selectedBattery === battery.id
                    ? "bg-slate-950 text-white shadow-glow"
                    : "bg-white/80 text-slate-700 ring-1 ring-slate-200 hover:bg-slate-100"
                }`}
                title={`Select battery ${battery.nombre}`}
              >
                <p className="text-xs uppercase tracking-[0.3em] text-blue-300">
                  Battery #{battery.id}
                </p>
                <p className="mt-2 text-lg font-semibold">{battery.nombre}</p>
                <p className="text-sm text-current/70">Execution-ready tests</p>
              </button>
            ))}
          </div>
        </aside>

        <section className="glass-panel rounded-[2rem] p-6 shadow-panel">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="brand-type text-sm font-semibold uppercase tracking-[0.25em] text-blue-700">
                Table
              </p>
              <h2 className="text-2xl font-semibold text-slate-950">
                Tests in battery
              </h2>
            </div>
            <button
              type="button"
              onClick={() => selectedBattery && void loadTests(selectedBattery)}
              className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700"
              title="Reload tests"
            >
              Reload
            </button>
          </div>

          {loading ? (
            <div className="mt-6 flex items-center justify-center p-8">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
            </div>
          ) : tests.length === 0 ? (
            <div className="mt-6 rounded-3xl bg-slate-50 p-8 text-center text-slate-600 ring-1 ring-slate-200">
              No tests in this battery. Upload JSON or DZN examples to get
              started.
            </div>
          ) : (
            <div className="mt-6 overflow-hidden rounded-[1.75rem] border border-slate-200 bg-white">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-950 text-white">
                  <tr>
                    <th className="px-6 py-3 text-left font-semibold">ID</th>
                    <th className="px-6 py-3 text-left font-semibold">Buses</th>
                    <th className="px-6 py-3 text-left font-semibold">
                      Stations
                    </th>
                    <th className="px-6 py-3 text-right font-semibold">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {tests.map((test) => (
                    <tr key={test.id} className="hover:bg-slate-50/80">
                      <td className="px-6 py-4 font-semibold text-slate-900">
                        #{test.id}
                      </td>
                      <td className="px-6 py-4 text-slate-700">
                        {test.num_buses}
                      </td>
                      <td className="px-6 py-4 text-slate-700">
                        {test.num_stations}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex justify-end gap-2">
                          <button
                            type="button"
                            onClick={() => openPreview(test)}
                            className="inline-flex items-center rounded-full border border-slate-200 p-2 text-slate-700 transition hover:border-blue-300 hover:text-blue-700"
                            title="Preview test"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          <button
                            type="button"
                            onClick={() => openEdit(test)}
                            className="inline-flex items-center rounded-full border border-slate-200 p-2 text-slate-700 transition hover:border-blue-300 hover:text-blue-700"
                            title="Edit test"
                          >
                            <Edit2 className="h-4 w-4" />
                          </button>
                          <button
                            type="button"
                            onClick={() => openDelete(test)}
                            className="inline-flex items-center rounded-full border border-rose-200 p-2 text-rose-600 transition hover:border-rose-300 hover:bg-rose-50"
                            title="Delete test"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </section>

      {showUploadModal ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 py-8 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-[2rem] bg-white p-6 shadow-glow">
            <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
              Upload tests
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-950">
              JSON or DZN file
            </h2>

            <div className="mt-5">
              <label className="block text-sm font-semibold text-slate-700">
                File type
              </label>
              <div className="mt-3 flex gap-4">
                <label className="flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-sm text-slate-700">
                  <input
                    type="radio"
                    checked={uploadType === "json"}
                    onChange={() => setUploadType("json")}
                  />
                  JSON
                </label>
                <label className="flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-sm text-slate-700">
                  <input
                    type="radio"
                    checked={uploadType === "dzn"}
                    onChange={() => setUploadType("dzn")}
                  />
                  DZN
                </label>
              </div>
            </div>

            <label className="mt-5 block text-sm font-semibold text-slate-700">
              Select file
            </label>
            <input
              type="file"
              accept={uploadType === "json" ? ".json" : ".dzn"}
              onChange={(event) =>
                setUploadFile(event.target.files?.[0] ?? null)
              }
              className="mt-3 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm"
            />

            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowUploadModal(false)}
                className="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700"
                title="Cancel upload"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleUploadTests}
                disabled={!uploadFile}
                className="rounded-full bg-slate-950 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
                title="Upload file"
              >
                Upload
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {showPreviewModal && previewTest ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 py-8 backdrop-blur-sm">
          <div className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-[2rem] bg-white p-6 shadow-glow">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
                  Test preview
                </p>
                <h2 className="mt-2 text-3xl font-semibold text-slate-950">
                  Test #{previewTest.id}
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

            <div className="mt-6 grid gap-4 md:grid-cols-4">
              <div className="rounded-3xl bg-slate-950 p-5 text-white">
                <p className="text-xs uppercase tracking-[0.25em] text-blue-300">
                  Buses
                </p>
                <p className="mt-2 text-2xl font-semibold">
                  {previewTest.num_buses}
                </p>
              </div>
              <div className="rounded-3xl bg-slate-100 p-5">
                <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
                  Stations
                </p>
                <p className="mt-2 text-2xl font-semibold text-slate-950">
                  {previewTest.num_stations}
                </p>
              </div>
              <div className="rounded-3xl bg-slate-100 p-5">
                <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
                  Max stops
                </p>
                <p className="mt-2 text-2xl font-semibold text-slate-950">
                  {previewTest.max_stops}
                </p>
              </div>
              <div className="rounded-3xl bg-slate-100 p-5">
                <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
                  Consumption max
                </p>
                <p className="mt-2 text-2xl font-semibold text-slate-950">
                  {previewTest.consumo_max}
                </p>
              </div>
            </div>

            <div className="mt-6 grid gap-4 lg:grid-cols-2">
              <section className="rounded-[1.75rem] border border-slate-200 bg-slate-50 p-5">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">
                  Basic cards
                </p>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  <div className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                      Stations vector size
                    </p>
                    <p className="mt-2 font-semibold text-slate-950">
                      {previewTest.num_stations}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                      Alpha
                    </p>
                    <p className="mt-2 font-semibold text-slate-950">
                      {previewTest.alpha}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                      Mu
                    </p>
                    <p className="mt-2 font-semibold text-slate-950">
                      {previewTest.mu}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                      Beta
                    </p>
                    <p className="mt-2 font-semibold text-slate-950">
                      {previewTest.beta}
                    </p>
                  </div>
                </div>
              </section>

              <section className="rounded-[1.75rem] border border-slate-200 bg-slate-50 p-5">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">
                  Route summary
                </p>
                <div className="mt-4 space-y-3">
                  <div className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                    <p className="text-xs uppercase tracking-[0.24em] text-blue-700">
                      st_bi
                    </p>
                    <p className="mt-2 text-sm font-semibold text-slate-950">
                      {Array.isArray(previewTest.st_bi)
                        ? `${previewTest.st_bi.length} route rows`
                        : "No data"}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                    <p className="text-xs uppercase tracking-[0.24em] text-blue-700">
                      d / t / tau_bi
                    </p>
                    <p className="mt-2 text-sm font-semibold text-slate-950">
                      Array data available for solver execution
                    </p>
                  </div>
                </div>
              </section>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowPreviewModal(false)}
                className="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700"
                title="Close preview"
              >
                Close
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowPreviewModal(false);
                  navigate(`/tests/${previewTest.id}`);
                }}
                className="rounded-full bg-slate-950 px-4 py-2 text-sm font-semibold text-white"
                title="View test detail"
              >
                View detail
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {showEditModal && editTest ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 py-8 backdrop-blur-sm">
          <div className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-[2rem] bg-white p-6 shadow-glow">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
                  Edit test
                </p>
                <h2 className="mt-2 text-3xl font-semibold text-slate-950">
                  Test #{editTest.id}
                </h2>
              </div>
              <button
                type="button"
                onClick={() => setShowEditModal(false)}
                className="rounded-full bg-slate-950 px-4 py-2 text-sm font-semibold text-white"
                title="Close edit modal"
              >
                Close
              </button>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-2">
              {Object.entries(editForm).map(([key, value]) => (
                <label
                  key={key}
                  className="rounded-2xl border border-slate-200 bg-slate-50 p-4"
                >
                  <span className="block text-xs font-semibold uppercase tracking-[0.24em] text-slate-500">
                    {key}
                  </span>
                  <input
                    type="number"
                    value={value}
                    onChange={(event) =>
                      setEditForm((current) => ({
                        ...current,
                        [key]: event.target.value,
                      }))
                    }
                    className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none"
                  />
                </label>
              ))}
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowEditModal(false)}
                className="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700"
                title="Cancel edit"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSaveEdit}
                className="rounded-full bg-slate-950 px-4 py-2 text-sm font-semibold text-white"
                title="Save edits"
              >
                Save changes
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {showDeleteModal && deleteCandidate ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 py-8 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-[2rem] bg-white p-6 shadow-glow">
            <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
              Delete test
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-950">
              Confirm deletion
            </h2>
            <p className="mt-4 text-sm leading-7 text-slate-600">
              Are you sure you want to delete{" "}
              <span className="font-semibold text-slate-950">
                Test #{deleteCandidate.id}
              </span>
              ? This action removes its cache entries too.
            </p>
            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowDeleteModal(false)}
                className="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700"
                title="Cancel delete test"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleDeleteTest}
                className="rounded-full bg-rose-600 px-4 py-2 text-sm font-semibold text-white"
                title="Confirm delete test"
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
