#!/usr/bin/env python3
"""Apply idempotent schema fixes to the live PostgreSQL/Supabase database.

This script removes the legacy bateria.solver column that blocks battery inserts
and ensures the new result uniqueness exists.
"""

from __future__ import annotations

import os
import sys
from sqlalchemy import inspect, text

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from config.db import build_engine


def main() -> int:
    engine = build_engine()
    inspector = inspect(engine)

    print(f"Database URL: {engine.url}")
    print(f"Tables before migration: {inspector.get_table_names()}")

    with engine.begin() as connection:
        bateria_columns = [column["name"] for column in inspector.get_columns("bateria")]
        if "solver" in bateria_columns:
            print("Dropping legacy bateria.solver column...")
            connection.execute(text("ALTER TABLE bateria DROP COLUMN IF EXISTS solver"))
        else:
            print("bateria.solver column already absent.")

        # Ensure the result table has the expected unique constraint.
        result_indexes = inspector.get_indexes("result") if "result" in inspector.get_table_names() else []
        has_unique = any(index.get("unique") and index.get("name") == "unique_prueba_solver" for index in result_indexes)
        if not has_unique and "result" in inspector.get_table_names():
            print("Creating unique constraint on result(prueba_id, solver)...")
            connection.execute(
                text(
                    "ALTER TABLE result "
                    "ADD CONSTRAINT unique_prueba_solver UNIQUE (prueba_id, solver)"
                )
            )
        else:
            print("Unique constraint on result(prueba_id, solver) already present.")

        if "result" in inspector.get_table_names():
            result_columns = [column["name"] for column in inspector.get_columns("result")]
            if "comment" not in result_columns:
                print("Adding result.comment column...")
                connection.execute(text("ALTER TABLE result ADD COLUMN comment VARCHAR"))
            else:
                print("result.comment column already present.")

    print("Migration complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
