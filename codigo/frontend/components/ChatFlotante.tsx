"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { ChatAsistente } from "./ChatAsistente";

export const EVENTO_ABRIR_CHAT = "bf:abrir-chat";

/** Abre el asistente flotante desde cualquier botón de la página. */
export const abrirChat = () => window.dispatchEvent(new Event(EVENTO_ABRIR_CHAT));

/** Botón flotante con el asistente. En el inicio no aparece porque el chat va incrustado. */
export function ChatFlotante() {
  const ruta = usePathname();
  const [abierto, setAbierto] = useState(false);

  useEffect(() => {
    const abrir = () => setAbierto(true);
    window.addEventListener(EVENTO_ABRIR_CHAT, abrir);
    return () => window.removeEventListener(EVENTO_ABRIR_CHAT, abrir);
  }, []);

  if (ruta === "/") return null;
  return (
    <>
      {/* Siempre montado (oculto con CSS) para no perder la conversación al cerrarlo. */}
      <ChatAsistente className={`floating ${abierto ? "on" : ""}`} />
      <button className="fab" onClick={() => setAbierto((a) => !a)} title="Asistente" aria-label="Abrir asistente">
        💬
      </button>
    </>
  );
}
