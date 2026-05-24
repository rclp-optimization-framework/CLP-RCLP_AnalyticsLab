#!/usr/bin/env python3
"""Debug script to test POST /bateria/ locally"""

import json
import sys
sys.path.insert(0, ".")

from config.db import build_engine, Base
from sqlalchemy.orm import sessionmaker
from services.bateria import create_bateria

# Build engine and session
engine = build_engine()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()

# Test payload
payload = {
    "nombre": "Baseline urban corridor",
    "solver": "gecode",
    "pruebas": {
        "pruebas": [
            {
                "num_buses": 2,
                "num_stations": 4,
                "max_stops": 3,
                "num_stops": [3, 2],
                "st_bi": [[1, 0, 1, 0], [0, 1, 0, 1]],
                "d": [[0, 14, 18, 22], [14, 0, 11, 19]],
                "t": [[0, 9, 12, 16], [9, 0, 10, 13]],
                "tau_bi": [[6, 18, 30, 42], [8, 20, 32, 44]],
                "consumo_max": 100,
                "consumo_min": 20,
                "alpha": 1.5,
                "mu": 8.0,
                "sm": 3,
                "psi": 2.5,
                "beta": 12.0,
                "m": 1000,
            }
        ]
    },
}

try:
    print("Testing create_bateria with pruebas...")
    bateria = create_bateria(
        db,
        payload["nombre"],
        payload["solver"],
        payload["pruebas"]["pruebas"],
    )
    print(f"SUCCESS: {bateria.id}, {bateria.nombre}, {bateria.solver}")
    db.close()
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    db.close()
    sys.exit(1)
