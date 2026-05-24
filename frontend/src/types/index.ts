export type SolverName = string;

export interface TestInput {
  num_buses: number;
  num_stations: number;
  max_stops?: number | null;
  num_stops?: number[] | null;
  st_bi?: number[][] | null;
  d?: number[][] | null;
  t?: number[][] | null;
  tau_bi?: number[][] | null;
  consumo_max?: number | null;
  consumo_min?: number | null;
  alpha?: number | null;
  mu?: number | null;
  sm?: number | null;
  psi?: number | null;
  beta?: number | null;
  m?: number | null;
}

// For backwards compatibility
export interface BatteryInput extends TestInput {}

export interface BatteryCreatePayload {
  nombre: string;
  solver?: string;
  pruebas?: {
    pruebas: TestInput[];
  };
}

export interface Battery {
  id: number;
  nombre: string;
  solver?: string;
  timestamp?: string;
}

// For backwards compatibility
export interface BatteryRecord extends Battery {}

export interface Test extends TestInput {
  id: number;
  bateria_id: number;
  timestamp?: string;
}

// For backwards compatibility
export interface TestRecord extends Test {}

export interface Result {
  id: number;
  prueba_id: number;
  solver: SolverName;
  execution_time_seconds: number;
  charged_stations: number;
  charging_locations: Record<string, any>[];
  station_vector?: number[];
  time_deviation_minutes: number;
  bateria: Record<string, any>;
  carga: Record<string, any>;
  comment?: string | null;
  timestamp?: string;
}

// For backwards compatibility
export interface CacheRecord extends Result {}

export interface StatsSummary {
  promedio: number;
  desviacion: number;
  mediana: number;
  moda: number | null;
}

export interface BatteryStats {
  execution_time_seconds: StatsSummary;
  time_deviation_minutes: StatsSummary;
}

export interface ChartPoint {
  label: string;
  stations: number;
  deviation: number;
  executionTime: number;
}

export interface ComparisonMetric {
  execution_time_seconds: StatsSummary | number;
  time_deviation_minutes: StatsSummary | number;
}
