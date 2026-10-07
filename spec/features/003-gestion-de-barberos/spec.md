# 003 · Gestión de barberos

## Descripción
El administrador da de alta a los barberos con sus credenciales, especialidades y los servicios que ofrecen, y puede activarlos o desactivarlos. El público ve solo los barberos activos y puede filtrarlos por servicio.

## Historias de usuario
- Como **visitante**, quiero conocer a los barberos, sus especialidades y los servicios que ofrecen.
- Como **cliente**, quiero que al elegir un servicio solo aparezcan los barberos que lo ofrecen.
- Como **administrador**, quiero crear un barbero con su cuenta, especialidades y servicios.
- Como **administrador**, quiero desactivar a un barbero para que deje de recibir citas sin perder su historial.

## Criterios de aceptación
- [x] `GET /api/barbers` devuelve los barberos activos; el administrador ve también los inactivos.
- [x] `GET /api/barbers?service_id=N` devuelve solo los barberos que ofrecen ese servicio.
- [x] Solo el administrador crea barberos (`POST /api/barbers`); exige nombre, identificación, correo válido y contraseña de 8+ caracteres.
- [x] Si no se eligen servicios, el barbero ofrece todos los servicios activos.
- [x] Correo o identificación repetidos responden 409.
- [x] `POST /api/barbers/{id}/toggle` activa o desactiva; un id que no es barbero responde 404.
- [x] Un barbero inactivo desaparece del público, no tiene franjas libres, no puede agendarse y no puede iniciar sesión.
- [x] `/admin/barberos` muestra el formulario con los servicios activos marcados por defecto y la tabla con especialidades, servicios y estado.
- [ ] Editar los datos y los servicios de un barbero existente.
