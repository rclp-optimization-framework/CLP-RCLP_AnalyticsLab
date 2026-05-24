from pydantic import BaseModel
from serializers.prueba import ListPruebaCreateAux

class BateriaCreate(BaseModel):
    nombre: str
    pruebas: ListPruebaCreateAux | None = None




