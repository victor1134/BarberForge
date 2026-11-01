"use client";

import Link from "next/link";
import { ChatAsistente } from "@/components/ChatAsistente";
import { useSesion } from "@/components/Sesion";

export default function Inicio() {
  const { usuario } = useSesion();

  return (
    <main>
      <div className="hero">
        <div>
          <span className="badge">💈 Agenda con IA local para barberías</span>
          <h1>Encuentra tu barbería y <em>agenda sin llamar.</em></h1>
          <p className="lead">
            Pregúntale al asistente por servicios, precios y horarios, o elige una barbería, escoge a tu barbero y
            reserva tu turno en un minuto.
          </p>
          <div className="row">
            <Link className="btn gold" href="/barberia">Ver la barbería</Link>
            {!usuario && <Link className="btn ghost" href="/registro">Crear mi cuenta</Link>}
          </div>
          <div className="facts">
            <div><b>24/7</b>asistente con IA</div>
            <div><b>40 min</b>recordatorio por correo</div>
            <div><b>0 cruces</b>de horario</div>
          </div>
        </div>
        <ChatAsistente />
      </div>
      <div className="pole" />

      <section className="sec alt" id="proceso">
        <div className="st">
          <h2>¿Cómo funciona?</h2>
          <p>Tres pasos, por formulario o conversando con el asistente.</p>
        </div>
        <div className="steps">
          <div className="step"><i>1</i><h3>Elige</h3><p>Barbería, servicio y barbero con disponibilidad real, sin citas dobles.</p></div>
          <div className="step"><i>2</i><h3>Agenda</h3><p>Por formulario o por chat. La franja se bloquea al instante.</p></div>
          <div className="step"><i>3</i><h3>Confirma</h3><p>Recibes un correo 40 minutos antes con un botón de confirmación.</p></div>
        </div>
      </section>
    </main>
  );
}
