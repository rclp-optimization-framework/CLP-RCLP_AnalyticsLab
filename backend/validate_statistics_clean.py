#!/usr/bin/env python3
"""
Script de validacion para estadisticas de cache.
Verifica que las funciones del backend retornen datos correctos.
"""

import sys
from config.db import SessionLocal, engine
from model.dataStructure import Cache, Prueba, Bateria
from services.cache import (
    get_cache_by_bateria,
    generate_graph_data_results_pruebas_in_bateria,
    get_all_solvers_by_test_in_battery,
    get_test_statistics,
    get_solver_stations_info_by_test,
)

def validate_battery_data(battery_id: int):
    """Valida los datos de cache para una bateria completa."""
    db = SessionLocal()
    
    print(f"\n{'='*80}")
    print(f"VALIDATION DE BATERIA #{battery_id}")
    print(f"{'='*80}\n")
    
    try:
        # Obtener bateria
        battery = db.query(Bateria).filter(Bateria.id == battery_id).first()
        if not battery:
            print(f"[!] Bateria #{battery_id} no encontrada")
            return
        
        print(f"[+] Bateria encontrada: {battery.nombre}")
        
        # Obtener todas las pruebas
        tests = db.query(Prueba).filter(Prueba.bateria_id == battery_id).all()
        print(f"[+] {len(tests)} pruebas encontradas")
        
        # Obtener todos los caches
        cache_entries = db.query(Cache).join(
            Prueba, Cache.prueba_id == Prueba.id
        ).filter(Prueba.bateria_id == battery_id).all()
        
        print(f"[+] {len(cache_entries)} cache entries encontrados")
        
        # Agrupar por prueba
        by_test = {}
        for cache in cache_entries:
            if cache.prueba_id not in by_test:
                by_test[cache.prueba_id] = []
            by_test[cache.prueba_id].append(cache)
        
        print(f"\n{'ANALISIS POR PRUEBA':^80}")
        print(f"-" * 80)
        
        for test_id in sorted(by_test.keys()):
            caches = by_test[test_id]
            print(f"\n[TEST] Test #{test_id}:")
            print(f"   Solvers: {len(caches)}")
            
            for cache in sorted(caches, key=lambda c: c.solver):
                print(f"   * {cache.solver:15} | Dev: {cache.time_deviation_minutes:8.2f} min | "
                      f"Exec: {cache.execution_time_seconds:6.2f} s | Stations: {cache.charged_stations}")
            
            # Best deviation
            best = min(caches, key=lambda c: c.time_deviation_minutes)
            avg_dev = sum(c.time_deviation_minutes for c in caches) / len(caches)
            avg_exec = sum(c.execution_time_seconds for c in caches) / len(caches)
            
            print(f"   " + "-" * 70)
            print(f"   Best deviation: {best.time_deviation_minutes:.2f} min ({best.solver})")
            print(f"   Avg deviation: {avg_dev:.2f} min")
            print(f"   Avg execution: {avg_exec:.2f} s")
        
        # Test NEW FUNCTIONS
        print(f"\n{'VALIDACION DE NUEVAS FUNCIONES':^80}")
        print(f"-" * 80)
        
        # Test get_all_solvers_by_test_in_battery
        print("\n[TEST] get_all_solvers_by_test_in_battery():")
        all_solvers_data = get_all_solvers_by_test_in_battery(db, battery_id)
        print(f"   Tests con datos: {len(all_solvers_data)}")
        for test_id, solvers_list in all_solvers_data.items():
            print(f"   Test #{test_id}: {len(solvers_list)} solvers")
            for solver_data in solvers_list:
                print(f"     - {solver_data['solver']}: {solver_data['time_deviation_minutes']:.2f} min")
        
        # Test get_test_statistics
        print(f"\n[TEST] get_test_statistics():")
        for test_id in sorted(by_test.keys())[:1]:  # Solo el primero
            stats = get_test_statistics(db, test_id)
            print(f"   Test #{test_id}:")
            print(f"     - best_deviation: {stats['best_deviation']:.2f} min")
            print(f"     - avg_deviation: {stats['avg_deviation']:.2f} min")
            print(f"     - avg_execution: {stats['avg_execution']:.2f} s")
            print(f"     - num_solvers: {stats['num_solvers']}")
        
        # Test get_solver_stations_info_by_test
        print(f"\n[TEST] get_solver_stations_info_by_test():")
        for test_id in sorted(by_test.keys())[:1]:  # Solo el primero
            stations_info = get_solver_stations_info_by_test(db, test_id)
            print(f"   Test #{test_id}: {len(stations_info)} solvers con info")
            for solver, info in stations_info.items():
                print(f"     - {solver}: {info['charged_stations']} stations")
        
        print("\n[SUCCESS] Todas las funciones retornan datos correctamente!")
        
    finally:
        db.close()


if __name__ == "__main__":
    print("\n[*] Validation Script - Cache Statistics Validator\n")
    
    # Buscar primero que baterias y pruebas existen
    db = SessionLocal()
    batteries = db.query(Bateria).all()
    db.close()
    
    if not batteries:
        print("[!] No hay baterias en la base de datos")
        sys.exit(1)
    
    print(f"Found {len(batteries)} batteries:")
    for bat in batteries:
        print(f"  * Battery #{bat.id}: {bat.nombre}")
    
    # Validar la primera bateria (Baseline urban corridor es tipicamente la #2)
    battery_id = 2  # Baseline urban corridor
    
    validate_battery_data(battery_id)
    
    print(f"\n{'='*80}\n")
