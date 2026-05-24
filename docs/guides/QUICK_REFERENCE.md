# Quick Reference

- Backend: `backend/` (FastAPI + SQLAlchemy)
- Frontend: `frontend/` (React + Vite + TypeScript)
- Local DB (SQLite): `rclp_local.db` (backend root)

Important endpoints:
- `POST /bateria/` - create battery
- `POST /bateria/upload/tests/{id}` - upload JSON/DZN tests
- `POST /ejecucion/ejecutar` - run tests with solvers
- `GET /resultado/prueba/{id}` - results for a test
- `GET /cache/test/{test_id}/all-solvers` - per-test solver payloads (v1.2.0)
- `GET /cache/test/{test_id}/statistics` - per-test statistics (v1.2.0)

Developer notes:
- Use `general_env` virtualenv for Python commands.
- Frontend dev server: `npm run dev` in `frontend/`.
- Frontend build: `npm run build`.
