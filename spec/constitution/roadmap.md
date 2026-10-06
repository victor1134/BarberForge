# Hoja de ruta

Las features siguen el orden en que se construyó el sistema: primero la identidad y el catálogo, luego la agenda y al final el asistente y la plataforma.

| # | Feature | Backend | Frontend | Estado |
|---|---|---|---|---|
| 001 | [Autenticación y cuentas](../features/001-autenticacion-y-cuentas/spec.md) | `auth`, `cuenta`, `usuarios` | `/login`, `/registro`, `/cuenta`, `Sesion`, `Panel` | 🟢 Implementada |
| 002 | [Barbería y catálogo de servicios](../features/002-barberia-y-servicios/spec.md) | `barberias`, `servicios` | `/`, `/barberia`, `/admin/servicios` | 🟢 Implementada; falta la sección “Barberías” del inicio |
| 003 | [Gestión de barberos](../features/003-gestion-de-barberos/spec.md) | `barberos` | `/admin/barberos`, `BarberoCard` | 🟢 Implementada |
| 004 | [Disponibilidad](../features/004-disponibilidad/spec.md) | `disponibilidad`, `arranque` | `/admin/disponibilidad` | 🟢 Implementada; faltan festivos y ausencias |
| 005 | [Agendamiento de citas](../features/005-agendamiento-de-citas/spec.md) | `citas` | `/agendar`, `/citas` | 🟢 Implementada |
| 006 | [Recordatorios y confirmación](../features/006-recordatorios-y-confirmacion/spec.md) | `citas`, `correo`, `arranque` | `/citas` (enviar recordatorio, buzón) | 🟢 Implementada |
| 007 | [Asistente con IA y RAG](../features/007-asistente-ia-rag/spec.md) | `chat`, `rag`, `ia` | `ChatAsistente`, `ChatFlotante` | 🟢 Implementada; faltan evaluación e historial |
| 008 | [Plataforma, despliegue y CI](../features/008-plataforma-y-despliegue/spec.md) | `health`, `arranque`, Alembic | Dockerfile + nginx | 🟢 Implementada |

## Decisiones tomadas
| Fecha | Decisión | Motivo |
|---|---|---|
| 2026-11-03 | Backend en **FastAPI + SQLAlchemy + Alembic** con arquitectura en capas | Sustituye el `main.py` único del primer MVP; permite pruebas por capa y migraciones versionadas. |
| 2026-11-03 | Frontend en **Next.js 16 con exportación estática servida por nginx** | Una página por carpeta y tipos compartidos con la API; sin servidor Node en producción. |
| 2026-11-03 | **Sin gateway aparte:** nginx del frontend hace de proxy inverso de `/api` | Un servicio menos que mantener; la API no necesita CORS. |
| 2026-11-03 | **Migraciones dentro de la API** con reintentos y `pg_advisory_lock` | `/api/health` explica por qué la base no está lista y varias réplicas no migran a la vez. |
| 2026-11-03 | **Agenda de 7 días generada al arrancar** (no en la semilla) | Depende de la fecha; la semilla solo carga datos fijos. |
| MVP | **Dokploy + Docker Compose** para el despliegue | Es lo que se usó en el Laboratorio 4. |
| MVP | **IA local con Ollama** (`nomic-embed-text` + `llama3`) y pgvector | Privacidad de los datos; sin dependencias de nube. |
| MVP | **MailHog** como servidor de correo | Probar recordatorios sin enviar correos reales. |

## Pendientes (backlog)
- **RF09:** días sin atención (festivos) que bloqueen la agenda → 004.
- **RF17:** ausencias de barberos → 004.
- Sección `#barberias` en el inicio: el enlace “Barberías” del `Navbar` apunta a un ancla que no existe → 002.
- Edición de barberos (hoy solo se crean y se activan o desactivan) → 003.
- Conjunto de preguntas de evaluación del asistente e historial de conversación → 007.
- Correo de confirmación al agendar (hoy solo existe el recordatorio) → 006.
