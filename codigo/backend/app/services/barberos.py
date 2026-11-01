"""Barberos: alta, activación y servicios que ofrecen."""
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.seguridad import hash_password
from app.models import Rol, Servicio, Usuario
from app.schemas.barbero import BarberoIn
from app.services.errores import Conflicto, DatosInvalidos, NoEncontrado
from app.services.usuarios import validar_clave, validar_correo


def listar(db: Session, incluir_inactivos: bool = False, servicio_id: int | None = None) -> list[Usuario]:
    q = select(Usuario).where(Usuario.role == Rol.BARBERO).order_by(Usuario.id)
    if not incluir_inactivos:
        q = q.where(Usuario.is_active)
    barberos = list(db.scalars(q))
    if servicio_id is not None:
        barberos = [b for b in barberos if servicio_id in b.service_ids]
    return barberos


def obtener(db: Session, barbero_id: int) -> Usuario:
    barbero = db.get(Usuario, barbero_id)
    if not barbero or barbero.role != Rol.BARBERO:
        raise NoEncontrado("Barbero no encontrado")
    return barbero


def crear(db: Session, datos: BarberoIn) -> Usuario:
    validar_clave(datos.password)
    correo = validar_correo(datos.email)
    if not datos.full_name.strip() or not datos.id_number.strip():
        raise DatosInvalidos("Escribe el nombre y la identificación del barbero")
    if datos.service_ids:
        servicios = list(db.scalars(select(Servicio).where(Servicio.id.in_(set(datos.service_ids)))))
    else:  # sin selección, ofrece todos los servicios activos
        servicios = list(db.scalars(select(Servicio).where(Servicio.is_active)))
    barbero = Usuario(email=correo, full_name=datos.full_name.strip(), id_type="CC",
                      id_number=datos.id_number.strip(), password_hash=hash_password(datos.password),
                      role=Rol.BARBERO, specialties=datos.specialties.strip()[:200], servicios=servicios)
    db.add(barbero)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise Conflicto("El correo o la identificación ya están registrados") from None
    return barbero


def alternar(db: Session, barbero_id: int) -> Usuario:
    barbero = obtener(db, barbero_id)
    barbero.is_active = not barbero.is_active
    db.commit()
    return barbero
