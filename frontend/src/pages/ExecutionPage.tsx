import { Plus, Play, RotateCcw, Save } from "lucide-react";
import { useMemo, useState } from "react";
import { toast } from "sonner";
import { api } from "../services/api";
import type { BatteryInput, BatteryRecord } from "../types";

interface DraftBatteryInput {
  num_buses: string;
  num_stations: string;
  max_stops: string;
  num_stops: string;
  st_bi: string;
  d: string;
  t: string;
  tau_bi: string;
  consumo_max: string;
  consumo_min: string;
  alpha: string;
  mu: string;
  sm: string;
  psi: string;
  beta: string;
  m: string;
}

const starterDraft: DraftBatteryInput = {
  num_buses: "2",
  num_stations: "4",
  max_stops: "3",
  num_stops: "[3,2]",
  st_bi: "[[1,0,1,0],[0,1,0,1]]",
  d: "[[0,14,18,22],[14,0,11,19]]",
  t: "[[0,9,12,16],[9,0,10,13]]",
  tau_bi: "[[6,18,30,42],[8,20,32,44]]",
  consumo_max: "100",
  consumo_min: "20",
  alpha: "1.5",
  mu: "8",
  sm: "3",
  psi: "2.5",
  beta: "12",
  m: "1000",
};

function cloneDraft(): DraftBatteryInput {
  return { ...starterDraft };
}

function parseDraft(draft: DraftBatteryInput): BatteryInput {
  return {
    num_buses: Number(draft.num_buses),
    num_stations: Number(draft.num_stations),
    max_stops: Number(draft.max_stops),
    num_stops: JSON.parse(draft.num_stops),
    st_bi: JSON.parse(draft.st_bi),
    d: JSON.parse(draft.d),
    t: JSON.parse(draft.t),
    tau_bi: JSON.parse(draft.tau_bi),
    consumo_max: Number(draft.consumo_max),
    consumo_min: Number(draft.consumo_min),
    alpha: Number(draft.alpha),
    mu: Number(draft.mu),
    sm: Number(draft.sm),
    psi: Number(draft.psi),
    beta: Number(draft.beta),
    m: Number(draft.m),
  };
}

