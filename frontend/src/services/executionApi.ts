import { request } from "./core";
import type { SolverName } from "../types";

export const executionApi = {
  executeBatteryTests: (
    batteryId: number,
    testIds: number[],
    solvers: SolverName[],
  ) =>
    request<any>("/ejecucion/ejecutar", {
      method: "POST",
      body: JSON.stringify({
        bateria_id: batteryId,
        prueba_ids: testIds,
        solvers,
      }),
    }),
  getAvailableSolversForExecution: () =>
    request<{ solvers: SolverName[] }>("/ejecucion/solvers"),
};
