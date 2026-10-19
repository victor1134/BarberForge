from tests.conftest import token

NUEVO = {"email": "luis@demo.co", "full_name": "Luis Ortiz", "id_number": "777", "password": "Clave12345",
         "specialties": "Tratamientos"}


def test_listar_y_filtrar_por_servicio(client, catalogo):
    barberos = client.get("/api/barbers").json()
    assert barberos[0]["full_name"] == "Carlos Mena"
    assert sorted(barberos[0]["service_ids"]) == sorted([catalogo["corte"].id, catalogo["barba"].id])
    assert client.get("/api/barbers", params={"service_id": 999}).json() == []


def test_crear_barbero_con_servicios_elegidos(client, catalogo):
    admin = token(client, "admin@correo.co")
    r = client.post("/api/barbers", json={**NUEVO, "service_ids": [catalogo["barba"].id]}, headers=admin)
    assert r.status_code == 200
    luis = next(b for b in client.get("/api/barbers").json() if b["full_name"] == "Luis Ortiz")
    assert luis["service_ids"] == [catalogo["barba"].id]


def test_crear_barbero_sin_servicios_ofrece_todos(client, catalogo):
    client.post("/api/barbers", json=NUEVO, headers=token(client, "admin@correo.co"))
    luis = next(b for b in client.get("/api/barbers").json() if b["full_name"] == "Luis Ortiz")
    assert len(luis["service_ids"]) == 2


def test_barbero_duplicado_y_permisos(client, catalogo):
    admin = token(client, "admin@correo.co")
    assert client.post("/api/barbers", json=NUEVO, headers=token(client, "ana@correo.co")).status_code == 403
    client.post("/api/barbers", json=NUEVO, headers=admin)
    assert client.post("/api/barbers", json=NUEVO, headers=admin).status_code == 409


def test_desactivar_barbero_lo_oculta_al_publico(client, catalogo):
    admin = token(client, "admin@correo.co")
    client.post(f"/api/barbers/{catalogo['barbero'].id}/toggle", headers=admin)
    assert client.get("/api/barbers").json() == []
    assert client.get("/api/barbers", headers=admin).json()[0]["is_active"] is False
