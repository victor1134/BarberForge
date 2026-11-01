from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.comun import SaludOut
from app.services.arranque import ESTADO

router = APIRouter(tags=["salud"])


@router.get("/api/health", response_model=SaludOut)
def salud_general() -> SaludOut:
    """Diagnóstico rápido para humanos: muestra el motivo si la base de datos falla."""
    return SaludOut(servicio="barberforge-ai", estado="ok",
                    base_de_datos="ok" if ESTADO["db"] else "sin conexión: " + ESTADO["error"])


@router.get("/health")
def liveness() -> dict[str, str]:
    """Liveness probe de Kubernetes: el proceso responde."""
    return {"estado": "ok"}


@router.get("/health/db")
def readiness(db: Session = Depends(get_db)):
    """Readiness probe: la base responde y las migraciones terminaron."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:  # noqa: BLE001
        return JSONResponse(status_code=503, content={"estado": "error", "detalle": type(e).__name__})
    if not ESTADO["db"]:
        return JSONResponse(status_code=503, content={"estado": "iniciando", "detalle": ESTADO["error"]})
    return {"estado": "ok"}
