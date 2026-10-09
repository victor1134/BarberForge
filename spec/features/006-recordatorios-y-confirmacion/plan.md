# 006 · Plan técnico

## Endpoints
| Método y ruta | Acceso | Servicio |
|---|---|---|
| `POST /api/appointments/{id}/remind` | administrador | `citas.recordar` → `enviar_recordatorio` |
| `GET /api/confirm/{token}` | público (enlace del correo) | `citas.confirmar_por_token` → HTML |

## Componentes
| Componente | Ubicación | Notas |
|---|---|---|
| Constantes | `app/services/citas.py` | `MINUTOS_RECORDATORIO = 40`, `MINUTOS_PARA_CONFIRMAR = 15` |
| Recordatorio | `citas.enviar_recordatorio` | genera token, guarda `token_hash` y `reminder_sent_at` (UTC) y envía el correo |
| Ciclo periódico | `citas.procesar_recordatorios` | envía los próximos, cancela los vencidos con un `UPDATE` y borra franjas antiguas |
| Tarea de fondo | `app/services/arranque.py` | `recordatorios()` cada 60 s, solo cuando la base está lista |
| Tokens | `app/core/seguridad.py` | `nuevo_token_un_uso` (`secrets.token_urlsafe(24)`) y `hash_token` |
| Correo | `app/services/correo.py` | `smtplib` hacia `SMTP_HOST:SMTP_PORT` (MailHog `mailhog:1025`) |
| Página HTML | `app/routers/citas.py` | `_pagina_confirmacion`, con estilos en línea |
| Web | `app/citas/page.tsx` | acción `recordar` y enlace al buzón tomado de `/api/barberias` |

## Decisiones
- **Ventana de envío en hora local** (la cita está en hora local) y **vencimiento en UTC** (`reminder_sent_at` es técnico).
- **Solo se guarda el hash del token:** quien lea la base no puede confirmar citas.
- **La confirmación no requiere sesión:** el enlace de un solo uso, que vence en 15 minutos, es la prueba.
- **El fallo del correo no bloquea:** `correo.enviar` devuelve `False` y deja la advertencia en el log.
