"""Dependencias de FastAPI: usuario autenticado y control de roles."""
from collections.abc import Callable

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.seguridad import leer_token
from app.db import get_db
from app.models import Usuario
from app.services.errores import NoAutenticado, SinPermiso


def get_current_user_opcional(authorization: str | None = Header(None),
                              db: Session = Depends(get_db)) -> Usuario | None:
    """Usuario del token Bearer, o None si no hay sesión (visitante)."""
    if not authorization:
        return None
    uid = leer_token(authorization.split()[-1])
    if uid is None:
        return None
    usuario = db.get(Usuario, uid)
    return usuario if usuario and usuario.is_active else None


def get_current_user(usuario: Usuario | None = Depends(get_current_user_opcional)) -> Usuario:
    if usuario is None:
        raise NoAutenticado("Inicia sesión para continuar")
    return usuario


def require_roles(*roles: str) -> Callable[..., Usuario]:
    def dependencia(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.role not in roles:
            raise SinPermiso("No autorizado")
        return usuario
    return dependencia
