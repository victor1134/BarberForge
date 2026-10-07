# 003 · Plan técnico

## Endpoints
| Método y ruta | Acceso | Servicio |
|---|---|---|
| `GET /api/barbers[?service_id=]` | público (admin ve inactivos) | `barberos.listar` → `BarberoOut[]` |
| `POST /api/barbers` | administrador | `barberos.crear` |
| `POST /api/barbers/{id}/toggle` | administrador | `barberos.alternar` |

## Componentes
| Componente | Ubicación | Notas |
|---|---|---|
| Modelo | `app/models/usuario.py`, `app/models/barbero_servicio.py` | el barbero es un `Usuario` con `role = barbero`; `servicios` por la tabla `barber_services`; propiedad `service_ids` |
| Esquemas | `app/schemas/barbero.py` | `BarberoIn` (con `service_ids`), `BarberoOut` (sin correo ni identificación) |
| Reglas | `app/services/barberos.py` | reutiliza `validar_correo` y `validar_clave` de `usuarios`; `specialties` máx. 200 caracteres |
| Semilla | `alembic/versions/002_datos_semilla.py` | con `SEED_DEMO=true`: Carlos Mena y Luis Ortiz (clave `Demo12345`); todo barbero sin servicios recibe el catálogo completo |
| Admin (web) | `app/admin/barberos/page.tsx` | formulario con casillas de servicios y tabla con activar/desactivar |
| Tarjeta (web) | `components/BarberoCard.tsx` | avatar con iniciales, especialidades, servicios y “Agendar con …” |

## Decisiones
- **Barberos en la tabla `users`:** comparten login y sesión con los demás roles; el rol los distingue.
- **`BarberoOut` no expone correo ni identificación**, porque el listado es público.
- **El filtro por servicio se hace en Python** sobre `service_ids` (pocos barberos por barbería).
