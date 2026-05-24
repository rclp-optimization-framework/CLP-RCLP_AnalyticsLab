## Testing & Deployment Guide

This guide walks you through testing the new backend schema and deploying the system.

### Prerequisites

- Python 3.13 (using virtual environment in `general_env/`)
- Node.js 18+ (for frontend)
- All dependencies installed (check `backend/requirements.txt` and `frontend/package.json`)

---

## PART 1: Backend Testing

### Step 1: Activate Python Environment

```powershell
cd "c:\Users\lu\Downloads\Código\ 2026-I\AVISPA\Framework\backend"
.\general_env\Scripts\Activate.ps1
```

### Step 2: Verify Python Version

```powershell
python --version
# Should output: Python 3.13.x
```

### Step 3: Run Integration Tests

```powershell
python test_integration.py
```

**Expected Output:**

```
======================================================================
COMPREHENSIVE INTEGRATION TEST
======================================================================

[TEST 1] Create Battery
------
✓ Battery created: id=1, nombre='Integration Test Battery'

[TEST 2] Add Test via JSON
------
✓ Battery created with 1 test(s)

[TEST 3] Parse DZN Format
------
✓ DZN parsed successfully
	Fields: ['num_buses', 'st_bi', 'D', 'T', 'tau_bi', 'Cmax', 'Cmin', ...]

[TEST 4] Add Test via DZN
------
✓ Battery created with DZN test(s)

[TEST 5] Create Results with Different Solvers
------
✓ Result created: solver=gecode, execution_time=2.5s
✓ Result created: solver=chuffed, execution_time=1.8s

[TEST 6] Update Result (Upsert same solver)
------
✓ Result updated: execution_time=2.0s (was 2.5)

[TEST 7] Query Results by Prueba
------
✓ Found 2 results for prueba 1:
	- gecode: 2.0s
	- chuffed: 1.8s

[TEST 8] Query Results by Bateria
------
✓ Found 2 results for battery 1

[TEST 9] Verify Unique Constraint (prueba_id, solver)
------
✓ Solvers for prueba 1: ['gecode', 'chuffed']
✓ Unique constraint verified: no duplicate (prueba_id, solver) pairs

======================================================================
✅ ALL TESTS PASSED!
======================================================================
```

### Step 4 (Optional): Run Schema Test

```powershell
python test_schema.py
```

This validates basic database schema creation.

---

## PART 2: Start Backend Server

```powershell
cd "c:\Users\lu\Downloads\Código\ 2026-I\AVISPA\Framework\backend"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

The API is now running at `http://localhost:8000`

- API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## PART 3: Frontend Testing

### Step 1: Navigate to Frontend Directory

```powershell
cd "c:\Users\lu\Downloads\Código\ 2026-I\AVISPA\Framework\frontend"
```

### Step 2: Start Development Server

```powershell
npm run dev
```

**Expected Output:**

```
	VITE v5.x.x  ready in 123 ms

	➜  Local:   http://localhost:5173/
	➜  press h to show help
```

Open your browser to `http://localhost:5173/`

### Step 3: Test API Connectivity

In browser console (F12), test:

```javascript
// Test backend connection
fetch("http://localhost:8000/docs")
	.then((r) =>
		r.ok
			? console.log("✓ Backend connected")
			: console.log("✗ Backend not responding"),
	)
	.catch((e) => console.log("✗ Backend error:", e.message));
```

---

## PART 4: End-to-End System Test

### Workflow: Create Battery → Add Tests → Execute → View Results

#### 4.1: Create Battery

1. Click **Batteries** in navbar
2. Click **"+ Create Battery"** button
3. Enter name: "My Test Battery"
4. Click **Create**
5. ✓ Battery appears in table

#### 4.2: Add Tests (Upload JSON/DZN)

1. Click **Tests** in navbar
2. Select the battery you just created from sidebar
3. In **Upload Tests** section:
	 - **Option A - JSON**: Upload test_sample.json
	 - **Option B - DZN**: Upload test_sample.dzn
4. ✓ Tests appear in the tests table

**Sample JSON format** (test_sample.json):

