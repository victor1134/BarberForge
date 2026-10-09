# 006 · Recordatorios y confirmación

## Descripción
Cada cita pendiente recibe un correo 40 minutos antes con un enlace de confirmación de un solo uso. Si el cliente no confirma en 15 minutos, la cita se cancela y la franja queda libre para otro cliente.

## Historias de usuario
- Como **cliente**, quiero recibir un recordatorio y confirmar mi cita con un clic, sin iniciar sesión.
- Como **barbería**, quiero que las citas no confirmadas se liberen solas para no perder la franja.
- Como **administrador**, quiero enviar un recordatorio a mano y abrir el buzón de correos de prueba.

## Criterios de aceptación
- [x] Una tarea de fondo revisa cada 60 s las citas `pendiente` sin recordatorio cuya hora cae entre ahora y 40 min después, y les envía el correo.
- [x] El correo incluye servicio, fecha, hora y el enlace `PUBLIC_URL/api/confirm/{token}`.
- [x] El token es aleatorio; en la base solo se guarda su hash SHA-256 y la hora de envío.
- [x] `GET /api/confirm/{token}` confirma la cita si está `pendiente` y el recordatorio se envió hace menos de 15 min; devuelve una página HTML de éxito o de “El enlace venció o ya fue usado”.
- [x] El enlace sirve una sola vez: al confirmar o cancelar se borra el hash.
- [x] Las citas `pendiente` con recordatorio de hace más de 15 min pasan a `cancelada_sin_confirmar`.
- [x] `POST /api/appointments/{id}/remind` (solo administrador) envía el recordatorio a una cita `pendiente`; en otro estado responde 400.
- [x] Si el SMTP falla, se registra una advertencia y la API sigue funcionando.
- [x] En `/citas` el administrador ve “Enviar recordatorio” en las citas pendientes y el enlace “Abrir buzón de correos” (`MAILHOG_URL`).
- [ ] Correo de aviso al agendar y al cancelar.
