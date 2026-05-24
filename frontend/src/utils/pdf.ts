import { jsPDF } from "jspdf";
import type { CacheRecord, TestRecord } from "../types";
import { formatStationVector } from "./cache-format";

export function downloadResultPdf(
  record: CacheRecord & { comment?: string | null; station_vector?: number[] },
  test?: TestRecord,
) {
  const pdf = new jsPDF({ unit: "pt", format: "a4" });
  pdf.setFont("helvetica", "bold");
  pdf.setFontSize(18);
  pdf.text("R-CLP Analytics Cache", 40, 48);

  pdf.setFontSize(11);
  pdf.setFont("helvetica", "normal");
  const lines = [
    `Cache ID: ${record.id}`,
    `Test ID: ${record.prueba_id}`,
    `Execution time: ${record.execution_time_seconds.toFixed(2)} s`,
    `Charged stations: ${record.charged_stations}`,
    `Deviation: ${record.time_deviation_minutes.toFixed(2)} min`,
    `Station vector: ${formatStationVector(record as any)}`,
    `Comment: ${record.comment ?? "No comment"}`,
    test ? `Buses: ${test.num_buses} | Stations: ${test.num_stations}` : "",
  ].filter(Boolean);

  lines.forEach((line, index) => pdf.text(line, 40, 90 + index * 22));
  pdf.save(`r-clp-analytics-cache-${record.id}.pdf`);
}
