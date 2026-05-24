"""
Routes para gestionar resultados de ejecución de pruebas.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.db import get_db
from typing import List
from services.resultado import (
    create_or_update_result,
    get_results_by_prueba,
    get_result_by_prueba_and_solver,
    get_results_by_bateria,
    delete_result,
    get_available_solvers,
    get_result_by_id,
    update_result_comment,
)
from serializers.resultado import ResultCreate, ResultOut

import logging
logger = logging.getLogger("uvicorn")

resultadoRouter = APIRouter(prefix="/resultado", tags=["Resultado"])


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


def _serialize_result(result):
    return {
        "id": result.id,
        "prueba_id": result.prueba_id,
        "solver": result.solver,
        "execution_time_seconds": result.execution_time_seconds,
        "charged_stations": result.charged_stations,
        "charging_locations": result.charging_locations,
        "station_vector": _station_vector(result.charging_locations),
        "time_deviation_minutes": result.time_deviation_minutes,
        "bateria": result.bateria,
        "carga": result.carga,
        "comment": getattr(result, "comment", None),
        "timestamp": result.timestamp,
    }


@resultadoRouter.post("/", response_model=ResultOut)
def crear_resultado(resultado: ResultCreate, db: Session = Depends(get_db)):
    """Crea o actualiza un resultado de ejecución (único por prueba+solver)"""
    try:
        result = create_or_update_result(
            db,
            prueba_id=resultado.prueba_id,
            solver=resultado.solver,
            execution_time_seconds=resultado.execution_time_seconds,
            charged_stations=resultado.charged_stations,
            charging_locations=resultado.charging_locations,
            time_deviation_minutes=resultado.time_deviation_minutes,
            bateria=resultado.bateria,
            carga=resultado.carga,
            comment=resultado.comment,
        )
        return _serialize_result(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating resultado: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@resultadoRouter.get("/prueba/{prueba_id}", response_model=List[ResultOut])
def obtener_resultados_prueba(prueba_id: int, db: Session = Depends(get_db)):
    """Obtiene todos los resultados (diferentes solvers) de una prueba"""
    try:
        results = get_results_by_prueba(db, prueba_id)
        return [_serialize_result(result) for result in results]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@resultadoRouter.get("/prueba/{prueba_id}/solver/{solver}", response_model=ResultOut)
def obtener_resultado_prueba_solver(
    prueba_id: int, solver: str, db: Session = Depends(get_db)
):
    """Obtiene el resultado de una prueba con un solver específico"""
    result = get_result_by_prueba_and_solver(db, prueba_id, solver)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No hay resultado para prueba {prueba_id} con solver {solver}",
        )
    return _serialize_result(result)


@resultadoRouter.get("/id/{resultado_id}", response_model=ResultOut)
def obtener_resultado_por_id(resultado_id: int, db: Session = Depends(get_db)):
    result = get_result_by_id(db, resultado_id)
    if not result:
        raise HTTPException(status_code=404, detail="Resultado no encontrado")
    return _serialize_result(result)


@resultadoRouter.get("/bateria/{bateria_id}", response_model=List[ResultOut])
def obtener_resultados_bateria(bateria_id: int, db: Session = Depends(get_db)):
    """Obtiene todos los resultados de todas las pruebas en una batería"""
    try:
        results = get_results_by_bateria(db, bateria_id)
        return [_serialize_result(result) for result in results]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@resultadoRouter.patch("/{resultado_id}/comment", response_model=ResultOut)
def comentar_resultado(resultado_id: int, comment: str | None = None, db: Session = Depends(get_db)):
    try:
        result = update_result_comment(db, resultado_id, comment)
        return _serialize_result(result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@resultadoRouter.delete("/{resultado_id}")
def eliminar_resultado(resultado_id: int, db: Session = Depends(get_db)):
    """Elimina un resultado específico"""
    if not delete_result(db, resultado_id):
        raise HTTPException(status_code=404, detail="Resultado no encontrado")
    return {"message": "Resultado eliminado"}


@resultadoRouter.get("/solvers/available")
def obtener_solvers_disponibles(db: Session = Depends(get_db)):
    """Obtiene la lista de solvers que tienen resultados almacenados"""
    solvers = get_available_solvers(db)
    return {"solvers": solvers}