export function ExecutionPage() {
  const [batteryName, setBatteryName] = useState("AVISPA execution batch");
  const [solver, setSolver] = useState("gecode");
  const [persist, setPersist] = useState(true);
  const [drafts, setDrafts] = useState<DraftBatteryInput[]>([cloneDraft()]);
  const [activeIndex, setActiveIndex] = useState(0);
  const [batteryResult, setBatteryResult] = useState<BatteryRecord | null>(
    null,
  );
  const [solverResult, setSolverResult] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);

  const activeDraft = drafts[activeIndex];

  const parsedDrafts = useMemo(() => drafts.map(parseDraft), [drafts]);

  const updateDraft = (field: keyof DraftBatteryInput, value: string) => {
    setDrafts((current) =>
      current.map((item, index) =>
        index === activeIndex ? { ...item, [field]: value } : item,
      ),
    );
  };

  const addExample = () => {
    setDrafts((current) => [
      ...current,
      { ...starterDraft, num_buses: String(current.length + 2) },
    ]);
    setActiveIndex(drafts.length);
    toast.message("Example added");
  };

  const removeExample = (index: number) => {
    setDrafts((current) =>
      current.filter((_, currentIndex) => currentIndex !== index),
    );
    setActiveIndex((current) =>
      Math.max(0, current - (index <= current ? 1 : 0)),
    );
    toast.message("Example removed");
  };

  const execute = async () => {
    try {
      setLoading(true);
      setBatteryResult(null);
      setSolverResult(null);

      if (persist) {
        const createdBattery = await api.createBattery({
          nombre: batteryName,
          solver,
          pruebas: { pruebas: parsedDrafts },
        });
        setBatteryResult(createdBattery);
        const stored = await api.createCacheForBattery(createdBattery.id);
        setSolverResult(stored);
        toast.success("Battery executed and stored in cache");
        return;
      }

      const quickResult = await api.runQuickTest(
        parsedDrafts[activeIndex],
        solver,
      );
      setSolverResult(quickResult);
      toast.success("Quick execution completed");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Execution failed";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <section className="grid gap-6 lg:grid-cols-[1fr_0.9fr]">
        <div className="glass-panel rounded-[2rem] p-6 shadow-panel">
          <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
            Execution workspace
          </p>
          <h1 className="mt-3 text-4xl font-bold text-slate-950">
            Build one or several test cases and decide whether the result is
            stored.
          </h1>
          <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-600">
            The UI mirrors the current backend workflow: quick execution for a
            single payload, or battery creation followed by cache persistence
            for analytics.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={execute}
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-glow transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Play className="h-4 w-4" />
              {loading
                ? "Processing..."
                : persist
                  ? "Run and store"
                  : "Run without storage"}
            </button>
            <button
              type="button"
              onClick={addExample}
              className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-blue-300 hover:text-blue-700"
            >
              <Plus className="h-4 w-4" />
              Add example
            </button>
            <button
              type="button"
              onClick={() => setDrafts([cloneDraft()])}
              className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-blue-300 hover:text-blue-700"
            >
              <RotateCcw className="h-4 w-4" />
              Reset set
            </button>
          </div>
        </div>

        <div className="glass-panel rounded-[2rem] p-6 shadow-panel">
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="space-y-2 text-sm font-semibold text-slate-700">
              Battery name
              <input
                value={batteryName}
                onChange={(event) => setBatteryName(event.target.value)}
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none ring-0 focus:border-blue-400"
              />
            </label>
            <label className="space-y-2 text-sm font-semibold text-slate-700">
              Solver
              <select
                value={solver}
                onChange={(event) => setSolver(event.target.value)}
                className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-blue-400"
              >
                <option value="gecode">gecode</option>
                <option value="chuffed">chuffed</option>
                <option value="cbc">cbc</option>
              </select>
            </label>
          </div>
          <label className="mt-4 flex items-center justify-between rounded-3xl border border-slate-200 bg-white px-5 py-4 text-sm font-semibold text-slate-700">
            Store cache entries in Supabase
            <input
              checked={persist}
              onChange={(event) => setPersist(event.target.checked)}
              type="checkbox"
              className="h-5 w-5 rounded border-slate-300 text-blue-600"
            />
          </label>
          {batteryResult ? (
            <div className="mt-4 rounded-3xl bg-slate-950 p-4 text-white">
              <p className="text-xs uppercase tracking-[0.3em] text-blue-300">
                Stored battery
              </p>
              <p className="mt-2 text-lg font-semibold">
                #{batteryResult.id} {batteryResult.nombre}
              </p>
              <p className="text-sm text-slate-300">
                Solver selected at execution
              </p>
            </div>
          ) : null}
        </div>
      </section>

      <section className="space-y-5">
        {drafts.map((draft, index) => {
          const selected = index === activeIndex;
          return (
            <article
              key={`${index}-${draft.num_buses}`}
              className={`glass-panel rounded-[2rem] p-6 shadow-panel transition ${selected ? "ring-2 ring-blue-400" : "opacity-92"}`}
            >
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-slate-500">
                    Test case {index + 1}
                  </p>
                  <h2 className="text-2xl font-semibold text-slate-950">
                    {selected ? "Active draft" : "Draft preview"}
                  </h2>
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => setActiveIndex(index)}
                    className="rounded-full bg-slate-950 px-4 py-2 text-sm font-semibold text-white"
                  >
                    Open
                  </button>
                  <button
                    type="button"
                    onClick={() => removeExample(index)}
                    className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700"
                  >
                    Delete
                  </button>
                </div>
              </div>

              {selected ? (
                <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                  {(
                    Object.keys(activeDraft) as (keyof DraftBatteryInput)[]
                  ).map((field) => (
                    <label
                      key={field}
                      className="space-y-2 text-xs font-semibold uppercase tracking-[0.22em] text-slate-500"
                    >
                      {field}
                      {["num_stops", "st_bi", "d", "t", "tau_bi"].includes(
                        field,
                      ) ? (
                        <textarea
                          value={activeDraft[field]}
                          onChange={(event) =>
                            updateDraft(field, event.target.value)
                          }
                          rows={4}
                          className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-normal uppercase tracking-normal text-slate-800 outline-none focus:border-blue-400"
                        />
                      ) : (
                        <input
                          value={activeDraft[field]}
                          onChange={(event) =>
                            updateDraft(field, event.target.value)
                          }
                          className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-normal tracking-normal text-slate-800 outline-none focus:border-blue-400"
                        />
                      )}
                    </label>
                  ))}
                </div>
              ) : (
                <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  <div className="rounded-2xl bg-white/80 p-4 ring-1 ring-slate-200">
                    <p className="text-xs uppercase text-slate-500">Buses</p>
                    <p className="mt-1 text-lg font-semibold">
                      {draft.num_buses}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-white/80 p-4 ring-1 ring-slate-200">
                    <p className="text-xs uppercase text-slate-500">Stations</p>
                    <p className="mt-1 text-lg font-semibold">
                      {draft.num_stations}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-white/80 p-4 ring-1 ring-slate-200">
                    <p className="text-xs uppercase text-slate-500">
                      Max stops
                    </p>
                    <p className="mt-1 text-lg font-semibold">
                      {draft.max_stops}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-white/80 p-4 ring-1 ring-slate-200">
                    <p className="text-xs uppercase text-slate-500">Solver</p>
                    <p className="mt-1 text-lg font-semibold">{solver}</p>
                  </div>
                </div>
              )}
            </article>
          );
        })}
      </section>

      <section className="glass-panel rounded-[2rem] p-6 shadow-panel">
        <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
          Solver output
        </p>
        <pre className="mt-4 overflow-x-auto rounded-3xl bg-slate-950 p-5 text-sm text-slate-100">
          {JSON.stringify(solverResult, null, 2) || "No execution yet."}
        </pre>
      </section>
    </div>
  );
}
