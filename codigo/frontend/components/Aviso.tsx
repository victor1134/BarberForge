"use client";

import { createContext, useCallback, useContext, useState, type ReactNode } from "react";

type TipoAviso = "ok" | "err" | "warn";
type Avisar = (mensaje: string, tipo?: TipoAviso) => void;

interface AvisoItem {
  id: number;
  mensaje: string;
  tipo: TipoAviso;
}

const Contexto = createContext<Avisar>(() => {});
let siguienteId = 0;

/** Avisos flotantes (toasts) que desaparecen solos. */
export function AvisoProvider({ children }: { children: ReactNode }) {
  const [avisos, setAvisos] = useState<AvisoItem[]>([]);

  const avisar = useCallback<Avisar>((mensaje, tipo = "ok") => {
    const id = ++siguienteId;
    setAvisos((a) => [...a, { id, mensaje, tipo }]);
    setTimeout(() => setAvisos((a) => a.filter((x) => x.id !== id)), 4500);
  }, []);

  return (
    <Contexto.Provider value={avisar}>
      {children}
      <div className="toasts" aria-live="polite">
        {avisos.map((a) => (
          <div key={a.id} className={`toast ${a.tipo === "ok" ? "" : a.tipo}`}>{a.mensaje}</div>
        ))}
      </div>
    </Contexto.Provider>
  );
}

export const useAviso = () => useContext(Contexto);

/** Mensaje en línea para estados vacíos, de carga o de error. */
export function Vacio({ children, sinBorde }: { children: ReactNode; sinBorde?: boolean }) {
  return <div className="empty" style={sinBorde ? { border: 0 } : undefined}>{children}</div>;
}
