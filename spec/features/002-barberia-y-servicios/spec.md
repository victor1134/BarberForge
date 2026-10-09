# 002 · Barbería y catálogo de servicios

## Descripción
Ficha pública de la barbería (nombre, dirección, horario, descripción), su catálogo de servicios con precio y duración, y la administración del catálogo. Cada cambio del catálogo actualiza la base de conocimiento del asistente.

## Historias de usuario
- Como **visitante**, quiero ver la barbería, sus servicios con precios en pesos y su duración, y filtrarlos por tipo.
- Como **visitante**, quiero pulsar “Agendar este servicio” y que se me pida iniciar sesión si no la tengo.
- Como **administrador**, quiero crear, editar, activar y desactivar servicios.
- Como **administrador**, quiero que el asistente conozca los cambios del catálogo sin hacer nada más.

## Criterios de aceptación
- [x] `GET /api/barberias` devuelve una lista con la ficha y el número de servicios y barberos activos.
- [x] `GET /api/barberias/1` devuelve la ficha con servicios y barberos activos; otro id responde 404.
- [x] Nombre, dirección y zona salen de `BARBERIA_NOMBRE` y `BARBERIA_DIRECCION`; la ficha incluye la URL del buzón (`MAILHOG_URL`).
- [x] `GET /api/services` muestra solo los activos a visitantes y clientes, y todos al administrador.
- [x] Solo el administrador crea (`POST`), edita (`PUT`) y activa/desactiva (`/toggle`) servicios; otros roles reciben 403.
- [x] Se rechaza un servicio sin nombre, con precio menor a $1.000, duración menor a 10 min o tipo fuera de `corte`, `barba`, `combo`, `tratamiento` (400 y `CHECK` en la base).
- [x] Crear, editar o alternar un servicio dispara el reindexado del asistente en segundo plano.
- [x] `/barberia` muestra filtros por tipo, tarjetas de servicios y de barberos; “Agendar” lleva a `/agendar` con el servicio o barbero preseleccionado, o a `/login?next=…` si no hay sesión; un barbero o administrador ve un aviso.
- [x] `/admin/servicios` lista todos los servicios con tipo, precio, duración y estado, y permite editar en el mismo formulario.
- [ ] El inicio tiene la sección `#barberias` a la que apunta el enlace “Barberías” del `Navbar`.
