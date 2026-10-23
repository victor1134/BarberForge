// Guarda el token JWT de la sesión en el navegador.
const CLAVE = "bf_t";

export function leerToken(): string | null {
  return typeof window === "undefined" ? null : localStorage.getItem(CLAVE);
}

export function guardarToken(token: string): void {
  localStorage.setItem(CLAVE, token);
}

export function borrarToken(): void {
  localStorage.removeItem(CLAVE);
}

// Solo se permite volver a rutas internas tras iniciar sesión (evita redirecciones abiertas).
export function rutaSegura(ruta: string | null | undefined): string | null {
  return ruta && ruta.startsWith("/") && !ruta.startsWith("//") ? ruta : null;
}
