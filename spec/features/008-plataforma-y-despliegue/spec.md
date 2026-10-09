# 008 · Plataforma, despliegue y CI

## Descripción
Todo lo que permite que la aplicación arranque, se diagnostique y se despliegue: contenedores, proxy nginx, migraciones automáticas, health checks, configuración por variables de entorno y el pipeline de GitHub Actions.

## Historias de usuario
- Como **desarrollador**, quiero levantar todo con `docker compose up` y que la base se migre y se llene sola.
- Como **operador**, quiero saber por qué la API no está lista sin entrar a los logs.
- Como **desarrollador**, quiero que cada push y pull request ejecute lint, pruebas, build y un escaneo de seguridad.
- Como **operador**, quiero que `main` se despliegue sola cuando el pipeline pasa.

## Criterios de aceptación
- [x] `docker-compose.yml` define `bf-db` (PostgreSQL 16 + pgvector), `bf-api`, `web`, `bf-ollama`, `ollama-init` y `mailhog`, con volúmenes para la base y los modelos.
- [x] En desarrollo, `docker-compose.override.yml` publica la web en 8080 y MailHog en 8025; Dokploy usa solo `docker-compose.yml`.
- [x] nginx sirve el sitio estático de Next.js y reenvía `/api/` a `bf-api:8000`; los archivos `/_next/static/` se cachean como inmutables.
- [x] La API ejecuta `alembic upgrade head` al arrancar, con reintentos cada 5 s y un candado para que dos réplicas no migren a la vez.
- [x] La migración `001` funciona sobre una base vacía y sobre la creada por la primera versión del MVP; la `002` carga la semilla sin duplicar.
- [x] `GET /health` (liveness) responde siempre; `GET /health/db` (readiness) responde 503 mientras la base no responde o las migraciones no terminan.
- [x] `GET /api/health` muestra el motivo si la base de datos falla; un error de conexión durante una petición se responde con 503 y un mensaje en español.
- [x] Toda la configuración sale de variables de entorno (`.env.example` documenta todas); CORS solo se activa si `CORS_ORIGINS` tiene valores.
- [x] La API corre con un usuario sin privilegios; la web se compila en dos etapas.
- [x] CI: ruff y pytest del backend, `npm ci` + `npm run build` del frontend (incluye TypeScript), build de imágenes y Trivy, que falla ante vulnerabilidades CRÍTICAS.
- [x] El despliegue por webhook de Dokploy corre solo en `main` y solo si todo lo anterior pasó.
