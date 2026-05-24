import time
from datetime import timedelta
from minizinc import Instance, Model, Solver, Driver
import os
import shutil
from pathlib import Path
from services.instance_generator import FeasibleInstanceGenerator

model_path = os.path.join(os.path.dirname(__file__), "..", "services", "bus_model.mzn")


def _scale_value(value):
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, float):
        return int(round(value * 10))
    return value


def _normalize_scalar_list(values, expected_length, fallback):
    if not isinstance(values, list):
        return fallback
    normalized = [_scale_value(value) for value in values[:expected_length]]
    if len(normalized) < expected_length:
        normalized.extend(fallback[len(normalized):expected_length])
    return normalized


def _normalize_matrix(values, rows, cols, fallback):
    if not isinstance(values, list) or len(values) != rows:
        return fallback
    matrix = []
    for row_index in range(rows):
        row = values[row_index]
        if not isinstance(row, list):
            return fallback
        normalized_row = [_scale_value(value) for value in row[:cols]]
        if len(normalized_row) < cols:
            normalized_row.extend(fallback[row_index][len(normalized_row):cols])
        matrix.append(normalized_row)
    return matrix


def _normalize_params(params):
    num_buses = int(params.get("num_buses", 1))
    num_stations = int(params.get("num_stations", 1))
    base = FeasibleInstanceGenerator(num_buses, num_stations).generate_instance()

    normalized = dict(base)
    for key in ("num_buses", "num_stations", "max_stops", "consumo_max", "consumo_min", "sm", "m"):
        if key in params and params[key] is not None:
            normalized[key] = int(round(params[key]))

    for key in ("alpha", "mu", "psi", "beta"):
        if key in params and params[key] is not None:
            normalized[key] = _scale_value(params[key])

    if isinstance(params.get("num_stops"), list):
        normalized["num_stops"] = _normalize_scalar_list(params["num_stops"], num_buses, base["num_stops"])

    # Calcular max_stops basado en el tamaño real de los arrays, si los hay
    max_stops_from_params = int(normalized.get("max_stops", num_stations))
    actual_max_stops = max_stops_from_params
    
    # Si tenemos parámetros de matriz, revisar su tamaño real y ajustar max_stops si es menor
    for key in ("st_bi", "d", "t", "tau_bi"):
        if isinstance(params.get(key), list) and params[key] and len(params[key]) > 0:
            if isinstance(params[key][0], list):
                actual_col_count = len(params[key][0])
                if actual_col_count < actual_max_stops:
                    actual_max_stops = actual_col_count
    
    normalized["max_stops"] = actual_max_stops
    
    for key in ("st_bi", "d", "t", "tau_bi"):
        if isinstance(params.get(key), list):
            normalized[key] = _normalize_matrix(params[key], num_buses, actual_max_stops, base[key])

    return normalized

def solve_bus_model_optimal(params, solver_name="gecode", timeout_seconds=30):
    """
    params: diccionario con todos los parámetros y arrays del modelo
    solver_name: nombre del solver (ej: "gecode", "chuffed", "cbc", "scip", "cplex")
    Retorna un JSON con los resultados
    """

    params = _normalize_params(params)

    # Cargar el modelo desde archivo .mzn (tu modelo original en MiniZinc)
    model = Model(model_path)

    # Seleccionar solver
    solver = Solver.lookup(solver_name)

    # Crear instancia
    instance = Instance(solver, model)

    # Pasar parámetros al modelo
    for k, v in params.items():
        instance[k] = v

    # Resolver

    start = time.time()
    sol = instance.solve(timeout=timedelta(seconds=timeout_seconds))
    end = time.time()

    # Empaquetar resultados en JSON
    station_vector = [int(value) for value in sol["xst"]]
    outputs = {
        "solver": solver_name,
        "execution_time_seconds": round(end - start, 3),
        "num_buses": params["num_buses"],
        "num_stations": params["num_stations"],
        "station_vector": station_vector,
        "charged_stations": sum(station_vector),
        "charging_locations": [
            {"station": index + 1, "active": bool(value)}
            for index, value in enumerate(station_vector)
        ],
        "time_deviation_minutes": round(float(sum(sum(sol["d_tbi"][b]) for b in range(params["num_buses"]))) / 10, 2),
        "bateria": sol["cbi"],
        "carga": sol["ebi"],
    }

    return outputs

import sys

async def solve_bus_model_subsolutions(params, solver_name="gecode", max_solutions=10):
    model = Model(model_path)
    solver = Solver.lookup(solver_name)
    instance = Instance(solver, model)

    for k, v in params.items():
        instance[k] = v

    outputs = []
    start = time.time()

    if sys.platform.startswith("win"):
        # Workaround para Windows: usar API síncrona
        result = instance.solve(all_solutions=True)
        for idx, sol in enumerate(result, start=1):
            elapsed = time.time() - start
            station_vector = [int(value) for value in sol["xst"]]
            outputs.append({
                "solver": solver_name,
                "solution_index": idx,
                "execution_time_seconds": round(elapsed, 3),
                "num_buses": params["num_buses"],
                "num_stations": params["num_stations"],
                "station_vector": station_vector,
                "charged_stations": sum(station_vector),
                "charging_locations": [
                    {"station": index + 1, "active": bool(value)}
                    for index, value in enumerate(station_vector)
                ],
                "time_deviation_minutes": round(float(sum(sum(sol["d_tbi"][b]) for b in range(params["num_buses"]))) / 10, 2),
                "bateria": sol["cbi"],
                "carga": sol["ebi"]
            })
            if max_solutions and idx >= max_solutions:
                break
    else:
        # En Linux/macOS: usar API asíncrona
        idx = 0
        async for sol in instance.solutions():
            idx += 1
            elapsed = time.time() - start
            station_vector = [int(value) for value in sol["xst"]]
            outputs.append({
                "solver": solver_name,
                "solution_index": idx,
                "execution_time_seconds": round(elapsed, 3),
                "num_buses": params["num_buses"],
                "num_stations": params["num_stations"],
                "station_vector": station_vector,
                "charged_stations": sum(station_vector),
                "charging_locations": [
                    {"station": index + 1, "active": bool(value)}
                    for index, value in enumerate(station_vector)
                ],
                "time_deviation_minutes": round(float(sum(sum(sol["d_tbi"][b]) for b in range(params["num_buses"]))) / 10, 2),
                "bateria": sol["cbi"],
                "carga": sol["ebi"]
            })
            if max_solutions and idx >= max_solutions:
                break

    return outputs
