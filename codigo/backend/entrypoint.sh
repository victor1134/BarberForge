#!/bin/sh
# Las migraciones (alembic upgrade head) corren dentro de la API al arrancar, con reintentos,
# para que /api/health muestre el motivo si la base de datos todavía no responde.
set -e
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --proxy-headers --forwarded-allow-ips="*"
