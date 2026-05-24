#!/usr/bin/env python3
"""Smoke test the FastAPI backend endpoints.

This assumes uvicorn is already running on http://127.0.0.1:8000.
"""

from __future__ import annotations

import json
import sys
from urllib import error, request

BASE_URL = "http://127.0.0.1:8000"


def call(method: str, path: str, payload: dict | None = None, headers: dict | None = None):
    data = None
    request_headers = headers or {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")

    req = request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers=request_headers,
        method=method,
    )
    with request.urlopen(req, timeout=20) as response:
        body = response.read().decode("utf-8")
        return response.status, body


def main() -> int:
    checks = [
        ("GET", "/ping", None),
        ("GET", "/ejecucion/solvers", None),
        ("GET", "/bateria/all", None),
    ]

    for method, path, payload in checks:
        try:
            status, body = call(method, path, payload)
            print(f"{method} {path} -> {status}")
            print(body)
            print()
        except error.HTTPError as exc:
            print(f"{method} {path} -> HTTP {exc.code}")
            print(exc.read().decode("utf-8"))
            return 1
        except Exception as exc:
            print(f"{method} {path} -> ERROR {exc}")
            return 1

    print("Backend API smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
