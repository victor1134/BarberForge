"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError, type OpcionChat, type Usuario } from "@/lib/api";
import { primerNombre, textoAlternativas } from "@/lib/formato";
import { useAviso } from "./Aviso";
import { useSesion } from "./Sesion";

interface Mensaje {
  id: number;
  texto: string;
  quien: "bot" | "me";
  fuentes?: string[];
  opciones?: OpcionChat[];
  escribiendo?: boolean;
}

const SUGERENCIAS = ["¿Qué servicios ofrecen?", "¿Cuánto cuesta un corte?", "¿Cuál es el horario?", "Quiero agendar"];
let siguienteId = 0;

function saludo(usuario: Usuario | null): Mensaje {
  const texto = usuario
    ? `¡Hola ${primerNombre(usuario.full_name)}! Soy el asistente de la barbería. Pregúntame por servicios, precios y horarios${usuario.role === "cliente" ? ", o escribe «agendar» para reservar" : ""}.`
    : "¡Hola! Soy el asistente de la barbería. Pregúntame por servicios, precios y horarios. Para agendar, inicia sesión.";
  return { id: ++siguienteId, texto, quien: "bot" };
}

export function ChatAsistente({ className = "" }: { className?: string }) {
  const { usuario } = useSesion();
  const avisar = useAviso();
  const router = useRouter();
  const [mensajes, setMensajes] = useState<Mensaje[]>(() => [saludo(null)]);
  const [mostrarSugerencias, setMostrarSugerencias] = useState(true);
  const [texto, setTexto] = useState("");
  const lista = useRef<HTMLDivElement>(null);

  // Al iniciar o cerrar sesión la conversación vuelve a empezar.
  useEffect(() => {
    setMensajes([saludo(usuario)]);
    setMostrarSugerencias(true);
  }, [usuario?.id]); // solo cuando cambia la persona, no en cada actualización de la cuenta

  useEffect(() => {
    lista.current?.scrollTo({ top: lista.current.scrollHeight });
  }, [mensajes]);

  const agregar = (m: Omit<Mensaje, "id">) => setMensajes((ms) => [...ms, { ...m, id: ++siguienteId }]);

  async function preguntar(pregunta: string) {
    setMostrarSugerencias(false);
    const idEscribiendo = ++siguienteId;
    setMensajes((ms) => [...ms, { id: ++siguienteId, texto: pregunta, quien: "me" },
      { id: idEscribiendo, texto: "Pensando", quien: "bot", escribiendo: true }]);
    let respuesta: Omit<Mensaje, "id">;
    try {
      const r = await api.chat(pregunta);
      respuesta = { texto: r.reply, quien: "bot", fuentes: r.sources, opciones: r.options };
    } catch (e) {
      respuesta = { texto: "No pude responder: " + (e as Error).message, quien: "bot" };
    }
    setMensajes((ms) => [...ms.filter((m) => m.id !== idEscribiendo), { ...respuesta, id: ++siguienteId }]);
  }

  async function elegir(opcion: OpcionChat) {
    if (opcion.action) return router.push(`/${opcion.action}`);
    if (opcion.send) return preguntar(opcion.send);
    if (!opcion.book) return;
    try {
      await api.agendar(opcion.book);
      agregar({ quien: "bot", texto: "¡Listo! Tu cita quedó creada y pendiente de confirmación. Te enviaremos un recordatorio por correo antes de la hora." });
      avisar("Cita creada");
    } catch (e) {
      const alts = e instanceof ApiError && e.alternativas.length ? "\nOtros horarios: " + textoAlternativas(e.alternativas) : "";
      agregar({ quien: "bot", texto: (e as Error).message + alts });
    }
  }

  function enviar(e: FormEvent) {
    e.preventDefault();
    const t = texto.trim();
    if (!t) return;
    setTexto("");
    preguntar(t);
  }

  const sugerencias = usuario && usuario.role !== "cliente" ? SUGERENCIAS.slice(0, 3) : SUGERENCIAS;

  return (
    <div className={`chat ${className}`}>
      <div className="ch">
        <div className="av">✂</div>
        <div><b>Asistente BarberForge</b><small>IA local · en línea</small></div>
      </div>
      <div className="msgs" ref={lista}>
        {mensajes.map((m) => (
          <div key={m.id} className={`m ${m.quien} ${m.escribiendo ? "typing" : ""}`}>
            {m.texto}
            {m.fuentes && m.fuentes.length > 0 && <small>Fuentes: {m.fuentes.join(", ")}</small>}
            {m.opciones && m.opciones.length > 0 && (
              <div className="opts">
                {m.opciones.map((o, i) => <button key={i} onClick={() => elegir(o)}>{o.label}</button>)}
              </div>
            )}
          </div>
        ))}
      </div>
      {mostrarSugerencias && (
        <div className="chips-chat">
          {sugerencias.map((s) => <button key={s} type="button" onClick={() => preguntar(s)}>{s}</button>)}
        </div>
      )}
      <form className="cf" onSubmit={enviar}>
        <input value={texto} onChange={(e) => setTexto(e.target.value)} placeholder="Pregunta o escribe «agendar»…"
          autoComplete="off" maxLength={500} aria-label="Mensaje para el asistente" />
        <button className="btn sm">Enviar</button>
      </form>
    </div>
  );
}
