import {
  BarChart,
  Bar,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Legend,
} from "recharts";
import { useState } from "react";
import type { BatteryStats, ChartPoint } from "../../types";

const chartColors = ["#1d4ed8", "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd"];

type ViewMode = "bars" | "line" | "pie";

interface StatsChartsProps {
  points: ChartPoint[];
  summary?: BatteryStats | null;
}

export function StatsCharts({ points, summary }: StatsChartsProps) {
  const [mode, setMode] = useState<ViewMode>("bars");

  const pieData = points.map((point) => ({
    name: point.label,
    value: point.deviation,
  }));

  return (
    <section className="glass-panel overflow-hidden rounded-3xl p-6 shadow-panel">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="brand-type text-sm font-semibold uppercase tracking-[0.3em] text-blue-700">
            Analytics view
          </p>
          <h3 className="mt-1 text-2xl font-semibold text-slate-950">
            Comparable statistics and chart presets
          </h3>
        </div>
        <div className="flex rounded-full bg-slate-100 p-1">
          {(["bars", "line", "pie"] as ViewMode[]).map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => setMode(item)}
              className={`rounded-full px-4 py-2 text-sm font-semibold capitalize transition ${
                mode === item
                  ? "bg-slate-950 text-white"
                  : "text-slate-600 hover:text-slate-950"
              }`}
            >
              {item}
            </button>
          ))}
        </div>
      </div>

      {summary ? (
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="rounded-3xl bg-white/75 p-4 ring-1 ring-slate-200">
            <p className="text-sm font-semibold text-slate-500">
              Execution time
            </p>
            <p className="mt-2 text-lg font-bold text-slate-950">
              Average {summary.execution_time_seconds.promedio.toFixed(2)} s
            </p>
            <p className="text-sm text-slate-600">
              Deviation {summary.execution_time_seconds.desviacion.toFixed(2)}
            </p>
          </div>
          <div className="rounded-3xl bg-white/75 p-4 ring-1 ring-slate-200">
            <p className="text-sm font-semibold text-slate-500">
              Time deviation
            </p>
            <p className="mt-2 text-lg font-bold text-slate-950">
              Average {summary.time_deviation_minutes.promedio.toFixed(2)} min
            </p>
            <p className="text-sm text-slate-600">
              Median {summary.time_deviation_minutes.mediana.toFixed(2)}
            </p>
          </div>
        </div>
      ) : null}

      <div className="mt-6 h-[360px] rounded-3xl bg-slate-950 p-4 text-white shadow-glow">
        <ResponsiveContainer width="100%" height="100%">
          {mode === "bars" ? (
            <BarChart data={points}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(255,255,255,0.14)"
              />
              <XAxis dataKey="label" stroke="#cbd5e1" />
              <YAxis stroke="#cbd5e1" />
              <Tooltip
                contentStyle={{
                  background: "#0f172a",
                  border: "1px solid rgba(148,163,184,0.35)",
                }}
              />
              <Legend />
              <Bar dataKey="stations" fill="#60a5fa" radius={[12, 12, 0, 0]} />
              <Bar dataKey="deviation" fill="#1d4ed8" radius={[12, 12, 0, 0]} />
              <Bar
                dataKey="executionTime"
                fill="#93c5fd"
                radius={[12, 12, 0, 0]}
              />
            </BarChart>
          ) : mode === "line" ? (
            <LineChart data={points}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(255,255,255,0.14)"
              />
              <XAxis dataKey="label" stroke="#cbd5e1" />
              <YAxis stroke="#cbd5e1" />
              <Tooltip
                contentStyle={{
                  background: "#0f172a",
                  border: "1px solid rgba(148,163,184,0.35)",
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="deviation"
                stroke="#60a5fa"
                strokeWidth={3}
                dot={{ r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="executionTime"
                stroke="#1d4ed8"
                strokeWidth={3}
                dot={{ r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="stations"
                stroke="#93c5fd"
                strokeWidth={3}
                dot={{ r: 4 }}
              />
            </LineChart>
          ) : (
            <PieChart>
              <Tooltip
                contentStyle={{
                  background: "#0f172a",
                  border: "1px solid rgba(148,163,184,0.35)",
                }}
              />
              <Legend />
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                outerRadius={120}
                innerRadius={70}
                paddingAngle={4}
              >
                {pieData.map((entry, index) => (
                  <Cell
                    key={entry.name}
                    fill={chartColors[index % chartColors.length]}
                  />
                ))}
              </Pie>
            </PieChart>
          )}
        </ResponsiveContainer>
      </div>
    </section>
  );
}
