# Scripts

This folder contains small utilities and checks used during development and CI.

Subfolders:
- `checks/` — environment and API validation scripts (Python)
- `tests/` — lightweight test helpers and API response checks
- `windows/` — PowerShell smoke tests for Windows environments
- `misc/` — miscellaneous utilities

How to run (examples):

- Run backend API checks:

```bash
python scripts/checks/check_backend_api.py
```

- Verify MiniZinc solvers (requires `minizinc` Python package and CLI):

```bash
python scripts/checks/check_minizinc_solvers.py
```

- Run Windows smoke test (PowerShell):

```powershell
./scripts/windows/smoke-test.ps1 -BackendUrl http://localhost:8000 -FrontendUrl http://localhost:5173
```

- Run battery example tests (PowerShell):

```powershell
./scripts/windows/test-battery-examples.ps1 -BackendUrl http://localhost:8000
```

Notes:
- Many scripts rely on the `general_env` virtual environment under `backend/`.
- Use `python -m pip install -r backend/requirements.txt` to install backend dependencies into the active env.
