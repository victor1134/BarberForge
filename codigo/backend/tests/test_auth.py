from tests.conftest import token

REGISTRO = {"email": "Ana@Correo.co", "full_name": "Ana Ruiz", "id_type": "CC", "id_number": "123",
            "password": "Clave12345", "accept_policy": True}


def test_primer_registro_queda_como_administrador_y_luego_clientes(client):
    assert client.get("/api/setup").json() == {"hay_admin": False}
    r = client.post("/api/register", json=REGISTRO)
    assert r.status_code == 200
    assert r.json()["user"]["role"] == "administrador"
    assert r.json()["user"]["email"] == "ana@correo.co"
    assert client.get("/api/setup").json() == {"hay_admin": True}

    r2 = client.post("/api/register", json={**REGISTRO, "email": "luis@correo.co", "id_number": "456"})
    assert r2.json()["user"]["role"] == "cliente"


def test_registro_valida_datos(client):
    casos = [
        ({"accept_policy": False}, "política"),
        ({"password": "corta"}, "8 caracteres"),
        ({"email": "sin-arroba"}, "correo"),
        ({"id_type": "XX"}, "identificación"),
        ({"full_name": "  "}, "nombre"),
    ]
    for cambio, texto in casos:
        r = client.post("/api/register", json={**REGISTRO, **cambio})
        assert r.status_code == 400
        assert texto in r.json()["detail"]


def test_registro_duplicado_da_409(client):
    client.post("/api/register", json=REGISTRO)
    r = client.post("/api/register", json={**REGISTRO, "id_number": "999"})
    assert r.status_code == 409


def test_login_y_me(client):
    client.post("/api/register", json=REGISTRO)
    r = client.post("/api/login", json={"email": "ana@correo.co", "password": "mala"})
    assert r.status_code == 401
    cab = token(client, "ana@correo.co")
    assert client.get("/api/me", headers=cab).json()["full_name"] == "Ana Ruiz"


def test_me_sin_token_da_401(client):
    assert client.get("/api/me").status_code == 401
    assert client.get("/api/me", headers={"Authorization": "Bearer basura"}).status_code == 401


def test_actualizar_cuenta(client, catalogo):
    cab = token(client, "ana@correo.co")
    r = client.patch("/api/me", headers=cab, json={"full_name": "Ana María", "style_pref": "fade bajo"})
    assert r.json()["user"]["full_name"] == "Ana María"
    assert r.json()["user"]["style_pref"] == "fade bajo"

    r = client.patch("/api/me", headers=cab, json={"current_password": "mala", "new_password": "NuevaClave1"})
    assert r.status_code == 400
    r = client.patch("/api/me", headers=cab, json={"current_password": "Clave12345", "new_password": "NuevaClave1"})
    assert r.status_code == 200
    assert client.post("/api/login", json={"email": "ana@correo.co", "password": "NuevaClave1"}).status_code == 200

    r = client.patch("/api/me", headers=cab, json={"email": "carlos@demo.co"})
    assert r.status_code == 409


def test_admin_inicial_por_variables(db, monkeypatch):
    from app.config import get_settings
    from app.models import Usuario
    from app.services.usuarios import asegurar_admin_inicial
    monkeypatch.setattr(get_settings(), "admin_email", "jefe@barberia.co")
    monkeypatch.setattr(get_settings(), "admin_password", "ClaveJefe123")
    asegurar_admin_inicial(db)
    asegurar_admin_inicial(db)  # idempotente
    admins = db.query(Usuario).filter_by(email="jefe@barberia.co").all()
    assert len(admins) == 1 and admins[0].role == "administrador"
