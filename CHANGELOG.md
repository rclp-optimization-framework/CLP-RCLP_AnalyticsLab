# Changelog

## 1.2.0

- Fix: Statistics page now shows all solvers per test (gecode, chuffed, coin-bc)
- Backend: new per-test cache endpoints `/cache/test/{id}/all-solvers`, `/cache/test/{id}/statistics`, `/cache/test/{id}/stations-info`
- Frontend: `StatisticsPage` refactored to call test-specific endpoints and render charts correctly
- Fix: `frontend/src/services/cacheApi.ts` TypeScript syntax and exports
- Misc: validation scripts and integration checks added

## 1.1.0

- Added English documentation for the project, transactional API, and statistics API.
- Added sample battery payloads for JSON-based solver execution.
- Added Supabase-oriented database configuration through environment variables.
- Added CORS support for the frontend application.
- Fixed statistics route contract issues and graph payload handling.
- Added a new React + Tailwind frontend scaffold with home, execution, results, and statistics pages.
- Added Docker and smoke-test scaffolding for repeatable runs.

## 1.0.0

- Initial backend API for battery creation, solver execution, and cached statistics.
- MiniZinc model integration for bus charging-location research experiments.
