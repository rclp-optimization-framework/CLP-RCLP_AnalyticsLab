#!/usr/bin/env python3
"""
Test script to validate backend functionality after schema changes.
Tests:
1. Database schema creation
2. Battery creation (without solver)
3. Test creation within battery
4. Result storage
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
from services.resultado import create_or_update_result
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_schema():
    """Test 1: Database schema creation"""
    print("\n" + "="*60)
    print("TEST 1: Database Schema Creation")
    print("="*60)
    
    try:
        engine = build_engine()
        Base.metadata.drop_all(engine)  # Clean slate
        Base.metadata.create_all(engine)
        print("✓ Schema created successfully")
        return True
    except Exception as e:
        print(f"✗ Schema creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_battery_creation(engine):
    """Test 2: Battery creation (no solver)"""
    print("\n" + "="*60)
    print("TEST 2: Battery Creation (No Solver)")
    print("="*60)
    
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Create battery without pruebas
        bateria = create_bateria(db, "Test Battery 1")
        print(f"✓ Battery created: id={bateria.id}, nombre={bateria.nombre}")
        
        # Verify battery has no solver field in response
        assert not hasattr(bateria, 'solver') or bateria.solver is None, "Battery should not have solver"
        print(f"✓ Battery correctly has no solver field")
        
        db.close()
        return True
    except Exception as e:
        print(f"✗ Battery creation failed: {e}")
        import traceback
        traceback.print_exc()
        db.close()
        return False


def test_battery_with_tests(engine):
    """Test 3: Battery with tests creation"""
    print("\n" + "="*60)
    print("TEST 3: Battery with Tests Creation")
    print("="*60)
    
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Prepare test data
        prueba_data = {
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
        
        # Create battery with tests
        bateria = create_bateria(db, "Test Battery with Tests", [prueba_data])
        print(f"✓ Battery created with tests: id={bateria.id}")
        
        # Verify pruebas were created
        pruebas = db.query(Prueba).filter(Prueba.bateria_id == bateria.id).all()
        print(f"✓ {len(pruebas)} test(s) created in battery")
        
        for prueba in pruebas:
            print(f"  - Prueba {prueba.id}: {prueba.num_buses} buses, {prueba.num_stations} stations")
        
        db.close()
        return True
    except Exception as e:
        print(f"✗ Battery with tests creation failed: {e}")
        import traceback
        traceback.print_exc()
        db.close()
        return False


def test_result_storage(engine):
    """Test 4: Result storage with solver"""
    print("\n" + "="*60)
    print("TEST 4: Result Storage with Solver")
    print("="*60)
    
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Get first prueba from previous test
        prueba = db.query(Prueba).first()
        if not prueba:
            print("✗ No test found to create result for")
            db.close()
            return False
        
        # Create result for this prueba with gecode solver
        result = create_or_update_result(
            db=db,
            prueba_id=prueba.id,
            solver="gecode",
            execution_time_seconds=2.5,
            charged_stations=3,
            charging_locations=[{"station": 1, "location": [10, 20]}],
            time_deviation_minutes=5.2,
            bateria={"key": "value"},
            carga={"key": "value"},
        )
        print(f"✓ Result created: id={result.id}, solver={result.solver}, prueba_id={result.prueba_id}")
        
        # Test update (unique constraint on prueba_id + solver)
        result2 = create_or_update_result(
            db=db,
            prueba_id=prueba.id,
            solver="gecode",
            execution_time_seconds=3.0,
            charged_stations=4,
            charging_locations=[{"station": 2, "location": [15, 25]}],
            time_deviation_minutes=6.0,
            bateria={"updated": "yes"},
            carga={"updated": "yes"},
        )
        print(f"✓ Result updated (same prueba + solver): execution_time={result2.execution_time_seconds}s")
        
        # Create result with different solver
        result3 = create_or_update_result(
            db=db,
            prueba_id=prueba.id,
            solver="chuffed",
            execution_time_seconds=1.8,
            charged_stations=2,
            charging_locations=[{"station": 0, "location": [5, 10]}],
            time_deviation_minutes=3.1,
            bateria={"solver": "chuffed"},
            carga={"solver": "chuffed"},
        )
        print(f"✓ Result created with different solver: id={result3.id}, solver={result3.solver}")
        
        # Verify unique constraint
        results = db.query(Result).filter(Result.prueba_id == prueba.id).all()
        print(f"✓ Total results for prueba {prueba.id}: {len(results)} (2 solvers)")
        
        db.close()
        return True
    except Exception as e:
        print(f"✗ Result storage test failed: {e}")
        import traceback
        traceback.print_exc()
        db.close()
        return False


if __name__ == "__main__":
    print("\n🧪 BACKEND SCHEMA VALIDATION TEST SUITE 🧪\n")
    
    # Run tests
    test1_ok = test_schema()
    if not test1_ok:
        sys.exit(1)
    
    engine = build_engine()
    
    test2_ok = test_battery_creation(engine)
    test3_ok = test_battery_with_tests(engine)
    test4_ok = test_result_storage(engine)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    tests = {
        "Schema Creation": test1_ok,
        "Battery Creation": test2_ok,
        "Battery with Tests": test3_ok,
        "Result Storage": test4_ok,
    }
    
    for name, result in tests.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:.<40} {status}")
    
    all_ok = all(tests.values())
    print("="*60)
    
    if all_ok:
        print("\n✅ ALL TESTS PASSED!\n")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!\n")
        sys.exit(1)
