from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.db import get_db
import minizinc
import traceback
from services.prueba import (
    create_prueba, get_all_pruebas, get_pruebas_by_fecha, 
    get_prueba_by_id, get_pruebas_by_num_buses, get_pruebas_by_num_stations, 
    quick_prove, get_pruebas_by_stations_buses, get_subsolutions_quick_prueba,
    get_subsolutions_by_prueba, delete_prueba, update_prueba_by_id
    )

from serializers.prueba import PruebaCreate, PruebaCreateAux, PruebaUpdate

pruebaRouter = APIRouter(prefix="/prueba", tags=["Prueba"])

"""
#@pruebaRouter.post("/")
def crear_prueba(data: PruebaCreate, db: Session = Depends(get_db)):
    try:
        prueba = create_prueba(db, data.bateria_id, data.data.model_dump())

        return prueba
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
"""    

@pruebaRouter.post("/rapida")
def prueba_rapida(data: PruebaCreateAux, solver: str, db: Session = Depends(get_db)):
    try:
        result = quick_prove(data.model_dump(), solver)

        if solver not in minizinc.default_driver.available_solvers().keys():
            raise HTTPException(status_code=400, detail="Solver no disponible")
        
        if not result:
            raise HTTPException(status_code=201, detail="Error de compilación")

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@pruebaRouter.post("/rapida/subsolutions/{max_solutions}")
async def crear_prueba_subsoluciones(data: PruebaCreateAux, solver: str = "gecode", max_solutions:int = 5):
    try:
        result = await get_subsolutions_quick_prueba(data.model_dump(), solver, max_solutions) #get_subsolutions_quick_prueba(data.model_dump(), solver, max_solutions)

        if solver not in minizinc.default_driver.available_solvers().keys():
            raise HTTPException(status_code=400, detail="Solver no disponible")
        
        if not result:
            raise HTTPException(status_code=201, detail="Error de compilación")
        
        if max_solutions <= 0:
            raise HTTPException(status_code=201, detail="La cantidad maxima de soluciones no puede ser menor o igual a 0")

        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    
@pruebaRouter.get("/value/{stations}/{buses}")
def read_pruebas_by_stations_buses(stations: int, buses: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):

    if not stations or not buses:
        raise HTTPException(status_code=400, detail="numero de estaciones y buses no enviado")
    
    pruebas = get_pruebas_by_stations_buses(db, stations, buses, skip, limit)

    if not pruebas:
        raise HTTPException(status_code=404,detail="pruebas nos encontradas")
    
    return pruebas

@pruebaRouter.get("/all")
def buscar_todas_pruebas(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_all_pruebas(db, skip=skip, limit=limit)

@pruebaRouter.get("/fecha/{fecha}")
def buscar_pruebas_fecha(fecha: str, db: Session = Depends(get_db)):
    return get_pruebas_by_fecha(db, fecha)

@pruebaRouter.get("/{id}")
def buscar_prueba_id(id: int, db: Session = Depends(get_db)):
    prueba = get_prueba_by_id(db, id)
    if not prueba:
        raise HTTPException(status_code=404, detail="Prueba no encontrada")
    return prueba


@pruebaRouter.put("/{id}")
def actualizar_prueba(id: int, data: PruebaUpdate, db: Session = Depends(get_db)):
    try:
        return update_prueba_by_id(db, id, data.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@pruebaRouter.get("/num_buses/{num}")
def buscar_pruebas_stations_buses(num: int, db: Session = Depends(get_db)):
    return get_pruebas_by_num_buses(db, num)

@pruebaRouter.get("/num_stations/{num}")
def buscar_pruebas_stations_buses(num: int, db: Session = Depends(get_db)):
    return get_pruebas_by_num_stations(db, num)

@pruebaRouter.get("/subsolutions/{prueba_id}")
def read_subsolutions_by_prueba(prueba_id: int, solver: str = "gecode", max_solutions: int = 5, db: Session = Depends(get_db)):
    
    if not prueba_id:
        raise HTTPException(status_code=400, detail="no se ha enviado el identificador de la prueba")
    
    try:
        subsolutions = get_subsolutions_by_prueba(db, prueba_id, solver, max_solutions)
        return subsolutions
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@pruebaRouter.delete("/{prueba_id}")
def delete_test(prueba_id: int, db: Session = Depends(get_db)):
    """Delete a single test and all its results"""
    try:
        result = delete_prueba(db, prueba_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


