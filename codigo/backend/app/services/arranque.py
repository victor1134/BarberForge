"""Tareas de arranque y de fondo: migraciones, datos iniciales, indexado del asistente y recordatorios."""
import asyncio
import logging
from datetime import time, timedelta
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import select, text

from app import db as bd
from app.core.tiempo import hoy
from app.models import Rol, Usuario
from app.services import citas, rag, usuarios
from app.services.disponibilidad import generar_franjas

log = logging.getLogger(__name__)
RAIZ_BACKEND = Path(__file__).resolve().parents[2]
DIAS_DE_AGENDA = 7

# Estado visible en /api/health mientras la base de datos arranca.
ESTADO = {"db": False, "error": "iniciando"}


def migrar() -> None:
    """alembic upgrade head con un candado para que varias réplicas no migren a la vez."""
    cfg = Config(str(RAIZ_BACKEND / "alembic.ini"))
    cfg.set_main_option("script_location", str(RAIZ_BACKEND / "alembic"))
    with bd.engine.connect() as conn:
        conn.execute(text("SELECT pg_advisory_lock(7002)"))
        conn.commit()
        try:
            cfg.attributes["connection"] = conn
            command.upgrade(cfg, "head")
            conn.commit()
        finally:
            conn.execute(text("SELECT pg_advisory_unlock(7002)"))
            conn.commit()


def preparar_datos() -> None:
    """Administrador inicial (si hay variables) y agenda de la próxima semana para los barberos activos."""
    with bd.SessionLocal() as db:
        usuarios.asegurar_admin_inicial(db)
        for barbero_id in db.scalars(select(Usuario.id).where(Usuario.role == Rol.BARBERO, Usuario.is_active)):
            generar_franjas(db, barbero_id, hoy(), hoy() + timedelta(days=DIAS_DE_AGENDA), time(9), time(17), 30)


async def iniciar_base_de_datos() -> None:
    """Reintenta hasta que la base responda; el motivo del fallo queda visible en /api/health."""
    while True:
        try:
            await asyncio.to_thread(migrar)
            await asyncio.to_thread(preparar_datos)
            ESTADO.update(db=True, error="")
            log.info("base de datos lista")
            return
        except Exception as e:  # noqa: BLE001 - se informa en /api/health y se reintenta
            ESTADO.update(db=False, error=f"{type(e).__name__}: {str(e)[:160]}")
            log.warning("esperando base de datos: %s", ESTADO["error"])
            await asyncio.sleep(5)


def _reindexar() -> bool:
    with bd.SessionLocal() as db:
        return rag.reindexar(db)


async def indexar_asistente() -> None:
    """Indexa la base de conocimiento; reintenta mientras Ollama descarga los modelos."""
    while not ESTADO["db"]:
        await asyncio.sleep(2)
    for _ in range(40):
        try:
            if await asyncio.to_thread(_reindexar):
                return
        except Exception:  # noqa: BLE001
            log.exception("indexado del asistente")
        await asyncio.sleep(30)


def _ciclo_recordatorios() -> None:
    with bd.SessionLocal() as db:
        citas.procesar_recordatorios(db)


async def recordatorios() -> None:
    while True:
        try:
            if ESTADO["db"]:
                await asyncio.to_thread(_ciclo_recordatorios)
        except Exception:  # noqa: BLE001
            log.exception("recordatorios")
        await asyncio.sleep(60)
