"use client";

import { useEffect, useRef, type ReactNode } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { Rol, Usuario } from "@/lib/api";
import { ROLES } from "@/lib/formato";
import { Vacio } from "./Aviso";
import { useSesion } from "./Sesion";

const PESTANAS: Record<Rol, [string, string][]> = {
  cliente: [["/agendar", "Agendar cita"], ["/citas", "Mis citas"]],
  barbero: [["/citas", "Mi agenda"]],
  administrador: [
    ["/citas", "Todas las citas"],
    ["/admin/barberos", "Barberos"],
    ["/admin/servicios", "Servicios"],
    ["/admin/disponibilidad", "Disponibilidad"],
  ],
};

interface Props {
  roles: Rol[];
  children: (usuario: Usuario) => ReactNode;
}

/** Marco de las páginas privadas: exige sesión y rol, y muestra las pestañas del rol. */
export function Panel({ roles, children }: Props) {
  const { usuario, cargando } = useSesion();
  const router = useRouter();
  const ruta = usePathname();

  // Si al entrar no hay sesión, se pide iniciar sesión. Si la sesión se cierra aquí mismo,
  // la barra de navegación ya lleva al inicio y no se redirige al login.
  const tuvoSesion = useRef(false);
  if (usuario) tuvoSesion.current = true;
  useEffect(() => {
    if (!cargando && !usuario && !tuvoSesion.current) router.replace(`/login?next=${encodeURIComponent(ruta)}`);
  }, [cargando, usuario, ruta, router]);

  if (cargando || !usuario) return <main className="panel"><Vacio>Cargando…</Vacio></main>;

  const pestanas = [...PESTANAS[usuario.role], ["/cuenta", "Mi cuenta"] as [string, string]];
  return (
    <main className="panel">
      <h2>Panel de {ROLES[usuario.role].toLowerCase()}</h2>
      <div className="tabs">
        {pestanas.map(([href, nombre]) => (
          <Link key={href} href={href} className={`tab ${ruta === href ? "on" : ""}`}>{nombre}</Link>
        ))}
      </div>
      {roles.includes(usuario.role)
        ? children(usuario)
        : <Vacio>Esta sección no está disponible para tu rol.</Vacio>}
    </main>
  );
}
