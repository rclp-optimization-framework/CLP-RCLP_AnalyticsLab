import type { CacheRecord } from "../types";

export function getStationVector(cache: CacheRecord) {
  if (Array.isArray(cache.station_vector) && cache.station_vector.length > 0) {
    return cache.station_vector;
  }

  if (Array.isArray(cache.charging_locations)) {
    const vector = cache.charging_locations
      .map((item) => {
        if (typeof item === "number") {
          return item;
        }
        if (item && typeof item === "object") {
          if ("active" in item) {
            return item.active ? 1 : 0;
          }
          if ("station" in item && typeof item.station === "number") {
            return item.station;
          }
        }
        return 0;
      })
      .filter((value) => Number.isFinite(value));

    if (vector.length > 0) {
      return vector;
    }
  }

  return [] as number[];
}

export function formatStationVector(cache: CacheRecord) {
  const vector = getStationVector(cache);
  return vector.length > 0 ? `[${vector.join(", ")}]` : "[]";
}

export function getCacheSummary(cache: CacheRecord) {
  return {
    executionTime: Number(cache.execution_time_seconds ?? 0),
    deviation: Number(cache.time_deviation_minutes ?? 0),
    stations: Number(cache.charged_stations ?? 0),
    stationVector: getStationVector(cache),
  };
}
