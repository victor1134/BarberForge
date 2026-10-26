"use client";

import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";
import { useAviso, Vacio } from "@/components/Aviso";
import { Panel } from "@/components/Panel";
import { api, type Servicio, type ServicioIn, type TipoServicio } from "@/lib/api";
import { cop, NOMBRE_TIPO, TIPOS } from "@/lib/formato";

const VACIO: ServicioIn = { name: "", description: "", price_cop: 0, duration_minutes: 0, service_type: "corte" };

function GestionServicios() {
  const avisar = useAviso();
  const formulario = useRef<HTMLFormElement>(null);
  const [servicios, setServicios] = useState<Servicio[] | null>(null);
  const [error, setError] = useState("");
  const [datos, setDatos] = useState<ServicioIn>(VACIO);
  const [editando, setEditando] = useState<number | null>(null);

  const cargar = useCallback(() => {
    api.servicios().then(setServicios).catch((e: Error) => setError(e.message));
  }, []);
  useEffect(cargar, [cargar]);

  const campo = <K extends keyof ServicioIn>(k: K, v: ServicioIn[K]) => setDatos((d) => ({ ...d, [k]: v }));

  function editar(s: Servicio) {
    setEditando(s.id);
    setDatos({ name: s.name, description: s.description ?? "", price_cop: s.price_cop,
      duration_minutes: s.duration_minutes, service_type: s.service_type });
    formulario.current?.scrollIntoView({ behavior: "smooth" });
  }

  function cancelarEdicion() {
    setEditando(null);
    setDatos(VACIO);
  }

  async function guardar(e: FormEvent) {
    e.preventDefault();
    try {
      if (editando) await api.editarServicio(editando, datos);
      else await api.crearServicio(datos);
      avisar(editando ? "Servicio actualizado" : "Servicio creado");
      cancelarEdicion();
      cargar();
    } catch (x) {
      avisar((x as Error).message, "err");
    }
  }

  async function alternar(id: number) {
    try {
      await api.alternarServicio(id);
      cargar();
    } catch (x) {
      avisar((x as Error).message, "err");
    }
  }

  if (error) return <Vacio>{error}</Vacio>;
  if (!servicios) return <Vacio>Cargando…</Vacio>;

  return (
    <>
      <form className="card form" ref={formulario} onSubmit={guardar}>
        <label>Nombre<input required value={datos.name} onChange={(e) => campo("name", e.target.value)} /></label>
        <label>Descripción<input value={datos.description} onChange={(e) => campo("description", e.target.value)} /></label>
        <label>Precio COP
          <input type="number" min={1000} required value={datos.price_cop || ""}
            onChange={(e) => campo("price_cop", Number(e.target.value))} />
        </label>
        <label>Minutos
          <input type="number" min={10} required value={datos.duration_minutes || ""}
            onChange={(e) => campo("duration_minutes", Number(e.target.value))} />
        </label>
        <label>Tipo
          <select value={datos.service_type} onChange={(e) => campo("service_type", e.target.value as TipoServicio)}>
            {TIPOS.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </label>
        <button className="btn">{editando ? "Guardar cambios" : "Crear servicio"}</button>
        {editando && <button type="button" className="btn line" onClick={cancelarEdicion}>Cancelar edición</button>}
      </form>
      <div className="tw">
        <table>
          <thead><tr><th>Servicio</th><th>Tipo</th><th>Precio</th><th>Duración</th><th>Estado</th><th></th></tr></thead>
          <tbody>
            {servicios.map((s) => (
              <tr key={s.id}>
                <td>{s.name}</td>
                <td>{NOMBRE_TIPO[s.service_type]}</td>
                <td>{cop(s.price_cop)}</td>
                <td>{s.duration_minutes} min</td>
                <td><span className={`pill ${s.is_active ? "st-confirmada" : "st-inasistencia"}`}>{s.is_active ? "Activo" : "Inactivo"}</span></td>
                <td>
                  <button className="ab" onClick={() => editar(s)}>Editar</button>
                  <button className="ab" onClick={() => alternar(s.id)}>{s.is_active ? "Desactivar" : "Activar"}</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default function Servicios() {
  return <Panel roles={["administrador"]}>{() => <GestionServicios />}</Panel>;
}
