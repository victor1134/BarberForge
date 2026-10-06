# 001 · Plan técnico

## Endpoints
| Método y ruta | Acceso | Servicio |
|---|---|---|
| `GET /api/setup` | público | `usuarios.hay_admin` |
| `POST /api/register` | público | `usuarios.registrar` → `SesionOut {token, user}` |
| `POST /api/login` | público | `usuarios.autenticar` → `SesionOut` |
| `GET /api/me` | con sesión | usuario de `get_current_user` |
| `PATCH /api/me` | con sesión | `usuarios.actualizar_cuenta` → `CuentaOut` |

## Componentes
| Componente | Ubicación | Notas |
|---|---|---|
| Modelo | `app/models/usuario.py` | `Usuario` y `Rol` (`StrEnum`); una sola tabla `users` para los tres roles |
| Esquemas | `app/schemas/usuario.py` | `RegistroIn`, `LoginIn`, `SesionOut`, `CuentaIn`, `CuentaOut`, `UsuarioOut`, `SetupOut` |
| Seguridad | `app/core/seguridad.py` | `hash_password`, `verificar_password`, `crear_token`, `leer_token` |
| Dependencias | `app/core/dependencias.py` | `get_current_user_opcional` (visitante = `None`), `get_current_user` (401), `require_roles(...)` (403) |
| Reglas | `app/services/usuarios.py` | validaciones, RN02 con `pg_advisory_xact_lock(7001)`, `asegurar_admin_inicial` |
| Sesión (web) | `components/Sesion.tsx`, `lib/auth.ts` | contexto `useSesion()` con `iniciar`, `actualizar`, `salir` |
| Acceso (web) | `components/Acceso.tsx` | `TarjetaAcceso` y `useDestino` (redirige si ya hay sesión) |
| Panel (web) | `components/Panel.tsx` | exige sesión y rol; pestañas por rol + “Mi cuenta” |
| Páginas | `app/login`, `app/registro`, `app/cuenta` | formularios controlados; errores de la API en el formulario |

## Decisiones
- **Un usuario inactivo no autentica**, ni por login ni por token vigente (`get_current_user_opcional` lo trata como visitante).
- **Correo normalizado** a minúsculas y sin espacios antes de validar y buscar.
- **El administrador inicial por variables** recibe `id_number = admin-<correo>` para no chocar con la unicidad de identificación.
- **Inicio del panel por rol:** cliente → `/agendar`; barbero y administrador → `/citas` (`inicioPanel`).
