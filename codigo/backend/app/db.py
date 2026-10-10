"""Motor de base de datos, sesiones y clase base de los modelos."""
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings


class Base(DeclarativeBase):
    pass


def _crear_motor():
    url = get_settings().url_bd
    if str(url).startswith("sqlite"):
        # SQLite en memoria (pruebas): una sola conexión compartida entre hilos.
        return create_engine(url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    return create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 5})


engine = _crear_motor()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def es_postgres(db: Session) -> bool:
    return db.get_bind().dialect.name == "postgresql"
