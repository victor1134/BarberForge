# Misión

## Qué se construye
**BarberForge AI** es una plataforma web de agendamiento para una barbería. El visitante consulta la ficha de la barbería, sus servicios con precios y sus barberos; el cliente agenda en una franja libre, por formulario en tres pasos o conversando con un asistente con IA local; la barbería administra catálogo, barberos y agenda desde un panel por rol.

Proyecto del Diplomado CloudForge AI 5.0 (Unicomfacauca).

## Para quién
| Rol | Qué puede hacer en la plataforma | Pantallas |
|---|---|---|
| Visitante (sin sesión) | Ver la barbería, servicios, barberos y horario; conversar con el asistente; registrarse. | `/`, `/barberia`, `/registro`, `/login` |
| Cliente | Agendar, ver y cancelar sus citas; confirmar el recordatorio por correo; editar su cuenta y su preferencia de estilo. | `/agendar`, `/citas`, `/cuenta` |
| Barbero | Ver su agenda y cerrar sus citas confirmadas (completada o inasistencia); consultar en el chat la agenda de hoy y los documentos internos. | `/citas` (“Mi agenda”), `/cuenta` |
| Administrador | Gestionar servicios, barberos y disponibilidad; ver y filtrar todas las citas; cancelar cualquiera; enviar recordatorios; reindexar el asistente. | `/citas`, `/admin/barberos`, `/admin/servicios`, `/admin/disponibilidad`, `/cuenta` |

## Diferenciadores
- **Cero cruces de horario:** el índice único parcial `uq_cita_activa` impide la doble reserva aunque dos clientes agenden al mismo tiempo (RN08). Si la franja se ocupó, la API responde 409 con tres alternativas.
- **Asistente con IA local (Ollama):** responde con RAG sobre la base de conocimiento de la barbería y guía el agendamiento con botones usando la disponibilidad real. Sin Ollama, sigue funcionando con búsqueda por palabras clave.
- **Recordatorio con confirmación:** correo 40 minutos antes con un enlace de un solo uso. Si no se confirma en 15 minutos, la cita pasa a `cancelada_sin_confirmar` y la franja se libera.
- **Seguridad por rol también en la IA:** los documentos internos solo se recuperan para barberos y administradores (filtro en SQL), y una guarda rechaza los intentos de inyección de prompts.

## Reglas de negocio
| Código | Regla | Dónde se aplica |
|---|---|---|
| RN02 | La primera cuenta registrada queda como administrador; las siguientes, como clientes. Alternativa: `ADMIN_EMAIL` + `ADMIN_PASSWORD` crean el administrador al arrancar. | `services/usuarios.py` |
| RN08 | Un barbero no puede tener dos citas activas (`pendiente` o `confirmada`) en la misma fecha y hora. | `models/cita.py`, `services/citas.py` |
| — | Solo los clientes agendan, y solo con un barbero activo que ofrezca un servicio activo, en una franja futura y libre. | `services/citas.py` |
| — | El cliente cancela sus citas activas; el administrador cancela cualquiera; el barbero no cancela. | `services/citas.py` |
| — | Solo una cita `confirmada` se cierra como `completada` o `inasistencia` (barbero dueño o administrador). | `services/citas.py` |
| — | No se generan franjas los domingos y generar dos veces el mismo rango no duplica. | `services/disponibilidad.py` |
| — | Servicio: precio mínimo $1.000 COP, duración mínima 10 min, tipo `corte`, `barba`, `combo` o `tratamiento`. | `models/servicio.py`, `services/servicios.py` |
| — | Contraseñas de al menos 8 caracteres; identificación `CC`, `CE` o `TI`; registro solo aceptando la política de datos (Ley 1581 de 2012). | `services/usuarios.py` |

## Estados de una cita
```
pendiente ──(confirma por correo)──> confirmada ──> completada | inasistencia
    │                                    │
    ├──(sin confirmar en 15 min)──> cancelada_sin_confirmar
    └──────────(cancelar)────────────────┴──> cancelada_cliente | cancelada_admin
```

## Alcance actual
- Una sola barbería (`ID_BARBERIA = 1`). La API ya devuelve una lista en `/api/barberias` para crecer sin cambiar la interfaz.
- Sin pagos en línea ni aplicación móvil.
- La IA es siempre local; ningún dato sale a servicios en la nube.

## Limitaciones conocidas
- Los datos son sintéticos (barberos de demostración `carlos@demo.co` y `luis@demo.co`, clave `Demo12345`).
- El correo sale por SMTP a MailHog: en el MVP no se envían correos reales.
- Sin Ollama, el asistente devuelve el fragmento encontrado, sin redactar la respuesta.
- El asistente no guarda historial: cada mensaje se responde por separado.
