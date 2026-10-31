# BarberForge AI (Diplomado CloudForge AI 5.0)

Plataforma de agendamiento para barberías con asistente RAG local (Ollama + pgvector). El cliente ve servicios y precios, consulta la disponibilidad real y agenda su cita por formulario o por chat.

## Estructura

```
spec/                          ← documentación spec-driven (se escribe antes del código)
├── constitution/              misión, stack tecnológico y hoja de ruta
└── features/NNN-nombre/       spec.md (qué) → plan.md (cómo) → tasks.md (checklist)
codigo/
├── backend/                   API: FastAPI + SQLAlchemy + Alembic
│   ├── app/
│   │   ├── models/            tablas (SQLAlchemy)
│   │   ├── schemas/           validación de entrada y salida (Pydantic)
│   │   ├── routers/           endpoints HTTP delgados
│   │   ├── services/          reglas de negocio (+ errores.py: errores de dominio)
│   │   ├── core/              seguridad (JWT, bcrypt), dependencias y hora local
│   │   ├── config.py          configuración por variables de entorno
│   │   └── main.py            aplicación, manejo de errores y tareas de fondo
│   ├── alembic/versions/      001 esquema · 002 datos semilla
│   └── tests/                 pytest sobre SQLite en memoria, un archivo por router
└── frontend/                  web: Next.js 16 (App Router) + React 19 + TypeScript
    ├── app/                   una carpeta por página (barberia, login, registro, agendar, citas, cuenta, admin/…)
    ├── components/            Navbar, ServicioCard, BarberoCard, ChatAsistente, Panel, Aviso…
    ├── lib/                   api.ts (tipos + fetch), auth.ts (token), formato.ts
    └── nginx.conf             sirve el sitio estático y reenvía /api a la API
docker-compose.yml             PostgreSQL + pgvector, API, web, Ollama y MailHog
.env.example                   variables de entorno de ejemplo (el .env real no se versiona)
```

Estado de cada feature: [spec/constitution/roadmap.md](spec/constitution/roadmap.md).

## Ejecutar en local (Docker)
    cp .env.example .env
    docker compose up -d --build
- App: http://localhost:8080 · Correos (MailHog): http://localhost:8025
- El primer registro queda como **administrador** (RN02), salvo que definas `ADMIN_EMAIL` y `ADMIN_PASSWORD`. Barberos demo: `carlos@demo.co` / `luis@demo.co`, clave `Demo12345`.
- `ollama-init` descarga `nomic-embed-text` y `llama3` (~5 GB); sin ellos el asistente usa búsqueda por palabras clave. Para equipos modestos: `LLM_MODEL=llama3.2:3b`.
- Las migraciones de Alembic corren solas al arrancar la API.

## Desarrollo sin Docker
Backend (necesita un PostgreSQL con pgvector, por ejemplo `docker compose up -d bf-db` con el puerto 5432 publicado):

    cd codigo/backend
    python -m venv .venv && .venv/Scripts/activate      # Linux/Mac: source .venv/bin/activate
    pip install -r requirements-dev.txt
    set DATABASE_URL=postgresql://barber:barber@localhost:5432/barber   # Linux/Mac: export …
    uvicorn app.main:app --reload
    pytest            # pruebas (SQLite en memoria, no necesitan base de datos)
    ruff check .      # estilo

Frontend (reenvía `/api` a `http://localhost:8000`; se cambia con `API_URL`):

    cd codigo/frontend
    npm install
    npm run dev       # http://localhost:3000
    npm run build     # genera el sitio estático en out/

## Desplegar en Dokploy (igual que el Laboratorio 4)
1. Proyecto → Create Service → **Compose** (Docker Compose). Provider GitHub, repo, rama `main`, Compose Path `./docker-compose.yml`.
2. Pestaña Environment: `DB_PASSWORD`, `JWT_SECRET`, `PUBLIC_URL=http://<dominio-de-web>`, `MAILHOG_URL=http://<dominio-de-mailhog>` (botón «Abrir buzón» del administrador) y `SEED_DEMO=false` en producción real.
3. Pestaña Domains → Add Domain (dos veces): `web` puerto `80` y `mailhog` puerto `8025`. Después, redespliega.
4. Desactiva **Autodeploy** y copia el Webhook URL (pestaña Deployments) en el secreto `DOKPLOY_WEBHOOK_URL` de GitHub: el workflow `.github/workflows/ci.yml` corre ruff, pytest, el build del frontend, el build de imágenes y Trivy, y solo entonces despliega.

Una base de datos creada por la primera versión del MVP se migra sola: la migración `001` solo crea lo que falta y conserva los datos.

## Qué incluye
Registro/login con roles · catálogo · barberos · disponibilidad · agendamiento por formulario y por chat · índice único parcial anti doble reserva · recordatorio por correo (40 min) con enlace de un solo uso y cancelación a los 15 min · asistente RAG con filtro por rol en SQL y guarda anti inyección de prompts · cancelación y cierre de citas · migraciones Alembic · pruebas automatizadas.

## Pendiente
Kubernetes/Helm (feature 001), endurecimiento DevSecOps (002), observabilidad (004), bot de WhatsApp (005), corte por referencia (006), días sin atención y ausencias de barberos (RF09, RF17).

## Diagnóstico rápido
`GET /api/health` responde `{"servicio":"barberforge-ai","estado":"ok","base_de_datos":"ok"}`. Si la base falla, `base_de_datos` muestra el motivo (por ejemplo `password authentication failed`: la clave `DB_PASSWORD` no coincide con la del volumen `pgdata`; se corrige borrando ese volumen en Dokploy y redesplegando). Para Kubernetes: `GET /health` (liveness) y `GET /health/db` (readiness).
