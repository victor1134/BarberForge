"""Entorno de Alembic: usa el motor y los modelos de la aplicación."""
from logging.config import fileConfig

from alembic import context

import app.models  # noqa: F401 - registra los modelos en Base.metadata
from app.db import Base, engine

config = context.config
target_metadata = Base.metadata

# Desde la línea de comandos (alembic upgrade head) se configura el logging;
# desde la aplicación (arranque.migrar) se respeta el logging de la API.
if config.config_file_name is not None and "connection" not in config.attributes:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    context.configure(url=engine.url.render_as_string(hide_password=False), target_metadata=target_metadata,
                      literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def _migrar(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    conexion = config.attributes.get("connection")
    if conexion is not None:
        _migrar(conexion)
        return
    with engine.connect() as connection:
        _migrar(connection)
        connection.commit()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
