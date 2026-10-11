"""Esquema inicial: usuarios, servicios, barberos-servicios, disponibilidad, citas y base de conocimiento.

Es idempotente: la primera versión del MVP creaba las tablas sin Alembic, así que en una base
existente solo crea lo que falte y Alembic queda al día sin perder datos.

Revision ID: 001
Revises:
Create Date: 2026-11-03
"""
import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def _existe(tabla: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(tabla)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    if not _existe("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("email", sa.Text, nullable=False, unique=True),
            sa.Column("full_name", sa.Text, nullable=False),
            sa.Column("id_type", sa.Text, nullable=False),
            sa.Column("id_number", sa.Text, nullable=False),
            sa.Column("password_hash", sa.Text, nullable=False),
            sa.Column("role", sa.Text, nullable=False),
            sa.Column("is_active", sa.Boolean, server_default=sa.true()),
            sa.Column("policy_accepted_at", sa.DateTime(timezone=True)),
            sa.Column("specialties", sa.Text, server_default=""),
            sa.Column("style_pref", sa.Text, server_default=""),
            sa.UniqueConstraint("id_type", "id_number"),
        )
    else:  # columnas agregadas en versiones posteriores del MVP
        op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS specialties text DEFAULT ''")
        op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS style_pref text DEFAULT ''")

    if not _existe("services"):
        op.create_table(
            "services",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("name", sa.Text, nullable=False),
            sa.Column("description", sa.Text),
            sa.Column("price_cop", sa.Integer, nullable=False),
            sa.Column("duration_minutes", sa.Integer, nullable=False),
            sa.Column("service_type", sa.Text, nullable=False),
            sa.Column("is_active", sa.Boolean, server_default=sa.true()),
            sa.CheckConstraint("price_cop >= 1000", name="services_price_cop_check"),
            sa.CheckConstraint("duration_minutes >= 10", name="services_duration_minutes_check"),
            sa.CheckConstraint("service_type IN ('corte','barba','combo','tratamiento')",
                               name="services_service_type_check"),
        )

    if not _existe("barber_services"):
        op.create_table(
            "barber_services",
            sa.Column("barber_id", sa.Integer, sa.ForeignKey("users.id"), primary_key=True),
            sa.Column("service_id", sa.Integer, sa.ForeignKey("services.id"), primary_key=True),
        )

    if not _existe("availability"):
        op.create_table(
            "availability",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("barber_id", sa.Integer, sa.ForeignKey("users.id")),
            sa.Column("slot_date", sa.Date),
            sa.Column("start_time", sa.Time),
            sa.UniqueConstraint("barber_id", "slot_date", "start_time"),
        )

    if not _existe("appointments"):
        op.create_table(
            "appointments",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("client_id", sa.Integer, sa.ForeignKey("users.id")),
            sa.Column("barber_id", sa.Integer, sa.ForeignKey("users.id")),
            sa.Column("service_id", sa.Integer, sa.ForeignKey("services.id")),
            sa.Column("appointment_date", sa.Date),
            sa.Column("start_time", sa.Time),
            sa.Column("status", sa.Text, server_default="pendiente"),
            sa.Column("token_hash", sa.Text),
            sa.Column("reminder_sent_at", sa.DateTime(timezone=True)),
        )
    # RN08: índice único parcial que impide la doble reserva de una franja.
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_cita_activa ON appointments(barber_id, appointment_date, "
               "start_time) WHERE status IN ('pendiente','confirmada')")

    if not _existe("knowledge_chunks"):
        op.create_table(
            "knowledge_chunks",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("source", sa.Text),
            sa.Column("content", sa.Text),
            sa.Column("access_level", sa.Text),
            sa.Column("embedding", Vector(768)),
        )
    op.execute("CREATE INDEX IF NOT EXISTS kc_hnsw ON knowledge_chunks USING hnsw (embedding vector_cosine_ops)")


def downgrade() -> None:
    for tabla in ("knowledge_chunks", "appointments", "availability", "barber_services", "services", "users"):
        op.execute(f"DROP TABLE IF EXISTS {tabla} CASCADE")
