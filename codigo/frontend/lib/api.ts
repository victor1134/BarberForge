// Tipos de la API y funciones fetch. Todas las llamadas al backend pasan por aquí.
import { leerToken } from "./auth";

// ---------- tipos ----------

export type Rol = "cliente" | "barbero" | "administrador";
export type TipoServicio = "corte" | "barba" | "combo" | "tratamiento";
export type EstadoCita =
  | "pendiente" | "confirmada" | "completada" | "inasistencia"
  | "cancelada_cliente" | "cancelada_admin" | "cancelada_sin_confirmar";

export interface Usuario {
  id: number;
  email: string;
  full_name: string;
  role: Rol;
  style_pref: string;
}

export interface Sesion {
  token: string;
  user: Usuario;
}

export interface Servicio {
  id: number;
  name: string;
  description: string | null;
  price_cop: number;
  duration_minutes: number;
  service_type: TipoServicio;
  is_active: boolean;
}

export interface ServicioIn {
  name: string;
  description: string;
  price_cop: number;
  duration_minutes: number;
  service_type: TipoServicio;
}

export interface Barbero {
  id: number;
  full_name: string;
  is_active: boolean;
  specialties: string;
  service_ids: number[];
}

export interface BarberoIn {
  email: string;
  full_name: string;
  id_number: string;
  password: string;
  specialties: string;
  service_ids: number[];
}

interface BarberiaBase {
  id: number;
  nombre: string;
  direccion: string;
  horario: string;
  descripcion: string;
  buzon_url: string;
}

export interface BarberiaResumen extends BarberiaBase {
  servicios: number;
  barberos: number;
}

export interface BarberiaDetalle extends BarberiaBase {
  servicios: Servicio[];
  barberos: Barbero[];
}

export interface Franja {
  date: string; // AAAA-MM-DD
  time: string; // HH:MM
}

export interface Cita {
  id: number;
  date: string;
  time: string;
  status: EstadoCita;
  service: string;
  barber: string;
  client: string;
}

export interface CitaIn {
  barber_id: number;
  service_id: number;
  date: string;
  time: string;
}

export interface RegistroIn {
  email: string;
  full_name: string;
  id_type: string;
  id_number: string;
  password: string;
  accept_policy: boolean;
}

export interface CuentaIn {
  full_name?: string;
  email?: string;
  style_pref?: string;
  current_password?: string;
  new_password?: string;
}

export interface GenerarDisponibilidadIn {
  barber_id: number;
  date_from: string;
  date_to: string;
  start: string;
  end: string;
  minutes: number;
}

export interface OpcionChat {
  label: string;
  send?: string;
  action?: "registro" | "login";
  book?: CitaIn;
}

export interface RespuestaChat {
  reply: string;
  sources: string[];
  options?: OpcionChat[];
}

// ---------- cliente HTTP ----------

export class ApiError extends Error {
  constructor(mensaje: string, public status: number, public alternativas: Franja[] = []) {
    super(mensaje);
  }
}

type Metodo = "GET" | "POST" | "PUT" | "PATCH";

async function pedir<T>(ruta: string, metodo: Metodo = "GET", cuerpo?: unknown): Promise<T> {
  const token = leerToken();
  let r: Response;
  try {
    r = await fetch("/api" + ruta, {
      method: metodo,
      headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo),
    });
  } catch {
    throw new ApiError("No se pudo conectar con el servidor. Revisa tu conexión.", 0);
  }
  let datos: unknown = {};
  try {
    const texto = await r.text();
    datos = texto ? JSON.parse(texto) : {};
  } catch {
    /* respuesta sin JSON */
  }
  if (!r.ok) {
    const detalle = (datos as { detail?: unknown }).detail;
    let mensaje: string | undefined;
    let alternativas: Franja[] = [];
    if (typeof detalle === "string") mensaje = detalle;
    else if (Array.isArray(detalle)) mensaje = "Revisa los datos del formulario.";
    else if (detalle && typeof detalle === "object") {
      const d = detalle as { message?: string; alternatives?: Franja[] };
      mensaje = d.message;
      alternativas = d.alternatives ?? [];
    }
    mensaje ??= r.status >= 500
      ? `El servidor no respondió bien (código ${r.status}). Abre /api/health para ver el estado.`
      : `Error ${r.status}`;
    throw new ApiError(mensaje, r.status, alternativas);
  }
  return datos as T;
}

type Ok = { ok: boolean };

export const api = {
  // sesión y cuenta
  setup: () => pedir<{ hay_admin: boolean }>("/setup"),
  registrar: (datos: RegistroIn) => pedir<Sesion>("/register", "POST", datos),
  login: (email: string, password: string) => pedir<Sesion>("/login", "POST", { email, password }),
  yo: () => pedir<Usuario>("/me"),
  actualizarCuenta: (datos: CuentaIn) => pedir<{ user: Usuario }>("/me", "PATCH", datos),

  // barberías
  barberias: () => pedir<BarberiaResumen[]>("/barberias"),
  barberia: (id: number) => pedir<BarberiaDetalle>(`/barberias/${id}`),

  // servicios
  servicios: () => pedir<Servicio[]>("/services"),
  crearServicio: (datos: ServicioIn) => pedir<Ok>("/services", "POST", datos),
  editarServicio: (id: number, datos: ServicioIn) => pedir<Ok>(`/services/${id}`, "PUT", datos),
  alternarServicio: (id: number) => pedir<Ok>(`/services/${id}/toggle`, "POST"),

  // barberos
  barberos: () => pedir<Barbero[]>("/barbers"),
  crearBarbero: (datos: BarberoIn) => pedir<Ok>("/barbers", "POST", datos),
  alternarBarbero: (id: number) => pedir<Ok>(`/barbers/${id}/toggle`, "POST"),

  // disponibilidad
  franjas: (barberoId: number) => pedir<Franja[]>(`/availability?barber_id=${barberoId}`),
  generarDisponibilidad: (datos: GenerarDisponibilidadIn) => pedir<Ok>("/availability", "POST", datos),

  // citas
  citas: () => pedir<Cita[]>("/appointments"),
  agendar: (datos: CitaIn) => pedir<{ id: number }>("/appointments", "POST", datos),
  cancelarCita: (id: number) => pedir<Ok>(`/appointments/${id}/cancel`, "POST"),
  cerrarCita: (id: number, status: "completada" | "inasistencia") =>
    pedir<Ok>(`/appointments/${id}/status`, "PATCH", { status }),
  recordarCita: (id: number) => pedir<Ok>(`/appointments/${id}/remind`, "POST"),

  // asistente
  chat: (message: string) => pedir<RespuestaChat>("/chat", "POST", { message }),
  reindexar: () => pedir<{ embeddings_ok: boolean }>("/admin/reindex", "POST"),
};
