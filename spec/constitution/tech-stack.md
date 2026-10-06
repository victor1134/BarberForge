# Stack tecnológico

> Si cambias una decisión de este archivo, actualízalo en el mismo cambio, junto con el `plan.md` de la feature afectada y el README.

## Servicios (`docker-compose.yml`)
| Servicio | Tecnología | Carpeta / imagen |
|---|---|---|
| `bf-api` | Python 3.12 · FastAPI · SQLAlchemy 2 · Alembic · Pydantic v2 · pydantic-settings · PyJWT · bcrypt · httpx · uvicorn | `codigo/backend/` |
| `web` | Next.js 16 (App Router, `output: "export"`) · React 19 · TypeScript, sin otras librerías; servido por nginx | `codigo/frontend/` |
| `bf-db` | PostgreSQL 16 + pgvector | `pgvector/pgvector:pg16` |
| `bf-ollama` | Ollama: `nomic-embed-text` (embeddings, 768 dim) y `llama3` (respuestas) | `ollama/ollama` |
| `ollama-init` | Descarga los dos modelos una vez | `ollama/ollama` |
| `mailhog` | SMTP de pruebas (puerto 1025) y buzón web (8025) | `mailhog/mailhog` |

nginx (`codigo/frontend/nginx.conf`) es el único punto de entrada: sirve el sitio estático y reenvía `/api/` a `bf-api:8000` (timeout de 180 s por las respuestas del LLM).

## Datos
| Tabla | Modelo | Contenido |
|---|---|---|
| `users` | `Usuario` | Clientes, barberos y administradores (columna `role`); `specialties` (barbero) y `style_pref` (cliente). Únicos: `email` y (`id_type`, `id_number`). |
| `services` | `Servicio` | Catálogo con `CHECK` de precio, duración y tipo. |
| `barber_services` | `barbero_servicio` | Qué servicios ofrece cada barbero (N:M). |
| `availability` | `Disponibilidad` | Franjas por barbero, fecha y hora (únicas). |
| `appointments` | `Cita` | Citas con estado, `token_hash` y `reminder_sent_at`; índice único parcial `uq_cita_activa`. |
| `knowledge_chunks` | `FragmentoConocimiento` | Base de conocimiento del asistente: `vector(768)` con índice HNSW y `access_level` (`public` / `internal`). |

- **Migraciones Alembic:** `001_esquema_inicial` (idempotente: completa bases creadas por la primera versión del MVP) y `002_datos_semilla` (4 servicios y, con `SEED_DEMO=true`, 2 barberos de demostración).
- Fechas y horas de las citas en hora local de la barbería (`ZONA_HORARIA`, por defecto `America/Bogota`), sin zona. Las marcas técnicas (`reminder_sent_at`, `policy_accepted_at`) van en UTC.

## Arquitectura del backend (capas)
| Carpeta | Responsabilidad |
|---|---|
| `app/main.py` | App FastAPI, ciclo de vida (tareas de fondo), CORS opcional y traducción de errores a HTTP |
| `app/routers/` | Endpoints delgados: `health`, `auth`, `cuenta`, `barberias`, `servicios`, `barberos`, `disponibilidad`, `citas`, `chat` |
| `app/schemas/` | Entrada y salida con Pydantic (`RegistroIn`, `CitaIn`, `CitaOut`, `ChatOut`…) |
| `app/services/` | Reglas de negocio: `usuarios`, `servicios`, `barberos`, `disponibilidad`, `citas`, `barberia`, `correo`, `chat`, `rag`, `ia`, `arranque` |
| `app/services/errores.py` | `DatosInvalidos` 400 · `NoAutenticado`/`CredencialesInvalidas` 401 · `SinPermiso` 403 · `NoEncontrado` 404 · `Conflicto` 409. Un `OperationalError` de la base se responde con 503. |
| `app/core/` | `seguridad.py` (bcrypt, JWT HS256, tokens de un solo uso con SHA-256), `dependencias.py` (`get_current_user[_opcional]`, `require_roles`), `tiempo.py` (hora local) |
| `app/config.py` | `Settings` desde variables de entorno o `.env` |
| `app/db.py` | Motor, sesiones, `Base`; SQLite en memoria con `StaticPool` para pruebas |

## Arquitectura del frontend
| Carpeta | Responsabilidad |
|---|---|
| `app/` | Una carpeta por página: inicio, `barberia`, `login`, `registro`, `agendar`, `citas`, `cuenta`, `admin/{barberos,servicios,disponibilidad}`, `not-found` |
| `components/` | `Sesion` (contexto de sesión), `Panel` (exige sesión y rol, pestañas por rol), `Acceso` (tarjeta de ingreso y destino seguro), `Aviso` (notificaciones), `Navbar`, `Footer`, `ChatAsistente`, `ChatFlotante`, `ServicioCard`, `BarberoCard` |
| `lib/api.ts` | Tipos de la API y única puerta al backend (`fetch("/api"…)` con el token Bearer); `ApiError` con estado y alternativas |
| `lib/auth.ts` | Token JWT en `localStorage` (`bf_t`) y `rutaSegura` contra redirecciones abiertas |
| `lib/formato.ts` | Pesos colombianos, fechas en español, etiquetas de estados, tipos y roles |

En desarrollo, `next.config.ts` reenvía `/api` a `API_URL` (por defecto `http://localhost:8000`).

## Infraestructura y CI
- **Local:** `docker compose up`. `docker-compose.override.yml` publica `web` en 8080 y MailHog en 8025.
- **Despliegue:** Dokploy (servicio Compose desde GitHub, solo `docker-compose.yml`).
- **Imágenes:** API sobre `python:3.12-slim` con usuario sin privilegios (uid 10001); web en dos etapas (`node:22-alpine` → `nginx:alpine`).
- **GitHub Actions** (`.github/workflows/ci.yml`): `backend` (ruff + pytest) y `frontend` (`npm ci` + `npm run build`) → `imagenes` (`docker compose build` + Trivy fs, falla con CRÍTICAS) → `desplegar` (webhook de Dokploy, solo en `main`).

## Convenciones
- Código, comentarios y mensajes al usuario en **español**. Tablas, columnas y campos JSON en inglés por compatibilidad con la base existente.
- Secretos solo en `.env` (no versionado). Se versiona `.env.example`.
- Un archivo de pruebas por router en `codigo/backend/tests/`, sobre SQLite en memoria con `TAREAS_FONDO=false`. Ollama y SMTP se simulan.
- El frontend llama a la API solo a través de `lib/api.ts`.
- Estilo Python: ruff (`pyproject.toml`), líneas de 120 caracteres. TypeScript se verifica en `npm run build`.
