import type {
  BatteryStats,
  ComparisonMetric,
  Result,
  TestInput,
} from "../types";
import { request } from "./core";
import { batteryApi } from "./batteryApi";
import { executionApi } from "./executionApi";
import { cacheApi } from "./cacheApi";

export const api = {
  ping: () => request<{ message: string }>("/ping"),
  ...batteryApi,
  ...cacheApi,
  ...executionApi,

  runQuickTest: (payload: TestInput, solver = "gecode") =>
    request("/prueba/rapida?solver=" + encodeURIComponent(solver), {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  createCacheForBattery: (batteryId: number) =>
    request<any[]>(`/cache/bateria/${batteryId}`, { method: "POST" }),
  getCacheById: (cacheId: number) => request<Result>(`/cache/${cacheId}`),
  getBatteryStats: (batteryId: number) =>
    request<BatteryStats>(`/cache/bateria/stats/${batteryId}`),
  getBatteryGraph: (batteryId: number) =>
    request<Record<string, [number, number]>>(
      `/cache/bateria/graph/${batteryId}`,
    ),
  getMultiBatteryStats: (batteryIds: number[]) =>
    request<Record<string, ComparisonMetric>>("/cache/bateria/stats", {
      method: "POST",
      body: JSON.stringify({ baterias: batteryIds }),
    }),
  getMultiBatteryMetric: (batteryIds: number[], metric: number) =>
    request<Record<string, ComparisonMetric>>(
      `/cache/bateria/stats/${metric}`,
      {
        method: "POST",
        body: JSON.stringify({ baterias: batteryIds }),
      },
    ),
};
