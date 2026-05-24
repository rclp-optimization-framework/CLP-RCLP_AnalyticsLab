# R-CLP Analytics

[![FastAPI](https://img.shields.io/badge/FastAPI-0.136.0-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3-38B2AC?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-remote-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Supabase](https://img.shields.io/badge/Supabase-storage-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com/)

R-CLP Analytics is a research platform for the AVISPA group. It executes MiniZinc-based battery experiments for bus charging-location studies, stores selected outcomes in PostgreSQL/Supabase, and exposes analytics for comparison dashboards.

## Project Layout

- [backend/](backend/) - FastAPI backend
- [frontend/](frontend/) - React + Tailwind frontend
- [docs/](docs/) - English documentation and sample payloads
- [scripts/](scripts/) - Smoke tests and helpers
- [minizinc/](minizinc/) - MiniZinc model assets

## Main Flows

- Create batteries and test payloads
- Run quick solver executions
- Persist cache results for later analysis
- Build statistics by battery, test, and metric
- Export result summaries to PDF from the front end

## Running with Docker

The recommended setup is Docker Compose. The backend and frontend services share a single network. Compose reads `backend/.env` and `frontend/.env` directly, and the backend still falls back to the local SQLite database if Supabase credentials are not provided.

## Requirements

- Backend dependencies: [backend/requirements.txt](backend/requirements.txt)
- Frontend dependencies: [frontend/package.json](frontend/package.json)

The frontend does not use a separate `requirements` file because it is a Vite application managed through npm.

## Documentation

- [Architecture](docs/architecture/ARCHITECTURE.md)
- [Quick Reference](docs/guides/QUICK_REFERENCE.md)
- [Testing & Deployment](docs/guides/TESTING_AND_DEPLOYMENT.md)
- [Features](docs/research/FEATURES_AND_IMPROVEMENTS.md)

## Version

Current version: 1.2.0
