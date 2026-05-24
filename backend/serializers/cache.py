from datetime import datetime
from typing import Any, List

from pydantic import BaseModel


class CacheCreate(BaseModel):
    prueba_id: int
    solver: str
    execution_time_seconds: float
    charged_stations: int
    charging_locations: List[dict[str, Any]]
    time_deviation_minutes: float
    bateria: Any
    carga: Any
    comment: str | None = None


class CacheOut(BaseModel):
    id: int
    prueba_id: int
    solver: str
    execution_time_seconds: float
    charged_stations: int
    charging_locations: List[dict[str, Any]]
    station_vector: List[int] | None = None
    time_deviation_minutes: float
    bateria: Any
    carga: Any
    comment: str | None = None
    timestamp: datetime

    class Config:
        from_attributes = True


class PostBateriaList(BaseModel):
    baterias: List[int]


# Backwards compatibility
CreateCache = CacheCreate

