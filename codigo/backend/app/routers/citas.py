from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.dependencias import require_roles
from app.db import get_db
from app.models import Rol, Usuario
from app.schemas.cita import CitaCreadaOut, CitaIn, CitaOut, EstadoCitaIn
from app.schemas.comun import OkOut
from app.services import citas

router = APIRouter(prefix="/api", tags=["citas"])
todos = require_roles(Rol.CLIENTE, Rol.BARBERO, Rol.ADMIN)


@router.post("/appointments", response_model=CitaCreadaOut)
def agendar(datos: CitaIn, usuario: Usuario = Depends(require_roles(Rol.CLIENTE)),
            db: Session = Depends(get_db)) -> CitaCreadaOut:
    return CitaCreadaOut(id=citas.agendar(db, usuario, datos).id)


@router.get("/appointments", response_model=list[CitaOut])
def listar(usuario: Usuario = Depends(todos), db: Session = Depends(get_db)) -> list[CitaOut]:
    return citas.listar_para(db, usuario)


@router.post("/appointments/{cita_id}/cancel", response_model=OkOut)
def cancelar(cita_id: int, usuario: Usuario = Depends(require_roles(Rol.CLIENTE, Rol.ADMIN)),
             db: Session = Depends(get_db)) -> OkOut:
    citas.cancelar(db, usuario, cita_id)
    return OkOut()


@router.patch("/appointments/{cita_id}/status", response_model=OkOut)
def cerrar(cita_id: int, datos: EstadoCitaIn, usuario: Usuario = Depends(require_roles(Rol.BARBERO, Rol.ADMIN)),
           db: Session = Depends(get_db)) -> OkOut:
    citas.cerrar(db, usuario, cita_id, datos.status)
    return OkOut()


@router.post("/appointments/{cita_id}/remind", response_model=OkOut)
def recordar(cita_id: int, _: Usuario = Depends(require_roles(Rol.ADMIN)), db: Session = Depends(get_db)) -> OkOut:
    citas.recordar(db, cita_id)
    return OkOut()


@router.get("/confirm/{token}", response_class=HTMLResponse)
def confirmar(token: str, db: Session = Depends(get_db)) -> str:
    """Enlace de un solo uso que llega en el correo de recordatorio."""
    return _pagina_confirmacion(citas.confirmar_por_token(db, token))


def _pagina_confirmacion(ok: bool) -> str:
    mensaje = "¡Cita confirmada! Te esperamos." if ok else "El enlace venció o ya fue usado."
    color, icono = ("#06a77d", "✅") if ok else ("#e63946", "⏰")
    return (
        "<!DOCTYPE html><html lang='es'><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'><title>BarberForge AI</title>"
        "<body style='margin:0;min-height:100vh;display:grid;place-items:center;background:#fff8ec;"
        "font-family:system-ui,sans-serif'>"
        f"<div style='text-align:center;background:#fff;padding:3rem 2.5rem;border-radius:20px;"
        f"border-top:8px solid {color};box-shadow:0 20px 50px rgba(20,33,61,.12)'>"
        f"<div style='font-size:3rem'>{icono}</div><h2 style='color:#14213d'>{mensaje}</h2>"
        "<p style='color:#667085'>BarberForge AI</p></div></body></html>")
