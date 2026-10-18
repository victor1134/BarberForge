from tests.conftest import token

NUEVO = {"name": "Cejas", "description": "Perfilado", "price_cop": 8000, "duration_minutes": 10,
         "service_type": "barba"}


def test_listado_publico_solo_activos(client, catalogo, db):
    catalogo["barba"].is_active = False
    db.commit()
    assert [s["name"] for s in client.get("/api/services").json()] == ["Corte clásico"]
    admin = token(client, "admin@correo.co")
    assert len(client.get("/api/services", headers=admin).json()) == 2


def test_solo_admin_crea_servicios(client, catalogo):
    assert client.post("/api/services", json=NUEVO).status_code == 401
    assert client.post("/api/services", json=NUEVO, headers=token(client, "ana@correo.co")).status_code == 403
    r = client.post("/api/services", json=NUEVO, headers=token(client, "admin@correo.co"))
    assert r.status_code == 200
    assert "Cejas" in [s["name"] for s in client.get("/api/services").json()]


def test_validacion_de_precio_duracion_y_tipo(client, catalogo):
    admin = token(client, "admin@correo.co")
    for cambio in ({"price_cop": 500}, {"duration_minutes": 5}, {"service_type": "masaje"}):
        r = client.post("/api/services", json={**NUEVO, **cambio}, headers=admin)
        assert r.status_code == 400
        assert "Precio mínimo" in r.json()["detail"]


def test_editar_y_alternar(client, catalogo):
    admin = token(client, "admin@correo.co")
    sid = catalogo["corte"].id
    r = client.put(f"/api/services/{sid}", json={**NUEVO, "name": "Corte premium"}, headers=admin)
    assert r.status_code == 200
    assert client.put("/api/services/999", json=NUEVO, headers=admin).status_code == 404
    client.post(f"/api/services/{sid}/toggle", headers=admin)
    assert "Corte premium" not in [s["name"] for s in client.get("/api/services").json()]
