from datetime import datetime, timedelta

from app.core.tiempo import ahora_local, ahora_utc
from app.models import Cita, Disponibilidad
from app.services import citas as citas_srv
from tests.conftest import crear_usuario, token


def _primera_franja(client, barbero_id):
    return client.get("/api/availability", params={"barber_id": barbero_id}).json()[0]


def _agendar(client, catalogo, cab, franja=None):
    franja = franja or _primera_franja(client, catalogo["barbero"].id)
    return client.post("/api/appointments", headers=cab, json={
        "barber_id": catalogo["barbero"].id, "service_id": catalogo["corte"].id,
        "date": franja["date"], "time": franja["time"]})


def test_cliente_agenda_y_la_franja_deja_de_estar_libre(client, catalogo):
    cab = token(client, "ana@correo.co")
    franja = _primera_franja(client, catalogo["barbero"].id)
    r = _agendar(client, catalogo, cab, franja)
    assert r.status_code == 200
    assert franja not in client.get("/api/availability", params={"barber_id": catalogo["barbero"].id}).json()
    citas = client.get("/api/appointments", headers=cab).json()
    assert citas[0]["status"] == "pendiente" and citas[0]["barber"] == "Carlos Mena"


def test_doble_reserva_da_409_con_alternativas(client, catalogo, db):
    crear_usuario(db, "otro@correo.co", "cliente")
    franja = _primera_franja(client, catalogo["barbero"].id)
    assert _agendar(client, catalogo, token(client, "ana@correo.co"), franja).status_code == 200
    r = _agendar(client, catalogo, token(client, "otro@correo.co"), franja)
    assert r.status_code == 409
    assert r.json()["detail"]["message"] == "Esa franja ya no está disponible"
    assert len(r.json()["detail"]["alternatives"]) == 3


def test_indice_unico_impide_doble_reserva_aunque_se_salte_la_validacion(db, catalogo):
    """RN08 a nivel de base: dos inserciones directas en la misma franja activa fallan."""
    import pytest
    from sqlalchemy.exc import IntegrityError
    f = db.query(Disponibilidad).first()
    datos = {"client_id": catalogo["cliente"].id, "barber_id": catalogo["barbero"].id,
             "service_id": catalogo["corte"].id, "appointment_date": f.slot_date, "start_time": f.start_time}
    db.add(Cita(**datos))
    db.commit()
    db.add(Cita(**datos))
    with pytest.raises(IntegrityError):
        db.commit()


def test_solo_clientes_agendan_y_barbero_debe_ofrecer_el_servicio(client, catalogo, db):
    assert _agendar(client, catalogo, token(client, "admin@correo.co")).status_code == 403
    catalogo["barbero"].servicios = [catalogo["barba"]]
    db.commit()
    assert _agendar(client, catalogo, token(client, "ana@correo.co")).status_code == 400


def test_visibilidad_por_rol(client, catalogo):
    _agendar(client, catalogo, token(client, "ana@correo.co"))
    for correo in ("ana@correo.co", "carlos@demo.co", "admin@correo.co"):
        assert len(client.get("/api/appointments", headers=token(client, correo)).json()) == 1


def test_cancelar_libera_la_franja(client, catalogo):
    cab = token(client, "ana@correo.co")
    franja = _primera_franja(client, catalogo["barbero"].id)
    cita_id = _agendar(client, catalogo, cab, franja).json()["id"]
    assert client.post(f"/api/appointments/{cita_id}/cancel", headers=cab).status_code == 200
    assert client.post(f"/api/appointments/{cita_id}/cancel", headers=cab).status_code == 400
    assert franja in client.get("/api/availability", params={"barber_id": catalogo["barbero"].id}).json()
    assert client.get("/api/appointments", headers=cab).json()[0]["status"] == "cancelada_cliente"


def test_recordatorio_confirmacion_y_cierre(client, catalogo, db, monkeypatch):
    enviados = []
    monkeypatch.setattr("app.services.correo.enviar", lambda *a: enviados.append(a) or True)
    cab = token(client, "ana@correo.co")
    cita_id = _agendar(client, catalogo, cab).json()["id"]
    admin = token(client, "admin@correo.co")

    assert client.post(f"/api/appointments/{cita_id}/remind", headers=admin).status_code == 200
    enlace = enviados[0][2].split("/api/confirm/")[1].split()[0]
    assert "¡Cita confirmada!" in client.get(f"/api/confirm/{enlace}").text
    assert "venció o ya fue usado" in client.get(f"/api/confirm/{enlace}").text  # un solo uso

    barbero = token(client, "carlos@demo.co")
    url = f"/api/appointments/{cita_id}/status"
    assert client.patch(url, json={"status": "volando"}, headers=barbero).status_code == 400
    assert client.patch(url, json={"status": "completada"}, headers=barbero).status_code == 200
    assert client.get("/api/appointments", headers=cab).json()[0]["status"] == "completada"


def test_proceso_de_recordatorios_envia_y_cancela_sin_confirmar(db, catalogo, monkeypatch):
    enviados = []
    monkeypatch.setattr("app.services.correo.enviar", lambda *a: enviados.append(a) or True)
    dentro_de_30 = ahora_local() + timedelta(minutes=30)
    proxima = Cita(client_id=catalogo["cliente"].id, barber_id=catalogo["barbero"].id, service_id=catalogo["corte"].id,
                   appointment_date=dentro_de_30.date(), start_time=dentro_de_30.time().replace(microsecond=0))
    vieja = Cita(client_id=catalogo["cliente"].id, barber_id=catalogo["barbero"].id, service_id=catalogo["corte"].id,
                 appointment_date=dentro_de_30.date(), start_time=datetime.min.time(),
                 reminder_sent_at=ahora_utc() - timedelta(minutes=20), token_hash="x")
    db.add_all([proxima, vieja])
    db.commit()

    citas_srv.procesar_recordatorios(db)
    db.refresh(proxima)
    db.refresh(vieja)
    assert len(enviados) == 1 and proxima.reminder_sent_at is not None
    assert vieja.status == "cancelada_sin_confirmar"
