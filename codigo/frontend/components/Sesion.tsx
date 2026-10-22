"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { api, ApiError, type Sesion as SesionApi, type Usuario } from "@/lib/api";
import { borrarToken, guardarToken, leerToken } from "@/lib/auth";

interface ContextoSesion {
  usuario: Usuario | null;
  cargando: boolean;
  iniciar: (sesion: SesionApi) => void;
  actualizar: (usuario: Usuario) => void;
  salir: () => void;
}

const Contexto = createContext<ContextoSesion | null>(null);

export function SesionProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [cargando, setCargando] = useState(true);

  // Al abrir la página se recupera la sesión guardada.
  useEffect(() => {
    if (!leerToken()) {
      setCargando(false);
      return;
    }
    api.yo()
      .then(setUsuario)
      .catch((e) => {
        if (e instanceof ApiError && (e.status === 401 || e.status === 403)) borrarToken();
      })
      .finally(() => setCargando(false));
  }, []);

  const iniciar = useCallback((sesion: SesionApi) => {
    guardarToken(sesion.token);
    setUsuario(sesion.user);
  }, []);

  const salir = useCallback(() => {
    borrarToken();
    setUsuario(null);
  }, []);

  return (
    <Contexto.Provider value={{ usuario, cargando, iniciar, actualizar: setUsuario, salir }}>
      {children}
    </Contexto.Provider>
  );
}

export function useSesion(): ContextoSesion {
  const ctx = useContext(Contexto);
  if (!ctx) throw new Error("useSesion debe usarse dentro de SesionProvider");
  return ctx;
}
