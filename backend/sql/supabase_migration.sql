-- Migration script for Supabase/PostgreSQL to the new battery/test/result schema.
-- Review before running in production.

BEGIN;

-- Battery table
CREATE TABLE IF NOT EXISTS bateria (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test table
CREATE TABLE IF NOT EXISTS prueba (
    id SERIAL PRIMARY KEY,
    bateria_id INTEGER NOT NULL REFERENCES bateria(id) ON DELETE CASCADE,
    num_buses INTEGER NOT NULL,
    num_stations INTEGER NOT NULL,
    max_stops INTEGER NOT NULL,
    num_stops JSONB NOT NULL,
    st_bi JSONB NOT NULL,
    d JSONB NOT NULL,
    t JSONB NOT NULL,
    tau_bi JSONB NOT NULL,
    consumo_max INTEGER NOT NULL,
    consumo_min INTEGER NOT NULL,
    alpha DOUBLE PRECISION NOT NULL,
    mu DOUBLE PRECISION NOT NULL,
    sm INTEGER NOT NULL,
    psi DOUBLE PRECISION NOT NULL,
    beta DOUBLE PRECISION NOT NULL,
    m INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Result table
CREATE TABLE IF NOT EXISTS result (
    id SERIAL PRIMARY KEY,
    prueba_id INTEGER NOT NULL REFERENCES prueba(id) ON DELETE CASCADE,
    solver VARCHAR(255) NOT NULL,
    execution_time_seconds DOUBLE PRECISION NOT NULL,
    charged_stations INTEGER NOT NULL,
    charging_locations JSONB NOT NULL,
    time_deviation_minutes DOUBLE PRECISION NOT NULL,
    bateria JSONB NOT NULL,
    carga JSONB NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_prueba_solver UNIQUE (prueba_id, solver)
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_prueba_bateria_id ON prueba (bateria_id);
CREATE INDEX IF NOT EXISTS idx_result_prueba_id ON result (prueba_id);
CREATE INDEX IF NOT EXISTS idx_result_solver ON result (solver);

COMMIT;
