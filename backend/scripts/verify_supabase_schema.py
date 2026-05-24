#!/usr/bin/env python3
"""Verify the target database schema matches the new battery/test/result design.

This script connects using DATABASE_URL if available. It prints the actual tables,
columns and constraints so you can compare Supabase with the expected model.
"""

from __future__ import annotations

import os
import sys
from sqlalchemy import inspect

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from config.db import build_engine  # noqa: E402
from model.dataStructure import Base  # noqa: E402

EXPECTED_TABLES = {
    "bateria": ["id", "nombre", "timestamp"],
    "prueba": [
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
    ],
    "result": [
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
    ],
}


def main() -> int:
    engine = build_engine()
    inspector = inspect(engine)

    print("DATABASE URL:", engine.url)
    print("TABLES:", inspector.get_table_names())
    print()

    missing_tables = []
    for table_name, expected_columns in EXPECTED_TABLES.items():
        if table_name not in inspector.get_table_names():
            missing_tables.append(table_name)
            print(f"[MISSING TABLE] {table_name}")
            continue

        columns = [column["name"] for column in inspector.get_columns(table_name)]
        print(f"[{table_name}] columns: {columns}")

        missing_columns = [name for name in expected_columns if name not in columns]
        extra_columns = [name for name in columns if name not in expected_columns]

        if missing_columns:
            print(f"  Missing columns: {missing_columns}")
        if extra_columns:
            print(f"  Extra columns: {extra_columns}")

        if table_name == "result":
            indexes = inspector.get_indexes(table_name)
            uniques = [index for index in indexes if index.get("unique")]
            print(f"  Unique indexes: {uniques}")

        print()

    if missing_tables:
        print("Schema check failed: missing tables ->", missing_tables)
        return 1

    print("Schema check complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
