from services.bus_model import solve_bus_model

data = {
    "num_buses": 2,
    "num_stations": 3,
    "max_stops": 2,
    "num_stops": [2, 2],
    "st_bi": [[1, 2], [2, 3]],
    "d": [[5, 7], [6, 8]],
    "t": [[10, 12], [11, 9]],
    "tau_bi": [[15, 30], [20, 35]],
    "cmax": 20,
    "cmin": 5,
    "alpha": 2,
    "mu": 10,
    "sm": 3,
    "psi": 1,
    "beta": 5,
    "m": 100
}

json_result = solve_bus_model(data, solver_name="gecode")
print(json_result)
