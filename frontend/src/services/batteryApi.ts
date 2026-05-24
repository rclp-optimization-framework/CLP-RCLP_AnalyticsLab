import { API_BASE_URL, request } from "./core";
import type { BatteryCreatePayload, Battery, Test, TestInput } from "../types";

export const batteryApi = {
  createBattery: (payload: BatteryCreatePayload) =>
    request<Battery>("/bateria/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getBatteries: (skip = 0, limit = 100) =>
    request<Battery[]>(`/bateria/all?skip=${skip}&limit=${limit}`),
  getBatteryById: (batteryId: number) =>
    request<Battery>(`/bateria/${batteryId}`),
  deleteBattery: (batteryId: number) =>
    request<{ message: string }>(`/bateria/${batteryId}`, { method: "DELETE" }),
  updateBattery: (batteryId: number, nombre: string) =>
    request<Battery>(`/bateria/${batteryId}`, {
      method: "PUT",
      body: JSON.stringify({ nombre }),
    }),
  getBatteryTests: (batteryId: number, skip = 0, limit = 100) =>
    request<Test[]>(`/bateria/prueba/${batteryId}?skip=${skip}&limit=${limit}`),
  getBatterySummary: (batteryId: number) =>
    request<{
      id: number;
      nombre: string;
      timestamp?: string;
      test_count: number;
      result_count: number;
    }>(`/bateria/${batteryId}/summary`),
  addTestToBattery: (batteryId: number, testData: TestInput) =>
    request<Test>(`/bateria/prueba/add/${batteryId}`, {
      method: "POST",
      body: JSON.stringify(testData),
    }),
  updateTest: (testId: number, testData: Partial<TestInput>) =>
    request<Test>(`/prueba/${testId}`, {
      method: "PUT",
      body: JSON.stringify(testData),
    }),
  uploadTestsFile: async (batteryId: number, file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(
      `${API_BASE_URL}/bateria/upload/tests/${batteryId}`,
      {
        method: "POST",
        body: formData,
      },
    );

    if (!response.ok) {
      const message = await response.text();
      throw new Error(
        message || `Upload failed with status ${response.status}`,
      );
    }

    return response.json() as Promise<Test[]>;
  },
  getTestById: (testId: number) => request<Test>(`/prueba/${testId}`),
  deleteTest: (testId: number) =>
    request<{ message: string }>(`/prueba/${testId}`, { method: "DELETE" }),
};
