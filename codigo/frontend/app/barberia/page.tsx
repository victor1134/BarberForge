"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAviso, Vacio } from "@/components/Aviso";
import { BarberoCard } from "@/components/BarberoCard";
import { abrirChat } from "@/components/ChatFlotante";
import { ServicioCard } from "@/components/ServicioCard";
import { useSesion } from "@/components/Sesion";
import { api, type BarberiaDetalle, type TipoServicio } from "@/lib/api";
import { NOMBRE_TIPO, TIPOS } from "@/lib/formato";

const ID_BARBERIA = 1; // el MVP atiende una sola barbería

export default function Barberia() {
  const { usuario } = useSesion();
  const avisar = useAviso();
  const router = useRouter();
  const [barberia, setBarberia] = useState<BarberiaDetalle | null>(null);
  const [error, setError] = useState("");
  const [filtro, setFiltro] = useState<TipoServicio | "todos">("todos");

  useEffect(() => {
    api.barberia(ID_BARBERIA).then(setBarberia).catch((e: Error) => setError(e.message));
  }, []);

  function agendar(pre: { servicio?: number; barbero?: number } = {}) {
    const params = new URLSearchParams();
    if (pre.servicio) params.set("servicio", String(pre.servicio));
    if (pre.barbero) params.set("barbero", String(pre.barbero));
    const destino = "/agendar" + (params.size ? `?${params}` : "");
    if (!usuario) return router.push(`/login?next=${encodeURIComponent(destino)}`);
    if (usuario.role !== "cliente") return avisar("Solo los clientes pueden agendar citas.", "warn");
    router.push(destino);
  }

  if (error) return <section className="sec"><Vacio>No se pudo cargar la barbería.<br /><small>{error}</small></Vacio></section>;
  if (!barberia) return <section className="sec"><Vacio>Cargando…</Vacio></section>;

  const servicios = barberia.servicios.filter((s) => filtro === "todos" || s.service_type === filtro);
  return (
    <main>
      <div className="banner">
        <Link className="back" href="/">← Volver al inicio</Link>
        <h1>💈 {barberia.nombre}</h1>
        <p>📍 {barberia.direccion} · 🕘 {barberia.horario}</p>
        <p>{barberia.descripcion}</p>
        <div className="row">
          <button className="btn gold" onClick={() => agendar()}>Agendar cita</button>
          <button className="btn ghost" onClick={abrirChat}>Preguntar al asistente</button>
        </div>
      </div>
      <div className="pole" />

      <section className="sec">
        <div className="st"><h2>Servicios</h2><p>Precios en pesos colombianos y duración de cada servicio.</p></div>
        <div className="filters">
          {(["todos", ...TIPOS] as const).map((t) => (
            <button key={t} className={`fchip ${filtro === t ? "on" : ""}`} onClick={() => setFiltro(t)}>
              {t === "todos" ? "Todos" : NOMBRE_TIPO[t]}
            </button>
          ))}
        </div>
        <div className="grid">
          {servicios.length ? servicios.map((s) => (
            <ServicioCard key={s.id} servicio={s} onAgendar={() => agendar({ servicio: s.id })} />
          )) : <Vacio>No hay servicios de este tipo.</Vacio>}
        </div>
      </section>

      <section className="sec alt">
        <div className="st"><h2>Barberos</h2><p>Elige con quién quieres tu cita.</p></div>
        <div className="grid">
          {barberia.barberos.length ? barberia.barberos.map((b, i) => (
            <BarberoCard key={b.id} barbero={b} servicios={barberia.servicios} indice={i}
              onAgendar={() => agendar({ barbero: b.id })} />
          )) : <Vacio>Esta barbería aún no tiene barberos.</Vacio>}
        </div>
      </section>
    </main>
  );
}