```json
{
	"num_buses": 2,
	"num_stations": 4,
	"max_stops": 3,
	"num_stops": [3, 2],
	"st_bi": [
		[1, 0, 1, 0],
		[0, 1, 0, 1]
	],
	"d": [
		[0, 14, 18, 22],
		[14, 0, 11, 19]
	],
	"t": [
		[0, 9, 12, 16],
		[9, 0, 10, 13]
	],
	"tau_bi": [
		[6, 18, 30, 42],
		[8, 20, 32, 44]
	],
	"consumo_max": 100,
	"consumo_min": 20,
	"alpha": 1.5,
	"mu": 8.0,
	"sm": 3,
	"psi": 2.5,
	"beta": 12.0,
	"m": 1000
}
```

**Sample DZN format** (test_sample.dzn):

```
num_buses = 2;
num_stations = 4;
Cmax = 100;
Cmin = 20;
alpha = 15;
mu = 80;
SM = 3;
psi = 25;
beta = 120;
M = 1000;
max_stops = 3;
num_stops = [3,2];
st_bi = array2d(1..2, 1..4, [
	1,2,3,4,
	4,3,2,1
]);
D = array2d(1..2, 1..4, [
	0,140,180,220,
	0,140,180,220
]);
T = array2d(1..2, 1..4, [
	0,90,120,160,
	0,90,120,160
]);
tau_bi = array2d(1..2, 1..4, [
	0,100,200,320,
	50,150,250,370
]);
```

#### 4.3: Execute Tests

1. Click **Execution** in navbar
2. Select battery from dropdown
3. Check **Select All** to select all tests
4. Select multiple solvers: ☑ gecode, ☑ chuffed
5. Click **Execute**
6. ✓ Results display with solver names

#### 4.4: View Results

1. Click **Results** in navbar
2. ✓ Results table shows all (test, solver) combinations
3. (Optional) Filter by solver using dropdown

#### 4.5: View Statistics

1. Click **Statistics** in navbar
2. ✓ Charts show performance comparison across solvers
3. (Optional) View carousel for charging locations

---

## PART 5: API Testing (curl/Postman)

### Create Battery

```bash
curl -X POST http://localhost:8000/bateria/ \
	-H "Content-Type: application/json" \
	-d '{"nombre": "Test Battery"}'
```

### Upload Tests (JSON)

```bash
curl -X POST http://localhost:8000/bateria/upload/tests/1 \
	-F "file=@test_sample.json"
```

### List Tests in Battery

```bash
curl http://localhost:8000/bateria/prueba/1
```

### Execute Tests

```bash
curl -X POST http://localhost:8000/ejecucion/ejecutar \
	-H "Content-Type: application/json" \
	-d '{
		"bateria_id": 1,
		"prueba_ids": [1],
		"solvers": ["gecode", "chuffed"]
	}'
```

### Get Results for Test

```bash
curl http://localhost:8000/resultado/prueba/1
```

### Get Results for Specific Solver

```bash
curl http://localhost:8000/resultado/prueba/1/solver/gecode
```

### Available Solvers

```bash
curl http://localhost:8000/ejecucion/solvers
```

---

## PART 6: Troubleshooting

### Issue: Backend not responding

