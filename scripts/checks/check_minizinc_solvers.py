#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import minizinc

REQUESTED_SOLVERS = {
	"gecode": ["gecode"],
	"chuffed": ["chuffed"],
	"coin-bc": ["coin-bc", "coinbc", "cbc"],
	"or-tools": ["or-tools", "ortools", "cp-sat", "cpsat"],
}

MODEL_TEXT = """
var 0..1: x;
solve satisfy;
output ["x=", show(x), "\n"];
"""


def normalize(value: str) -> str:
	return "".join(character.lower() for character in value if character.isalnum())


def find_solver(available: list[str], candidates: list[str]) -> str | None:
	normalized = {normalize(item): item for item in available}
	for candidate in candidates:
		match = normalized.get(normalize(candidate))
		if match:
			return match
	return None


def run_cli_solver(minizinc_bin: str, solver_id: str, model_path: Path) -> subprocess.CompletedProcess[str]:
	return subprocess.run(
		[minizinc_bin, "--solver", solver_id, str(model_path)],
		capture_output=True,
		text=True,
		timeout=120,
	)


def main() -> int:
	available_solvers = sorted(minizinc.default_driver.available_solvers().keys())
	print("MiniZinc driver available solvers:")
	for solver in available_solvers:
		print(f"  - {solver}")

	minizinc_bin = shutil.which("minizinc")
	if not minizinc_bin:
		print("ERROR: minizinc executable not found on PATH")
		return 1

	print(f"MiniZinc CLI: {minizinc_bin}")

	requested_resolved: dict[str, str] = {}
	missing: list[str] = []
	for requested_name, aliases in REQUESTED_SOLVERS.items():
		solver_id = find_solver(available_solvers, aliases)
		if solver_id:
			requested_resolved[requested_name] = solver_id
		else:
			missing.append(requested_name)

	print("Requested solver resolution:")
	for requested_name, solver_id in requested_resolved.items():
		print(f"  - {requested_name} -> {solver_id}")
	for requested_name in missing:
		print(f"  - {requested_name} -> MISSING")

	if missing:
		print("ERROR: one or more requested solvers are not available in the MiniZinc runtime")
		return 1

	with tempfile.TemporaryDirectory() as temp_dir:
		model_path = Path(temp_dir) / "smoke_test.mzn"
		model_path.write_text(MODEL_TEXT, encoding="utf-8")

		for requested_name, solver_id in requested_resolved.items():
			result = run_cli_solver(minizinc_bin, solver_id, model_path)
			print(f"\n[{requested_name}] return code = {result.returncode}")
			if result.stdout.strip():
				print(result.stdout.strip())
			if result.stderr.strip():
				print(result.stderr.strip())
			if result.returncode != 0:
				return 1

	print("MiniZinc solver validation passed.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
