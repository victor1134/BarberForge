"use client";

import { useEffect, type ReactNode } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import type { Usuario } from "@/lib/api";
import { rutaSegura } from "@/lib/auth";
import { inicioPanel } from "@/lib/formato";
import { useSesion } from "./Sesion";

/** Página a la que se vuelve después de iniciar sesión o registrarse. */
export function useDestino() {
  const params = useSearchParams();
  const siguiente = rutaSegura(params.get("next"));
  return {
    siguiente,
    destinoPara(usuario: Usuario) {
      // /agendar es solo para clientes; los demás roles van a su panel.
      if (siguiente && (usuario.role === "cliente" || !siguiente.startsWith("/agendar"))) return siguiente;
      return inicioPanel(usuario.role);
    },
  };
}

/** Tarjeta centrada de ingreso/registro. Si ya hay sesión, redirige al panel. */
export function TarjetaAcceso({ titulo, nota, children }: { titulo: string; nota?: string; children: ReactNode }) {
  const { usuario, cargando } = useSesion();
  const { destinoPara } = useDestino();
  const router = useRouter();

  useEffect(() => {
    if (!cargando && usuario) router.replace(destinoPara(usuario));
  }, [cargando, usuario]); // destinoPara depende de la URL, que no cambia en esta página

  return (
    <main className="auth">
      <div className="card">
        <h2>{titulo}</h2>
        {nota && <div className="note">{nota}</div>}
        {children}
      </div>
    </main>
  );
}
