from pydantic import BaseModel

from app.schemas.barbero import BarberoOut
from app.schemas.servicio import ServicioOut


class OkOut(BaseModel):
    ok: bool = True


class SaludOut(BaseModel):
    servicio: str
    estado: str
    base_de_datos: str


class ReindexOut(BaseModel):
    embeddings_ok: bool


class BarberiaBase(BaseModel):
    id: int
    nombre: str
    direccion: str
    horario: str
    descripcion: str
    buzon_url: str


class BarberiaResumen(BarberiaBase):
    servicios: int
    barberos: int


class BarberiaDetalle(BarberiaBase):
    servicios: list[ServicioOut]
    barberos: list[BarberoOut]
