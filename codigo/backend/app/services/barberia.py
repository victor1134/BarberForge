"""Ficha de la barbería. El MVP atiende una sola barbería; la lista se arma desde esta ficha
para que sumar más barberías después no cambie la interfaz."""
from sqlalchemy.orm import Session

from app.config import get_settings
from app.schemas.barbero import BarberoOut
from app.schemas.comun import BarberiaBase, BarberiaDetalle, BarberiaResumen
from app.schemas.servicio import ServicioOut
from app.services import barberos as barberos_srv
from app.services import servicios as servicios_srv
from app.services.errores import NoEncontrado

ID_BARBERIA = 1


def ficha() -> BarberiaBase:
    s = get_settings()
    return BarberiaBase(
        id=ID_BARBERIA, nombre=s.barberia_nombre, direccion=s.barberia_direccion,
        horario="Lunes a sábado de 9:00 a 17:00 · domingos cerrado",
        descripcion="Corte, barba y tratamiento capilar con agenda en línea, recordatorios por correo "
                    "y un asistente con IA que responde a cualquier hora.",
        buzon_url=s.mailhog_url)


def listar(db: Session) -> list[BarberiaResumen]:
    return [BarberiaResumen(**ficha().model_dump(), servicios=len(servicios_srv.listar(db)),
                            barberos=len(barberos_srv.listar(db)))]


def detalle(db: Session, barberia_id: int) -> BarberiaDetalle:
    if barberia_id != ID_BARBERIA:
        raise NoEncontrado("Barbería no encontrada")
    return BarberiaDetalle(
        **ficha().model_dump(),
        servicios=[ServicioOut.model_validate(s) for s in servicios_srv.listar(db)],
        barberos=[BarberoOut.model_validate(b) for b in barberos_srv.listar(db)])
