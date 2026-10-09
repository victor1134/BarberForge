# 004 · Plan técnico

## Endpoints
| Método y ruta | Acceso | Servicio |
|---|---|---|
| `GET /api/availability?barber_id=` | público | `disponibilidad.franjas_libres` → `FranjaOut[]` |
| `POST /api/availability` | administrador | `disponibilidad.generar` |

## Componentes
| Componente | Ubicación | Notas |
|---|---|---|
| Modelo | `app/models/disponibilidad.py` | `Disponibilidad(barber_id, slot_date, start_time)` con `UniqueConstraint` |
| Esquemas | `app/schemas/disponibilidad.py` | `GenerarDisponibilidadIn` (por defecto 9:00–17:00, 30 min), `FranjaOut` |
| Reglas | `app/services/disponibilidad.py` | `generar_franjas`, `generar`, `franjas_libres`, `esta_libre`, `etiqueta` (“lun 03/11 · 09:00”), `borrar_antiguas` |
| Hora local | `app/core/tiempo.py` | `ahora_local()` y `hoy()` en `ZONA_HORARIA` |
| Arranque | `app/services/arranque.py` | `preparar_datos`: `DIAS_DE_AGENDA = 7` |
| Admin (web) | `app/admin/disponibilidad/page.tsx` | formulario y botón “Reindexar asistente” (ver 007) |
| Agendar (web) | `app/agendar/page.tsx` | paso 3: franjas agrupadas por día con `fechaLarga` |

## Decisiones
- **Libre = sin cita activa**, calculado con `NOT EXISTS` sobre `appointments`; no se marca la franja como ocupada, así cancelar la libera sin pasos extra.
- **La hora actual se calcula en Python** y se compara en SQL, para que la consulta funcione igual en PostgreSQL y en SQLite.
- **Duración de la franja independiente del servicio:** la franja es el inicio de la cita; la duración del servicio es informativa.
- **`hoyISO()` en el frontend** usa la fecha local del navegador (no `toISOString`, que en la noche de Colombia daría el día siguiente).
