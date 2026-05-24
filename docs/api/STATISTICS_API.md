# Statistics API

This section documents the cached-results layer and the analytics endpoints.

## Purpose

The statistics layer reads stored solver outputs and transforms them into aggregated indicators for dashboards, rankings, and comparative charts.

## Inputs

The endpoints receive either a battery identifier or a list of battery identifiers.

### Single-battery analytics

- `GET /cache/bateria/{bateria_id}`
- `GET /cache/prueba/{prueba_id}`
- `GET /cache/bateria/stats/{bateria_id}`
- `GET /cache/bateria/stats/{bateria_id}` for per-test graph-oriented values

### Multi-battery analytics

- `POST /cache/bateria/stats`
- `POST /cache/bateria/stats/{metric}`

The request body uses a list structure with the battery ids to compare.

## Outputs

### Cache record

A stored cache entry includes:

- `id`
- `prueba_id`
- `execution_time_seconds`
- `charged_stations`
- `charging_locations`
- `time_deviation_minutes`
- `bateria`
- `carga`
- `timestamp`

### Aggregated statistics

`GET /cache/bateria/stats/{bateria_id}` returns summary statistics for:

- `execution_time_seconds`
- `time_deviation_minutes`

Each summary includes:

- `promedio`
- `desviacion`
- `mediana`
- `moda`

### Multi-battery graph data

`POST /cache/bateria/stats`
returns grouped values per battery for execution time and deviation.

`POST /cache/bateria/stats/{metric}` returns a single metric across batteries, where:

- `1` = average
- `2` = standard deviation
- `3` = median
- `4` = mode

## Analytics Use Cases

The front end can use this layer to build:

- ranking views for the lowest time deviation
- comparative bar charts across batteries
- pie or line charts for execution patterns
- drill-down views from battery to test to cache entry

## Interpretation

The most relevant indicators for the research dashboard are:

- number of charging stations
- station locations
- deviation time
- execution time

These values are the base for ranking, filtering, and visual comparison.
