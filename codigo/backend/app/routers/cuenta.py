from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencias import get_current_user
from app.db import get_db
from app.models import Usuario
from app.schemas.usuario import CuentaIn, CuentaOut, UsuarioOut
from app.services import usuarios

router = APIRouter(prefix="/api/me", tags=["cuenta"])


@router.get("", response_model=UsuarioOut)
def mi_usuario(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    return usuario


@router.patch("", response_model=CuentaOut)
def actualizar_cuenta(datos: CuentaIn, usuario: Usuario = Depends(get_current_user),
                      db: Session = Depends(get_db)) -> CuentaOut:
    return CuentaOut(user=UsuarioOut.model_validate(usuarios.actualizar_cuenta(db, usuario, datos)))
