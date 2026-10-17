"""Agendamiento, consulta, cancelación y cierre de citas; recordatorios y confirmación por correo."""
from datetime import datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.seguridad import hash_token, nuevo_token_un_uso
from app.core.tiempo import ahora_local, ahora_utc
from app.models import Cita, Rol, Servicio, Usuario
from app.models.cita import ESTADOS_ACTIVOS
from app.schemas.cita import CitaIn, CitaOut
from app.services import correo
from app.services import disponibilidad as disp
from app.services.errores import Conflicto, DatosInvalidos, NoEncontrado

MINUTOS_RECORDATORIO = 40   # el correo sale 40 min antes de la cita
MINUTOS_PARA_CONFIRMAR = 15  # si no confirma en 15 min, se cancela y la franja queda libre
ESTADOS_CIERRE = ("completada", "inasistencia")


# ---------- agendar ----------

def agendar(db: Session, cliente: Usuario, datos: CitaIn) -> Cita:
    servicio = db.get(Servicio, datos.service_id)
    if not servicio or not servicio.is_active:
        raise NoEncontrado("Servicio no disponible")
    barbero = db.get(Usuario, datos.barber_id)
    if (not barbero or barbero.role != Rol.BARBERO or not barbero.is_active
            or servicio.id not in barbero.service_ids):
        raise DatosInvalidos("Ese barbero no ofrece el servicio elegido")

    cita = None
    if disp.esta_libre(db, barbero.id, datos.date, datos.time):
        cita = Cita(client_id=cliente.id, barber_id=barbero.id, service_id=servicio.id,
                    appointment_date=datos.date, start_time=datos.time, status="pendiente")
        try:  # el índice único parcial impide la doble reserva aunque dos clientes lleguen a la vez (RN08)
            with db.begin_nested():
                db.add(cita)
            db.commit()
        except IntegrityError:
            db.rollback()
            cita = None
    if cita is None:
        alternativas = [{"date": str(f.slot_date), "time": f"{f.start_time:%H:%M}"}
                        for f in disp.franjas_libres(db, barbero.id, limite=3)]
        raise Conflicto("Esa franja ya no está disponible", alternatives=alternativas)
    return cita


# ---------- consultar ----------

def listar_para(db: Session, usuario: Usuario, limite: int = 200) -> list[CitaOut]:
    """El cliente ve sus citas, el barbero su agenda y el administrador todas."""
    q = select(Cita).order_by(Cita.appointment_date.desc(), Cita.start_time).limit(limite)
    if usuario.role == Rol.CLIENTE:
        q = q.where(Cita.client_id == usuario.id)
    elif usuario.role == Rol.BARBERO:
        q = q.where(Cita.barber_id == usuario.id)
    return [CitaOut(id=c.id, date=c.appointment_date, time=f"{c.start_time:%H:%M}", status=c.status,
                    service=c.servicio.name, barber=c.barbero.full_name, client=c.cliente.full_name)
            for c in db.scalars(q).unique()]


def _obtener(db: Session, cita_id: int) -> Cita:
    cita = db.get(Cita, cita_id)
    if not cita:
        raise NoEncontrado("Cita no encontrada")
    return cita


# ---------- cambiar estado ----------

def cancelar(db: Session, usuario: Usuario, cita_id: int) -> None:
    cita = _obtener(db, cita_id)
    if usuario.role == Rol.CLIENTE and cita.client_id != usuario.id:
        raise NoEncontrado("Cita no encontrada")
    if cita.status not in ESTADOS_ACTIVOS:
        raise DatosInvalidos("La cita ya no está activa")
    cita.status = "cancelada_admin" if usuario.role == Rol.ADMIN else "cancelada_cliente"
    cita.token_hash = None
    db.commit()


def cerrar(db: Session, usuario: Usuario, cita_id: int, estado: str) -> None:
    if estado not in ESTADOS_CIERRE:
        raise DatosInvalidos("Estado inválido")
    cita = _obtener(db, cita_id)
    if usuario.role == Rol.BARBERO and cita.barber_id != usuario.id:
        raise NoEncontrado("Cita no encontrada")
    if cita.status != "confirmada":
        raise DatosInvalidos("Solo se puede cerrar una cita confirmada")
    cita.status = estado
    db.commit()


# ---------- recordatorio y confirmación ----------

def enviar_recordatorio(db: Session, cita_id: int) -> bool:
    """Envía el correo con el enlace de confirmación de un solo uso. Solo para citas pendientes."""
    cita = db.get(Cita, cita_id)
    if not cita or cita.status != "pendiente":
        return False
    token, token_hash = nuevo_token_un_uso()
    cita.token_hash, cita.reminder_sent_at = token_hash, ahora_utc()
    db.commit()
    url = get_settings().public_url.rstrip("/")
    correo.enviar(cita.cliente.email, "Confirma tu cita en BarberForge AI",
                  f"Tu cita de {cita.servicio.name} es el {cita.appointment_date} a las {cita.start_time:%H:%M}.\n"
                  f"Confirma en los próximos {MINUTOS_PARA_CONFIRMAR} minutos: {url}/api/confirm/{token}\n"
                  "Si no confirmas, la cita se cancelará y la franja quedará libre.")
    return True


def recordar(db: Session, cita_id: int) -> None:
    if not enviar_recordatorio(db, cita_id):
        raise DatosInvalidos("Solo se envía recordatorio a citas pendientes")


def confirmar_por_token(db: Session, token: str) -> bool:
    limite = ahora_utc() - timedelta(minutes=MINUTOS_PARA_CONFIRMAR)
    cita = db.scalar(select(Cita).where(Cita.token_hash == hash_token(token), Cita.status == "pendiente",
                                        Cita.reminder_sent_at > limite))
    if not cita:
        return False
    cita.status, cita.token_hash = "confirmada", None
    db.commit()
    return True


def procesar_recordatorios(db: Session) -> None:
    """Tarea periódica: envía recordatorios próximos y cancela las citas que no se confirmaron a tiempo."""
    ahora = ahora_local()
    ventana = ahora + timedelta(minutes=MINUTOS_RECORDATORIO)
    pendientes = db.scalars(select(Cita).where(
        Cita.status == "pendiente", Cita.reminder_sent_at.is_(None),
        Cita.appointment_date.between(ahora.date(), ventana.date())))
    for cita in list(pendientes.unique()):
        if ahora <= datetime.combine(cita.appointment_date, cita.start_time) <= ventana:
            enviar_recordatorio(db, cita.id)

    vencidas = ahora_utc() - timedelta(minutes=MINUTOS_PARA_CONFIRMAR)
    db.execute(update(Cita)
               .where(Cita.status == "pendiente", Cita.reminder_sent_at < vencidas)
               .values(status="cancelada_sin_confirmar", token_hash=None))
    db.commit()
    disp.borrar_antiguas(db)
