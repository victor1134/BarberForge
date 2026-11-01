"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useAviso, Vacio } from "@/components/Aviso";
import { Panel } from "@/components/Panel";
import { api, type Barbero, type BarberoIn, type Servicio } from "@/lib/api";

const VACIO: Omit<BarberoIn, "service_ids"> = { full_name: "", email: "", id_number: "", password: "", specialties: "" };

function GestionBarberos() {
  const avisar = useAviso();
  const [barberos, setBarberos] = useState<Barbero[] | null>(null);
  const [servicios, setServicios] = useState<Servicio[]>([]);
  const [error, setError] = useState("");
  const [datos, setDatos] = useState(VACIO);
  const [elegidos, setElegidos] = useState<number[]>([]);

  const cargar = useCallback(() => {
    Promise.all([api.barberos(), api.servicios()])
      .then(([b, s]) => {
        setBarberos(b);
        setServicios(s);
        setElegidos(s.filter((x) => x.is_active).map((x) => x.id));
      })
      .catch((e: Error) => setError(e.message));
  }, []);
  useEffect(cargar, [cargar]);

  const campo = (k: keyof typeof VACIO, v: string) => setDatos((d) => ({ ...d, [k]: v }));
  const alternarServicio = (id: number) =>
    setElegidos((e) => (e.includes(id) ? e.filter((x) => x !== id) : [...e, id]));

  async function crear(e: FormEvent) {
    e.preventDefault();
    try {
      await api.crearBarbero({ ...datos, service_ids: elegidos });
      avisar("Barbero creado");
      setDatos(VACIO);
      cargar();
    } catch (x) {
      avisar((x as Error).message, "err");
    }
  }

  async function alternar(id: number) {
    try {
      await api.alternarBarbero(id);
      cargar();
    } catch (x) {
      avisar((x as Error).message, "err");
    }
  }

  if (error) return <Vacio>{error}</Vacio>;
  if (!barberos) return <Vacio>Cargando…</Vacio>;

  return (
    <>
      <form className="card form" onSubmit={crear}>
        <label>Nombre<input required value={datos.full_name} onChange={(e) => campo("full_name", e.target.value)} /></label>
        <label>Correo<input type="email" required value={datos.email} onChange={(e) => campo("email", e.target.value)} /></label>
        <label>Identificación<input required value={datos.id_number} onChange={(e) => campo("id_number", e.target.value)} /></label>
        <label>Contraseña
          <input type="password" minLength={8} required value={datos.password} onChange={(e) => campo("password", e.target.value)} />
        </label>
        <label style={{ flexBasis: "100%" }}>Especialidades
          <input placeholder="Ej.: fade, barba clásica" value={datos.specialties} onChange={(e) => campo("specialties", e.target.value)} />
        </label>
        <div className="checks">
          {servicios.filter((s) => s.is_active).map((s) => (
            <label key={s.id}>
              <input type="checkbox" checked={elegidos.includes(s.id)} onChange={() => alternarServicio(s.id)} /> {s.name}
            </label>
          ))}
        </div>
        <button className="btn">Crear barbero</button>
      </form>
      <div className="tw">
        <table>
          <thead><tr><th>Barbero</th><th>Especialidades</th><th>Servicios</th><th>Estado</th><th></th></tr></thead>
          <tbody>
            {barberos.map((b) => {
              const suyos = servicios.filter((s) => b.service_ids.includes(s.id));
              return (
                <tr key={b.id}>
                  <td>{b.full_name}</td>
                  <td>{b.specialties || "—"}</td>
                  <td>{suyos.length ? suyos.map((s) => <span key={s.id} className="tag">{s.name}</span>) : "—"}</td>
                  <td><span className={`pill ${b.is_active ? "st-confirmada" : "st-inasistencia"}`}>{b.is_active ? "Activo" : "Inactivo"}</span></td>
                  <td><button className="ab" onClick={() => alternar(b.id)}>{b.is_active ? "Desactivar" : "Activar"}</button></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default function Barberos() {
  return <Panel roles={["administrador"]}>{() => <GestionBarberos />}</Panel>;
}
