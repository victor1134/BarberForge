from datetime import date, time

from pydantic import BaseModel


class GenerarDisponibilidadIn(BaseModel):
    barber_id: int
    date_from: date
    date_to: date
    start: time = time(9)
    end: time = time(17)
    minutes: int = 30


class FranjaOut(BaseModel):
    date: str  # AAAA-MM-DD
    time: str  # HH:MM
