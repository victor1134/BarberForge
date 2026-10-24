"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAviso, Vacio } from "@/components/Aviso";
import { Panel } from "@/components/Panel";
import { api, ApiError, type Barbero, type Franja, type Servicio } from "@/lib/api";
import { cop, fechaLarga, ICONO_TIPO, textoAlternativas } from "@/lib/formato";

/** Agendar en tres pasos: servicio → barbero → horario. */
function Asistente() {
  const params = useSearchParams();
  const router = useRouter();
  const avisar = useAviso();
  const [servicios, setServicios] = useState<Servicio[] | null>(null);
  const [barberos, setBarberos] = useState<Barbero[]>([]);
  const [error, setError] = useState("");
  const [servicioId, setServicioId] = useState<number | null>(Number(params.get("servicio")) || null);
  const [barberoId, setBarberoId] = useState<number | null>(Number(params.get("barbero")) || null);
  const [franjas, setFranjas] = useState<Franja[] | null>(null);
  const [errorFranjas, setErrorFranjas] = useState("");
  const [franja, setFranja] = useState<Franja | null>(null);
  const [reservando, setReservando] = useState(false);
  const [recarga, setRecarga] = useState(0);

  useEffect(() => {
    Promise.all([api.servicios(), api.barberos()])
      .then(([s, b]) => { setServicios(s); setBarberos(b); })
      .catch((e: Error) => setError(e.message));
  }, []);

  const servicio = servicios?.find((s) => s.id === servicioId) ?? null;
  const disponibles = useMemo(
    () => (servicio ? barberos.filter((b) => b.service_ids.includes(servicio.id)) : []), [servicio, barberos]);
  const barbero = disponibles.find((b) => b.id === barberoId) ?? null;

  const idBarbero = barbero?.id;
  useEffect(() => {
    setFranja(null);
    if (!idBarbero) return;
    setFranjas(null);
    setErrorFranjas("");
    api.franjas(idBarbero).then(setFranjas).catch((e: Error) => setErrorFranjas(e.message));
  }, [idBarbero, recarga]);

  const porDia = useMemo(() => {
    const dias: Record<string, string[]> = {};
    for (const f of franjas ?? []) (dias[f.date] ??= []).push(f.time);
    return dias;
  }, [franjas]);

  async function reservar() {
    if (!servicio || !barbero || !franja) return;
    setReservando(true);
    try {
      await api.agendar({ barber_id: barbero.id, service_id: servicio.id, date: franja.date, time: franja.time });
      avisar("¡Cita creada! Quedó pendiente de confirmación; recibirás un recordatorio por correo.");
      router.push("/citas");
    } catch (e) {
      const alts = e instanceof ApiError && e.alternativas.length ? " Alternativas: " + textoAlternativas(e.alternativas) : "";
      avisar((e as Error).message + alts, "err");
      setReservando(false);
      setRecarga((n) => n + 1);
    }
  }

  if (error) return <Vacio>{error}</Vacio>;
  if (!servicios) return <Vacio>Cargando…</Vacio>;

  return (
    <>
      <div className="stepn"><i>1</i><b>Elige el servicio</b></div>
      <div className="grid">
        {servicios.map((s) => (
          <button key={s.id} className={`pick ${s.id === servicioId ? "on" : ""}`} onClick={() => setServicioId(s.id)}>
            <b>{ICONO_TIPO[s.service_type] ?? "✂"} {s.name}</b>
            <span>{cop(s.price_cop)} · {s.duration_minutes} min</span>
          </button>
        ))}
      </div>

      {servicio && (
        <>
          <div className="stepn"><i>2</i><b>Elige el barbero</b></div>
          <div className="grid">
            {disponibles.length ? disponibles.map((b) => (
              <button key={b.id} className={`pick ${b.id === barberoId ? "on" : ""}`} onClick={() => setBarberoId(b.id)}>
                <b>👤 {b.full_name}</b>
                <span>{b.specialties || "Barbero profesional"}</span>
              </button>
            )) : <Vacio>Ningún barbero ofrece este servicio por ahora.</Vacio>}
          </div>
        </>
      )}

      {barbero && (
        <>
          <div className="stepn"><i>3</i><b>Elige el horario</b></div>
          {errorFranjas ? <Vacio>{errorFranjas}</Vacio> : franjas === null ? <Vacio>Buscando horarios…</Vacio> :
            franjas.length === 0 ? <Vacio>Este barbero no tiene horarios libres. Prueba con otro.</Vacio> : (
              <div className="days">
                {Object.entries(porDia).map(([dia, horas]) => (
                  <div key={dia} className="day">
                    <h4>{fechaLarga(dia)}</h4>
                    <div className="slots">
                      {horas.map((h) => (
                        <button key={h} className={`slot ${franja?.date === dia && franja.time === h ? "on" : ""}`}
                          onClick={() => setFranja({ date: dia, time: h })}>{h}</button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
        </>
      )}

      {servicio && barbero && franja && (
        <div className="sumbar">
          <div>
            <b>{servicio.name}</b> con <b>{barbero.full_name}</b><br />
            <small>{fechaLarga(franja.date)} · {franja.time} · {cop(servicio.price_cop)}</small>
          </div>
          <button className="btn gold" disabled={reservando} onClick={reservar}>Confirmar cita</button>
        </div>
      )}
    </>
  );
}

export default function Agendar() {
  return (
    <Panel roles={["cliente"]}>
      {() => <Suspense fallback={<Vacio>Cargando…</Vacio>}><Asistente /></Suspense>}
    </Panel>
  );
}
