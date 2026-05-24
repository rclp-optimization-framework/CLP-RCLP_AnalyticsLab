from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from config.db import get_db
from typing import List
from services.bateria import (
    create_bateria, get_all_baterias, get_bateria_by_nombre, 
    get_bateria_by_fecha, get_bateria_by_id, add_prueba_to_bateria,
    add_pruebas_to_bateria, get_pruebas_of_bateria
    )
from services.cache import get_cache_records_by_bateria
from serializers.bateria import BateriaCreate
from serializers.prueba import PruebaCreateAux, ListPruebaCreateAux, PruebaOut
from utils.dzn_parser import parse_dzn_to_test_input
import json
import logging

logger = logging.getLogger("uvicorn")

bateriaRouter = APIRouter(prefix="/bateria", tags=["Bateria"])

@bateriaRouter.post("/")
def crear_bateria(bateria: BateriaCreate, db: Session = Depends(get_db)):
    pruebas = bateria.pruebas
    
    try:
        if not pruebas:
            bateria = create_bateria(db, bateria.nombre)
        else:
            bateria = create_bateria(db, bateria.nombre, pruebas.pruebas)

        return {"id": bateria.id, "nombre": bateria.nombre}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@bateriaRouter.get("/nombre/{nombre}")
def buscar_bateria_nombre(nombre: str, db: Session = Depends(get_db)):
    return get_bateria_by_nombre(db, nombre)

