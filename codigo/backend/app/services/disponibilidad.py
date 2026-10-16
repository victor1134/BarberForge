"""Franjas de atención de los barberos y consulta de franjas libres."""
from datetime import date, datetime, time, timedelta

from sqlalchemy import and_, delete, exists, or_, select
from sqlalchemy.orm import Session

from app.core.tiempo import ahora_local, hoy
from app.models import Cita, Disponibilidad, Rol, Usuario
from app.models.cita import ESTADOS_ACTIVOS
from app.schemas.disponibilidad import GenerarDisponibilidadIn
from app.services import barberos as barberos_srv
from app.services.errores import DatosInvalidos

DOMINGO = 6
DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]


def generar_franjas(db: Session, barbero_id: int, desde: date, hasta: date,
                    inicio: time, fin: time, minutos: int) -> int:
    """Crea las franjas de lunes a sábado sin duplicar las existentes. Devuelve cuántas creó."""
    existentes = {(d.slot_date, d.start_time) for d in db.scalars(
        select(Disponibilidad).where(Disponibilidad.barber_id == barbero_id,
                                     Disponibilidad.slot_date.between(desde, hasta)))}
    nuevas = 0
    dia = desde
    while dia <= hasta:
        if dia.weekday() != DOMINGO:
            t, limite = datetime.combine(dia, inicio), datetime.combine(dia, fin)
            while t < limite:
                if (dia, t.time()) not in existentes:
                    db.add(Disponibilidad(barber_id=barbero_id, slot_date=dia, start_time=t.time()))
                    nuevas += 1
                t += timedelta(minutes=minutos)
        dia += timedelta(days=1)
    db.commit()
    return nuevas


def generar(db: Session, datos: GenerarDisponibilidadIn) -> int:
    if datos.minutes < 10 or datos.date_to < datos.date_from or datos.end <= datos.start:
        raise DatosInvalidos("Rango de fechas, horas o duración inválidos")
    barberos_srv.obtener(db, datos.barber_id)
    return generar_franjas(db, datos.barber_id, datos.date_from, datos.date_to, datos.start, datos.end, datos.minutes)


def franjas_libres(db: Session, barbero_id: int, limite: int = 80,
                   fecha: date | None = None, hora: time | None = None) -> list[Disponibilidad]:
    """Franjas futuras de un barbero activo que no tienen una cita activa."""
    ahora = ahora_local()
    ocupada = exists().where(Cita.barber_id == Disponibilidad.barber_id,
                             Cita.appointment_date == Disponibilidad.slot_date,
                             Cita.start_time == Disponibilidad.start_time,
                             Cita.status.in_(ESTADOS_ACTIVOS))
    q = (select(Disponibilidad)
         .join(Usuario, Usuario.id == Disponibilidad.barber_id)
         .where(Usuario.is_active, Usuario.role == Rol.BARBERO, Disponibilidad.barber_id == barbero_id,
                or_(Disponibilidad.slot_date > ahora.date(),
                    and_(Disponibilidad.slot_date == ahora.date(), Disponibilidad.start_time > ahora.time())),
                ~ocupada)
         .order_by(Disponibilidad.slot_date, Disponibilidad.start_time)
         .limit(limite))
    if fecha is not None:
        q = q.where(Disponibilidad.slot_date == fecha)
    if hora is not None:
        q = q.where(Disponibilidad.start_time == hora)
    return list(db.scalars(q))


def esta_libre(db: Session, barbero_id: int, fecha: date, hora: time) -> bool:
    return bool(franjas_libres(db, barbero_id, limite=1, fecha=fecha, hora=hora))


def etiqueta(franja: Disponibilidad) -> str:
    d = franja.slot_date
    return f"{DIAS[d.weekday()]} {d:%d/%m} · {franja.start_time:%H:%M}"


def borrar_antiguas(db: Session) -> None:
    db.execute(delete(Disponibilidad).where(Disponibilidad.slot_date < hoy() - timedelta(days=1)))
    db.commit()
