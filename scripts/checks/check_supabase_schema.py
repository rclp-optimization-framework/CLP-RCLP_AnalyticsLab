#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))
VENV_SITE_PACKAGES = BACKEND_ROOT / "general_env" / "Lib" / "site-packages"
if VENV_SITE_PACKAGES.exists():
	sys.path.insert(0, str(VENV_SITE_PACKAGES))

from sqlalchemy import inspect

from config.db import engine  # noqa: E402

EXPECTED_SCHEMA = {
	"bateria": {
		"id",
		"nombre",
		"timestamp",
	},
	"prueba": {
		"id",
		"bateria_id",
		"num_buses",
		"num_stations",
		"max_stops",
		"num_stops",
		"st_bi",
		"d",
		"t",
		"tau_bi",
		"consumo_max",
		"consumo_min",
		"alpha",
		"mu",
		"sm",
		"psi",
		"beta",
		"m",
		"timestamp",
	},
	"result": {
		"id",
		"prueba_id",
		"solver",
		"execution_time_seconds",
		"charged_stations",
		"charging_locations",
		"time_deviation_minutes",
		"bateria",
		"carga",
		"timestamp",
	},
}

EXPECTED_UNIQUE_CONSTRAINT = "unique_prueba_solver"


def main() -> int:
	inspector = inspect(engine)
	tables = set(inspector.get_table_names())
	diagnostics: dict[str, object] = {
		"database_url": str(engine.url),
		"backend": engine.url.get_backend_name(),
		"tables": sorted(tables),
		"missing_tables": [],
		"missing_columns": {},
		"constraints": {},
	}

	missing_tables = sorted(set(EXPECTED_SCHEMA) - tables)
	diagnostics["missing_tables"] = missing_tables

	missing_columns: dict[str, list[str]] = {}
	for table_name, expected_columns in EXPECTED_SCHEMA.items():
		if table_name not in tables:
			continue
		existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
		missing = sorted(expected_columns - existing_columns)
		if missing:
			missing_columns[table_name] = missing
		constraints = [constraint.get("name") for constraint in inspector.get_unique_constraints(table_name)]
		diagnostics["constraints"][table_name] = constraints

	diagnostics["missing_columns"] = missing_columns

	print(json.dumps(diagnostics, indent=2, ensure_ascii=False))

	failed = bool(missing_tables or missing_columns)
	if "result" in tables:
		unique_constraints = diagnostics["constraints"].get("result", [])
		if EXPECTED_UNIQUE_CONSTRAINT not in unique_constraints:
			print(f"Missing unique constraint: {EXPECTED_UNIQUE_CONSTRAINT}")
			failed = True

	if failed:
		return 1

	print("Schema check passed.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
