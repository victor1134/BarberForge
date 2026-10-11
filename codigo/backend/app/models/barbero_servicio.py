from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db import Base

# Relación muchos a muchos: qué servicios ofrece cada barbero.
barbero_servicio = Table(
    "barber_services",
    Base.metadata,
    Column("barber_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("service_id", Integer, ForeignKey("services.id"), primary_key=True),
)
