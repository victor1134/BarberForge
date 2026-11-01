import type { Servicio } from "@/lib/api";
import { cop, ICONO_TIPO } from "@/lib/formato";

export function ServicioCard({ servicio, onAgendar }: { servicio: Servicio; onAgendar: () => void }) {
  return (
    <div className={`sc t-${servicio.service_type}`}>
      <div className="ic">{ICONO_TIPO[servicio.service_type] ?? "✂"}</div>
      <h3>{servicio.name}</h3>
      <p>{servicio.description}</p>
      <div className="pr">
        <b>{cop(servicio.price_cop)}</b>
        <small>{servicio.duration_minutes} min</small>
      </div>
      <button className="btn sm" onClick={onAgendar}>Agendar este servicio</button>
    </div>
  );
}
