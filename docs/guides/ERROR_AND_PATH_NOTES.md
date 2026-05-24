# Common Path and Import Notes

- The backend database configuration must use environment variables, not a hardcoded localhost connection.
- Supabase passwords should be passed through separated variables so the SQLAlchemy URL is built safely.
- The frontend talks to the backend through CORS, so the API must allow the browser origin during development.
- The statistics graph endpoint is `/cache/bateria/graph/{bateria_id}`. The summary endpoint remains `/cache/bateria/stats/{bateria_id}`.
- Multi-battery statistics expect the `baterias` array in the request body.
- Battery examples live in `docs/examples/` and are JSON payloads, not DZN files.
- Frontend build tooling requires `@types/node` plus a Vite client env declaration file.
- Keep Docker Compose service names aligned with the folder names: `backend` and `frontend`.
