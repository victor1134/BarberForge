from datetime import date, time

from pydantic import BaseModel


class CitaIn(BaseModel):
    barber_id: int
    service_id: int
    date: date
    time: time


class CitaCreadaOut(BaseModel):
    id: int


class CitaOut(BaseModel):
    id: int
    date: date
    time: str  # HH:MM
    status: str
    service: str
    barber: str
    client: str


class EstadoCitaIn(BaseModel):
    status: str
