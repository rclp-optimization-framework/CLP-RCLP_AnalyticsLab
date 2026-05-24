from sqlalchemy.orm import Session
from model.dataStructure import Prueba, Bateria
from services.instance_generator import FeasibleInstanceGenerator
from sqlalchemy import func
from services.bus_model import solve_bus_model_subsolutions, solve_bus_model_optimal


def _normalize_prueba_data(data: dict) -> dict:
    """
    Completa o normaliza campos de una prueba usando un generador feasible cuando
    solo llegan datos parciales. Esto evita NULLs en columnas NOT NULL.
    """
    if hasattr(data, "model_dump"):
        data = data.model_dump(exclude_none=True)

    payload = dict(data)
    has_basic_shape = "num_buses" in payload and "num_stations" in payload

    if has_basic_shape:
        generator = FeasibleInstanceGenerator(payload["num_buses"], payload["num_stations"])
        instance = generator.generate_instance()
        merged = dict(instance)
        merged.update(payload)
        return merged

    return payload

def create_prueba_aux(data: dict) -> Prueba:
    data = _normalize_prueba_data(data)
    prueba = Prueba(**data)
    
    return prueba

def create_prueba_with_bateria_aux(db: Session, bateria_id : int, data: dict) -> Prueba:
    data = _normalize_prueba_data(data)

    bateria = db.query(Bateria).filter(Bateria.id == bateria_id).first()
    if not bateria:
        raise ValueError("La batería no existe")

    prueba = Prueba(bateria_id=bateria_id, **data)
    
    return prueba


def update_prueba_by_id(db: Session, prueba_id: int, data: dict) -> Prueba:
    prueba = db.query(Prueba).filter(Prueba.id == prueba_id).first()
    if not prueba:
        raise ValueError("La prueba no existe")

    update_fields = {
        "num_buses",
        "num_stations",
        "max_stops",
        "num_stops",
        "st_bi",
        "d",
        "t",
        "tau_bi",
        "consumo_max",
        "consumo_min",
        "alpha",
        "mu",
        "sm",
        "psi",
        "beta",
        "m",
    }

    normalized = _normalize_prueba_data(data)
    for field in update_fields:
        if field in normalized and normalized[field] is not None:
            setattr(prueba, field, normalized[field])

    db.commit()
    db.refresh(prueba)
    return prueba
        

######################################## YA EN ROUTES ############################################################
# Por defecto por ahora solo se admite pruebas dentro de baterias, no hay otra posibilidad
def create_prueba(db: Session, bateria_params: dict, data: dict) -> Prueba:
    """
    Crea una prueba asociada directamente a una batería.
    Ya no existe la tabla intermedia, por lo tanto la prueba
    tiene un campo bateria_id obligatorio.
    """

    if bateria_params["exist"]:
        prueba = create_prueba_with_bateria_aux(db, bateria_params["id"], data)
    
    else:
        prueba = create_prueba_aux(data)

    #db.add(prueba)
    #db.commit()
    #db.refresh(prueba)

    return prueba

######################################## YA EN ROUTES ############################################################
def get_all_pruebas(db: Session, skip: int = 0, limit: int = 10):
    """
    Devuelve pruebas únicas agrupadas por sus valores.
    """
    return (
        db.query(Prueba)
        .group_by(
            Prueba.num_buses,
            Prueba.num_stations,
            Prueba.max_stops,
            Prueba.num_stops,
            Prueba.st_bi,
            Prueba.d,
            Prueba.t,
            Prueba.tau_bi,
            Prueba.consumo_max,
            Prueba.consumo_min,
            Prueba.alpha,
            Prueba.mu,
            Prueba.sm,
            Prueba.psi,
            Prueba.beta,
            Prueba.m,
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

######################################## YA EN ROUTES ############################################################
def get_pruebas_by_fecha(db: Session, fecha):
    return db.query(Prueba).filter(func.date(Prueba.timestamp) == fecha).all()


######################################## YA EN ROUTES ############################################################
def get_prueba_by_id(db: Session, id: int):
    return db.query(Prueba).filter(Prueba.id == id).first()


######################################## YA EN ROUTES ############################################################
def get_pruebas_by_stations_buses(db: Session, num_stations: int, num_buses: int, skip: int = 0, limit: int = 10):
    return db.query(Prueba).filter(
        Prueba.num_stations == num_stations,
        Prueba.num_buses == num_buses
    ).offset(skip).limit(limit).all()

######################################## YA EN ROUTES ############################################################
def get_pruebas_by_num_buses(db: Session, num_buses: int):
    return db.query(Prueba).filter(
        Prueba.num_buses == num_buses
    ).all()


######################################## YA EN ROUTES ############################################################
def get_pruebas_by_num_stations(db: Session, num_stations: int):
    return db.query(Prueba).filter(
        Prueba.num_stations == num_stations
    ).all()


######################################## YA EN ROUTES ############################################################
def quick_prove(data: dict, solver: str):
    """
    Ejecuta una prueba rápida sin necesidad de guardarla en BD.
    """
    keys = data.keys()
    llenas = [k for k, v in data.items() if v not in (None, "", "null", [], {}, ())]

    if "num_buses" in keys and "num_stations" in keys and len(llenas) == 2:
        generator = FeasibleInstanceGenerator(data["num_buses"], data["num_stations"])
        instance = generator.generate_instance()
        result = solve_bus_model_optimal(params=instance, solver_name=solver)
    else:
        result = solve_bus_model_optimal(params=data, solver_name=solver)
    
    return result

######################################## YA EN ROUTES ############################################################
async def get_subsolutions_quick_prueba(data: dict, solver: str, max_solutions: int = 5):

    keys = data.keys()
    llenas = [k for k, v in data.items() if v not in (None, "", "null", [], {}, ())]

    try:

        if "num_buses" in keys and "num_stations" in keys and len(llenas) == 2:
            generator = FeasibleInstanceGenerator(data["num_buses"], data["num_stations"])
            instance = generator.generate_instance()
            result = await solve_bus_model_subsolutions(instance, solver_name=solver, max_solutions=max_solutions)
        else:
            result = await solve_bus_model_subsolutions(data, solver_name=solver, max_solutions=max_solutions)
    
    except Exception as e:
        raise Exception(str(e))
        
    return result

######################################## YA EN ROUTES ############################################################
def get_subsolutions_by_prueba(db: Session, prueba_id: int, solver: str, max_solutions: int = 5):
    """
    Obtiene subsoluciones de una prueba existente en la BD.
    """
    prueba = db.query(Prueba).filter(Prueba.id == prueba_id).first()
    if not prueba:
        raise ValueError("La prueba no existe")

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

    return solve_bus_model_subsolutions(params, solver_name=solver, all_solutions=True, max_solutions=max_solutions)


def delete_prueba(db: Session, prueba_id: int):
    """
    Delete a single test by ID.
    Cascade delete is handled by SQLAlchemy relationship.
    """
    prueba = db.query(Prueba).filter(Prueba.id == prueba_id).first()
    if not prueba:
        raise ValueError(f"Test with id {prueba_id} not found")
    
    db.delete(prueba)
    db.commit()
    return {"message": f"Test {prueba_id} deleted successfully"}

