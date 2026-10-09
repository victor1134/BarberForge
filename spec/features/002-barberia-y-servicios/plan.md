# 002 · Plan técnico

## Endpoints
| Método y ruta | Acceso | Servicio |
|---|---|---|
| `GET /api/barberias` | público | `barberia.listar` → `BarberiaResumen[]` |
| `GET /api/barberias/{id}` | público | `barberia.detalle` → `BarberiaDetalle` |
| `GET /api/services` | público (admin ve inactivos) | `servicios.listar` |
| `POST /api/services` | administrador | `servicios.crear` + `reindexar_en_segundo_plano` |
| `PUT /api/services/{id}` | administrador | `servicios.actualizar` + reindexado |
| `POST /api/services/{id}/toggle` | administrador | `servicios.alternar` + reindexado |

## Componentes
| Componente | Ubicación | Notas |
|---|---|---|
| Modelo | `app/models/servicio.py` | `TIPOS_SERVICIO`, `PRECIO_MINIMO = 1000`, `DURACION_MINIMA = 10` y sus `CHECK` |
| Ficha | `app/services/barberia.py` | `ID_BARBERIA = 1`; horario fijo “Lunes a sábado de 9:00 a 17:00 · domingos cerrado” |
| Reglas | `app/services/servicios.py` | `_validar`, `_aplicar`, `obtener` (404) |
| Esquemas | `app/schemas/servicio.py`, `app/schemas/comun.py` | `ServicioIn/Out`, `BarberiaBase`, `BarberiaResumen`, `BarberiaDetalle` |
| Semilla | `alembic/versions/002_datos_semilla.py` | Corte clásico $25.000/30 min, Barba perfilada $18.000/20 min, Combo $40.000/50 min, Tratamiento capilar $35.000/40 min |
| Inicio (web) | `app/page.tsx` | hero con chat incrustado, cifras (24/7, 40 min, 0 cruces) y “¿Cómo funciona?” |
| Barbería (web) | `app/barberia/page.tsx` | filtros por tipo, `ServicioCard`, `BarberoCard`, botón para abrir el chat flotante |
| Admin (web) | `app/admin/servicios/page.tsx` | formulario crear/editar y tabla con activar/desactivar |
| Formatos (web) | `lib/formato.ts` | `cop()`, `TIPOS`, `NOMBRE_TIPO`, `ICONO_TIPO` |

## Decisiones
- **Una sola barbería, interfaz de lista:** la API ya responde una lista para que sumar barberías no cambie el frontend.
- **Desactivar en vez de borrar:** las citas históricas siguen apuntando al servicio.
- **Reindexado con `BackgroundTasks`:** la respuesta al administrador no espera a Ollama; un error del indexado se registra y no afecta la petición.
