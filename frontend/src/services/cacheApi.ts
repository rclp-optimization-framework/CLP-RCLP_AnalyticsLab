import { request } from "./core";
import type { CacheRecord, SolverName } from "../types";

export const cacheApi = {
  createCache: (
    pruebaId: number,
    solver: SolverName,
    data: Omit<CacheRecord, "id" | "timestamp" | "prueba_id" | "solver">,
  ) =>
    request<CacheRecord>("/cache/", {
      method: "POST",
      body: JSON.stringify({ prueba_id: pruebaId, solver, ...data }),
    }),
  getCacheByTest: (testId: number) =>
    request<CacheRecord[]>(`/cache/prueba/${testId}`),
  getCacheByTestAndSolver: (testId: number, solver: SolverName) =>
    request<CacheRecord>(`/cache/prueba/${testId}/solver/${solver}`),
  getCacheById: (cacheId: number) =>
    request<CacheRecord>(`/cache/${cacheId}`),
  getCacheByBattery: (batteryId: number) =>
    request<CacheRecord[]>(`/cache/bateria/${batteryId}`),
  deleteCache: (cacheId: number) =>
    request<{ message: string }>(`/cache/${cacheId}`, {
      method: "DELETE",
    }),
  updateCacheComment: (cacheId: number, comment: string | null) =>
    request<CacheRecord>(
      `/cache/${cacheId}/comment?comment=${encodeURIComponent(comment ?? "")}`,
      { method: "PATCH" },
    ),
  getAvailableSolvers: () =>
    request<{ solvers: SolverName[] }>("/cache/solvers/available"),
  getAllSolversForTest: (testId: number) =>
    request<CacheRecord[]>(`/cache/test/${testId}/all-solvers`),
  getTestStatistics: (testId: number) =>
    request<{
      best_deviation: number;
      worst_deviation: number;
      avg_deviation: number;
      avg_execution: number;
      num_solvers: number;
      solvers: string[];
      cache_count: number;
    }>(`/cache/test/${testId}/statistics`),
  getTestStationsInfo: (testId: number) =>
    request<Record<string, {
      charged_stations: number;
      charging_locations: any;
      station_vector: number[] | null;
      bateria: any;
      carga: any;
      execution_time_seconds: number;
      time_deviation_minutes: number;
    }>>(`/cache/test/${testId}/stations-info`),
  getAllSolversByBattery: (batteryId: number) =>
    request<Record<number, CacheRecord[]>>(`/cache/battery/${batteryId}/all-tests-with-solvers`),
};
