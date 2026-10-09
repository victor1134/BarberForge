# 008 · Tareas

## Backend
- [x] Configuración por variables de entorno (`app/config.py`)
- [x] Motor y sesiones de SQLAlchemy; SQLite para pruebas (`app/db.py`)
- [x] Errores de dominio traducidos a HTTP y 503 ante fallos de la base
- [x] Migración 001 idempotente y 002 de datos semilla
- [x] Migraciones al arrancar con reintentos y candado
- [x] Health checks `/health`, `/health/db` y `/api/health`
- [x] Pruebas de salud y fixtures comunes

## Contenedores
- [x] Dockerfile de la API con usuario sin privilegios
- [x] Dockerfile del frontend en dos etapas con nginx
- [x] `nginx.conf` con proxy de `/api` y caché de estáticos
- [x] `docker-compose.yml` y `docker-compose.override.yml`
- [x] `.env.example` con todas las variables

## CI/CD
- [x] Trabajo `backend`: ruff + pytest
- [x] Trabajo `frontend`: `npm ci` + `npm run build`
- [x] Trabajo `imagenes`: `docker compose build` + Trivy
- [x] Trabajo `desplegar`: webhook de Dokploy solo en `main`
