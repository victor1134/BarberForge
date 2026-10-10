"""Hora local de la barbería. Las fechas y horas de las citas se guardan en hora local (sin zona)."""
from datetime import UTC, date, datetime
from functools import lru_cache
from zoneinfo import ZoneInfo

from app.config import get_settings


@lru_cache
def zona() -> ZoneInfo:
    return ZoneInfo(get_settings().zona_horaria)


def ahora_local() -> datetime:
    """Fecha y hora actual en la zona de la barbería, sin tzinfo (igual que las citas)."""
    return datetime.now(zona()).replace(tzinfo=None)


def hoy() -> date:
    return ahora_local().date()


def ahora_utc() -> datetime:
    return datetime.now(UTC)
