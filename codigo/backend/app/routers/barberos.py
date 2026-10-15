from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencias import get_current_user_opcional, require_roles
from app.db import get_db
from app.models import Rol, Usuario
from app.schemas.barbero import BarberoIn, BarberoOut
from app.schemas.comun import OkOut
from app.services import barberos

router = APIRouter(prefix="/api/barbers", tags=["barberos"])
solo_admin = require_roles(Rol.ADMIN)


@router.get("", response_model=list[BarberoOut])
def listar(service_id: int | None = None, usuario: Usuario | None = Depends(get_current_user_opcional),
           db: Session = Depends(get_db)) -> list[Usuario]:
    return barberos.listar(db, incluir_inactivos=bool(usuario and usuario.role == Rol.ADMIN), servicio_id=service_id)


@router.post("", response_model=OkOut)
def crear(datos: BarberoIn, _: Usuario = Depends(solo_admin), db: Session = Depends(get_db)) -> OkOut:
    barberos.crear(db, datos)
    return OkOut()


@router.post("/{barbero_id}/toggle", response_model=OkOut)
def alternar(barbero_id: int, _: Usuario = Depends(solo_admin), db: Session = Depends(get_db)) -> OkOut:
    barberos.alternar(db, barbero_id)
    return OkOut()
