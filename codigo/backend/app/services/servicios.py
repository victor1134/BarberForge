"""Catálogo de servicios de la barbería."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Servicio
from app.models.servicio import DURACION_MINIMA, PRECIO_MINIMO, TIPOS_SERVICIO
from app.schemas.servicio import ServicioIn
from app.services.errores import DatosInvalidos, NoEncontrado


def listar(db: Session, incluir_inactivos: bool = False) -> list[Servicio]:
    q = select(Servicio).order_by(Servicio.id)
    if not incluir_inactivos:
        q = q.where(Servicio.is_active)
    return list(db.scalars(q))


def _validar(datos: ServicioIn) -> None:
    if not datos.name.strip():
        raise DatosInvalidos("Escribe el nombre del servicio")
    if (datos.price_cop < PRECIO_MINIMO or datos.duration_minutes < DURACION_MINIMA
            or datos.service_type not in TIPOS_SERVICIO):
        raise DatosInvalidos("Precio mínimo $1.000, duración mínima 10 min y tipo corte/barba/combo/tratamiento")


def _aplicar(servicio: Servicio, datos: ServicioIn) -> None:
    servicio.name = datos.name.strip()
    servicio.description = datos.description
    servicio.price_cop = datos.price_cop
    servicio.duration_minutes = datos.duration_minutes
    servicio.service_type = datos.service_type


def obtener(db: Session, servicio_id: int) -> Servicio:
    servicio = db.get(Servicio, servicio_id)
    if not servicio:
        raise NoEncontrado("Servicio no encontrado")
    return servicio


def crear(db: Session, datos: ServicioIn) -> Servicio:
    _validar(datos)
    servicio = Servicio(is_active=True)
    _aplicar(servicio, datos)
    db.add(servicio)
    db.commit()
    return servicio


def actualizar(db: Session, servicio_id: int, datos: ServicioIn) -> Servicio:
    _validar(datos)
    servicio = obtener(db, servicio_id)
    _aplicar(servicio, datos)
    db.commit()
    return servicio


def alternar(db: Session, servicio_id: int) -> Servicio:
    servicio = obtener(db, servicio_id)
    servicio.is_active = not servicio.is_active
    db.commit()
    return servicio
