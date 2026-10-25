"use client";

import { useCallback, useEffect, useState } from "react";
import { useAviso, Vacio } from "@/components/Aviso";
import { Panel } from "@/components/Panel";
import { api, type Cita, type EstadoCita, type Usuario } from "@/lib/api";
import { ESTADOS } from "@/lib/formato";

type Accion = "cancelar" | "recordar" | "completada" | "inasistencia";

function Acciones({ cita, rol, onAccion }: { cita: Cita; rol: Usuario["role"]; onAccion: (a: Accion) => void }) {
  const activa = cita.status === "pendiente" || cita.status === "confirmada";
  return (
    <>
      {activa && rol !== "barbero" && <button className="ab red" onClick={() => onAccion("cancelar")}>Cancelar</button>}
      {rol === "administrador" && cita.status === "pendiente" &&
        <button className="ab" onClick={() => onAccion("recordar")}>Enviar recordatorio</button>}
      {cita.status === "confirmada" && rol !== "cliente" && (
        <>
          <button className="ab" onClick={() => onAccion("completada")}>Completada</button>
          <button className="ab red" onClick={() => onAccion("inasistencia")}>Inasistencia</button>
        </>
      )}
    </>
  );
}

function ListaCitas({ usuario }: { usuario: Usuario }) {
  const avisar = useAviso();
  const [citas, setCitas] = useState<Cita[] | null>(null);
  const [error, setError] = useState("");
  const [buzon, setBuzon] = useState("");
  const [fecha, setFecha] = useState("");
  const [barbero, setBarbero] = useState("");
  const [estado, setEstado] = useState<EstadoCita | "">("");
  const esAdmin = usuario.role === "administrador";

  const cargar = useCallback(() => {
    api.citas().then(setCitas).catch((e: Error) => setError(e.message));
  }, []);

  useEffect(() => {
    cargar();
    if (esAdmin) api.barberias().then((b) => setBuzon(b[0]?.buzon_url ?? "")).catch(() => {});
  }, [cargar, esAdmin]);

  async function ejecutar(cita: Cita, accion: Accion) {
    try {
      if (accion === "cancelar") await api.cancelarCita(cita.id);
      else if (accion === "recordar") {
        await api.recordarCita(cita.id);
        avisar("Recordatorio enviado. Revisa el buzón de correos.");
      } else await api.cerrarCita(cita.id, accion);
      cargar();
    } catch (e) {
      avisar((e as Error).message, "err");
    }
  }

  if (error) return <Vacio>{error}</Vacio>;
  if (!citas) return <Vacio>Cargando…</Vacio>;

  const barberos = [...new Set(citas.map((c) => c.barber))];
  const filtradas = citas.filter((c) =>
    (!fecha || c.date === fecha) && (!barbero || c.barber === barbero) && (!estado || c.status === estado));

  return (
    <>
      {esAdmin && (
        <div className="card fbar">
          <label>Fecha<input type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} /></label>
          <label>Barbero
            <select value={barbero} onChange={(e) => setBarbero(e.target.value)}>
              <option value="">Todos</option>
              {barberos.map((b) => <option key={b}>{b}</option>)}
            </select>
          </label>
          <label>Estado
            <select value={estado} onChange={(e) => setEstado(e.target.value as EstadoCita | "")}>
              <option value="">Todos</option>
              {Object.entries(ESTADOS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </label>
          {buzon && <a className="btn line sm" target="_blank" rel="noopener" href={buzon}>📬 Abrir buzón de correos</a>}
        </div>
      )}
      <div className="tw">
        {filtradas.length ? (
          <table>
            <thead>
              <tr><th>Fecha</th><th>Hora</th><th>Servicio</th><th>Barbero</th><th>Cliente</th><th>Estado</th><th></th></tr>
            </thead>
            <tbody>
              {filtradas.map((c) => (
                <tr key={c.id}>
                  <td>{c.date}</td><td>{c.time}</td><td>{c.service}</td><td>{c.barber}</td><td>{c.client}</td>
                  <td><span className={`pill st-${c.status}`}>{ESTADOS[c.status] ?? c.status}</span></td>
                  <td><Acciones cita={c} rol={usuario.role} onAccion={(a) => ejecutar(c, a)} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : <Vacio sinBorde>{citas.length ? "No hay citas con esos filtros." : "Aún no hay citas."}</Vacio>}
      </div>
    </>
  );
}

export default function Citas() {
  return (
    <Panel roles={["cliente", "barbero", "administrador"]}>
      {(usuario) => <ListaCitas usuario={usuario} />}
    </Panel>
  );
}
