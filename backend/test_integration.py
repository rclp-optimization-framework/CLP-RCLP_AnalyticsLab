#!/usr/bin/env python3
"""
Comprehensive integration test for the new backend schema.
Tests the complete workflow:
1. Create battery
2. Add tests via JSON
3. Add tests via DZN
4. Create and store results with solvers
5. Query results by solver
"""

import sys
import os
import json

# Set backend path
backend_path = r"c:\Users\lu\Downloads\Código\ 2026-I\AVISPA\Framework\backend"
os.chdir(backend_path)
sys.path.insert(0, backend_path)

from config.db import build_engine, Base
from sqlalchemy.orm import sessionmaker
from model.dataStructure import Bateria, Prueba, Result
from services.bateria import create_bateria
from services.resultado import create_or_update_result, get_results_by_prueba, get_results_by_bateria
from utils.dzn_parser import parse_dzn_to_test_input
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample test data
SAMPLE_TEST_JSON = {
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

SAMPLE_DZN = """
num_buses = 2;
num_stations = 4;
Cmax = 100;
Cmin = 20;
alpha = 15;
mu = 80;
SM = 3;
psi = 25;
beta = 120;
M = 1000;
max_stops = 3;
num_stops = [3,2];
st_bi = array2d(1..2, 1..4, [
  1,2,3,4,
  4,3,2,1
]);
D = array2d(1..2, 1..4, [
  0,140,180,220,
  0,140,180,220
]);
T = array2d(1..2, 1..4, [
  0,90,120,160,
  0,90,120,160
]);
tau_bi = array2d(1..2, 1..4, [
  0,100,200,320,
  50,150,250,370
]);
"""


def test_complete_workflow():
    """Run complete workflow test"""
    print("\n" + "="*70)
    print("COMPREHENSIVE INTEGRATION TEST")
    print("="*70)

    # Setup
    engine = build_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # ========== TEST 1: Create Battery ==========
        print("\n[TEST 1] Create Battery")
        print("-" * 70)
        bateria = create_bateria(db, "Integration Test Battery")
        print(f"✓ Battery created: id={bateria.id}, nombre='{bateria.nombre}'")
        assert bateria.id is not None
        assert bateria.nombre == "Integration Test Battery"
        battery_id = bateria.id

        # ========== TEST 2: Add Test via JSON ==========
        print("\n[TEST 2] Add Test via JSON")
        print("-" * 70)
        bateria2 = create_bateria(db, "Battery with JSON tests", [SAMPLE_TEST_JSON])
        pruebas = db.query(Prueba).filter(Prueba.bateria_id == bateria2.id).all()
        print(f"✓ Battery created with {len(pruebas)} test(s)")
        assert len(pruebas) == 1
        prueba_id = pruebas[0].id

        # ========== TEST 3: Parse DZN ==========
        print("\n[TEST 3] Parse DZN Format")
        print("-" * 70)
        dzn_parsed = parse_dzn_to_test_input(SAMPLE_DZN)
        print(f"✓ DZN parsed successfully")
        print(f"  Fields: {list(dzn_parsed.keys())}")
        assert "num_buses" in dzn_parsed
        assert "st_bi" in dzn_parsed
        assert dzn_parsed["num_buses"] == 2

        # ========== TEST 4: Add Test via DZN ==========
        print("\n[TEST 4] Add Test via DZN")
        print("-" * 70)
        bateria3 = create_bateria(db, "Battery with DZN tests", [dzn_parsed])
        pruebas3 = db.query(Prueba).filter(Prueba.bateria_id == bateria3.id).all()
        print(f"✓ Battery created with DZN test(s)")
        assert len(pruebas3) == 1
        prueba_dzn_id = pruebas3[0].id

        # ========== TEST 5: Create Results with Solvers ==========
        print("\n[TEST 5] Create Results with Different Solvers")
        print("-" * 70)

        # Result with gecode
        result_gecode = create_or_update_result(
            db=db,
            prueba_id=prueba_id,
            solver="gecode",
            execution_time_seconds=2.5,
            charged_stations=3,
            charging_locations=[{"station": 1, "location": [10, 20]}],
            time_deviation_minutes=5.2,
            bateria={"test": "gecode"},
            carga={"test": "gecode"},
        )
        print(f"✓ Result created: solver=gecode, execution_time={result_gecode.execution_time_seconds}s")

        # Result with chuffed
        result_chuffed = create_or_update_result(
            db=db,
            prueba_id=prueba_id,
            solver="chuffed",
            execution_time_seconds=1.8,
            charged_stations=2,
            charging_locations=[{"station": 0, "location": [5, 10]}],
            time_deviation_minutes=3.1,
            bateria={"test": "chuffed"},
            carga={"test": "chuffed"},
        )
        print(f"✓ Result created: solver=chuffed, execution_time={result_chuffed.execution_time_seconds}s")

        # ========== TEST 6: Update Result (Upsert) ==========
        print("\n[TEST 6] Update Result (Upsert same solver)")
        print("-" * 70)
        result_gecode_updated = create_or_update_result(
            db=db,
            prueba_id=prueba_id,
            solver="gecode",
            execution_time_seconds=2.0,  # Updated value
            charged_stations=4,
            charging_locations=[{"station": 2, "location": [15, 25]}],
            time_deviation_minutes=4.5,
            bateria={"test": "gecode_updated"},
            carga={"test": "gecode_updated"},
        )
        print(f"✓ Result updated: execution_time={result_gecode_updated.execution_time_seconds}s (was 2.5)")
        assert result_gecode_updated.execution_time_seconds == 2.0
        assert result_gecode_updated.id == result_gecode.id  # Same ID, not new

        # ========== TEST 7: Query Results by Prueba ==========
        print("\n[TEST 7] Query Results by Prueba")
        print("-" * 70)
        results_by_prueba = get_results_by_prueba(db, prueba_id)
        print(f"✓ Found {len(results_by_prueba)} results for prueba {prueba_id}:")
        for r in results_by_prueba:
            print(f"  - {r.solver}: {r.execution_time_seconds}s")
        assert len(results_by_prueba) == 2  # gecode + chuffed

        # ========== TEST 8: Query Results by Bateria ==========
        print("\n[TEST 8] Query Results by Bateria")
        print("-" * 70)
        results_by_bateria = get_results_by_bateria(db, bateria2.id)
        print(f"✓ Found {len(results_by_bateria)} results for battery {bateria2.id}")
        assert len(results_by_bateria) == 2

        # ========== TEST 9: Verify Unique Constraint ==========
        print("\n[TEST 9] Verify Unique Constraint (prueba_id, solver)")
        print("-" * 70)
        all_results = db.query(Result).filter(Result.prueba_id == prueba_id).all()
        solvers_used = [r.solver for r in all_results]
        print(f"✓ Solvers for prueba {prueba_id}: {solvers_used}")
        assert len(solvers_used) == len(set(solvers_used))  # No duplicates
        print(f"✓ Unique constraint verified: no duplicate (prueba_id, solver) pairs")

        # ========== SUMMARY ==========
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\nSummary:")
        print(f"  • Batteries created: 3")
        print(f"  • Tests created: 3")
        print(f"  • Results created: 2 (for 1 prueba with 2 solvers)")
        print(f"  • DZN parsing: ✓")
        print(f"  • Upsert functionality: ✓")
        print(f"  • Unique constraints: ✓")

        db.close()
        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        db.close()
        return False


if __name__ == "__main__":
    success = test_complete_workflow()
    sys.exit(0 if success else 1)
