from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from model.dataStructure import Cache, Prueba, Bateria
from services.bateria import get_bateria_by_id
from services.bus_model import solve_bus_model_optimal, solve_bus_model_subsolutions
import statistics
from const.const import relatives_metrics

def createCacheRegister(db: Session, data: dict) -> Cache:
    newCacheRegister = Cache(**data)
    db.add(newCacheRegister)
    db.commit()
    db.refresh(newCacheRegister)
    return newCacheRegister


def create_or_update_cache(
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
) -> Cache:
    prueba = db.query(Prueba).filter(Prueba.id == prueba_id).first()
    if not prueba:
        raise ValueError(f"Prueba con id {prueba_id} no encontrada")

    cache_entry = db.query(Cache).filter(
        Cache.prueba_id == prueba_id,
        Cache.solver == solver,
    ).first()

    if cache_entry:
        cache_entry.execution_time_seconds = execution_time_seconds
        cache_entry.charged_stations = charged_stations
        cache_entry.charging_locations = charging_locations
        cache_entry.time_deviation_minutes = time_deviation_minutes
        cache_entry.bateria = bateria
        cache_entry.carga = carga
        cache_entry.comment = comment
    else:
        cache_entry = Cache(
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
        db.add(cache_entry)

    try:
        db.commit()
        db.refresh(cache_entry)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Error al guardar cache: {str(e)}")

    return cache_entry


# Esto se ejecuta al compilar las pruebas de una bateria, les saca el resultado y las guarda en un sistema caché
#################################################### YA EN RUTAS ##################################################################
def get_optimal_solutions_for_bateria(db: Session, bateria_id: int):
    bateria = get_bateria_by_id(db, bateria_id)

    if not bateria:
        raise ValueError("La batería no existe")
    
    solver = bateria.solver

    pruebas = db.query(Prueba).filter(Prueba.bateria_id == bateria_id).all()

    if not pruebas:
        return []

    resultados = []
    for prueba in pruebas:
        # Ejecutar solver con los datos de la prueba
        result = solve_bus_model_optimal(params={
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
        }, solver_name=solver)

        # Crear registro en cache con el resultado
        cache_entry = createCacheRegister(db, result)
        resultados.append(cache_entry)

    return resultados

#################################################### YA EN RUTAS ##################################################################
def get_subsolutions_by_bateria(db: Session, bateria_id: int, max_solutions: int = 5):
    """
    Obtiene subsoluciones de todas las pruebas asociadas a una batería.
    """
    bateria = db.query(Bateria).filter(Bateria.id == bateria_id).first()
    if not bateria:
        raise ValueError("La batería no existe")

    solver = bateria.solver
    pruebas = db.query(Prueba).filter(Prueba.bateria_id == bateria_id).all()

    if not pruebas:
        return []

    resultados = {}
    for prueba in pruebas:
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
        resultados[prueba.id] = solve_bus_model_subsolutions(params, solver_name=solver, all_solutions=True, max_solutions=max_solutions)

    return resultados

#################################################### YA EN RUTAS ##################################################################
def get_cache_by_prueba(db: Session, prueba_id: int):
    return db.query(Cache).filter(Cache.prueba_id == prueba_id).first()


def get_cache_by_prueba_and_solver(db: Session, prueba_id: int, solver: str):
    return db.query(Cache).filter(
        Cache.prueba_id == prueba_id,
        Cache.solver == solver,
    ).first()

#################################################### YA EN RUTAS ##################################################################
def get_cache_by_id(db: Session, cache_id: int):
    return db.query(Cache).filter(Cache.id == cache_id).first()


def update_cache_comment(db: Session, cache_id: int, comment: str | None):
    cache_entry = get_cache_by_id(db, cache_id)
    if not cache_entry:
        raise ValueError(f"Cache con id {cache_id} no encontrado")

    cache_entry.comment = comment
    db.commit()
    db.refresh(cache_entry)
    return cache_entry


def delete_cache(db: Session, cache_id: int) -> bool:
    cache_entry = get_cache_by_id(db, cache_id)
    if not cache_entry:
        return False

    db.delete(cache_entry)
    db.commit()
    return True

# Esta función retorna la lista de resultados guardados en la cache de una una bateria especifica
#################################################### YA EN RUTAS ##################################################################
def get_cache_by_bateria(db: Session, bateria_id: int):
    return (
        db.query(Prueba, Cache)
        .join(Cache, Cache.prueba_id == Prueba.id)
        .filter(Prueba.bateria_id == bateria_id)
        .all()
    )


def get_cache_records_by_bateria(db: Session, bateria_id: int):
    return (
        db.query(Cache)
        .join(Prueba, Cache.prueba_id == Prueba.id)
        .filter(Prueba.bateria_id == bateria_id)
        .all()
    )

# Esta función retorna toda la lista de resultados guardados en la cache de todas las pruebas de cada bateria
#################################################### YA EN RUTAS ##################################################################
def list_cache_grouped_all_baterias(db: Session, skip: int = 0, limit: int = 10):
    return (
        db.query(Bateria, Cache)
        .join(Prueba, Prueba.bateria_id == Bateria.id)
        .join(Cache, Cache.prueba_id == Prueba.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_available_solvers(db: Session) -> list[str]:
    results = db.query(Cache.solver).distinct().all()
    return [row[0] for row in results] if results else []

# Calcula los promedios, desviación estandar, mediana y moda de los datos execution_time_seconds y time_deviation_minutes 
# de los resultados de las pruebas guardados en la cache de una bateria especifica
def get_cache_stats_for_bateria(db: Session, bateria_id: int):
    caches = (
        db.query(Cache)
        .join(Prueba, Cache.prueba_id == Prueba.id)
        .filter(Prueba.bateria_id == bateria_id)
        .all()
    )
    if not caches:
        return None

    exec_times = [c.execution_time_seconds for c in caches]
    deviations = [c.time_deviation_minutes for c in caches]

    def stats(values):
        return {
            "promedio": statistics.mean(values),
            "desviacion": statistics.pstdev(values),
            "mediana": statistics.median(values),
            "moda": statistics.mode(values) if len(values) > 0 else None
        }

    return {
        "execution_time_seconds": stats(exec_times),
        "time_deviation_minutes": stats(deviations)
    }

# genera los datos de todos los tipos de metrica (media, mediana, moda o desviación estandar), de un conjunto de pruebas
def generate_graph_data(db: Session, bateria_ids: list[int]):
    # metric puede ser "promedio", "desviacion", "mediana", "moda"
    data = {}
    for bid in bateria_ids:
        stats = get_cache_stats_for_bateria(db, bid)

        if not stats:
            raise ValueError("Baterias no encontradas")

        if stats:
            data[bid] = {
                "execution_time_seconds": stats["execution_time_seconds"],
                "time_deviation_minutes": stats["time_deviation_minutes"]
            }
    return data

# genera los datos de un tipo de metrica (media, mediana, moda o desviación estandar), de un conjunto de pruebas
def generate_graph_data_metrics(db: Session, bateria_ids: list[int], metric: int):
    # metric puede ser "promedio", "desviacion", "mediana", "moda"

    data = {}
    for bid in bateria_ids:
        stats = get_cache_stats_for_bateria(db, bid)

        if not stats:
            raise ValueError("Baterias no encontradas")
        
        if stats:
            data[bid] = {
                "execution_time_seconds": stats["execution_time_seconds"][relatives_metrics[metric]],
                "time_deviation_minutes": stats["time_deviation_minutes"][relatives_metrics[metric]]
            }
    return data

# Dada una bateria de pruebas, retorna los valores de execution_time_seconds y time_deviation_minutes
def generate_graph_data_results_pruebas_in_bateria(db: Session, bateria_id: int):
    pruebasWithResult = get_cache_by_bateria(db, bateria_id)

    if not pruebasWithResult:
        raise ValueError("Resultados no encontrados")

    result = {}

    for prueba, cache in pruebasWithResult:
        result[prueba.id] = [cache.execution_time_seconds, cache.time_deviation_minutes]
    
    return result

# NUEVA FUNCIÓN: Retorna TODOS los solvers para cada prueba con información completa
def get_all_solvers_by_test_in_battery(db: Session, bateria_id: int):
    """
    Retorna TODOS los solvers para cada prueba de una batería.
    Estructura: {
        test_id: [
            {
                'solver': 'gecode',
                'execution_time_seconds': 0.41,
                'time_deviation_minutes': 229.80,
                'charged_stations': 2,
                'charging_locations': [...],
                'bateria': [...],
                'carga': [...],
                'id': 43
            },
            ...
        ]
    }
    """
    caches = (
        db.query(Cache)
        .join(Prueba, Cache.prueba_id == Prueba.id)
        .filter(Prueba.bateria_id == bateria_id)
        .all()
    )

    if not caches:
        return {}

    result = {}
    for cache in caches:
        if cache.prueba_id not in result:
            result[cache.prueba_id] = []
        
        result[cache.prueba_id].append({
            'id': cache.id,
            'solver': cache.solver,
            'execution_time_seconds': cache.execution_time_seconds,
            'time_deviation_minutes': cache.time_deviation_minutes,
            'charged_stations': cache.charged_stations,
            'charging_locations': cache.charging_locations,
            'bateria': cache.bateria,
            'carga': cache.carga,
            'comment': cache.comment,
            'timestamp': cache.timestamp.isoformat() if cache.timestamp else None,
        })
    
    # Ordenar por desviación para cada prueba
    for test_id in result:
        result[test_id].sort(key=lambda x: x['time_deviation_minutes'])
    
    return result


# NUEVA FUNCIÓN: Obtiene estadísticas específicas de una prueba (no de toda la batería)
def get_test_statistics(db: Session, test_id: int):
    """
    Retorna estadísticas específicas de una prueba.
    Estructura: {
        'best_deviation': 229.80,
        'worst_deviation': 2000.00,
        'avg_deviation': 1414.00,
        'avg_execution': 1.95,
        'num_solvers': 3,
        'solvers': ['gecode', 'chuffed', 'coin-bc']
    }
    """
    caches = db.query(Cache).filter(Cache.prueba_id == test_id).all()

    if not caches:
        return None

    deviations = [c.time_deviation_minutes for c in caches]
    exec_times = [c.execution_time_seconds for c in caches]
    solvers = [c.solver for c in caches]

    return {
        'best_deviation': min(deviations),
        'worst_deviation': max(deviations),
        'avg_deviation': sum(deviations) / len(deviations),
        'avg_execution': sum(exec_times) / len(exec_times),
        'num_solvers': len(caches),
        'solvers': solvers,
        'cache_count': len(caches),
    }


# NUEVA FUNCIÓN: Retorna información de estaciones por solver para una prueba
def get_solver_stations_info_by_test(db: Session, test_id: int):
    """
    Retorna información detallada de estaciones para cada solver en una prueba.
    Estructura: {
        'gecode': {
            'charged_stations': 2,
            'charging_locations': [...],
            'station_vector': [0, 0, 0, 0, 1, 1, 0, 0],
            'bateria': [...],
            'carga': [...]
        },
        ...
    }
    """
    caches = db.query(Cache).filter(Cache.prueba_id == test_id).all()

    if not caches:
        return {}

    result = {}
    for cache in caches:
        # Extraer vector de estaciones desde charging_locations
        station_vector = []
        if isinstance(cache.charging_locations, list):
            for item in cache.charging_locations:
                if isinstance(item, dict):
                    station_vector.append(1 if item.get('active') else 0)
                elif isinstance(item, int):
                    station_vector.append(item)
        
        result[cache.solver] = {
            'charged_stations': cache.charged_stations,
            'charging_locations': cache.charging_locations,
            'station_vector': station_vector if station_vector else None,
            'bateria': cache.bateria,  # Matriz de batería por tiempo
            'carga': cache.carga,      # Matriz de carga por tiempo
            'execution_time_seconds': cache.execution_time_seconds,
            'time_deviation_minutes': cache.time_deviation_minutes,
        }
    
    return result
