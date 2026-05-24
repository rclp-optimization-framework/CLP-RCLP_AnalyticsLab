#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')
from config.db import SessionLocal
from model.dataStructure import Prueba

db = SessionLocal()

test = db.query(Prueba).filter(Prueba.id == 18).first()
if test:
    print(f"Test 18:")
    print(f"  num_buses: {test.num_buses}")
    print(f"  num_stations: {test.num_stations}")
    print(f"  max_stops: {test.max_stops}")
    print(f"  num_stops: {test.num_stops} (len={len(test.num_stops) if isinstance(test.num_stops, list) else 'N/A'})")
    print(f"  st_bi shape: {len(test.st_bi)}x{len(test.st_bi[0]) if test.st_bi else 0}")
    print(f"  d shape: {len(test.d)}x{len(test.d[0]) if test.d else 0}")
else:
    print("Test not found")

db.close()