@bateriaRouter.get("/all")
def buscar_todas_baterias(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_all_baterias(db, skip=skip, limit=limit)

### tira lista vacia si no encontro
@bateriaRouter.get("/fecha/{fecha}")
def buscar_bateria_fecha(fecha: str, db: Session = Depends(get_db)):
    try:
        return get_bateria_by_fecha(db, fecha)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@bateriaRouter.get("/{id}")
def buscar_bateria_id(id: int, db: Session = Depends(get_db)):
    bateria = get_bateria_by_id(db, id)
    if not bateria:
        raise HTTPException(status_code=404, detail="Bateria no encontrada")
    return bateria

@bateriaRouter.delete("/{id}")
def eliminar_bateria(id: int, db: Session = Depends(get_db)):
    bateria = get_bateria_by_id(db, id)
    if not bateria:
        raise HTTPException(status_code=404, detail="Bateria no encontrada")
    
    db.delete(bateria)
    db.commit()
    return {"message": "Bateria eliminada"}

@bateriaRouter.put("/{id}")
def actualizar_bateria(id: int, nombre: str, db: Session = Depends(get_db)):
    bateria = get_bateria_by_id(db, id)
    if not bateria:
        raise HTTPException(status_code=404, detail="Bateria no encontrada")
    
    bateria.nombre = nombre
    db.commit()
    db.refresh(bateria)
    return bateria

@bateriaRouter.post("/prueba/add/{bateria_id}")
def create_prueba_in_bateria(bateria_id: int, data: PruebaCreateAux, db: Session = Depends(get_db)):
    try:
        prueba = add_prueba_to_bateria(db, bateria_id, data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not prueba:
        raise HTTPException(status_code=500, detail="No se pudo crear la prueba")
    return prueba

@bateriaRouter.post("/prueba/many/{bateria_id}", response_model=List[PruebaOut])
def create_pruebas_in_baterias(bateria_id: int, data: ListPruebaCreateAux, db: Session = Depends(get_db)):
    try:
        pruebas = add_pruebas_to_bateria(db, bateria_id, data.pruebas)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not pruebas:
        raise HTTPException(status_code=500, detail="No se pudo crear la prueba")
    return pruebas

@bateriaRouter.get("/prueba/{bateria_id}")
def read_pruebas_of_bateria(bateria_id: int, db: Session = Depends(get_db), skip: int = 0, limit: int = 10 ): 
    bateria = get_bateria_by_id(db, bateria_id)
    if not bateria:
        raise HTTPException(status_code=404, detail="Bateria no encontrada")

    pruebas = get_pruebas_of_bateria(db, bateria_id, skip, limit)
    if not pruebas:
        return []

    # Normalizar campos que pueden venir como scalars o strings desde la BD
    import json as _json
    def ensure_list(value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, (int, float, str)):
            if isinstance(value, str):
                try:
                    parsed = _json.loads(value)
                    if isinstance(parsed, list):
                        return parsed
                except Exception:
                    pass
            return [value]
        return value

    def ensure_list_of_lists(value):
        """Ensure value is a list of lists. If it's a list of scalars, wrap each scalar into a list."""
        if value is None:
            return []
        if isinstance(value, str):
            try:
                parsed = _json.loads(value)
                value = parsed
            except Exception:
                # fallback: wrap string
                return [[value]]

        if isinstance(value, list):
            # if elements are lists, assume ok
            if all(isinstance(el, list) for el in value):
                return value
            # if elements are scalars, wrap each
            return [[el] if not isinstance(el, list) else el for el in value]
        # scalar -> wrap twice
        if isinstance(value, (int, float)):
            return [[value]]
        return [[value]]

    normalized = []
    for p in pruebas:
        normalized.append({
            "id": p.id,
            "bateria_id": p.bateria_id,
            "num_buses": p.num_buses,
            "num_stations": p.num_stations,
            "max_stops": p.max_stops if p.max_stops is not None else 0,
            "num_stops": ensure_list(p.num_stops),
            "st_bi": ensure_list_of_lists(p.st_bi),
            "d": ensure_list_of_lists(p.d),
            "t": ensure_list_of_lists(p.t),
            "tau_bi": ensure_list_of_lists(p.tau_bi),
            "consumo_max": p.consumo_max if p.consumo_max is not None else 0,
            "consumo_min": p.consumo_min if p.consumo_min is not None else 0,
            "alpha": p.alpha if p.alpha is not None else 0.0,
            "mu": p.mu if p.mu is not None else 0.0,
            "sm": p.sm if p.sm is not None else 0,
            "psi": p.psi if p.psi is not None else 0.0,
            "beta": p.beta if p.beta is not None else 0.0,
            "m": p.m if p.m is not None else 0,
            "timestamp": p.timestamp.isoformat() if p.timestamp is not None else None,
        })

    return normalized


@bateriaRouter.post("/upload/tests/{bateria_id}")
async def upload_tests_file(
    bateria_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload JSON or DZN file with test cases to a battery.
    Supports:
    - JSON: Array of test objects or single test object
    - DZN: MiniZinc data format
    """
    try:
        # Verify battery exists
        bateria = get_bateria_by_id(db, bateria_id)
        if not bateria:
            raise HTTPException(status_code=404, detail="Bateria no encontrada")

        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')

        # Determine file type and parse
        if file.filename and file.filename.endswith('.dzn'):
            # Parse DZN format
            test_data = parse_dzn_to_test_input(content_str)
            tests_list = [test_data]  # Wrap in list for consistency
        elif file.filename and file.filename.endswith('.json'):
            # Parse JSON format
            data = json.loads(content_str)
            tests_list = data if isinstance(data, list) else [data]
        else:
            raise HTTPException(status_code=400, detail="File must be .json or .dzn")

        # Add tests to battery (be permissive: create_prueba will generate missing details when possible)
        created_tests = []
        for test_data in tests_list:
            try:
                prueba = add_prueba_to_bateria(db, bateria_id, test_data)
                created_tests.append(prueba)
            except ValueError as e:
                logger.error(f"Error creating test for battery {bateria_id}: {e}")
                raise HTTPException(status_code=400, detail=str(e))

        # Normalize created tests for response
        def ensure_list(value):
            if value is None:
                return []
            if isinstance(value, list):
                return value
            if isinstance(value, (int, float, str)):
                try:
                    parsed = json.loads(value) if isinstance(value, str) else None
                    if isinstance(parsed, list):
                        return parsed
                except Exception:
                    pass
                return [value]
            return value

        def ensure_list_of_lists(value):
            if value is None:
                return []
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                    value = parsed
                except Exception:
                    return [[value]]
            if isinstance(value, list):
                if all(isinstance(el, list) for el in value):
                    return value
                return [[el] if not isinstance(el, list) else el for el in value]
            if isinstance(value, (int, float)):
                return [[value]]
            return [[value]]

        resp = []
        for p in created_tests:
            resp.append({
                "id": p.id,
                "bateria_id": p.bateria_id,
                "num_buses": p.num_buses,
                "num_stations": p.num_stations,
                "max_stops": p.max_stops if p.max_stops is not None else 0,
                "num_stops": ensure_list(p.num_stops),
                "st_bi": ensure_list_of_lists(p.st_bi),
                "d": ensure_list_of_lists(p.d),
                "t": ensure_list_of_lists(p.t),
                "tau_bi": ensure_list_of_lists(p.tau_bi),
                "consumo_max": p.consumo_max if p.consumo_max is not None else 0,
                "consumo_min": p.consumo_min if p.consumo_min is not None else 0,
                "alpha": p.alpha if p.alpha is not None else 0.0,
                "mu": p.mu if p.mu is not None else 0.0,
                "sm": p.sm if p.sm is not None else 0,
                "psi": p.psi if p.psi is not None else 0.0,
                "beta": p.beta if p.beta is not None else 0.0,
                "m": p.m if p.m is not None else 0,
                "timestamp": p.timestamp.isoformat() if p.timestamp is not None else None,
            })

        logger.info(f"Uploaded {len(resp)} tests to battery {bateria_id}")
        return resp

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Parse error: {str(e)}")
    except Exception as e:
        logger.error(f"Error uploading tests: {e}")
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


@bateriaRouter.get("/{bateria_id}/summary")
def battery_summary(bateria_id: int, db: Session = Depends(get_db)):
    bateria = get_bateria_by_id(db, bateria_id)
    if not bateria:
        raise HTTPException(status_code=404, detail="Bateria no encontrada")

    tests = get_pruebas_of_bateria(db, bateria_id, 0, 1000)
    results = get_cache_records_by_bateria(db, bateria_id)

    return {
        "id": bateria.id,
        "nombre": bateria.nombre,
        "timestamp": bateria.timestamp.isoformat() if bateria.timestamp else None,
        "test_count": len(tests),
        "result_count": len(results),
    }
