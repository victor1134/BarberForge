def test_liveness(client):
    assert client.get("/health").json() == {"estado": "ok"}


def test_health_api_informa_estado_de_la_base(client):
    r = client.get("/api/health").json()
    assert r["servicio"] == "barberforge-ai"
    assert r["estado"] == "ok"
    # En pruebas no corre el arranque (migraciones), así que la base figura como "iniciando".
    assert r["base_de_datos"].startswith("sin conexión")


def test_readiness_ok_cuando_la_base_esta_lista(client, monkeypatch):
    from app.services import arranque
    monkeypatch.setitem(arranque.ESTADO, "db", True)
    assert client.get("/health/db").status_code == 200


def test_readiness_503_mientras_arranca(client):
    assert client.get("/health/db").status_code == 503
