"""
Routes para ejecución de pruebas con solvers específicos.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.db import get_db
from typing import List, Any
from pydantic import BaseModel
import minizinc
from services.prueba import get_prueba_by_id
from services.cache import create_or_update_cache
from services.bus_model import solve_bus_model_optimal
import logging

logger = logging.getLogger("uvicorn")

ejecucionRouter = APIRouter(prefix="/ejecucion", tags=["Ejecucion"])


class EjecucionRequest(BaseModel):
    """Solicitud para ejecutar pruebas con solvers específicos"""
    bateria_id: int
    prueba_ids: List[int]  # IDs de pruebas a ejecutar ([] = todas)
    solvers: List[str]      # Solvers a usar


class EjecucionResponse(BaseModel):
    """Respuesta con resultados de ejecución"""
    prueba_id: int
    solver: str
    success: bool
    error: str | None = None
    result_id: int | None = None
    station_vector: list[int] | None = None
    execution_time_seconds: float | None = None
    time_deviation_minutes: float | None = None
    charged_stations: int | None = None


@ejecucionRouter.post("/ejecutar", response_model=List[EjecucionResponse])
def ejecutar_pruebas(
    request: EjecucionRequest,
    db: Session = Depends(get_db),
):
    """
    Ejecuta pruebas con solvers específicos y almacena resultados.
    
    - bateria_id: ID de la batería (para referencia)
    - prueba_ids: IDs de pruebas a ejecutar (vacío = todas en la batería)
    - solvers: Lista de solvers a usar
    """
    from model.dataStructure import Prueba, Bateria
    
    # Validar batería existe
    bateria = db.query(Bateria).filter(Bateria.id == request.bateria_id).first()
    if not bateria:
        raise HTTPException(status_code=404, detail="Batería no encontrada")

    # Map short solver names from client to available MiniZinc solver keys.
    available_map = minizinc.default_driver.available_solvers()

    def find_solver_key(short_name: str) -> str | None:
        for key in available_map.keys():
            if short_name.lower() in key.lower() or short_name.lower() == key.lower():
                return key
        return None

    solver_key_map: dict[str, str] = {}
    for solver in request.solvers:
        key = find_solver_key(solver)
        if not key:
            raise HTTPException(
                status_code=400,
                detail=f"Solver '{solver}' no disponible. Disponibles: {list(available_map.keys())}"
            )
        solver_key_map[solver] = key

    # Obtener pruebas a ejecutar
    if not request.prueba_ids:
        # Todas las pruebas de la batería
        pruebas = db.query(Prueba).filter(Prueba.bateria_id == request.bateria_id).all()
    else:
        # Pruebas específicas
        pruebas = db.query(Prueba).filter(
            (Prueba.bateria_id == request.bateria_id) &
            (Prueba.id.in_(request.prueba_ids))
        ).all()

    if not pruebas:
        raise HTTPException(status_code=404, detail="No hay pruebas para ejecutar")

    resultados = []

    # Ejecutar cada prueba con cada solver
    for prueba in pruebas:
        for solver in request.solvers:
            try:
                logger.info(f"Ejecutando prueba {prueba.id} con solver {solver}")

                # Preparar parámetros de la prueba
                params = {
                    "num_buses": prueba.num_buses,
                    "num_stations": prueba.num_stations,
                    "max_stops": prueba.max_stops,
                    "num_stops": prueba.num_stops,
                    "st_bi": prueba.st_bi,
                    "d": prueba.d,
                    "t": prueba.t,
                    "tau_bi": prueba.tau_bi,
                    "consumo_max": prueba.consumo_max,
                    "consumo_min": prueba.consumo_min,
                    "alpha": prueba.alpha,
                    "mu": prueba.mu,
                    "sm": prueba.sm,
                    "psi": prueba.psi,
                    "beta": prueba.beta,
                    "m": prueba.m,
                }

                real_solver_key = solver_key_map.get(solver, solver)
                result = solve_bus_model_optimal(params=params, solver_name=real_solver_key)

                # Guardar resultado
                saved_result = create_or_update_cache(
                    db=db,
                    prueba_id=prueba.id,
                    solver=solver,
                    execution_time_seconds=result["execution_time_seconds"],
                    charged_stations=result["charged_stations"],
                    charging_locations=result["charging_locations"],
                    time_deviation_minutes=result["time_deviation_minutes"],
                    bateria=result["bateria"],
                    carga=result["carga"],
                )

                resultados.append(EjecucionResponse(
                    prueba_id=prueba.id,
                    solver=solver,
                    success=True,
                    result_id=saved_result.id,
                    station_vector=result.get("station_vector"),
                    execution_time_seconds=result.get("execution_time_seconds"),
                    time_deviation_minutes=result.get("time_deviation_minutes"),
                    charged_stations=result.get("charged_stations"),
                ))

            except Exception as e:
                logger.error(f"Error ejecutando prueba {prueba.id} con {solver}: {e}")
                resultados.append(EjecucionResponse(
                    prueba_id=prueba.id,
                    solver=solver,
                    success=False,
                    error=str(e),
                ))

    return resultados


@ejecucionRouter.get("/solvers")
def obtener_solvers_disponibles():
    """Obtiene la lista de solvers disponibles en MiniZinc"""
    try:
        available = minizinc.default_driver.available_solvers()

        # We only expose a fixed, whitelisted set of solvers (short names).
        # Map these short names to any matching available solver key.
        desired = {
            'chuffed': ['chuffed', 'org.chuffed.chuffed'],
            'coin-bc': ['coin-bc', 'coinbc', 'osicbc', 'org.minizinc.mip.coin-bc'],
            'gurobi': ['gurobi', 'org.minizinc.mip.gurobi'],
            'cplex': ['cplex', 'org.minizinc.mip.cplex'],
            'gecode': ['gecode', 'org.gecode.gecode'],
            'or-tools': ['or-tools', 'cp-sat', 'org.minizinc.mip.cp-sat', 'org.minizinc.mip.scip']
        }

        available_keys = list(available.keys())
        chosen: list[str] = []

        for short, aliases in desired.items():
            found = None
            for key in available_keys:
                for alias in aliases:
                    if alias.lower() in key.lower():
                        found = key
                        break
                if found:
                    break
            if found:
                # Expose the short, user-friendly name (short) so UI shows clean labels.
                chosen.append(short)

        return {"solvers": chosen}
    except Exception as e:
        logger.error(f"Error obteniendo solvers: {e}")
        raise HTTPException(status_code=500, detail=str(e))
