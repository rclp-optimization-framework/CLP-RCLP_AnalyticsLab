#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
VENV_SITE_PACKAGES = BACKEND_ROOT / "general_env" / "Lib" / "site-packages"
if VENV_SITE_PACKAGES.exists():
    sys.path.insert(0, str(VENV_SITE_PACKAGES))

SAMPLE_TESTS = [
    {
        "num_buses": 2,
        "num_stations": 4,
        "max_stops": 3,
        "num_stops": [3, 2],
        "st_bi": [[1, 0, 1, 0], [0, 1, 0, 1]],
        "d": [[0, 14, 18, 22], [14, 0, 11, 19]],
        "t": [[0, 9, 12, 16], [9, 0, 10, 13]],
        "tau_bi": [[6, 18, 30, 42], [8, 20, 32, 44]],
        "consumo_max": 100,
        "consumo_min": 20,
        "alpha": 1.5,
        "mu": 8.0,
        "sm": 3,
        "psi": 2.5,
        "beta": 12.0,
        "m": 1000,
    },
    {
        "num_buses": 3,
        "num_stations": 5,
        "max_stops": 4,
        "num_stops": [3, 3, 4],
        "st_bi": [[1, 0, 0, 1, 0], [0, 1, 1, 0, 0], [0, 0, 1, 0, 1]],
        "d": [[0, 10, 12, 15, 18], [10, 0, 14, 17, 21], [12, 14, 0, 13, 19]],
        "t": [[0, 7, 8, 11, 14], [7, 0, 9, 10, 12], [8, 9, 0, 9, 15]],
        "tau_bi": [[5, 12, 20, 28, 35], [6, 14, 22, 30, 38], [7, 16, 24, 32, 40]],
        "consumo_max": 120,
        "consumo_min": 30,
        "alpha": 1.2,
        "mu": 6.5,
        "sm": 2,
        "psi": 3.0,
        "beta": 10.0,
        "m": 500,
    },
]

SINGLE_TEST = {
    "num_buses": 1,
    "num_stations": 3,
    "max_stops": 2,
    "num_stops": [2],
    "st_bi": [[1, 0, 1]],
    "d": [[0, 5, 9]],
    "t": [[0, 4, 7]],
    "tau_bi": [[2, 6, 10]],
    "consumo_max": 80,
    "consumo_min": 15,
    "alpha": 1.0,
    "mu": 4.0,
    "sm": 1,
    "psi": 2.0,
    "beta": 8.0,
    "m": 250,
}

REQUESTED_SOLVERS = ["gecode", "chuffed", "coin-bc", "or-tools"]


def request(method: str, path: str, **kwargs: Any) -> requests.Response:
    url = f"{API_BASE_URL}{path}"
    response = requests.request(method, url, timeout=60, **kwargs)
    response.raise_for_status()
    return response


def normalize_solver_name(value: str) -> str:
    return "".join(character.lower() for character in value if character.isalnum())


def find_available_solver(available: list[str], candidates: list[str]) -> str | None:
    normalized = {normalize_solver_name(item): item for item in available}
    for candidate in candidates:
        match = normalized.get(normalize_solver_name(candidate))
        if match:
            return match
    return None


def main() -> int:
    print(f"API base URL: {API_BASE_URL}")

    ping = request("GET", "/ping").json()
    print(f"Ping: {ping}")

    battery_name = "validation-battery"
    battery = request("POST", "/bateria/", json={"nombre": battery_name}).json()
    battery_id = battery["id"]
    print(f"Created battery: {battery}")

    try:
        upload_path = PROJECT_ROOT / "scripts" / "validation-tests.json"
        upload_path.write_text(json.dumps(SAMPLE_TESTS, indent=2), encoding="utf-8")
        with upload_path.open("rb") as handle:
            uploaded = request("POST", f"/bateria/upload/tests/{battery_id}", files={"file": ("validation-tests.json", handle, "application/json")}).json()
        print(f"Uploaded tests: {len(uploaded)}")

        single_added = request("POST", f"/bateria/prueba/add/{battery_id}", json=SINGLE_TEST).json()
        print(f"Single test added: {single_added['id']}")

        tests = request("GET", f"/bateria/prueba/{battery_id}").json()
        print(f"Battery tests: {len(tests)}")
        if len(tests) < 3:
            raise RuntimeError("Expected at least 3 tests after upload and single insert")

        solver_payload = request("GET", "/ejecucion/solvers").json()
        available_solvers = solver_payload.get("solvers", [])
        print(f"Available solvers: {available_solvers}")

        selected_solvers: list[str] = []
        solver_aliases = {
            "gecode": ["gecode"],
            "chuffed": ["chuffed"],
            "coin-bc": ["coin-bc", "coinbc", "cbc"],
            "or-tools": ["or-tools", "ortools", "cp-sat", "cpsat"],
        }
        for requested in REQUESTED_SOLVERS:
            match = find_available_solver(available_solvers, solver_aliases[requested])
            if match:
                selected_solvers.append(match)
            else:
                print(f"WARNING: solver not available in MiniZinc environment: {requested}")

        if not selected_solvers:
            raise RuntimeError("No requested solvers are available in the current MiniZinc runtime")

        execution = request(
            "POST",
            "/ejecucion/ejecutar",
            json={
                "bateria_id": battery_id,
                "prueba_ids": [item["id"] for item in tests[:2]],
                "solvers": selected_solvers,
            },
        ).json()
        print(f"Execution results: {json.dumps(execution, ensure_ascii=False, indent=2)}")

        results_by_battery = request("GET", f"/resultado/bateria/{battery_id}").json()
        print(f"Results by battery: {len(results_by_battery)}")

        first_test_id = tests[0]["id"]
        first_test_results = request("GET", f"/resultado/prueba/{first_test_id}").json()
        print(f"Results by test {first_test_id}: {len(first_test_results)}")

        if first_test_results:
            first_solver = first_test_results[0]["solver"]
            specific = request("GET", f"/resultado/prueba/{first_test_id}/solver/{first_solver}").json()
            print(f"Specific result: {specific['id']} / {specific['solver']}")
            request("DELETE", f"/resultado/{specific['id']}")
            print(f"Deleted result id {specific['id']}")

        request("DELETE", f"/bateria/{battery_id}")
        print(f"Deleted battery {battery_id}")
    finally:
        try:
            if upload_path.exists():
                upload_path.unlink()
        except Exception:
            pass

    print("Backend API validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