```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process using port 8000
taskkill /PID <PID> /F

# Restart backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Issue: Frontend can't reach backend

1. Check CORS in [main.py](backend/main.py):
	 ```python
	 app.add_middleware(
			 CORSMiddleware,
			 allow_origins=["*"],
			 allow_credentials=True,
			 allow_methods=["*"],
			 allow_headers=["*"],
	 )
	 ```
2. Check backend URL in [api.ts](frontend/src/services/api.ts):
	 ```typescript
	 const API_BASE_URL =
		 process.env.REACT_APP_API_URL || "http://localhost:8000";
	 ```

### Issue: Tests fail with "Pydantic validation error"

- Ensure all required fields are provided in JSON/DZN
- Check field names match exactly (case-sensitive)

### Issue: Unique constraint violation on results

- This is expected if you try to insert the same (prueba_id, solver) pair twice
- Use the upsert endpoint (POST /resultado/) to update instead

### Issue: DZN parser fails

- Verify DZN syntax (check for missing semicolons)
- Check array2d format: `array2d(1..rows, 1..cols, [...])`
- Verify numbers are separated by commas

---

## PART 7: Database Management

### View Database Schema

```powershell
cd "c:\Users\lu\Downloads\Código\ 2026-I\AVISPA\Framework\backend"
python -c "
from config.db import build_engine, Base
engine = build_engine()
from model.dataStructure import Bateria, Prueba, Result
from sqlalchemy import inspect
inspector = inspect(engine)
print('Tables:', inspector.get_table_names())
print('Bateria columns:', [c['name'] for c in inspector.get_columns('bateria')])
print('Prueba columns:', [c['name'] for c in inspector.get_columns('prueba')])
print('Result columns:', [c['name'] for c in inspector.get_columns('result')])
"
```

### Reset Database

```powershell
# Delete the database file
Remove-Item "rclp_local.db" -ErrorAction SilentlyContinue

# Recreate on first API call
```

### View Database Contents (SQLite)

```powershell
# If sqlite3 installed:
sqlite3 rclp_local.db

# Then:
SELECT * FROM bateria;
SELECT * FROM prueba;
SELECT * FROM result;
```

---

## PART 8: Production Deployment

### Backend (Windows Service / Cloud)

1. Build production bundle:

	 ```powershell
	 # Create executable script
	 $content = @"
	 #!/batch
	 @echo off
	 cd /d "c:\Users\lu\Downloads\Código\ 2026-I\AVISPA\Framework\backend"
	 call general_env\Scripts\activate.bat
	 uvicorn main:app --host 0.0.0.0 --port 8000
	 "@

	 Set-Content -Path "run_backend.bat" -Value $content
	 ```

2. Or use Docker:
	 ```dockerfile
	 FROM python:3.13
	 WORKDIR /app
	COPY requirements.txt .
	RUN pip install -r requirements.txt
	 COPY . .
	 CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
	 ```

### Frontend (Build & Deploy)

```powershell
cd "c:\Users\lu\Downloads\Código\ 2026-I\AVISPA\Framework\frontend"

# Build for production
npm run build

# Serve locally to test
npm run preview
```

Output in `dist/` folder - deploy to web server (nginx, Vercel, GitHub Pages, etc.)

---

## Summary: Key Endpoints

| Method | Endpoint                                 | Purpose                       |
| ------ | ---------------------------------------- | ----------------------------- |
| POST   | `/bateria/`                              | Create battery                |
| GET    | `/bateria/all`                           | List batteries                |
| GET    | `/bateria/{id}`                          | Get battery                   |
| PUT    | `/bateria/{id}`                          | Update battery name           |
| DELETE | `/bateria/{id}`                          | Delete battery                |
| POST   | `/bateria/upload/tests/{id}`             | Upload JSON/DZN tests         |
| GET    | `/bateria/prueba/{id}`                   | List tests in battery         |
| DELETE | `/prueba/{id}`                           | Delete test                   |
| POST   | `/resultado/`                            | Create/update result (upsert) |
| GET    | `/resultado/prueba/{id}`                 | Get all results for test      |
| GET    | `/resultado/prueba/{id}/solver/{solver}` | Get specific result           |
| GET    | `/resultado/bateria/{id}`                | Get all results in battery    |
| DELETE | `/resultado/{id}`                        | Delete result                 |
| POST   | `/ejecucion/ejecutar`                    | Execute tests with solvers    |
| GET    | `/ejecucion/solvers`                     | Get available solvers         |

---

## Success Criteria Checklist

- [ ] test_integration.py passes all 9 tests
- [ ] Backend server starts without errors
- [ ] Frontend loads at http://localhost:5173/
- [ ] Can create battery via UI
- [ ] Can upload JSON test file
- [ ] Can upload DZN test file
- [ ] Can select solvers and execute
- [ ] Results display correctly with solver names
- [ ] Can filter results by solver
- [ ] Statistics page shows solver comparison charts
- [ ] Delete operations work (battery, test, result)
