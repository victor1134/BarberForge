"""Datos semilla: catálogo de servicios y, si SEED_DEMO=true, dos barberos de demostración.

La agenda de los barberos no va aquí porque depende de la fecha: se genera al arrancar la API
(app/services/arranque.py) para los próximos 7 días.

Revision ID: 002
Revises: 001
Create Date: 2026-11-03
"""
import bcrypt
import sqlalchemy as sa
from alembic import op

from app.config import get_settings

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None

SERVICIOS = [
    ("Corte clásico", "Corte con máquina y tijera, lavado y peinado.", 25000, 30, "corte"),
    ("Barba perfilada", "Perfilado con navaja, toalla caliente y aceite.", 18000, 20, "barba"),
    ("Combo corte + barba", "Corte clásico más barba perfilada.", 40000, 50, "combo"),
    ("Tratamiento capilar", "Limpieza profunda e hidratación del cuero cabelludo.", 35000, 40, "tratamiento"),
]
BARBEROS_DEMO = [
    ("Carlos Mena", "carlos@demo.co", "90000", "Fade, degradados y barba clásica"),
    ("Luis Ortiz", "luis@demo.co", "90001", "Corte clásico y tratamientos capilares"),
]
CLAVE_DEMO = "Demo12345"


def upgrade() -> None:
    conn = op.get_bind()
    if conn.execute(sa.text("SELECT 1 FROM services LIMIT 1")).first() is None:
        for nombre, descripcion, precio, minutos, tipo in SERVICIOS:
            conn.execute(sa.text("INSERT INTO services(name, description, price_cop, duration_minutes, service_type) "
                                 "VALUES (:n, :d, :p, :m, :t)"),
                         {"n": nombre, "d": descripcion, "p": precio, "m": minutos, "t": tipo})

    if get_settings().seed_demo:
        clave = bcrypt.hashpw(CLAVE_DEMO.encode(), bcrypt.gensalt()).decode()
        for nombre, correo, documento, especialidades in BARBEROS_DEMO:
            conn.execute(sa.text(
                "INSERT INTO users(email, full_name, id_type, id_number, password_hash, role, specialties) "
                "VALUES (:e, :n, 'CC', :doc, :h, 'barbero', :esp) ON CONFLICT DO NOTHING"),
                {"e": correo, "n": nombre, "doc": documento, "h": clave, "esp": especialidades})

    # Todo barbero sin servicios asignados ofrece el catálogo completo.
    conn.execute(sa.text(
        "INSERT INTO barber_services(barber_id, service_id) "
        "SELECT u.id, s.id FROM users u CROSS JOIN services s "
        "WHERE u.role = 'barbero' AND NOT EXISTS (SELECT 1 FROM barber_services b WHERE b.barber_id = u.id) "
        "ON CONFLICT DO NOTHING"))


def downgrade() -> None:
    conn = op.get_bind()
    correos = [b[1] for b in BARBEROS_DEMO]
    demo_sin_citas = ("SELECT id FROM users WHERE email = ANY(:c) AND NOT EXISTS "
                      "(SELECT 1 FROM appointments a WHERE a.barber_id = users.id)")
    conn.execute(sa.text(f"DELETE FROM availability WHERE barber_id IN ({demo_sin_citas})"), {"c": correos})
    conn.execute(sa.text(f"DELETE FROM barber_services WHERE barber_id IN ({demo_sin_citas})"), {"c": correos})
    conn.execute(sa.text("DELETE FROM users WHERE email = ANY(:c) AND NOT EXISTS "
                         "(SELECT 1 FROM appointments a WHERE a.barber_id = users.id)"), {"c": correos})
