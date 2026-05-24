## System Architecture Overview

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React + Vite)                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Pages: Batteries | Tests | Execution | Results | Stats   │   │
│  │ • BatteriesPage: CRUD batteries                          │   │
│  │ • TestsPage: Upload JSON/DZN, manage tests               │   │
│  │ • ExecutionPageNew: Multi-select tests & solvers         │   │
│  │ • ResultsPage: View results with solver filter           │   │
│  │ • StatisticsPage: Charts & comparisons                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│  Utilities:                                                      │
│  • services/api.ts: HTTP client for all endpoints               │
│  • utils/dzn-parser.ts: Parse DZN files in browser              │
│  • types/index.ts: TypeScript interfaces                        │
└─────────────────────────────────────────────────────────────────┘
							  ↕ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI + SQLAlchemy)             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Routes Layer                                             │   │
│  │ • routes/bateria.py: POST/GET/PUT/DELETE batteries      │   │
│  │ • routes/prueba.py: GET tests, DELETE test              │   │
│  │ • routes/resultado.py: Result CRUD                       │   │
│  │ • routes/ejecucion.py: Execute tests with solvers       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↕                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Services Layer (Business Logic)                          │   │
│  │ • services/bateria.py: Battery operations                │   │
│  │ • services/prueba.py: Test creation & queries            │   │
│  │ • services/resultado.py: Result CRUD with upsert         │   │
│  │ • services/bus_model.py: Solver execution (stub)         │   │
│  │ • services/pdf_service.py: PDF generation                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↕                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Model Layer (ORM)                                        │   │
│  │ • Bateria: id, nombre, timestamp                         │   │
│  │ • Prueba: id, bateria_id, [test_params], timestamp       │   │
│  │ • Result: id, prueba_id, solver, [exec_data], timestamp  │   │
│  │   - Unique constraint: (prueba_id, solver)               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              ↕                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Database (SQLite or Supabase PostgreSQL)                 │   │
│  │ • bateria table: batteries                               │   │
│  │ • prueba table: tests                                    │   │
│  │ • result table: test execution results                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│ Utilities:                                                       │
│ • utils/dzn_parser.py: Parse MiniZinc DZN format               │
│ • config/db.py: Database connection setup                       │
│ • serializers/: Pydantic request/response schemas               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Model

### Relationships & Constraints

```
Bateria (1) ──┬── (many) Prueba
			  │          ├─ num_buses: int
			  │          ├─ num_stations: int
			  │          ├─ max_stops: int
			  │          ├─ num_stops JSON
			  │          └─ (many) Result
			  │                     ├─ prueba_id: FK
			  │                     ├─ solver: string
			  │                     ├─ execution_time: float
			  │                     ├─ charged_stations: int
			  │                     ├─ [other result fields]
			  │                     └─ UNIQUE(prueba_id, solver)
			  │
			  └─ Cascade delete on prueba & result
```

**Key Design Decision**: Solver stored in **Result**, not Bateria

- Allows same test to run with multiple solvers
- Prevents duplicates via unique constraint on (prueba_id, solver)
- Enables upsert pattern for re-execution

### Schema Details

#### Bateria Table

```sql
CREATE TABLE bateria (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	nombre VARCHAR(255) NOT NULL,
	timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

#### Prueba Table

```sql
CREATE TABLE prueba (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	bateria_id INTEGER NOT NULL FK,
	num_buses INTEGER,
	num_stations INTEGER,
	max_stops INTEGER,
	num_stops JSON,
	st_bi JSON,
	d JSON,
	t JSON,
	tau_bi JSON,
	consumo_max FLOAT,
	consumo_min FLOAT,
	alpha FLOAT,
	mu FLOAT,
	sm INTEGER,
	psi FLOAT,
	beta FLOAT,
	m FLOAT,
	timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

#### Result Table

```sql
CREATE TABLE result (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	prueba_id INTEGER NOT NULL FK,
	solver VARCHAR(50) NOT NULL,
	execution_time_seconds FLOAT,
	charged_stations INTEGER,
	charging_locations JSON,
	time_deviation_minutes FLOAT,
	bateria JSON,
	carga JSON,
	timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
	UNIQUE(prueba_id, solver)
)
```

---

## API Flow Diagram

### Create Battery & Tests

```
Frontend UI (Batteries Page)
	↓ POST {nombre}
Backend POST /bateria/
	↓
services/bateria.py::create_bateria()
	↓ SQLAlchemy ORM
Database insert
	↓ returns Bateria object
Frontend receives battery ID
```

### Upload & Parse Test File

```
Frontend UI (Tests Page - File Upload)
	↓ POST FormData {file}
Backend POST /bateria/upload/tests/{id}
	↓ File type detection (.json or .dzn)
	├─ if .json: Parse as JSON → TestInput
	└─ if .dzn: utils/dzn_parser.py → TestInput
	↓
services/prueba.py::create_prueba_aux()
	↓ .model_dump(exclude_none=True) [FIX for None values]
	↓ SQLAlchemy ORM
Database insert Prueba
	↓
Frontend receives test list
```

### Execute Tests with Solvers

```
Frontend UI (Execution Page)
	↓ POST {bateria_id, prueba_ids[], solvers[]}
Backend POST /ejecucion/ejecutar
	↓
routes/ejecucion.py::execute_battery_tests()
	├─ For each (prueba_id in prueba_ids)
	└─ For each (solver in solvers)
		├─ services/bus_model.py::solve_bus_model_optimal() [STUB]
		├─ Generate mock execution data
		└─ services/resultado.py::create_or_update_result()
			├─ Try: Insert new Result
			└─ On unique constraint conflict: Update existing Result (upsert)
	↓ SQLAlchemy ORM
Database insert/update Result(s)
	↓
Frontend receives execution summary
```

---

## Design Notes

- Keep battery-level and per-test statistics separate to avoid mixing aggregation scopes.
- Prefer explicit service functions for battery summaries versus single-test solver breakdowns.
- Use JSON fields for matrices and route responses so the frontend can render charts without extra transformation.
