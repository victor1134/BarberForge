# 008 · Plan técnico

## Endpoints de salud
| Ruta | Uso | Respuesta |
|---|---|---|
| `GET /health` | liveness (y `healthcheck` de Compose) | `{"estado": "ok"}` |
| `GET /health/db` | readiness | 200, o 503 con `error` / `iniciando` |
| `GET /api/health` | diagnóstico humano | `{servicio, estado, base_de_datos}` con el motivo del fallo |

## Arranque de la API (`app/main.py` → `app/services/arranque.py`)
Con `TAREAS_FONDO=true` el ciclo de vida lanza tres tareas:
1. `iniciar_base_de_datos`: `migrar()` (`pg_advisory_lock(7002)` + `alembic upgrade head`) y `preparar_datos()` (admin inicial y 7 días de agenda). Reintenta cada 5 s y guarda el error en `ESTADO`.
2. `indexar_asistente`: espera la base y reindexa hasta 40 veces, cada 30 s (ver 007).
3. `recordatorios`: cada 60 s (ver 006).

## Contenedores
| Archivo | Contenido |
|---|---|
| `codigo/backend/Dockerfile` | `python:3.12-slim`, usuario `app` (uid 10001), limpia CRLF de `entrypoint.sh` |
| `codigo/backend/entrypoint.sh` | `uvicorn app.main:app --proxy-headers` en `PORT` (8000) |
| `codigo/frontend/Dockerfile` | `node:22-alpine` (`npm ci` + `npm run build` → `out/`) → `nginx:alpine` |
| `codigo/frontend/nginx.conf` | resolver de Docker, `proxy_read_timeout 180s`, `try_files $uri $uri.html $uri/`, 404 de Next |
| `codigo/frontend/next.config.ts` | producción: `output: "export"`; desarrollo: `rewrites` de `/api` a `API_URL` |

## Configuración (`app/config.py`)
`DATABASE_URL` o `DB_HOST/PORT/USER/PASSWORD/NAME` · `JWT_SECRET`, `JWT_HORAS`, `CORS_ORIGINS` · `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_NOMBRE` · `OLLAMA_URL`, `LLM_MODEL`, `EMBED_MODEL` · `PUBLIC_URL`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_REMITENTE`, `MAILHOG_URL` · `BARBERIA_NOMBRE`, `BARBERIA_DIRECCION`, `ZONA_HORARIA`, `SEED_DEMO` · `TAREAS_FONDO`.

## Pipeline (`.github/workflows/ci.yml`)
```
backend  (ruff + pytest)    ─┐
                             ├─> imagenes (compose build + Trivy fs CRITICAL) ─> desplegar (webhook Dokploy, solo main)
frontend (npm ci + build)   ─┘
```
Secreto del pipeline: `DOKPLOY_WEBHOOK_URL`.

## Pruebas (`codigo/backend/tests/`)
- `conftest.py`: SQLite en memoria, `TAREAS_FONDO=false`, Ollama y SMTP apuntan a puertos cerrados; fixtures de cliente HTTP y catálogo.
- `test_health.py`: liveness, `/api/health`, readiness 200 y 503 mientras arranca.
