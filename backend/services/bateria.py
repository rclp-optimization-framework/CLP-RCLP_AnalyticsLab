from sqlalchemy.orm import Session
from model.dataStructure import Bateria, Prueba
from services.prueba import create_prueba
from sqlalchemy import func

def bateria_duplicada(db: Session, pruebas_data: list[dict]) -> bool:
    baterias = db.query(Bateria).all()

    for b in baterias:
        pruebas_b = db.query(Prueba).filter(Prueba.bateria_id == b.id).all()

        existentes = [{
            "num_buses": p.num_buses,
            "num_stations": p.num_stations,
            "max_stops": p.max_stops,
            "num_stops": p.num_stops,
            "st_bi": p.st_bi,
            "d": p.d,
            "t": p.t,
            "tau_bi": p.tau_bi,
            "consumo_max": p.consumo_max,
            "consumo_min": p.consumo_min,
            "alpha": p.alpha,
            "mu": p.mu,
            "sm": p.sm,
            "psi": p.psi,
            "beta": p.beta,
            "m": p.m,
        } for p in pruebas_b]

        # Ignorar caso sin pruebas
        if not existentes and not pruebas_data:
            continue

        if existentes == pruebas_data:
            return True

    return False


def bateria_nombre_duplicado(db: Session, nombre: str) -> bool:
    normalized = nombre.strip().lower()
    return db.query(Bateria).filter(func.lower(Bateria.nombre) == normalized).first() is not None

def add_prueba_to_bateria(db: Session, bateria_id: int, data: dict) -> Prueba:
    bateria = db.query(Bateria).filter(Bateria.id == bateria_id).first()
    if not bateria:
        raise ValueError("La batería no existe")

    # Lista de pruebas actuales + la nueva
    nuevas_pruebas = [data] + [{
        "num_buses": p.num_buses,
        "num_stations": p.num_stations,
        "max_stops": p.max_stops,
        "num_stops": p.num_stops,
        "st_bi": p.st_bi,
        "d": p.d,
        "t": p.t,
        "tau_bi": p.tau_bi,
        "consumo_max": p.consumo_max,
        "consumo_min": p.consumo_min,
        "alpha": p.alpha,
        "mu": p.mu,
        "sm": p.sm,
        "psi": p.psi,
        "beta": p.beta,
        "m": p.m,
    } for p in bateria.pruebas]

    if bateria_duplicada(db, nuevas_pruebas):
        raise ValueError("Ya existe una batería con las mismas pruebas.")

    # Si no hay duplicado, crear la prueba
    prueba = create_prueba(db, {"exist":True, "id": bateria.id}, data)
    db.add(prueba)
    db.commit()
    db.refresh(prueba)
    return prueba

def add_pruebas_to_bateria(db: Session, bateria_id: int, pruebas_data: list[dict]) -> list[Prueba]:
    bateria = db.query(Bateria).filter(Bateria.id == bateria_id).first()
    if not bateria:
        raise ValueError("La batería no existe")

    # Lista de pruebas actuales + las nuevas
    nuevas_pruebas = pruebas_data + [{
        "num_buses": p.num_buses,
        "num_stations": p.num_stations,
        "max_stops": p.max_stops,
        "num_stops": p.num_stops,
        "st_bi": p.st_bi,
        "d": p.d,
        "t": p.t,
        "tau_bi": p.tau_bi,
        "consumo_max": p.consumo_max,
        "consumo_min": p.consumo_min,
        "alpha": p.alpha,
        "mu": p.mu,
        "sm": p.sm,
        "psi": p.psi,
        "beta": p.beta,
        "m": p.m,
    } for p in bateria.pruebas]

    if bateria_duplicada(db, nuevas_pruebas):
        raise ValueError("Ya existe una batería con las mismas pruebas.")

    # Si no hay duplicados, crear las pruebas
    pruebas = []
    for data in pruebas_data:
        prueba = create_prueba(db, {"exist":True, "id": bateria.id}, data)
        db.add(prueba)
        pruebas.append(prueba)
    db.commit()

    # Refresh all
    for p in pruebas:
        db.refresh(p)
    return pruebas
    nuevas_pruebas = pruebas_data + [{
        "num_buses": p.num_buses,
        "num_stations": p.num_stations,
        "max_stops": p.max_stops,
        "num_stops": p.num_stops,
        "st_bi": p.st_bi,
        "d": p.d,
        "t": p.t,
        "tau_bi": p.tau_bi,
        "consumo_max": p.consumo_max,
        "consumo_min": p.consumo_min,
        "alpha": p.alpha,
        "mu": p.mu,
        "sm": p.sm,
        "psi": p.psi,
        "beta": p.beta,
        "m": p.m,
    } for p in bateria.pruebas]

    if bateria_duplicada(db, bateria.solver, nuevas_pruebas):
        raise ValueError("Ya existe una batería con las mismas pruebas y el mismo solver.")

    # Si no hay duplicado, crear las pruebas
    nuevas = []
    for data in pruebas_data:
        prueba = create_prueba(db, {"exist":True, "id": bateria.id}, data.dict())
        db.add(prueba)
        nuevas.append(prueba)
    db.commit()
    return nuevas

######################################## YA EN ROUTES ############################################################
def create_bateria(db: Session, nombre: str, pruebas_data: list[dict] = None) -> Bateria:
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre de la batería es obligatorio")

    if bateria_nombre_duplicado(db, nombre):
        raise ValueError("Ya existe una batería con ese nombre.")

    # Validar duplicados por pruebas (no por solver)
    if bateria_duplicada(db, pruebas_data or []):
        raise ValueError("Ya existe una batería con las mismas pruebas.")

    # Crear batería
    bateria = Bateria(nombre=nombre)
    db.add(bateria)
    db.commit()
    db.refresh(bateria)

    # Crear pruebas si hay
    if pruebas_data:
        for data in pruebas_data:
            prueba = create_prueba(db, {"exist":True, "id": bateria.id}, data)
            db.add(prueba)
        db.commit()

    return bateria

######################################## YA EN ROUTES ############################################################
def get_bateria_by_solver(db: Session, solver: str, skip: int = 0, limit: int = 10):
    return (
        db.query(Bateria)
        .filter(Bateria.solver == solver)
        .offset(skip)
        .limit(limit)
        .all()
    )

######################################## YA EN ROUTES ############################################################
def get_bateria_by_nombre(db: Session, nombre: str):
    return db.query(Bateria).filter(Bateria.nombre.startswith(nombre)).all()

######################################## YA EN ROUTES ############################################################
def get_all_baterias(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Bateria).offset(skip).limit(limit).all()

######################################## YA EN ROUTES ############################################################
def get_bateria_by_fecha(db: Session, fecha):
    return db.query(Bateria).filter(func.date(Bateria.timestamp) == fecha).all()

######################################## YA EN ROUTES ############################################################
def get_bateria_by_id(db: Session, id: int):
    return db.query(Bateria).filter(Bateria.id == id).first()


def get_pruebas_of_bateria(db: Session, id: int, skip: int = 0, limit: int = 10):
    """
    Obtiene las pruebas asociadas a una batería, con paginación.
    """
    return (
        db.query(Prueba)
        .filter(Prueba.bateria_id == id)
        .offset(skip)
        .limit(limit)
        .all()
    )

"""
def get_pruebas_of_bateria_noPagination(db: Session, id: int):


    return db.query(Prueba).filter(Prueba.bateria_id == id).all()
"""