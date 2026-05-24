from pydantic import BaseModel
from typing import Any
from datetime import datetime


class ResultCreate(BaseModel):
    """Datos de entrada para crear/actualizar un resultado"""
    prueba_id: int
    solver: str
    execution_time_seconds: float
    charged_stations: int
    charging_locations: list[dict[str, Any]]
    time_deviation_minutes: float
    bateria: dict[str, Any]
    carga: dict[str, Any]
    comment: str | None = None


class ResultOut(BaseModel):
    """Respuesta con datos de un resultado"""
    id: int
    prueba_id: int
    solver: str
    execution_time_seconds: float
    charged_stations: int
    charging_locations: list[dict[str, Any]]
    station_vector: list[int] | None = None
    time_deviation_minutes: float
    bateria: dict[str, Any]
    carga: dict[str, Any]
    comment: str | None = None
    timestamp: datetime

    class Config:
        from_attributes = True


class ResultDetailOut(ResultOut):
    """Resultado con información extendida"""
    pass
