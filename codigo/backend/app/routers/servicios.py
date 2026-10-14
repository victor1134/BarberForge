from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.core.dependencias import get_current_user_opcional, require_roles
from app.db import get_db
from app.models import Rol, Servicio, Usuario
from app.schemas.comun import OkOut
from app.schemas.servicio import ServicioIn, ServicioOut
from app.services import servicios
from app.services.rag import reindexar_en_segundo_plano

router = APIRouter(prefix="/api/services", tags=["servicios"])
solo_admin = require_roles(Rol.ADMIN)


@router.get("", response_model=list[ServicioOut])
def listar(usuario: Usuario | None = Depends(get_current_user_opcional),
           db: Session = Depends(get_db)) -> list[Servicio]:
    """Los visitantes y clientes ven los activos; el administrador ve también los inactivos."""
    return servicios.listar(db, incluir_inactivos=bool(usuario and usuario.role == Rol.ADMIN))


@router.post("", response_model=OkOut)
def crear(datos: ServicioIn, tareas: BackgroundTasks, _: Usuario = Depends(solo_admin),
          db: Session = Depends(get_db)) -> OkOut:
    servicios.crear(db, datos)
    tareas.add_task(reindexar_en_segundo_plano)  # el asistente aprende el cambio de catálogo
    return OkOut()


@router.put("/{servicio_id}", response_model=OkOut)
def actualizar(servicio_id: int, datos: ServicioIn, tareas: BackgroundTasks,
               _: Usuario = Depends(solo_admin), db: Session = Depends(get_db)) -> OkOut:
    servicios.actualizar(db, servicio_id, datos)
    tareas.add_task(reindexar_en_segundo_plano)
    return OkOut()


@router.post("/{servicio_id}/toggle", response_model=OkOut)
def alternar(servicio_id: int, tareas: BackgroundTasks, _: Usuario = Depends(solo_admin),
             db: Session = Depends(get_db)) -> OkOut:
    servicios.alternar(db, servicio_id)
    tareas.add_task(reindexar_en_segundo_plano)
    return OkOut()
