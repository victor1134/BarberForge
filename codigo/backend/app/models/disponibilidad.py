from datetime import date, time

from sqlalchemy import Date, ForeignKey, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Disponibilidad(Base):
    """Franja en la que un barbero puede atender. Está libre si no tiene una cita activa."""

    __tablename__ = "availability"
    __table_args__ = (UniqueConstraint("barber_id", "slot_date", "start_time"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    barber_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    slot_date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[time] = mapped_column(Time)
