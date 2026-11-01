from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.comun import BarberiaDetalle, BarberiaResumen
from app.services import barberia

router = APIRouter(prefix="/api/barberias", tags=["barberías"])


@router.get("", response_model=list[BarberiaResumen])
def listar(db: Session = Depends(get_db)) -> list[BarberiaResumen]:
    return barberia.listar(db)


@router.get("/{barberia_id}", response_model=BarberiaDetalle)
def detalle(barberia_id: int, db: Session = Depends(get_db)) -> BarberiaDetalle:
    return barberia.detalle(db, barberia_id)
