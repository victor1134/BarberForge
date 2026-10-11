from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Text, UniqueConstraint, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.barbero_servicio import barbero_servicio


class Rol(StrEnum):
    CLIENTE = "cliente"
    BARBERO = "barbero"
    ADMIN = "administrador"


class Usuario(Base):
    """Clientes, barberos y administradores comparten la tabla; el rol los distingue."""

    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("id_type", "id_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(Text, unique=True)
    full_name: Mapped[str] = mapped_column(Text)
    id_type: Mapped[str] = mapped_column(Text)
    id_number: Mapped[str] = mapped_column(Text)
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
    policy_accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    specialties: Mapped[str] = mapped_column(Text, default="", server_default="")
    style_pref: Mapped[str] = mapped_column(Text, default="", server_default="")

    # Solo aplica a barberos: servicios que ofrece.
    servicios: Mapped[list["Servicio"]] = relationship(  # noqa: F821
        secondary=barbero_servicio, lazy="selectin", order_by="Servicio.id")

    @property
    def service_ids(self) -> list[int]:
        return [s.id for s in self.servicios]
