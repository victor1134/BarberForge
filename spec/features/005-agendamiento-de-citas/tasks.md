# 005 · Tareas

## Backend
- [x] Modelo `Cita` con estados e índice único parcial
- [x] Agendar con validación de servicio, barbero y franja
- [x] Conflicto 409 con tres alternativas
- [x] Listado por rol
- [x] Cancelar según el rol
- [x] Cerrar como completada o inasistencia
- [x] Pruebas (`tests/test_citas.py`): la franja deja de estar libre, 409 con alternativas, índice único sin la validación previa, solo clientes agendan y el barbero debe ofrecer el servicio, visibilidad por rol, cancelar libera la franja

## Frontend
- [x] `/agendar` en tres pasos con preselección por URL
- [x] Resumen y botón “Confirmar cita”
- [x] Manejo de 409 con alternativas
- [x] `/citas` con acciones por rol y estado
- [x] Filtros del administrador por fecha, barbero y estado
