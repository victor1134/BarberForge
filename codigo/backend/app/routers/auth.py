from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.seguridad import crear_token
from app.db import get_db
from app.schemas.usuario import LoginIn, RegistroIn, SesionOut, SetupOut, UsuarioOut
from app.services import usuarios

router = APIRouter(prefix="/api", tags=["autenticación"])


@router.get("/setup", response_model=SetupOut)
def setup(db: Session = Depends(get_db)) -> SetupOut:
    """Indica si ya existe un administrador (si no, el próximo registro lo será)."""
    return SetupOut(hay_admin=usuarios.hay_admin(db))


@router.post("/register", response_model=SesionOut)
def registrar(datos: RegistroIn, db: Session = Depends(get_db)) -> SesionOut:
    usuario = usuarios.registrar(db, datos)
    return SesionOut(token=crear_token(usuario.id), user=UsuarioOut.model_validate(usuario))


@router.post("/login", response_model=SesionOut)
def login(datos: LoginIn, db: Session = Depends(get_db)) -> SesionOut:
    usuario = usuarios.autenticar(db, datos.email, datos.password)
    return SesionOut(token=crear_token(usuario.id), user=UsuarioOut.model_validate(usuario))
