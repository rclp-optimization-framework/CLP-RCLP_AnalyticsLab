import { Download, Eye, FileText, MessageSquare, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { api } from "../services/api";
import type { Battery, Result } from "../types";
import { formatStationVector, getCacheSummary } from "../utils/cache-format";
import { downloadResultPdf } from "../utils/pdf";

const searchResult = (result: Result, batteryName: string, query: string) => {
  const normalized = query.toLowerCase();
  return (
    batteryName.toLowerCase().includes(normalized) ||
    result.solver.toLowerCase().includes(normalized) ||
    String(result.prueba_id).includes(normalized) ||
    String(result.id).includes(normalized)
  );
};

export function CachePage() {
  const navigate = useNavigate();
  const [batteries, setBatteries] = useState<Battery[]>([]);
  const [activeBatteryId, setActiveBatteryId] = useState<number | null>(null);
  const [results, setResults] = useState<Result[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [previewResult, setPreviewResult] = useState<Result | null>(null);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [commentResult, setCommentResult] = useState<Result | null>(null);
  const [commentText, setCommentText] = useState("");
  const [showCommentModal, setShowCommentModal] = useState(false);
  const [deleteCandidate, setDeleteCandidate] = useState<Result | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    void loadInitialData();
  }, []);

  useEffect(() => {
    if (activeBatteryId) {
      void loadBatteryResults(activeBatteryId);
    }
  }, [activeBatteryId]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const batteryList = await api.getBatteries().catch(() => []);
      setBatteries(batteryList);
      setActiveBatteryId(batteryList[0]?.id ?? null);
      if (batteryList[0]?.id) {
        await loadBatteryResults(batteryList[0].id, batteryList);
      }
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Could not load cache",
      );
    } finally {
      setLoading(false);
    }
  };

  const loadBatteryResults = async (
    batteryId: number,
    batterySource = batteries,
  ) => {
    const battery =
      batterySource.find((item) => item.id === batteryId) ??
      batteries.find((item) => item.id === batteryId);
    if (!battery) return;

    try {
      setLoading(true);
      const data = await api
        .getCacheByBattery(batteryId)
        .catch(() => [] as Result[]);
      setResults(data);
    } finally {
      setLoading(false);
    }
  };

  const batteryNameById = useMemo(
    () => new Map(batteries.map((battery) => [battery.id, battery.nombre])),
    [batteries],
  );

  const filteredResults = useMemo(() => {
    return results.filter((result) =>
      searchResult(
        result,
        batteryNameById.get(activeBatteryId ?? 0) ?? "",
        search,
      ),
    );
  }, [results, search, batteryNameById, activeBatteryId]);

  const sortedResults = useMemo(() => {
    return [...filteredResults].sort(
      (left, right) =>
        left.time_deviation_minutes - right.time_deviation_minutes,
    );
  }, [filteredResults]);

  const openPreview = (result: Result) => {
    setPreviewResult(result);
    setShowPreviewModal(true);
  };

  const openComment = (result: Result) => {
    setCommentResult(result);
    setCommentText(result.comment ?? "");
    setShowCommentModal(true);
  };

  const saveComment = async () => {
    if (!commentResult) return;
    try {
      const updated = await api.updateCacheComment(
        commentResult.id,
        commentText.trim() || null,
      );
      setResults((current) =>
        current.map((item) => (item.id === updated.id ? updated : item)),
      );
      setShowCommentModal(false);
      setCommentResult(null);
      toast.success("Comment saved");
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Could not save comment",
      );
    }
  };

  const openDelete = (result: Result) => {
    setDeleteCandidate(result);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!deleteCandidate) return;
    try {
      await api.deleteCache(deleteCandidate.id);
      setResults((current) =>
        current.filter((item) => item.id !== deleteCandidate.id),
      );
      setShowDeleteModal(false);
      setDeleteCandidate(null);
      toast.success("Result deleted");
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Could not delete result",
      );
    }
  };

  return (
    <div className="space-y-8">
      <section className="glass-panel rounded-[2rem] p-6 shadow-panel">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
              <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
              Cache
            </p>
            <h1 className="mt-3 text-4xl font-bold text-slate-950">
              Solver cache and comments
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600">
              Preview the compact summary, navigate to the full detail page,
              attach comments, and export a PDF without showing raw JSON.
            </p>
          </div>
          <label className="flex min-w-[280px] items-center gap-3 rounded-full bg-white px-4 py-3 ring-1 ring-slate-200">
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              className="w-full bg-transparent text-sm outline-none"
              placeholder="Search battery, cache, solver or test"
              title="Search cache"
            />
          </label>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[0.82fr_1.18fr]">
        <aside className="glass-panel rounded-[2rem] p-6 shadow-panel">
          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">
            Batteries
          </p>
          <div className="mt-4 space-y-3">
            {batteries.map((battery) => (
              <button
                key={battery.id}
                type="button"
                onClick={() => setActiveBatteryId(battery.id)}
                className={`w-full rounded-3xl px-4 py-4 text-left transition ${activeBatteryId === battery.id ? "bg-slate-950 text-white shadow-glow" : "bg-white/80 text-slate-700 ring-1 ring-slate-200 hover:bg-slate-100"}`}
                title={`Select battery ${battery.nombre}`}
              >
                <p className="text-xs uppercase tracking-[0.3em] text-blue-300">
                  Battery #{battery.id}
                </p>
                <p className="mt-2 text-lg font-semibold">{battery.nombre}</p>
                <p className="text-sm text-current/70">
                  {battery.timestamp
                    ? new Date(battery.timestamp).toLocaleDateString()
                    : "No timestamp"}
                </p>
              </button>
            ))}
          </div>
        </aside>

        <section className="glass-panel rounded-[2rem] p-6 shadow-panel">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="brand-type text-sm font-semibold uppercase tracking-[0.25em] text-blue-700">
                Cache table
              </p>
              <h2 className="text-2xl font-semibold text-slate-950">
                Cache for selected battery
              </h2>
            </div>
            <button
              type="button"
              onClick={() =>
                activeBatteryId && void loadBatteryResults(activeBatteryId)
              }
              className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700"
              title="Reload cache"
            >
              Reload
            </button>
          </div>

          {loading ? (
            <div className="mt-6 rounded-3xl bg-slate-50 p-8 text-center text-slate-600 ring-1 ring-slate-200">
              Loading cache...
            </div>
          ) : sortedResults.length === 0 ? (
            <div className="mt-6 rounded-3xl bg-slate-50 p-8 text-center text-slate-600 ring-1 ring-slate-200">
              No cache found for this battery.
            </div>
          ) : (
            <div className="mt-6 overflow-hidden rounded-[1.75rem] border border-slate-200 bg-white">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-950 text-white">
                  <tr>
                    <th className="px-6 py-3 text-left font-semibold">
                      Result
                    </th>
                    <th className="px-6 py-3 text-left font-semibold">
                      Solver
                    </th>
                    <th className="px-6 py-3 text-left font-semibold">
                      Deviation
                    </th>
                    <th className="px-6 py-3 text-left font-semibold">
                      Stations
                    </th>
                    <th className="px-6 py-3 text-left font-semibold">
                      Vector
                    </th>
                    <th className="px-6 py-3 text-right font-semibold">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {sortedResults.map((result) => (
                    <tr key={result.id} className="hover:bg-slate-50/80">
                      <td className="px-6 py-4 font-semibold text-slate-900">
                        #{result.id}
                      </td>
                      <td className="px-6 py-4 text-slate-700">
                        {result.solver}
                      </td>
                      <td className="px-6 py-4 text-slate-700">
                        {result.time_deviation_minutes.toFixed(2)} min
                      </td>
                      <td className="px-6 py-4 text-slate-700">
                        {result.charged_stations}
                      </td>
                      <td className="px-6 py-4 text-slate-700">
                        {formatStationVector(result)}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex justify-end gap-2">
                          <button
                            type="button"
                            onClick={() => openPreview(result)}
                            className="inline-flex items-center rounded-full border border-slate-200 p-2 text-slate-700 transition hover:border-blue-300 hover:text-blue-700"
                            title="Preview result"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          <button
                            type="button"
                            onClick={() => navigate(`/cache/${result.id}`)}
                            className="inline-flex items-center rounded-full border border-slate-200 p-2 text-slate-700 transition hover:border-blue-300 hover:text-blue-700"
                            title="Open cache detail page"
                          >
                            <FileText className="h-4 w-4" />
                          </button>
                          <button
                            type="button"
                            onClick={() => downloadResultPdf(result as any)}
                            className="inline-flex items-center rounded-full border border-blue-200 p-2 text-blue-700 transition hover:bg-blue-50"
                            title="Download PDF"
                          >
                            <Download className="h-4 w-4" />
                          </button>
                          <button
                            type="button"
                            onClick={() => openComment(result)}
                            className="inline-flex items-center rounded-full border border-blue-200 p-2 text-blue-700 transition hover:bg-blue-50"
                            title="Add comment"
                          >
                            <MessageSquare className="h-4 w-4" />
                          </button>
                          <button
                            type="button"
                            onClick={() => openDelete(result)}
                            className="inline-flex items-center rounded-full border border-rose-200 p-2 text-rose-600 transition hover:bg-rose-50"
                            title="Delete cache"
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

      {showPreviewModal && previewResult ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 py-8 backdrop-blur-sm">
          <div className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-[2rem] bg-white p-6 shadow-glow">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
                  Result preview
                </p>
                <h2 className="mt-2 text-3xl font-semibold text-slate-950">
                  Result #{previewResult.id}
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
                  Battery
                </p>
                <p className="mt-2 text-lg font-semibold">
                  {batteryNameById.get(activeBatteryId ?? 0) ??
                    `Battery #${previewResult.prueba_id}`}
                </p>
              </div>
              <div className="rounded-3xl bg-slate-100 p-5">
                <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
                  Execution
                </p>
                <p className="mt-2 text-lg font-semibold text-slate-950">
                  {previewResult.execution_time_seconds.toFixed(2)} s
                </p>
              </div>
              <div className="rounded-3xl bg-slate-100 p-5">
                <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
                  Deviation
                </p>
                <p className="mt-2 text-lg font-semibold text-slate-950">
                  {previewResult.time_deviation_minutes.toFixed(2)} min
                </p>
              </div>
              <div className="rounded-3xl bg-slate-100 p-5">
                <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
                  Charging stations
                </p>
                <p className="mt-2 text-lg font-semibold text-slate-950">
                  {previewResult.charged_stations}
                </p>
              </div>
            </div>

            <div className="mt-6 grid gap-4 lg:grid-cols-2">
              <section className="rounded-[1.75rem] border border-slate-200 bg-slate-50 p-5">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">
                  Summary
                </p>
                <div className="mt-4 space-y-3">
                  <div className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                      Solver
                    </p>
                    <p className="mt-2 text-sm font-semibold text-slate-950">
                      {previewResult.solver}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                      Station vector
                    </p>
                    <p className="mt-2 text-sm font-semibold text-slate-950">
                      {formatStationVector(previewResult)}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                      Comment
                    </p>
                    <p className="mt-2 text-sm text-slate-700">
                      {previewResult.comment ?? "No comment stored"}
                    </p>
                  </div>
                </div>
              </section>
              <section className="rounded-[1.75rem] border border-slate-200 bg-slate-50 p-5">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">
                  Details
                </p>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  <div className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                      Result ID
                    </p>
                    <p className="mt-2 font-semibold text-slate-950">
                      #{previewResult.id}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                      Test
                    </p>
                    <p className="mt-2 font-semibold text-slate-950">
                      #{previewResult.prueba_id}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                      Timestamp
                    </p>
                    <p className="mt-2 font-semibold text-slate-950">
                      {previewResult.timestamp
                        ? new Date(previewResult.timestamp).toLocaleString()
                        : "-"}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-white p-4 ring-1 ring-slate-200">
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                      Stations vector
                    </p>
                    <p className="mt-2 font-semibold text-slate-950">
                      {getCacheSummary(previewResult).stationVector.join(
                        ", ",
                      ) || "[]"}
                    </p>
                  </div>
                </div>
              </section>
            </div>
          </div>
        </div>
      ) : null}

      {showCommentModal && commentResult ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 py-8 backdrop-blur-sm">
          <div className="w-full max-w-2xl rounded-[2rem] bg-white p-6 shadow-glow">
            <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
              Comment result
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-950">
              Result #{commentResult.id}
            </h2>
            <textarea
              value={commentText}
              onChange={(event) => setCommentText(event.target.value)}
              rows={8}
              className="mt-5 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none"
              placeholder="Write a comment about the solver output, quality, or deviations..."
            />
            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowCommentModal(false)}
                className="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700"
                title="Cancel comment"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={saveComment}
                className="rounded-full bg-slate-950 px-4 py-2 text-sm font-semibold text-white"
                title="Save comment"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {showDeleteModal && deleteCandidate ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 px-4 py-8 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-[2rem] bg-white p-6 shadow-glow">
            <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
              Delete result
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-950">
              Confirm deletion
            </h2>
            <p className="mt-4 text-sm leading-7 text-slate-600">
              Delete result{" "}
              <span className="font-semibold text-slate-950">
                #{deleteCandidate.id}
              </span>
              ? This cannot be undone.
            </p>
            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowDeleteModal(false)}
                className="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700"
                title="Cancel delete result"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={confirmDelete}
                className="rounded-full bg-rose-600 px-4 py-2 text-sm font-semibold text-white"
                title="Confirm delete result"
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
