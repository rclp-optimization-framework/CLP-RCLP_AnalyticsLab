# R-CLP Analytics Overview

R-CLP Analytics is a FastAPI-based research API for the AVISPA group. It supports two core workflows: running battery-based experiments over a MiniZinc solver, and storing the resulting measurements to compute statistics later.

The project serves a research need in bus charging-location experiments. It helps the team execute controlled test cases, persist results, and analyze performance indicators such as execution time, charging locations, and time deviation.

## What It Solves

The system centralizes the lifecycle of a research experiment:

- define a battery of test cases
- execute each test case against a solver
- store the results of the execution
- aggregate stored outcomes into statistics and chart-ready datasets

This removes manual repetition and makes experiment comparison more consistent and traceable.

## Main Parts

- Transactional API: creates batteries and tests, runs solvers, and returns execution results.
- Statistics API: reads cached results, computes aggregates, and prepares grouped data for dashboards.
- MiniZinc model: defines the optimization problem used by the solver.

## Data Flow

1. A user creates a battery or sends a direct test payload.
2. The backend validates the solver and parameters.
3. MiniZinc executes the model and returns the optimization result.
4. The result can be stored in the cache table.
5. Statistics endpoints aggregate cached results for dashboards and ranking views.

## Research Context

The platform supports the research practice developed by Juan Francesco García Vargas and Andrey Quiceno Cabrera inside the AVISPA research group.

## Current Contract

The API currently receives structured JSON payloads for batteries and tests. The solver parameters are passed to the backend as JSON objects and are consumed internally by the MiniZinc integration.
