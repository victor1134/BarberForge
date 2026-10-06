# 001 · Autenticación y cuentas

## Descripción
Registro, inicio de sesión con JWT y roles (`cliente`, `barbero`, `administrador`), gestión de la propia cuenta y protección de las páginas privadas del frontend según el rol.

## Historias de usuario
- Como **visitante**, quiero crear mi cuenta aceptando la política de datos para poder agendar.
- Como **primera persona en registrarse**, quiero quedar como administrador de la barbería y que el formulario me lo avise.
- Como **usuario registrado**, quiero iniciar sesión y volver a la página que intentaba abrir.
- Como **usuario**, quiero cambiar mi nombre, correo y contraseña; como **cliente**, además, mi preferencia de estilo.
- Como **usuario**, quiero ver solo las pestañas de mi rol en el panel.
- Como **operador**, quiero crear el administrador inicial por variables de entorno.

## Criterios de aceptación
- [x] `POST /api/register` exige nombre, número de identificación, tipo `CC`/`CE`/`TI`, correo válido, contraseña de 8+ caracteres y `accept_policy = true`; guarda la fecha de aceptación de la política.
- [x] La primera cuenta queda como `administrador` y las siguientes como `cliente` (RN02); en PostgreSQL un candado evita dos administradores por registros simultáneos.
- [x] `GET /api/setup` indica si ya hay administrador; el registro muestra el aviso cuando no lo hay.
- [x] Correo o identificación repetidos responden 409.
- [x] `POST /api/login` responde 401 con “Correo o contraseña incorrectos” si las credenciales fallan o la cuenta está inactiva.
- [x] Las contraseñas se guardan con bcrypt; el token JWT (HS256) vence a las `JWT_HORAS` (8 por defecto).
- [x] `GET /api/me` devuelve el usuario de la sesión; sin token, 401.
- [x] `PATCH /api/me` actualiza nombre y correo; cambiar la contraseña exige la actual; `style_pref` solo se guarda para clientes (máx. 200 caracteres); el rol no se puede cambiar.
- [x] Con `ADMIN_EMAIL` y `ADMIN_PASSWORD` el administrador se crea al arrancar si no existe.
- [x] El frontend guarda el token en `localStorage`, recupera la sesión al abrir la página y la borra si la API responde 401/403.
- [x] Las páginas privadas redirigen a `/login?next=…`; tras ingresar se vuelve a `next` solo si es una ruta interna (`rutaSegura`) y, si es `/agendar`, solo para clientes.
- [x] El `Panel` muestra pestañas por rol y un aviso si la sección no corresponde al rol.
