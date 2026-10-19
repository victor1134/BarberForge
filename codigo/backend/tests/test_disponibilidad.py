from datetime import timedelta

from app.core.tiempo import hoy
from tests.conftest import token


def test_franjas_libres_futuras(client, catalogo):
    franjas = client.get("/api/availability", params={"barber_id": catalogo["barbero"].id}).json()
    assert franjas, "debe haber franjas para los próximos días"
    assert all(f["date"] > str(hoy()) for f in franjas)
    assert franjas[0]["time"] == "09:00"


def test_generar_disponibilidad_sin_domingos_ni_duplicados(client, catalogo, db):
    from app.models import Disponibilidad
    admin = token(client, "admin@correo.co")
    inicio = hoy() + timedelta(days=10)
    cuerpo = {"barber_id": catalogo["barbero"].id, "date_from": str(inicio), "date_to": str(inicio + timedelta(days=6)),
              "start": "09:00", "end": "10:00", "minutes": 30}
    assert client.post("/api/availability", json=cuerpo, headers=admin).status_code == 200
    client.post("/api/availability", json=cuerpo, headers=admin)  # repetir no duplica
    franjas = db.query(Disponibilidad).filter(Disponibilidad.slot_date >= inicio).all()
    assert len(franjas) == 6 * 2  # 6 días hábiles (sin domingo) x 2 franjas
    assert all(f.slot_date.weekday() != 6 for f in franjas)


def test_generar_disponibilidad_valida_rango(client, catalogo):
    admin = token(client, "admin@correo.co")
    cuerpo = {"barber_id": catalogo["barbero"].id, "date_from": "2030-01-10", "date_to": "2030-01-01"}
    assert client.post("/api/availability", json=cuerpo, headers=admin).status_code == 400
    cuerpo = {"barber_id": 999, "date_from": "2030-01-01", "date_to": "2030-01-02"}
    assert client.post("/api/availability", json=cuerpo, headers=admin).status_code == 404
