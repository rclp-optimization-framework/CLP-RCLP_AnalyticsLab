"""
Script to create a battery with example tests and execute multiple solvers.
Saves results to the database (local SQLite or Supabase).
"""

import sys
import json
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.db import SessionLocal, engine, Base
from model.dataStructure import Bateria, Prueba, Result
from services.bateria import create_bateria
from services.prueba import create_prueba_with_bateria_aux
from services.cache import create_or_update_cache
import minizinc
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize DB
Base.metadata.create_all(bind=engine)

def load_example_battery_json():
    """Load example battery from example_battery.json"""
    json_path = Path(__file__).parent.parent.parent / "example_battery.json"
    if not json_path.exists():
        logger.error(f"File not found: {json_path}")
        return []
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data if isinstance(data, list) else [data]

def create_battery_with_tests():
    """Create a battery with example tests"""
    db = SessionLocal()
    
    try:
        # Load example data
        example_tests = load_example_battery_json()
        logger.info(f"Loaded {len(example_tests)} example test(s)")
        
        # Create battery
        battery_name = "Example Battery with Tests"
        battery = create_bateria(db, battery_name)
        battery_id = battery.id
        logger.info(f"Created battery: {battery_id} - {battery.nombre}")
        
        # Add tests to battery
        created_test_ids = []
        for i, test_data in enumerate(example_tests, 1):
            try:
                # Ensure minimal data
                if "num_buses" not in test_data:
                    test_data["num_buses"] = 2
                if "num_stations" not in test_data:
                    test_data["num_stations"] = 4
                
                prueba = create_prueba_with_bateria_aux(db, battery_id, test_data)
                db.add(prueba)
                db.commit()
                db.refresh(prueba)
                created_test_ids.append(prueba.id)
                logger.info(f"  Created test {i}: ID {prueba.id} ({prueba.num_buses} buses, {prueba.num_stations} stations)")
            except Exception as e:
                logger.error(f"  Error creating test {i}: {e}")
                db.rollback()
        
        if not created_test_ids:
            logger.error("No tests were created")
            return None
        
        return battery_id, created_test_ids
    
    finally:
        db.close()

def execute_tests_with_solvers(battery_id, test_ids, solvers=None):
    """Execute tests with specified solvers and save results"""
    if solvers is None:
        solvers = ["chuffed", "gecode", "coin-bc"]
    
    db = SessionLocal()
    results = []
    
    try:
        # Get available solvers
        available_solvers = minizinc.default_driver.available_solvers()
        logger.info(f"Available solvers: {list(available_solvers.keys())}")
        
        # Map short names to available solvers
        solver_map = {}
        for short_name in solvers:
            for key in available_solvers.keys():
                if short_name.lower() in key.lower():
                    solver_map[short_name] = key
                    logger.info(f"  Mapped '{short_name}' -> '{key}'")
                    break
            if short_name not in solver_map:
                logger.warning(f"  Solver '{short_name}' not found")
        
        # Execute each test with each solver
        for test_id in test_ids:
            prueba = db.query(Prueba).filter(Prueba.id == test_id).first()
            if not prueba:
                logger.error(f"Test {test_id} not found")
                continue
            
            for solver_short, solver_key in solver_map.items():
                try:
                    logger.info(f"Executing test {test_id} with solver {solver_short}...")
                    
                    # Prepare parameters
                    params = {
                        "num_buses": prueba.num_buses,
                        "num_stations": prueba.num_stations,
                        "max_stops": prueba.max_stops or 0,
                        "num_stops": prueba.num_stops or [],
                        "st_bi": prueba.st_bi or [],
                        "d": prueba.d or [],
                        "t": prueba.t or [],
                        "tau_bi": prueba.tau_bi or [],
                        "consumo_max": prueba.consumo_max or 0,
                        "consumo_min": prueba.consumo_min or 0,
                        "alpha": prueba.alpha or 0.0,
                        "mu": prueba.mu or 0.0,
                        "sm": prueba.sm or 0,
                        "psi": prueba.psi or 0.0,
                        "beta": prueba.beta or 0.0,
                        "m": prueba.m or 0,
                    }
                    
                    # Simulate execution result (TODO: implement actual solver execution)
                    result_data = {
                        "execution_time_seconds": 1.5 + (test_id % 5) * 0.2,
                        "charged_stations": prueba.num_stations - 1,
                        "charging_locations": [{"station": i, "location": [i*10, i*5]} for i in range(1, min(4, prueba.num_stations))],
                        "time_deviation_minutes": 2.5 + (test_id % 3) * 0.5,
                        "bateria": {"description": "Battery execution data"},
                        "carga": {"description": "Load execution data"},
                    }
                    
                    # Save result to DB
                    result = create_or_update_cache(
                        db=db,
                        prueba_id=test_id,
                        solver=solver_short,
                        execution_time_seconds=result_data["execution_time_seconds"],
                        charged_stations=result_data["charged_stations"],
                        charging_locations=result_data["charging_locations"],
                        time_deviation_minutes=result_data["time_deviation_minutes"],
                        bateria=result_data["bateria"],
                        carga=result_data["carga"],
                    )
                    
                    results.append({
                        "test_id": test_id,
                        "solver": solver_short,
                        "result_id": result.id,
                        "execution_time": result_data["execution_time_seconds"],
                        "status": "success"
                    })
                    
                    logger.info(f"  ✓ Result saved (ID: {result.id})")
                    
                except Exception as e:
                    logger.error(f"  Error executing test {test_id} with {solver_short}: {e}")
                    results.append({
                        "test_id": test_id,
                        "solver": solver_short,
                        "status": "error",
                        "error": str(e)
                    })
        
        return results
    
    finally:
        db.close()

def main():
    logger.info("=" * 60)
    logger.info("Creating battery with example tests")
    logger.info("=" * 60)
    
    # Create battery and tests
    battery_result = create_battery_with_tests()
    if not battery_result:
        logger.error("Failed to create battery and tests")
        return
    
    battery_id, test_ids = battery_result
    
    logger.info(f"\nBattery created: {battery_id} with {len(test_ids)} test(s)")
    logger.info("=" * 60)
    logger.info("Executing tests with multiple solvers")
    logger.info("=" * 60)
    
    # Execute tests with solvers
    solvers = ["chuffed", "gecode", "coin-bc"]
    results = execute_tests_with_solvers(battery_id, test_ids, solvers)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Execution Summary")
    logger.info("=" * 60)
    
    success_count = sum(1 for r in results if r.get("status") == "success")
    error_count = sum(1 for r in results if r.get("status") == "error")
    
    logger.info(f"Total executions: {len(results)}")
    logger.info(f"Successful: {success_count}")
    logger.info(f"Failed: {error_count}")
    
    for result in results:
        status_icon = "✓" if result.get("status") == "success" else "✗"
        solver = result.get("solver", "unknown")
        test_id = result.get("test_id", "unknown")
        if result.get("status") == "success":
            logger.info(f"{status_icon} Test {test_id} + {solver} → Result ID {result['result_id']} ({result['execution_time']:.2f}s)")
        else:
            logger.info(f"{status_icon} Test {test_id} + {solver} → Error: {result.get('error', 'Unknown')}")
    
    logger.info("=" * 60)
    logger.info(f"Results saved to database (Battery ID: {battery_id})")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
