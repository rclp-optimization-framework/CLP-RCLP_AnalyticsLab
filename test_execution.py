#!/usr/bin/env python3
import requests
import json
import time
import sys

# Add backend to path for imports
sys.path.insert(0, 'backend')
from config.db import SessionLocal
from model.dataStructure import Prueba

# Load test parameters from DB
db = SessionLocal()
test = db.query(Prueba).filter(Prueba.id == 18).first()
db.close()

if not test:
    print("Test 18 not found")
    sys.exit(1)

print(f"Test 18 info:")
print(f"  num_buses={test.num_buses}, num_stations={test.num_stations}")
print(f"  max_stops={test.max_stops}, num_stops={test.num_stops}")

payload = {'bateria_id': 2, 'prueba_ids': [18], 'solvers': ['chuffed']}
start = time.time()

try:
    print("Sending execution request...")
    r = requests.post('http://localhost:8000/ejecucion/ejecutar', json=payload, timeout=60)
    elapsed = time.time() - start
    print(f'Status: {r.status_code}, Time: {elapsed:.2f}s')
    
    if r.status_code == 200:
        results = r.json()
        print(f'Results received: {len(results)}')
        for res in results:
            print(f"  Solver={res['solver']}, Success={res['success']}, ExecTime={res.get('execution_time_seconds', 'N/A')}s, StationVector={res.get('station_vector', 'N/A')}")
    else:
        print(f"Error response: {r.text}")
except Exception as e:
    elapsed = time.time() - start
    print(f'Error after {elapsed:.2f}s: {type(e).__name__}: {e}')
    sys.exit(1)
