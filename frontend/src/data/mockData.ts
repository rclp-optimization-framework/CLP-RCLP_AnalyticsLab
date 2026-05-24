import type {
  BatteryRecord,
  CacheRecord,
  ChartPoint,
  TestRecord,
} from "../types";

export const mockBatteries: BatteryRecord[] = [
  {
    id: 1,
    nombre: "Baseline urban corridor",
    timestamp: "2026-05-01T12:30:00Z",
  },
  {
    id: 2,
    nombre: "Expanded comparative set",
    timestamp: "2026-05-02T09:45:00Z",
  },
];

export const mockTests: TestRecord[] = [
  {
    id: 11,
    bateria_id: 1,
    num_buses: 2,
    num_stations: 4,
    max_stops: 3,
    num_stops: [3, 2],
    st_bi: [
      [1, 0, 1, 0],
      [0, 1, 0, 1],
    ],
    d: [
      [0, 14, 18, 22],
      [14, 0, 11, 19],
    ],
    t: [
      [0, 9, 12, 16],
      [9, 0, 10, 13],
    ],
    tau_bi: [
      [6, 18, 30, 42],
      [8, 20, 32, 44],
    ],
    consumo_max: 100,
    consumo_min: 20,
    alpha: 1.5,
    mu: 8,
    sm: 3,
    psi: 2.5,
    beta: 12,
    m: 1000,
    timestamp: "2026-05-01T12:30:00Z",
  },
  {
    id: 12,
    bateria_id: 2,
    num_buses: 3,
    num_stations: 5,
    max_stops: 4,
    num_stops: [4, 3, 4],
    st_bi: [
      [1, 0, 1, 0, 0],
      [0, 1, 0, 1, 0],
      [0, 0, 1, 0, 1],
    ],
    d: [
      [0, 10, 16, 24, 30],
      [10, 0, 9, 17, 25],
      [16, 9, 0, 11, 18],
    ],
    t: [
      [0, 6, 10, 14, 19],
      [6, 0, 8, 12, 16],
      [10, 8, 0, 7, 13],
    ],
    tau_bi: [
      [5, 17, 29, 40, 51],
      [7, 19, 31, 42, 54],
      [9, 21, 33, 45, 57],
    ],
    consumo_max: 120,
    consumo_min: 30,
    alpha: 1.8,
    mu: 10,
    sm: 4,
    psi: 3,
    beta: 14,
    m: 1000,
    timestamp: "2026-05-02T09:45:00Z",
  },
];

export const mockCaches: CacheRecord[] = [
  {
    id: 201,
    prueba_id: 11,
    solver: "gecode",
    execution_time_seconds: 1.28,
    charged_stations: 2,
    charging_locations: [{ station: 1, location: [0, 0] }],
    time_deviation_minutes: 4.8,
    bateria: { values: [80, 71] },
    carga: { values: [12, 13] },
    timestamp: "2026-05-02T15:10:00Z",
  },
  {
    id: 202,
    prueba_id: 12,
    solver: "chuffed",
    execution_time_seconds: 1.74,
    charged_stations: 3,
    charging_locations: [{ station: 2, location: [1, 1] }],
    time_deviation_minutes: 3.2,
    bateria: { values: [88, 76, 70] },
    carga: { values: [10, 11, 12] },
    timestamp: "2026-05-02T15:18:00Z",
  },
];

export const mockChartPoints: ChartPoint[] = [
  { label: "Battery 1", stations: 2, deviation: 4.8, executionTime: 1.28 },
  { label: "Battery 2", stations: 3, deviation: 3.2, executionTime: 1.74 },
  { label: "Battery 3", stations: 4, deviation: 2.7, executionTime: 1.19 },
  { label: "Battery 4", stations: 5, deviation: 5.1, executionTime: 1.89 },
];
