# 005 · Agendamiento de citas

## Descripción
El cliente agenda una cita eligiendo servicio, barbero y franja libre, sin posibilidad de doble reserva. Cada rol ve las citas que le corresponden y puede cancelarlas o cerrarlas según sus permisos.

## Historias de usuario
- Como **cliente**, quiero agendar en tres pasos (servicio → barbero → horario) y ver un resumen antes de confirmar.
- Como **cliente**, si mi horario se ocupó mientras elegía, quiero ver alternativas.
- Como **cliente**, quiero ver y cancelar mis citas.
- Como **barbero**, quiero ver mi agenda y marcar cada cita confirmada como completada o inasistencia.
- Como **administrador**, quiero ver todas las citas, filtrarlas por fecha, barbero y estado, y cancelar cualquiera.

## Criterios de aceptación
- [x] Solo un `cliente` puede crear citas (`POST /api/appointments`); los demás roles reciben 403.
- [x] El servicio debe estar activo (404 si no) y el barbero debe ser un barbero activo que lo ofrezca (400 si no).
- [x] La franja debe estar libre y ser futura; la cita nace `pendiente`.
- [x] RN08: dos citas activas del mismo barbero en la misma fecha y hora son imposibles, incluso de forma concurrente; si la franja ya no está libre se responde 409 con hasta tres alternativas.
- [x] `GET /api/appointments`: el cliente ve sus citas, el barbero su agenda y el administrador todas (máx. 200, de la más reciente a la más antigua).
- [x] `POST /api/appointments/{id}/cancel`: el cliente cancela solo sus citas activas (`cancelada_cliente`); el administrador, cualquiera (`cancelada_admin`); la cita de otro cliente responde 404; una cita no activa, 400.
- [x] `PATCH /api/appointments/{id}/status` con `completada` o `inasistencia`: solo el barbero dueño o el administrador, y solo si la cita está `confirmada`.
- [x] `/agendar` acepta `?servicio=` y `?barbero=` para preseleccionar; al reservar redirige a `/citas`; ante 409 muestra las alternativas y recarga los horarios.
- [x] `/citas` muestra la tabla con estado en español y las acciones permitidas por rol; el administrador tiene filtros por fecha, barbero y estado.
