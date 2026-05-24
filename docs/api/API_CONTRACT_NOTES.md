# API Contract Notes

- The transactional API currently receives JSON payloads through FastAPI request bodies.
- The solver layer converts those payloads into MiniZinc parameters internally.
- The statistics layer is driven by cached execution results, not by local frontend state.
- The backend persists data through PostgreSQL models for batteries, tests, and cache records.
- Supabase is the target remote database, so connection variables should be defined through environment configuration.
