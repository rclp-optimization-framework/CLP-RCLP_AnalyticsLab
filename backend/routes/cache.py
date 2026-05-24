from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.db import get_db
from model.dataStructure import Cache
from serializers.cache import PostBateriaList, CacheCreate, CacheOut
from services.cache import (
    create_or_update_cache,
    get_optimal_solutions_for_bateria,
    get_cache_by_prueba,
    get_cache_by_id,
    get_cache_by_bateria,
    get_cache_records_by_bateria,
    list_cache_grouped_all_baterias,
    get_subsolutions_by_bateria,
    get_cache_stats_for_bateria,
    generate_graph_data,
    generate_graph_data_metrics,
    generate_graph_data_results_pruebas_in_bateria,
    get_cache_by_prueba_and_solver,
    update_cache_comment,
    delete_cache,
    get_available_solvers,
    get_all_solvers_by_test_in_battery,
    get_test_statistics,
    get_solver_stations_info_by_test,
)

cacheRouter = APIRouter(prefix="/cache", tags=["Cache"])


def _station_vector(charging_locations):
    if isinstance(charging_locations, list) and charging_locations:
        if all(isinstance(item, int) for item in charging_locations):
            return [int(item) for item in charging_locations]
        if all(isinstance(item, dict) for item in charging_locations):
            vector = []
            for item in charging_locations:
                if "active" in item:
                    vector.append(1 if item.get("active") else 0)
                elif "station" in item:
                    vector.append(int(item.get("station", 0)))
            return vector
    return []


def _serialize_cache(cache_entry):
    return {
        "id": cache_entry.id,
        "prueba_id": cache_entry.prueba_id,
        "solver": cache_entry.solver,
        "execution_time_seconds": cache_entry.execution_time_seconds,
        "charged_stations": cache_entry.charged_stations,
        "charging_locations": cache_entry.charging_locations,
        "station_vector": _station_vector(cache_entry.charging_locations),
        "time_deviation_minutes": cache_entry.time_deviation_minutes,
        "bateria": cache_entry.bateria,
        "carga": cache_entry.carga,
        "comment": getattr(cache_entry, "comment", None),
        "timestamp": cache_entry.timestamp,
    }

