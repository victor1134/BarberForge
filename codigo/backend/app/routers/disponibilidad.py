from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencias import require_roles
from app.db import get_db
from app.models import Rol, Usuario
from app.schemas.comun import OkOut
from app.schemas.disponibilidad import FranjaOut, GenerarDisponibilidadIn
from app.services import disponibilidad

router = APIRouter(prefix="/api/availability", tags=["disponibilidad"])


@router.post("", response_model=OkOut)
def generar(datos: GenerarDisponibilidadIn, _: Usuario = Depends(require_roles(Rol.ADMIN)),
            db: Session = Depends(get_db)) -> OkOut:
    disponibilidad.generar(db, datos)
    return OkOut()


@router.get("", response_model=list[FranjaOut])
def libres(barber_id: int, db: Session = Depends(get_db)) -> list[FranjaOut]:
    return [FranjaOut(date=str(f.slot_date), time=f"{f.start_time:%H:%M}")
            for f in disponibilidad.franjas_libres(db, barber_id)]
