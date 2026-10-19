def test_lista_y_detalle(client, catalogo):
    lista = client.get("/api/barberias").json()
    assert lista[0]["servicios"] == 2 and lista[0]["barberos"] == 1
    detalle = client.get("/api/barberias/1").json()
    assert [s["name"] for s in detalle["servicios"]] == ["Corte clásico", "Barba perfilada"]
    assert detalle["barberos"][0]["full_name"] == "Carlos Mena"
    assert client.get("/api/barberias/2").status_code == 404
