"""
Servicios para gestionar resultados de ejecución de pruebas.
Cada resultado representa la ejecución de una prueba con un solver específico.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from model.dataStructure import Result, Prueba
import logging

logger = logging.getLogger("uvicorn")


def create_or_update_result(
    db: Session,
    prueba_id: int,
    solver: str,
    execution_time_seconds: float,
    charged_stations: int,
    charging_locations: dict,
    time_deviation_minutes: float,
    bateria: dict,
    carga: dict,
    comment: str | None = None,
) -> Result:
    """
    Crea o actualiza un resultado para una prueba con un solver específico.
    Debido a la constraint UNIQUE(prueba_id, solver), si ya existe se actualiza.
    """
    prueba = db.query(Prueba).filter(Prueba.id == prueba_id).first()
    if not prueba:
        raise ValueError(f"Prueba con id {prueba_id} no encontrada")

    # Intentar actualizar si existe
    result = db.query(Result).filter(
        Result.prueba_id == prueba_id,
        Result.solver == solver
    ).first()

    if result:
        # Actualizar resultado existente
        result.execution_time_seconds = execution_time_seconds
        result.charged_stations = charged_stations
        result.charging_locations = charging_locations
        result.time_deviation_minutes = time_deviation_minutes
        result.bateria = bateria
        result.carga = carga
        result.comment = comment
    else:
        # Crear nuevo resultado
        result = Result(
            prueba_id=prueba_id,
            solver=solver,
            execution_time_seconds=execution_time_seconds,
            charged_stations=charged_stations,
            charging_locations=charging_locations,
            time_deviation_minutes=time_deviation_minutes,
            bateria=bateria,
            carga=carga,
            comment=comment,
        )
        db.add(result)

    try:
        db.commit()
        db.refresh(result)
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError: {e}")
        raise ValueError(f"Error al guardar resultado: {str(e)}")

    return result


def get_results_by_prueba(db: Session, prueba_id: int) -> list[Result]:
    """Obtiene todos los resultados (solvers) de una prueba."""
    prueba = db.query(Prueba).filter(Prueba.id == prueba_id).first()
    if not prueba:
        raise ValueError(f"Prueba con id {prueba_id} no encontrada")

    return db.query(Result).filter(Result.prueba_id == prueba_id).all()


def get_result_by_prueba_and_solver(
    db: Session, prueba_id: int, solver: str
) -> Result | None:
    """Obtiene el resultado específico de una prueba con un solver."""
    return db.query(Result).filter(
        Result.prueba_id == prueba_id,
        Result.solver == solver
    ).first()


def get_result_by_id(db: Session, result_id: int) -> Result | None:
    return db.query(Result).filter(Result.id == result_id).first()


def update_result_comment(db: Session, result_id: int, comment: str | None) -> Result:
    result = get_result_by_id(db, result_id)
    if not result:
        raise ValueError(f"Resultado con id {result_id} no encontrado")

    result.comment = comment
    db.commit()
    db.refresh(result)
    return result


def get_results_by_bateria(db: Session, bateria_id: int) -> list[Result]:
    """Obtiene todos los resultados (todos los solvers) de todas las pruebas en una batería."""
    from model.dataStructure import Bateria

    bateria = db.query(Bateria).filter(Bateria.id == bateria_id).first()
    if not bateria:
        raise ValueError(f"Batería con id {bateria_id} no encontrada")

    # Obtener todos los resultados de las pruebas en la batería
    results = db.query(Result).join(Prueba).filter(
        Prueba.bateria_id == bateria_id
    ).all()

    return results


def delete_result(db: Session, result_id: int) -> bool:
    """Elimina un resultado."""
    result = db.query(Result).filter(Result.id == result_id).first()
    if not result:
        return False

    db.delete(result)
    db.commit()
    return True


def get_available_solvers(db: Session) -> list[str]:
    """Obtiene la lista de solvers que tienen resultados en la BD."""
    results = db.query(Result.solver).distinct().all()
    return [r[0] for r in results] if results else []