@cacheRouter.post("/bateria/{bateria_id}")
def create_cache(bateria_id: int, db: Session = Depends(get_db)):
    try:
        resultados = get_optimal_solutions_for_bateria(db, bateria_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron pruebas para la batería")

    return resultados


@cacheRouter.post("/", response_model=CacheOut)
def create_cache_entry(cache: CacheCreate, db: Session = Depends(get_db)):
    try:
        cache_entry = create_or_update_cache(
            db,
            prueba_id=cache.prueba_id,
            solver=cache.solver,
            execution_time_seconds=cache.execution_time_seconds,
            charged_stations=cache.charged_stations,
            charging_locations=cache.charging_locations,
            time_deviation_minutes=cache.time_deviation_minutes,
            bateria=cache.bateria,
            carga=cache.carga,
            comment=cache.comment,
        )
        return _serialize_cache(cache_entry)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@cacheRouter.get("/bateria/subsolutions/{bateria_id}") 
def return_subsolutions_by_bateria(bateria_id: int, max_solutions: int = 5, db: Session = Depends(get_db)):
    try:
        subsolutions = get_subsolutions_by_bateria(db, bateria_id, max_solutions)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    if not subsolutions:
        raise HTTPException(status_code=404,detail="No se encontraron resultados para la batería")
    return subsolutions

@cacheRouter.get("/prueba/{prueba_id}")
def read_cache_by_prueba(prueba_id: int, db: Session = Depends(get_db)):
    cache = get_cache_by_prueba(db, prueba_id)
    if not cache:
        raise HTTPException(status_code=404, detail="Cache no encontrado para la prueba")
    return _serialize_cache(cache)


@cacheRouter.get("/prueba/{prueba_id}/solver/{solver}", response_model=CacheOut)
def read_cache_by_prueba_and_solver(prueba_id: int, solver: str, db: Session = Depends(get_db)):
    cache_entry = get_cache_by_prueba_and_solver(db, prueba_id, solver)
    if not cache_entry:
        raise HTTPException(
            status_code=404,
            detail=f"No hay cache para la prueba {prueba_id} con solver {solver}",
        )
    return _serialize_cache(cache_entry)

@cacheRouter.get("/id/{cache_id}", response_model=CacheOut)
def read_cache_by_id(cache_id: int, db: Session = Depends(get_db)):
    cache = get_cache_by_id(db, cache_id)
    if not cache:
        raise HTTPException(status_code=404, detail="Cache no encontrado")
    return _serialize_cache(cache)

@cacheRouter.get("/{cache_id}", response_model=CacheOut)
def read_cache_by_id_alias(cache_id: int, db: Session = Depends(get_db)):
    return read_cache_by_id(cache_id, db)


@cacheRouter.get("/bateria/{bateria_id}", response_model=list[CacheOut])
def read_cache_by_bateria(bateria_id: int, db: Session = Depends(get_db)):
    caches = get_cache_records_by_bateria(db, bateria_id)
    if not caches:
        raise HTTPException(status_code=404, detail="No se encontraron cache entries para la batería")
    return [_serialize_cache(cache_entry) for cache_entry in caches]

@cacheRouter.get("/")
def list_cache(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    caches = list_cache_grouped_all_baterias(db, skip=skip, limit=limit)
    if not caches:
        raise HTTPException(status_code=404, detail="No se encontraron cache entries para la batería")
    return caches


@cacheRouter.patch("/{cache_id}/comment", response_model=CacheOut)
def comment_cache(cache_id: int, comment: str | None = None, db: Session = Depends(get_db)):
    try:
        cache_entry = update_cache_comment(db, cache_id, comment)
        return _serialize_cache(cache_entry)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@cacheRouter.delete("/{cache_id}")
def remove_cache(cache_id: int, db: Session = Depends(get_db)):
    if not delete_cache(db, cache_id):
        raise HTTPException(status_code=404, detail="Cache no encontrado")
    return {"message": "Cache eliminado"}


@cacheRouter.get("/solvers/available")
def read_available_solvers(db: Session = Depends(get_db)):
    return {"solvers": get_available_solvers(db)}

@cacheRouter.get("/bateria/stats/{bateria_id}")
def read_cache_stats_for_bateria(bateria_id: int, db: Session = Depends(get_db)):
    caches = get_cache_stats_for_bateria(db, bateria_id)
    if not caches:
        raise HTTPException(status_code=404, detail="No se encontraron resultados para la batería")
    return caches

@cacheRouter.post("/bateria/stats")
def read_bateria_ids_for_graph_data(data: PostBateriaList, db: Session = Depends(get_db)):
    if not data.baterias:
        raise HTTPException(status_code=400, detail="No se enviaron las baterias correspondientes")

    if len(data.baterias) == 1:
        raise HTTPException(status_code=400, detail="Solo un id fue enviado")

    try:
        graph_stats = generate_graph_data(db, data.baterias)
        return graph_stats
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@cacheRouter.post("/bateria/stats/{metric}")
def read_bateria_ids_for_graph_data_withMetric(data: PostBateriaList, metric: int, db: Session = Depends(get_db)):
    if not data.baterias:
        raise HTTPException(status_code=400, detail="No se enviaron las baterias correspondientes")

    if len(data.baterias) == 1:
        raise HTTPException(status_code=400, detail="Solo un id fue enviado")

    try:
        graph_stats = generate_graph_data_metrics(db, data.baterias, metric)
        return graph_stats
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@cacheRouter.get("/bateria/graph/{bateria_id}")
def read_cache_times_for_bateria(bateria_id: int, db: Session = Depends(get_db)):
    try:
        caches = generate_graph_data_results_pruebas_in_bateria(db, bateria_id)
        return caches
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# NUEVAS RUTAS PARA ESTADÍSTICAS POR PRUEBA
@cacheRouter.get("/test/{test_id}/all-solvers")
def read_all_solvers_for_test(test_id: int, db: Session = Depends(get_db)):
    """Retorna TODOS los solvers para una prueba específica con toda la información."""
    try:
        solvers_data = []
        caches = db.query(Cache).filter(Cache.prueba_id == test_id).all()
        
        if not caches:
            raise HTTPException(status_code=404, detail="No hay datos para esta prueba")
        
        for cache in sorted(caches, key=lambda c: c.time_deviation_minutes):
            solvers_data.append({
                'id': cache.id,
                'solver': cache.solver,
                'execution_time_seconds': cache.execution_time_seconds,
                'time_deviation_minutes': cache.time_deviation_minutes,
                'charged_stations': cache.charged_stations,
                'charging_locations': cache.charging_locations,
                'bateria': cache.bateria,
                'carga': cache.carga,
                'comment': cache.comment,
            })
        
        return solvers_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@cacheRouter.get("/test/{test_id}/statistics")
def read_test_statistics(test_id: int, db: Session = Depends(get_db)):
    """Retorna estadísticas específicas de una prueba."""
    try:
        stats = get_test_statistics(db, test_id)
        if not stats:
            raise HTTPException(status_code=404, detail="No hay datos para esta prueba")
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@cacheRouter.get("/test/{test_id}/stations-info")
def read_solver_stations_info(test_id: int, db: Session = Depends(get_db)):
    """Retorna información de estaciones para cada solver en una prueba."""
    try:
        info = get_solver_stations_info_by_test(db, test_id)
        if not info:
            raise HTTPException(status_code=404, detail="No hay datos para esta prueba")
        return info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@cacheRouter.get("/battery/{battery_id}/all-tests-with-solvers")
def read_all_solvers_by_battery(battery_id: int, db: Session = Depends(get_db)):
    """Retorna TODOS los solvers agrupados por prueba para una batería."""
    try:
        all_data = get_all_solvers_by_test_in_battery(db, battery_id)
        if not all_data:
            raise HTTPException(status_code=404, detail="No hay datos para esta batería")
        return all_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
