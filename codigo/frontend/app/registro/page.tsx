"use client";

import { Suspense, useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import { TarjetaAcceso, useDestino } from "@/components/Acceso";
import { useAviso } from "@/components/Aviso";
import { useSesion } from "@/components/Sesion";
import { api, type RegistroIn } from "@/lib/api";
import { primerNombre } from "@/lib/formato";

const VACIO: RegistroIn = { full_name: "", id_type: "CC", id_number: "", email: "", password: "", accept_policy: false };

function FormularioRegistro() {
  const { iniciar } = useSesion();
  const avisar = useAviso();
  const { siguiente } = useDestino();
  const [datos, setDatos] = useState<RegistroIn>(VACIO);
  const [hayAdmin, setHayAdmin] = useState(true);
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    api.setup().then((r) => setHayAdmin(r.hay_admin)).catch(() => {});
  }, []);

  const campo = <K extends keyof RegistroIn>(k: K, v: RegistroIn[K]) => setDatos((d) => ({ ...d, [k]: v }));

  async function enviar(e: FormEvent) {
    e.preventDefault();
    setEnviando(true);
    setError("");
    try {
      const sesion = await api.registrar(datos);
      iniciar(sesion); // TarjetaAcceso redirige al destino al detectar la sesión
      avisar(`¡Bienvenido, ${primerNombre(sesion.user.full_name)}!`);
    } catch (x) {
      setError((x as Error).message);
      setEnviando(false);
    }
  }

  const ingreso = "/login" + (siguiente ? `?next=${encodeURIComponent(siguiente)}` : "");
  return (
    <TarjetaAcceso titulo="Crear cuenta">
      <form onSubmit={enviar}>
        <label>Nombre completo
          <input required autoComplete="name" value={datos.full_name} onChange={(e) => campo("full_name", e.target.value)} />
        </label>
        <div style={{ display: "flex", gap: 10 }}>
          <label style={{ flex: 0.6 }}>Tipo
            <select value={datos.id_type} onChange={(e) => campo("id_type", e.target.value)}>
              <option>CC</option><option>CE</option><option>TI</option>
            </select>
          </label>
          <label>Número
            <input required inputMode="numeric" value={datos.id_number} onChange={(e) => campo("id_number", e.target.value)} />
          </label>
        </div>
        <label>Correo
          <input type="email" required autoComplete="email" value={datos.email} onChange={(e) => campo("email", e.target.value)} />
        </label>
        <label>Contraseña (mínimo 8)
          <input type="password" minLength={8} required autoComplete="new-password" value={datos.password}
            onChange={(e) => campo("password", e.target.value)} />
        </label>
        <label className="chk">
          <input type="checkbox" checked={datos.accept_policy} onChange={(e) => campo("accept_policy", e.target.checked)} />
          Acepto la política de tratamiento de datos (Ley 1581 de 2012)
        </label>
        {!hayAdmin && <div className="note">Aún no hay administrador: esta primera cuenta quedará como administrador de la barbería.</div>}
        <div className="err">{error}</div>
        <button className="btn" disabled={enviando}>Crear mi cuenta</button>
        <div className="switch">¿Ya tienes cuenta? <Link href={ingreso}>Ingresar</Link></div>
      </form>
    </TarjetaAcceso>
  );
}

export default function Registro() {
  return <Suspense><FormularioRegistro /></Suspense>;
}
