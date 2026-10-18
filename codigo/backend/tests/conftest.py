"""Pruebas sobre SQLite en memoria. Las variables se fijan antes de importar la aplicación."""
import os

os.environ.update({
    "DATABASE_URL": "sqlite+pysqlite:///:memory:",
    "TAREAS_FONDO": "false",
    "JWT_SECRET": "secreto-de-pruebas-con-mas-de-32-caracteres",
    # Puertos cerrados: Ollama y SMTP fallan al instante y se prueban los caminos alternativos.
    "OLLAMA_URL": "http://127.0.0.1:9",
    "SMTP_HOST": "127.0.0.1",
    "SMTP_PORT": "9",
    "ADMIN_EMAIL": "",
    "ADMIN_PASSWORD": "",
})

from datetime import time, timedelta  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import db as bd  # noqa: E402
from app.core.seguridad import hash_password  # noqa: E402
from app.core.tiempo import hoy  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Rol, Servicio, Usuario  # noqa: E402
from app.services.disponibilidad import generar_franjas  # noqa: E402

CLAVE = "Clave12345"


@pytest.fixture(autouse=True)
def base_limpia():
    bd.Base.metadata.create_all(bd.engine)
    yield
    bd.Base.metadata.drop_all(bd.engine)


@pytest.fixture(autouse=True)
def sin_red(monkeypatch):
    """Sin Ollama ni SMTP: se prueban los caminos alternativos sin esperar conexiones fallidas."""
    import httpx

    def sin_llm(_prompt):
        raise httpx.ConnectError("sin Ollama en pruebas")

    monkeypatch.setattr("app.services.ia.embedding", lambda _texto: None)
    monkeypatch.setattr("app.services.ia.generar", sin_llm)
    monkeypatch.setattr("app.services.correo.enviar", lambda *a: False)
    # bcrypt con el mínimo de rondas para que las pruebas sean rápidas.
    import bcrypt
    original = bcrypt.gensalt
    monkeypatch.setattr(bcrypt, "gensalt", lambda rounds=4, prefix=b"2b": original(4, prefix))


@pytest.fixture
def db():
    with bd.SessionLocal() as sesion:
        yield sesion


@pytest.fixture
def client():
    return TestClient(app)


def crear_usuario(db, correo: str, rol: str, nombre: str = "Persona Prueba", **extra) -> Usuario:
    usuario = Usuario(email=correo, full_name=nombre, id_type="CC", id_number=correo, role=rol,
                      password_hash=hash_password(CLAVE), **extra)
    db.add(usuario)
    db.commit()
    return usuario


def token(client: TestClient, correo: str) -> dict[str, str]:
    r = client.post("/api/login", json={"email": correo, "password": CLAVE})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


@pytest.fixture
def catalogo(db):
    """Dos servicios, un barbero que ofrece ambos con agenda para los próximos días, un cliente y un admin."""
    corte = Servicio(name="Corte clásico", description="Máquina y tijera", price_cop=25000,
                     duration_minutes=30, service_type="corte")
    barba = Servicio(name="Barba perfilada", description="Navaja", price_cop=18000,
                     duration_minutes=20, service_type="barba")
    db.add_all([corte, barba])
    db.commit()
    barbero = crear_usuario(db, "carlos@demo.co", Rol.BARBERO, "Carlos Mena", servicios=[corte, barba])
    cliente = crear_usuario(db, "ana@correo.co", Rol.CLIENTE, "Ana Ruiz")
    admin = crear_usuario(db, "admin@correo.co", Rol.ADMIN, "Admin Barbería")
    manana = hoy() + timedelta(days=1)
    generar_franjas(db, barbero.id, manana, manana + timedelta(days=2), time(9), time(11), 30)
    return {"corte": corte, "barba": barba, "barbero": barbero, "cliente": cliente, "admin": admin}
