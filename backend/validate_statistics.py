#!/usr/bin/env python3
"""
Script de validación para estadísticas de cache.
Verifica que las funciones del backend retornen datos correctos.
"""

import sys
from config.db import SessionLocal, engine
from model.dataStructure import Cache, Prueba, Bateria
from services.cache import (
    get_cache_by_bateria,
    generate_graph_data_results_pruebas_in_bateria,
)

def validate_battery_data(battery_id: int):
    """Valida los datos de cache para una batería completa."""
    db = SessionLocal()
    
    print(f"\n{'='*80}")
    print(f"VALIDACIÓN DE BATERÍA #{battery_id}")
    print(f"{'='*80}\n")
    
    try:
        # Obtener batería
        battery = db.query(Bateria).filter(Bateria.id == battery_id).first()
        if not battery:
            print(f"❌ Batería #{battery_id} no encontrada")
            return
        
        print(f"✓ Batería encontrada: {battery.nombre}")
        
        # Obtener todas las pruebas
        tests = db.query(Prueba).filter(Prueba.bateria_id == battery_id).all()
        print(f"✓ {len(tests)} pruebas encontradas")
        
        # Obtener todos los caches
        cache_entries = db.query(Cache).join(
            Prueba, Cache.prueba_id == Prueba.id
        ).filter(Prueba.bateria_id == battery_id).all()
        
        print(f"✓ {len(cache_entries)} cache entries encontrados")
        
        # Agrupar por prueba
        by_test = {}
        for cache in cache_entries:
            if cache.prueba_id not in by_test:
                by_test[cache.prueba_id] = []
            by_test[cache.prueba_id].append(cache)
        
        print(f"\n{'ANÁLISIS POR PRUEBA':^80}")
        print(f"-" * 80)
        
        for test_id in sorted(by_test.keys()):
            caches = by_test[test_id]
            print(f"\n📊 Test #{test_id}:")
            print(f"   Solvers: {len(caches)}")
            
            for cache in sorted(caches, key=lambda c: c.solver):
                print(f"   • {cache.solver:15} | Dev: {cache.time_deviation_minutes:8.2f} min | "
                      f"Exec: {cache.execution_time_seconds:6.2f} s | Stations: {cache.charged_stations}")
            
            # Best deviation
            best = min(caches, key=lambda c: c.time_deviation_minutes)
            avg_dev = sum(c.time_deviation_minutes for c in caches) / len(caches)
            avg_exec = sum(c.execution_time_seconds for c in caches) / len(caches)
            
            print(f"   ─────────────────────────────────────────────────────────────────")
            print(f"   Best deviation: {best.time_deviation_minutes:.2f} min ({best.solver})")
            print(f"   Avg deviation: {avg_dev:.2f} min")
            print(f"   Avg execution: {avg_exec:.2f} s")
        
        # Validar función actual
        print(f"\n{'VALIDACIÓN DE FUNCIÓN':^80}")
        print(f"-" * 80)
        
        current_result = generate_graph_data_results_pruebas_in_bateria(db, battery_id)
        print(f"\nFunción `generate_graph_data_results_pruebas_in_bateria` retorna:")
        print(f"  - Estructura: {type(current_result)}")
        print(f"  - Pruebas: {len(current_result)}")
        
        for test_id, data in current_result.items():
            print(f"  - Test #{test_id}: {data} (tipo: {type(data)})")
        
        print(f"\n⚠️  PROBLEMA: Retorna solo UNA cache por prueba, debería retornar TODAS")
        print(f"   Comparación:")
        print(f"   - Caches totales en BD: {len(cache_entries)}")
        print(f"   - Items en respuesta: {len(current_result)}")
        
    finally:
        db.close()


def validate_test_details(battery_id: int, test_id: int):
    """Valida los datos específicos de una prueba."""
    db = SessionLocal()
    
    print(f"\n{'='*80}")
    print(f"VALIDACIÓN DE TEST #{test_id} EN BATERÍA #{battery_id}")
    print(f"{'='*80}\n")
    
    try:
        # Obtener prueba
        test = db.query(Prueba).filter(
            Prueba.id == test_id,
            Prueba.bateria_id == battery_id
        ).first()
        
        if not test:
            print(f"❌ Test #{test_id} no encontrado en batería #{battery_id}")
            return
        
        print(f"✓ Test encontrado: {test.num_buses} buses / {test.num_stations} estaciones")
        
        # Obtener todos los caches para esta prueba
        caches = db.query(Cache).filter(Cache.prueba_id == test_id).all()
        print(f"✓ {len(caches)} solvers ejecutados")
        
        if len(caches) == 0:
            print(f"⚠️  NO HAY DATOS PARA ESTA PRUEBA")
            return
        
        print(f"\n{'DETALLE DE SOLVERS':^80}")
        print(f"-" * 80)
        
        solvers_data = {}
        for cache in sorted(caches, key=lambda c: c.time_deviation_minutes):
            print(f"\n🔹 {cache.solver}:")
            print(f"   Execution time: {cache.execution_time_seconds:.2f} s")
            print(f"   Time deviation: {cache.time_deviation_minutes:.2f} min")
            print(f"   Charged stations: {cache.charged_stations}")
            print(f"   Station vector: {cache.charging_locations[:5] if cache.charging_locations else 'N/A'}...")
            
            solvers_data[cache.solver] = {
                'exec_time': cache.execution_time_seconds,
                'deviation': cache.time_deviation_minutes,
                'stations': cache.charged_stations,
                'locations': cache.charging_locations
            }
        
        # Estadísticas
        print(f"\n{'ESTADÍSTICAS PARA ESTA PRUEBA':^80}")
        print(f"-" * 80)
        
        deviations = [c.time_deviation_minutes for c in caches]
        exec_times = [c.execution_time_seconds for c in caches]
        
        print(f"Best deviation: {min(deviations):.2f} min")
        print(f"Worst deviation: {max(deviations):.2f} min")
        print(f"Avg deviation: {sum(deviations)/len(deviations):.2f} min")
        print(f"Avg execution: {sum(exec_times)/len(exec_times):.2f} s")
        
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🔍 VALIDADOR DE ESTADÍSTICAS - Cache Statistics Validator\n")
    
    # Buscar primero qué baterías y pruebas existen
    db = SessionLocal()
    batteries = db.query(Bateria).all()
    db.close()
    
    if not batteries:
        print("❌ No hay baterías en la base de datos")
        sys.exit(1)
    
    print(f"Found {len(batteries)} batteries:")
    for bat in batteries:
        print(f"  • Battery #{bat.id}: {bat.nombre}")
    
    # Validar la primera batería (Baseline urban corridor es típicamente la #2)
    battery_id = 2  # Baseline urban corridor
    
    validate_battery_data(battery_id)
    
    # Validar un test específico
    db = SessionLocal()
    tests = db.query(Prueba).filter(Prueba.bateria_id == battery_id).all()
    db.close()
    
    if tests:
        test_id = tests[0].id
        validate_test_details(battery_id, test_id)
    
    print(f"\n{'='*80}\n")
