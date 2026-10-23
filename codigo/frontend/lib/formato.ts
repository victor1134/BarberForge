// Formatos y etiquetas en español para la interfaz.
import type { EstadoCita, Franja, Rol, TipoServicio } from "./api";

export const cop = (n: number) => "$" + Number(n).toLocaleString("es-CO");

export const fechaLarga = (d: string) =>
  new Date(d + "T12:00:00").toLocaleDateString("es-CO", { weekday: "long", day: "numeric", month: "long" });

export const iniciales = (nombre: string) =>
  nombre.split(" ").filter(Boolean).slice(0, 2).map((x) => x[0]).join("").toUpperCase();

export const primerNombre = (nombre: string) => nombre.split(" ")[0];

// Fecha local AAAA-MM-DD (toISOString usaría UTC y en la noche de Colombia daría el día siguiente).
export const hoyISO = () => {
  const d = new Date();
  const dos = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${dos(d.getMonth() + 1)}-${dos(d.getDate())}`;
};

export const textoAlternativas = (alts: Franja[]) =>
  alts.map((a) => `${a.date.slice(5)} ${a.time}`).join(", ");

export const ESTADOS: Record<EstadoCita, string> = {
  pendiente: "Pendiente",
  confirmada: "Confirmada",
  completada: "Completada",
  inasistencia: "Inasistencia",
  cancelada_cliente: "Cancelada por el cliente",
  cancelada_sin_confirmar: "Cancelada: sin confirmar",
  cancelada_admin: "Cancelada por administración",
};

export const TIPOS: TipoServicio[] = ["corte", "barba", "combo", "tratamiento"];
export const NOMBRE_TIPO: Record<TipoServicio, string> = {
  corte: "Corte", barba: "Barba", combo: "Combo", tratamiento: "Tratamiento",
};
export const ICONO_TIPO: Record<TipoServicio, string> = {
  corte: "✂", barba: "🧔", combo: "💈", tratamiento: "✨",
};

export const ROLES: Record<Rol, string> = {
  cliente: "Cliente", barbero: "Barbero", administrador: "Administrador",
};

export const COLORES_AVATAR = [
  "linear-gradient(135deg,#22407a,#2f6fed)",
  "linear-gradient(135deg,#e63946,#ff6b4a)",
  "linear-gradient(135deg,#fca311,#e08a00)",
  "linear-gradient(135deg,#06a77d,#3ddc97)",
];

// Página de inicio del panel según el rol.
export const inicioPanel = (rol: Rol) => (rol === "cliente" ? "/agendar" : "/citas");
