import type { Barbero, Servicio } from "@/lib/api";
import { COLORES_AVATAR, iniciales, primerNombre } from "@/lib/formato";

interface Props {
  barbero: Barbero;
  servicios: Servicio[];
  indice: number;
  onAgendar: () => void;
}

export function BarberoCard({ barbero, servicios, indice, onAgendar }: Props) {
  return (
    <div className="bc">
      <div className="av2" style={{ background: COLORES_AVATAR[indice % COLORES_AVATAR.length] }}>
        {iniciales(barbero.full_name)}
      </div>
      <h3>{barbero.full_name}</h3>
      <div className="esp">{barbero.specialties || "Barbero profesional"}</div>
      <div className="tags">
        {servicios.filter((s) => barbero.service_ids.includes(s.id)).map((s) => (
          <span key={s.id} className="tag">{s.name}</span>
        ))}
      </div>
      <button className="btn sm" onClick={onAgendar}>Agendar con {primerNombre(barbero.full_name)}</button>
    </div>
  );
}
