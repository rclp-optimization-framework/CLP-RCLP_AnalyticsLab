# Transactional API

This section documents the part of the backend that creates batteries, executes test cases, and returns solver responses.

## Purpose

The transactional layer manages experiment definition and execution. It is responsible for:

- creating a battery of tests
- adding one or many tests to a battery
- running a quick solver execution for a single test payload
- returning direct solver outputs or subsolution lists

## Inputs

The API receives JSON bodies with the following structure.

### Battery creation

`POST /bateria/`

Input fields:

- `nombre`: battery name
- `solver`: solver identifier supported by MiniZinc
- `pruebas`: optional list of test payloads

### Single test payload

Used by `POST /prueba/rapida` and by battery creation when tests are embedded.

Input fields:

- `num_buses`
- `num_stations`
- `max_stops`
- `num_stops`
- `st_bi`
- `d`
- `t`
- `tau_bi`
- `consumo_max`
- `consumo_min`
- `alpha`
- `mu`
- `sm`
- `psi`
- `beta`
- `m`

## Outputs

### `POST /prueba/rapida`

Returns the solver result for a single payload.

Output fields usually include:

- `solver`
- `execution_time_seconds`
- `num_buses`
- `num_stations`
- `charged_stations`
- `charging_locations`
- `time_deviation_minutes`
- `bateria`
- `carga`

### `POST /prueba/rapida/subsolutions/{max_solutions}`

Returns a list of solutions, each with the same solver metadata plus a `solution_index`.

### `POST /bateria/`

Returns the created battery summary:

- `id`
- `nombre`
- `solver`

### `GET /bateria/prueba/{bateria_id}`

Returns the tests belonging to a battery.

### Response shape reference

Most transactional read endpoints return SQLAlchemy-backed objects serialized by FastAPI, so the front should expect plain JSON objects or arrays with nested JSON fields for the matrices and schedules.

## Behavior Notes

- The backend validates that the solver exists before execution.
- Battery creation rejects duplicate batteries with the same solver and the same test set.
- The current API contract is JSON-first, not DZN-first. MiniZinc receives internal parameter mappings after JSON validation.
- Pagination is available on list endpoints through `skip` and `limit`.
