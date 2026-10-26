"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useAviso, Vacio } from "@/components/Aviso";
import { Panel } from "@/components/Panel";
import { api, type Barbero, type GenerarDisponibilidadIn } from "@/lib/api";
import { hoyISO } from "@/lib/formato";

function GestionDisponibilidad() {
  const avisar = useAviso();
  const [barberos, setBarberos] = useState<Barbero[] | null>(null);
  const [error, setError] = useState("");
  const [reindexando, setReindexando] = useState(false);
  const [datos, setDatos] = useState<GenerarDisponibilidadIn>({
    barber_id: 0, date_from: hoyISO(), date_to: hoyISO(), start: "09:00", end: "17:00", minutes: 30,
  });

  useEffect(() => {
    api.barberos()
      .then((b) => {
        const activos = b.filter((x) => x.is_active);
        setBarberos(activos);
        if (activos[0]) setDatos((d) => ({ ...d, barber_id: activos[0].id }));
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  const campo = <K extends keyof GenerarDisponibilidadIn>(k: K, v: GenerarDisponibilidadIn[K]) =>
    setDatos((d) => ({ ...d, [k]: v }));

  async function generar(e: FormEvent) {
    e.preventDefault();
    try {
      await api.generarDisponibilidad(datos);
      avisar("Disponibilidad generada");
    } catch (x) {
      avisar((x as Error).message, "err");
    }
  }

  async function reindexar() {
    setReindexando(true);
    avisar("Reindexando… puede tardar si el modelo está ocupado.", "warn");
    try {
      const r = await api.reindexar();
      if (r.embeddings_ok) avisar("Asistente reindexado");
      else avisar("Reindexado sin embeddings: Ollama aún descarga los modelos", "warn");
    } catch (x) {
      avisar((x as Error).message, "err");
    }
    setReindexando(false);
  }

  if (error) return <Vacio>{error}</Vacio>;
  if (!barberos) return <Vacio>Cargando…</Vacio>;

  return (
    <>
      <form className="card form" onSubmit={generar}>
        <label>Barbero
          <select value={datos.barber_id} onChange={(e) => campo("barber_id", Number(e.target.value))}>
            {barberos.map((b) => <option key={b.id} value={b.id}>{b.full_name}</option>)}
          </select>
        </label>
        <label>Desde<input type="date" required value={datos.date_from} onChange={(e) => campo("date_from", e.target.value)} /></label>
        <label>Hasta<input type="date" required value={datos.date_to} onChange={(e) => campo("date_to", e.target.value)} /></label>
        <label>Inicio<input type="time" value={datos.start} onChange={(e) => campo("start", e.target.value)} /></label>
        <label>Fin<input type="time" value={datos.end} onChange={(e) => campo("end", e.target.value)} /></label>
        <label>Minutos por franja
          <input type="number" min={10} value={datos.minutes} onChange={(e) => campo("minutes", Number(e.target.value))} />
        </label>
        <button className="btn" disabled={!barberos.length}>Generar disponibilidad</button>
      </form>
      <p className="mute" style={{ margin: "14px 0" }}>
        Los domingos no se generan franjas y no se duplican las que ya existen.
      </p>
      <button className="btn line" disabled={reindexando} onClick={reindexar}>Reindexar asistente</button>
    </>
  );
}

export default function Disponibilidad() {
  return <Panel roles={["administrador"]}>{() => <GestionDisponibilidad />}</Panel>;
}
