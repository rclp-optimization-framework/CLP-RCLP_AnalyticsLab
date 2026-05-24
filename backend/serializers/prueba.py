from pydantic import BaseModel, ConfigDict
from typing import List, Any
from datetime import datetime

class PruebaCreateAux(BaseModel):

    # Campos mínimos para generación automática
    num_buses: int
    num_stations: int

    # Campos opcionales para creación manual
    max_stops: int | None = None
    num_stops: List[int] | None = None
    st_bi: List[List[int]] | None = None
    d: List[List[int]] | None = None
    t: List[List[int]] | None = None
    tau_bi: List[List[int]] | None = None
    consumo_max: int | None = None
    consumo_min: int | None = None
    alpha: float | None = None
    mu: float | None = None
    sm: int | None = None
    psi: float | None = None
    beta: float | None = None
    m: int | None = None

    model_config = ConfigDict(from_attributes=True)

class ListPruebaCreateAux(BaseModel):

    pruebas: List[PruebaCreateAux]

class PruebaCreate(BaseModel):
    bateria_id: int
    data: PruebaCreateAux

class PruebaOut(BaseModel):
    """
    Modelo flexible para salida de pruebas.
    Acepta Any para campos de array que pueden tener valores inconsistentes en BD.
    """
    id: int
    bateria_id: int
    num_buses: int
    num_stations: int
    max_stops: int 
    num_stops: Any = None
    st_bi: Any = None
    d: Any = None
    t: Any = None
    tau_bi: Any = None
    consumo_max: int
    consumo_min: int 
    alpha: float
    mu: float
    sm: int 
    psi: float
    beta: float
    m: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class PruebaUpdate(BaseModel):
    num_buses: int | None = None
    num_stations: int | None = None
    max_stops: int | None = None
    num_stops: List[int] | None = None
    st_bi: List[List[int]] | None = None
    d: List[List[int]] | None = None
    t: List[List[int]] | None = None
    tau_bi: List[List[int]] | None = None
    consumo_max: int | None = None
    consumo_min: int | None = None
    alpha: float | None = None
    mu: float | None = None
    sm: int | None = None
    psi: float | None = None
    beta: float | None = None
    m: int | None = None

    model_config = ConfigDict(from_attributes=True)