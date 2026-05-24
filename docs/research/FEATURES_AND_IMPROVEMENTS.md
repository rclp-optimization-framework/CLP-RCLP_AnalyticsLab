## System Features & Improvements

### ✨ New Features (v1.0.0)

#### 1. **Solver Selection at Execution Time**

- **Before**: Solver was selected and stored when creating a battery
- **After**: Solver is selected at the moment of test execution
- **Benefit**: Same test can be executed with multiple solvers, enabling solver comparison

#### 2. **Multi-Solver Result Storage**

- **New Structure**: Result table with unique constraint on (prueba_id, solver)
- **Feature**: Multiple solvers' results for the same test can coexist in database
- **Benefit**: Compare solver performance on identical test cases

#### 3. **File Upload Support (JSON & DZN)**

- **JSON Format**: Upload batch of tests in JSON format
- **DZN Format**: Upload MiniZinc data files directly
- **Benefit**: Import test cases from existing optimization workflows

#### 4. **Automatic DZN Format Conversion**

- **Parser**: Converts MiniZinc DZN files to application test format
- **Field Mapping**: Automatic translation (Cmax→consumo_max, D→d, etc.)
- **Benefit**: Seamless integration with MiniZinc ecosystem

#### 5. **Upsert Results Pattern**

- **Feature**: Re-executing same test with same solver updates (not duplicates)
- **Implementation**: Unique constraint + INSERT OR REPLACE logic
- **Benefit**: Safe result updates without manual deletion

#### 6. **New User Interface Pages**

- **Batteries Page**: CRUD operations for batteries
- **Tests Page**: Upload and manage tests within batteries
- **Execution Page**: Multi-select tests and solvers, execute, view results
- **Results Page**: View and filter results by solver
- **Statistics Page**: Compare solver performance with charts

#### 7. **RESTful API Redesign**

- **Endpoints**: Cleaner separation: /bateria, /prueba, /resultado, /ejecucion
- **Methods**: Proper HTTP verbs (POST create, PUT update, DELETE remove)
- **File Upload**: Native FormData support for file uploads
- **Response Format**: Consistent JSON schemas with proper status codes

---

### 📊 Schema Improvements

#### Before (v0.x)

```
Bateria Table
├─ id
├─ nombre
├─ solver ❌ (wrong place - execution-specific)
└─ timestamp

Prueba Table
├─ id
├─ bateria_id
├─ [test parameters]
└─ timestamp

Cache Table (Results)
├─ id
├─ prueba_id
├─ [execution data]
└─ timestamp
```

#### After (v1.0.0)

```
Bateria Table ✅ (simplified)
├─ id
├─ nombre
└─ timestamp

Prueba Table ✅ (unchanged)
├─ id
├─ bateria_id
├─ [test parameters]
└─ timestamp

Result Table ✅ (enhanced)
├─ id
├─ prueba_id
├─ solver ✅ (moved here - execution-specific)
├─ execution_time_seconds
├─ charged_stations
├─ charging_locations
├─ time_deviation_minutes
├─ bateria (JSON)
├─ carga (JSON)
├─ timestamp
└─ UNIQUE(prueba_id, solver) ✅ (prevents duplicates)
```

---

### 🔧 API Endpoints

#### Batteries

```
POST   /bateria/                     → Create battery
GET    /bateria/all                  → List all batteries
GET    /bateria/{id}                 → Get battery
PUT    /bateria/{id}                 → Update battery name
DELETE /bateria/{id}                 → Delete battery
```

#### Tests

```
POST   /bateria/upload/tests/{id}    → Upload JSON/DZN file
GET    /bateria/prueba/{id}          → List tests in battery
DELETE /prueba/{id}                  → Delete test
```

#### Results

```
POST   /resultado/                   → Create/update result (upsert)
GET    /resultado/prueba/{id}        → Get all results for test
GET    /resultado/prueba/{id}/solver/{solver}  → Get specific result
GET    /resultado/bateria/{id}       → Get all results in battery
DELETE /resultado/{id}               → Delete result
```

#### Execution

```
POST   /ejecucion/ejecutar           → Execute tests with multiple solvers
GET    /ejecucion/solvers            → Get available solvers
```

---

### 💾 Code Quality Improvements

#### Bug Fixes

1. **Pydantic None Value Handling**
	- **Issue**: `.model_dump()` included None values; DB nullable=False columns rejected them
	- **Fix**: Changed to `.model_dump(exclude_none=True)` in services/prueba.py
	- **Impact**: Fixes HTTP 500 error on POST /bateria/

2. **Unique Constraint Handling**
	- **Feature**: Upsert pattern for result updates
	- **Implementation**: SQLAlchemy IntegrityError catch → update on conflict

3. **File Upload Support**
	- **Issue**: No previous support for file uploads
	- **Solution**: FormData endpoint with file type detection

#### Code Organization

- **Separation of Concerns**: Routes → Services → Models → Database
- **Reusable Services**: Each service handles one domain (bateria, prueba, resultado)
- **Consistent Error Handling**: HTTP exceptions with proper status codes
- **Type Safety**: Pydantic schemas for all inputs/outputs

#### Testing Infrastructure

- **Unit Tests**: Schema validation (test_schema.py)
- **Integration Tests**: Complete workflow testing (test_integration.py)
- **Sanity Checks**: Module imports and basic connectivity (sanity_check.py)

---

### 🎨 Frontend Enhancements

#### New Components

- **BatteriesPage**: Full CRUD for batteries with modals
- **TestsPage**: File upload with type detection, test management
- **ExecutionPageNew**: Multi-select interface for tests and solvers
- **ResultsPage**: Results table with solver filtering
- **StatisticsPage**: Performance comparison charts

#### New Utilities

- **dzn-parser.ts**: TypeScript DZN file parser matching Python implementation
- **Enhanced API Service**: Wrapper for all new endpoints with FormData support

#### UI/UX Improvements

- **Navigation**: Clear navbar with all pages
- **Forms**: Modal dialogs for battery creation
- **File Upload**: Native file input with feedback
- **Multi-Select**: Checkboxes for tests and solvers
- **Filtering**: Dropdown filters for solver selection
- **Responsive**: Works on desktop and tablet
