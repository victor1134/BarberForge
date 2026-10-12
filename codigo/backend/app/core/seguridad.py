"""Contraseñas (bcrypt), tokens JWT y tokens de un solo uso."""
import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.config import get_settings

ALGORITMO = "HS256"


def hash_password(clave: str) -> str:
    return bcrypt.hashpw(clave.encode(), bcrypt.gensalt()).decode()


def verificar_password(clave: str, hash_guardado: str) -> bool:
    try:
        return bcrypt.checkpw(clave.encode(), hash_guardado.encode())
    except ValueError:
        return False


def crear_token(usuario_id: int) -> str:
    s = get_settings()
    exp = datetime.now(UTC) + timedelta(hours=s.jwt_horas)
    return jwt.encode({"sub": str(usuario_id), "exp": exp}, s.jwt_secret, ALGORITMO)


def leer_token(token: str) -> int | None:
    """Devuelve el id del usuario o None si el token es inválido o venció."""
    try:
        datos = jwt.decode(token, get_settings().jwt_secret, [ALGORITMO])
        return int(datos["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None


def nuevo_token_un_uso() -> tuple[str, str]:
    """Token para enlaces de correo: se envía el token y se guarda solo su hash."""
    token = secrets.token_urlsafe(24)
    return token, hash_token(token)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
