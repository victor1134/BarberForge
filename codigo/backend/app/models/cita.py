from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Index, Text, Time, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

ESTADOS_ACTIVOS = ("pendiente", "confirmada")
ESTADOS = (*ESTADOS_ACTIVOS, "completada", "inasistencia",
           "cancelada_cliente", "cancelada_admin", "cancelada_sin_confirmar")
_ACTIVA = text("status IN ('pendiente','confirmada')")


class Cita(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        # RN08: un barbero no puede tener dos citas activas en la misma franja.
        Index("uq_cita_activa", "barber_id", "appointment_date", "start_time", unique=True,
              postgresql_where=_ACTIVA, sqlite_where=_ACTIVA),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    barber_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    appointment_date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[time] = mapped_column(Time)
    status: Mapped[str] = mapped_column(Text, default="pendiente", server_default="pendiente")
    token_hash: Mapped[str | None] = mapped_column(Text)
    reminder_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    cliente: Mapped["Usuario"] = relationship(foreign_keys=[client_id], lazy="joined")  # noqa: F821
    barbero: Mapped["Usuario"] = relationship(foreign_keys=[barber_id], lazy="joined")  # noqa: F821
    servicio: Mapped["Servicio"] = relationship(lazy="joined")  # noqa: F821
