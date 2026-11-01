"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAviso } from "./Aviso";
import { useSesion } from "./Sesion";
import { inicioPanel, ROLES } from "@/lib/formato";

export function Navbar() {
  const { usuario, salir } = useSesion();
  const avisar = useAviso();
  const router = useRouter();

  function cerrarSesion() {
    salir();
    router.push("/");
    avisar("Sesión cerrada");
  }

  return (
    <header className="top">
      <Link href="/" className="logo">
        <i>💈</i>
        <span>Barber<b>Forge</b> AI</span>
      </Link>
      <nav className="main">
        <Link href="/#barberias">Barberías</Link>
        <Link href="/#proceso">¿Cómo funciona?</Link>      </nav>
      <div className="hd">
        {usuario ? (
          <>
            <span className="who">
              {usuario.full_name}
              <span className="role">{ROLES[usuario.role]}</span>
            </span>
            <Link className="btn line sm" href={inicioPanel(usuario.role)}>Mi panel</Link>
            <button className="btn sm" onClick={cerrarSesion}>Salir</button>
          </>
        ) : (
          <>
            <Link className="btn line sm" href="/login">Ingresar</Link>
            <Link className="btn sm" href="/registro">Registrarse</Link>
          </>
        )}
      </div>
    </header>
  );
}
