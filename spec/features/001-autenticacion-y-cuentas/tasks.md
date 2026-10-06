# 001 · Tareas

## Backend
- [x] Modelo `Usuario` con roles y restricciones de unicidad
- [x] Esquemas de registro, login, sesión y cuenta
- [x] bcrypt y JWT con vencimiento configurable
- [x] Dependencias `get_current_user`, `get_current_user_opcional` y `require_roles`
- [x] Registro con validaciones, política de datos y RN02
- [x] Login, `/api/me` y actualización de cuenta
- [x] Administrador inicial por `ADMIN_EMAIL` / `ADMIN_PASSWORD`
- [x] Pruebas (`tests/test_auth.py`): RN02, validaciones, duplicados 409, login y `/me`, 401 sin token, actualizar cuenta, admin por variables

## Frontend
- [x] `lib/auth.ts`: token en `localStorage` y `rutaSegura`
- [x] `SesionProvider` y `useSesion`
- [x] Páginas `/login` y `/registro` con regreso a `next`
- [x] Aviso de “primera cuenta = administrador”
- [x] `Panel` con control de rol y pestañas
- [x] Página `/cuenta` (preferencia de estilo solo para clientes)
- [x] `Navbar` con nombre, rol, “Mi panel” y “Salir”
