"use client";

import { Suspense, useState, type FormEvent } from "react";
import Link from "next/link";
import { TarjetaAcceso, useDestino } from "@/components/Acceso";
import { useAviso } from "@/components/Aviso";
import { useSesion } from "@/components/Sesion";
import { api } from "@/lib/api";
import { primerNombre } from "@/lib/formato";

function FormularioIngreso() {
  const { iniciar } = useSesion();
  const avisar = useAviso();
  const { siguiente } = useDestino();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function enviar(e: FormEvent) {
    e.preventDefault();
    setEnviando(true);
    setError("");
    try {
      const sesion = await api.login(email, password);
      iniciar(sesion); // TarjetaAcceso redirige al destino al detectar la sesión
      avisar(`¡Bienvenido, ${primerNombre(sesion.user.full_name)}!`);
    } catch (x) {
      setError((x as Error).message);
      setEnviando(false);
    }
  }

  const registro = "/registro" + (siguiente ? `?next=${encodeURIComponent(siguiente)}` : "");
  return (
    <TarjetaAcceso titulo="Ingresar" nota={siguiente ? "Inicia sesión o crea tu cuenta para agendar tu cita." : undefined}>
      <form onSubmit={enviar}>
        <label>Correo
          <input type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label>Contraseña
          <input type="password" required autoComplete="current-password" value={password}
            onChange={(e) => setPassword(e.target.value)} />
        </label>
        <div className="err">{error}</div>
        <button className="btn" disabled={enviando}>Entrar</button>
        <div className="switch">¿Primera vez? <Link href={registro}>Crear cuenta</Link></div>
      </form>
    </TarjetaAcceso>
  );
}

export default function Ingreso() {
  return <Suspense><FormularioIngreso /></Suspense>;
}
