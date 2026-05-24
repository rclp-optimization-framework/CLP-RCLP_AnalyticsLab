#!/usr/bin/env python3
"""End-to-end workflow test for the backend API.

Exercises:
- create battery
- upload multiple tests via JSON file
- add a test directly
- execute with multiple solvers
- query results
- cleanup
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import requests

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

SAMPLE_TEST = {
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
}

SECOND_TEST = {
    "num_buses": 3,
    "num_stations": 5,
    "max_stops": 2,
    "num_stops": [2, 2, 1],
    "st_bi": [[1, 0, 0, 1, 0], [0, 1, 0, 0, 1], [1, 1, 0, 0, 0]],
    "d": [[0, 10, 12, 14, 16], [10, 0, 8, 11, 13], [12, 8, 0, 9, 10]],
    "t": [[0, 7, 8, 9, 10], [7, 0, 6, 7, 8], [8, 6, 0, 5, 7]],
    "tau_bi": [[2, 4, 6, 8, 10], [3, 5, 7, 9, 11], [4, 6, 8, 10, 12]],
    "consumo_max": 120,
    "consumo_min": 25,
    "alpha": 2.0,
    "mu": 9.5,
    "sm": 4,
    "psi": 3.5,
    "beta": 15.0,
    "m": 1500,
}


def call(method: str, path: str, **kwargs):
    response = requests.request(method, f"{BASE_URL}{path}", timeout=30, **kwargs)
    print(f"{method} {path} -> {response.status_code}")
    print(response.text)
    print()
    response.raise_for_status()
    return response


def main() -> int:
    battery_id = None
    direct_test_id = None
    uploaded_test_ids: list[int] = []

    try:
        battery = call("POST", "/bateria/", json={"nombre": "Workflow Smoke Battery"}).json()
        battery_id = battery["id"]
        print("Battery created:", battery)

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
            json.dump([SAMPLE_TEST, SECOND_TEST], tmp)
            upload_path = Path(tmp.name)

        with upload_path.open("rb") as handle:
            upload_response = requests.post(
                f"{BASE_URL}/bateria/upload/tests/{battery_id}",
                files={"file": (upload_path.name, handle, "application/json")},
                timeout=30,
            )
        print(f"POST /bateria/upload/tests/{battery_id} -> {upload_response.status_code}")
        print(upload_response.text)
        print()
        upload_response.raise_for_status()
        uploaded_tests = upload_response.json()
        uploaded_test_ids = [test["id"] for test in uploaded_tests]

        direct_test = call(
            "POST",
            f"/bateria/prueba/add/{battery_id}",
            json=SAMPLE_TEST,
        ).json()
        direct_test_id = direct_test["id"]
        print("Direct test created:", direct_test)

        tests_response = call("GET", f"/bateria/prueba/{battery_id}").json()
        test_ids = [test["id"] for test in tests_response]
        print("Test IDs in battery:", test_ids)

        execution_response = call(
            "POST",
            "/ejecucion/ejecutar",
            json={
                "bateria_id": battery_id,
                "prueba_ids": test_ids[:2],
                "solvers": ["gecode", "chuffed", "coin-bc"],
            },
        ).json()
        print("Execution results count:", len(execution_response))

        results_response = call("GET", f"/resultado/bateria/{battery_id}").json()
        print("Results by battery:", len(results_response))

        if test_ids:
            one_test = test_ids[0]
            results_by_test = call("GET", f"/resultado/prueba/{one_test}").json()
            print(f"Results for test {one_test}:", len(results_by_test))

            specific_result = call("GET", f"/resultado/prueba/{one_test}/solver/gecode").json()
            print("Specific result solver:", specific_result.get("solver"))

        print("Workflow smoke test passed.")
        return 0

    finally:
        if direct_test_id is not None:
            try:
                call("DELETE", f"/prueba/{direct_test_id}")
            except Exception:
                pass
        if battery_id is not None:
            try:
                call("DELETE", f"/bateria/{battery_id}")
            except Exception:
                pass
        for path in [p for p in [locals().get("upload_path")] if p]:
            try:
                path.unlink(missing_ok=True)
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
