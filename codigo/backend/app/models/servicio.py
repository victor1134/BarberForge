from sqlalchemy import Boolean, CheckConstraint, Integer, Text, true
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

TIPOS_SERVICIO = ("corte", "barba", "combo", "tratamiento")
PRECIO_MINIMO = 1000
DURACION_MINIMA = 10


class Servicio(Base):
    __tablename__ = "services"
    __table_args__ = (
        CheckConstraint(f"price_cop >= {PRECIO_MINIMO}", name="services_price_cop_check"),
        CheckConstraint(f"duration_minutes >= {DURACION_MINIMA}", name="services_duration_minutes_check"),
        CheckConstraint("service_type IN ('corte','barba','combo','tratamiento')", name="services_service_type_check"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    price_cop: Mapped[int] = mapped_column(Integer)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    service_type: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
