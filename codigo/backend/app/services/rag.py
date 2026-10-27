"""Base de conocimiento del asistente: indexado con embeddings y búsqueda con filtro por rol."""
import logging
import re

from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from app.db import es_postgres
from app.models import FragmentoConocimiento, Rol, Servicio, Usuario
from app.models.conocimiento import NIVEL_INTERNO, NIVEL_PUBLICO
from app.services import ia

log = logging.getLogger(__name__)

# Documentos fijos de la barbería: (fuente, nivel de acceso, contenido).
DOCUMENTOS = [
    ("Preguntas frecuentes", NIVEL_PUBLICO,
     "Horario: lunes a sábado de 9:00 a 17:00, domingos cerrado. Dirección: Popayán, Cauca. "
     "Se agenda desde la plataforma o por este chat."),
    ("Políticas de la barbería", NIVEL_PUBLICO,
     "Puedes cancelar desde Mis citas. Si no confirmas el recordatorio enviado 40 minutos antes, "
     "la cita se cancela a los 15 minutos y la franja queda libre."),
    ("Guía de estilos", NIVEL_PUBLICO,
     "Fade bajo para rostro ovalado; barba perfilada con navaja para rostro redondo. "
     "Usa producto mate y repite el corte cada dos semanas."),
    ("Manual de procedimientos", NIVEL_INTERNO,
     "Higiene: desinfectar máquinas y peines con barbicida entre clientes y cambiar la capa. "
     "Caja: registrar cada servicio completado antes de llamar al siguiente cliente."),
]


def _texto_servicio(s: Servicio) -> str:
    precio = f"{s.price_cop:,}".replace(",", ".")
    return (f"{s.name} ({s.service_type}): {s.description} Precio ${precio} COP. "
            f"Duración {s.duration_minutes} minutos.")


def reindexar(db: Session) -> bool:
    """Reconstruye la base de conocimiento. Devuelve False si algún embedding no se pudo calcular."""
    servicios = db.scalars(select(Servicio).where(Servicio.is_active).order_by(Servicio.id))
    items = [("Catálogo de servicios", NIVEL_PUBLICO, _texto_servicio(s)) for s in servicios] + DOCUMENTOS
    fragmentos, todo_ok = [], True
    for fuente, nivel, contenido in items:
        # Si Ollama no responde, no se insiste en cada fragmento: se guardan sin vector
        # (la búsqueda por palabras clave funciona igual) y la tarea de arranque reintenta luego.
        vector = ia.embedding(contenido) if todo_ok else None
        todo_ok = todo_ok and vector is not None
        fragmentos.append(FragmentoConocimiento(source=fuente, content=contenido, access_level=nivel, embedding=vector))
    db.execute(delete(FragmentoConocimiento))
    db.add_all(fragmentos)
    db.commit()
    return todo_ok


def reindexar_en_segundo_plano() -> None:
    """Para BackgroundTasks: abre su propia sesión y nunca propaga errores."""
    from app import db as bd
    try:
        with bd.SessionLocal() as db:
            reindexar(db)
    except Exception:  # noqa: BLE001 - una falla del indexado no debe afectar la petición
        log.exception("No se pudo reindexar el asistente")


def niveles_para(usuario: Usuario | None) -> list[str]:
    """Filtro por rol: solo barberos y administradores ven los documentos internos."""
    if usuario and usuario.role in (Rol.BARBERO, Rol.ADMIN):
        return [NIVEL_PUBLICO, NIVEL_INTERNO]
    return [NIVEL_PUBLICO]


def buscar(db: Session, pregunta: str, niveles: list[str], limite: int = 3) -> list[FragmentoConocimiento]:
    """Búsqueda semántica con pgvector; si no hay embeddings, búsqueda por palabras clave."""
    base = select(FragmentoConocimiento).where(FragmentoConocimiento.access_level.in_(niveles))
    resultados: list[FragmentoConocimiento] = []
    if es_postgres(db):
        vector = ia.embedding(pregunta)
        if vector:
            resultados = list(db.scalars(
                base.where(FragmentoConocimiento.embedding.is_not(None))
                .order_by(FragmentoConocimiento.embedding.cosine_distance(vector)).limit(limite)))
    palabras = re.findall(r"\w{4,}", pregunta.lower())[:6]
    if not resultados and palabras:
        resultados = list(db.scalars(base.where(
            or_(*[func.lower(FragmentoConocimiento.content).like(f"%{p}%") for p in palabras])).limit(limite)))
    return resultados
