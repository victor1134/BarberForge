# 005 · Plan técnico

## Endpoints
| Método y ruta | Acceso | Servicio |
|---|---|---|
| `POST /api/appointments` | cliente | `citas.agendar` → `{id}` |
| `GET /api/appointments` | cliente, barbero, administrador | `citas.listar_para` → `CitaOut[]` |
| `POST /api/appointments/{id}/cancel` | cliente, administrador | `citas.cancelar` |
| `PATCH /api/appointments/{id}/status` | barbero, administrador | `citas.cerrar` |

## Componentes
| Componente | Ubicación | Notas |
|---|---|---|
| Modelo | `app/models/cita.py` | `Cita`, `ESTADOS`, `ESTADOS_ACTIVOS`; índice `uq_cita_activa` (barbero, fecha, hora) con `WHERE status IN ('pendiente','confirmada')` en PostgreSQL y SQLite |
| Esquemas | `app/schemas/cita.py` | `CitaIn`, `CitaCreadaOut`, `CitaOut` (con nombres de servicio, barbero y cliente), `EstadoCitaIn` |
| Reglas | `app/services/citas.py` | `agendar`, `listar_para`, `cancelar`, `cerrar`; `ESTADOS_CIERRE` |
| Errores | `app/services/errores.py` | `Conflicto("Esa franja ya no está disponible", alternatives=[…])` → `detail: {message, alternatives}` |
| Agendar (web) | `app/agendar/page.tsx` | tres pasos y barra de resumen con precio; solo rol cliente |
| Citas (web) | `app/citas/page.tsx` | componente `Acciones` por rol y estado; filtros solo para administrador |
| Cliente HTTP (web) | `lib/api.ts` | `ApiError.alternativas`; `textoAlternativas` en `lib/formato.ts` |

## Decisiones
- **Doble defensa contra la doble reserva:** primero `esta_libre`; luego el `INSERT` dentro de `begin_nested()`. Si el índice único lanza `IntegrityError`, se convierte en `Conflicto` con alternativas.
- **Cancelar libera la franja** sin tocar `availability`: la franja vuelve a estar libre porque la cita deja de ser activa. También se borra el `token_hash` del recordatorio.
- **Ocultar con 404** las citas de otros clientes o barberos, en lugar de 403, para no revelar que existen.
