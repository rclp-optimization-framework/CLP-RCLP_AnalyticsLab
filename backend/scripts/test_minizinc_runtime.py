#!/usr/bin/env python3
"""Validate MiniZinc is available and the expected solvers can be discovered.

This does not solve the full model yet; it verifies runtime + solver discovery.
"""

from __future__ import annotations

import json
import sys

import minizinc

EXPECTED_SOLVERS = ["gecode", "chuffed", "coin-bc", "cbc", "cp-sat"]


def main() -> int:
    driver = minizinc.default_driver
    solvers = driver.available_solvers()
    solver_names = sorted(set(solvers.keys()))

    print("Available solvers:")
    print(json.dumps(solver_names, indent=2))

    missing = [solver for solver in EXPECTED_SOLVERS if solver not in solver_names]
    if missing:
        print("Missing expected solvers:", missing)
        return 1

    print("MiniZinc runtime check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
