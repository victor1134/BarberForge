import type { NextConfig } from "next";

// En producción se exporta como sitio estático (carpeta out/) que sirve nginx, el cual
// también reenvía /api al backend. En desarrollo, Next reenvía /api a la API local.
const desarrollo = process.env.NODE_ENV !== "production";
const API_URL = process.env.API_URL ?? "http://localhost:8000";

const config: NextConfig = desarrollo
  ? { async rewrites() { return [{ source: "/api/:ruta*", destination: `${API_URL}/api/:ruta*` }]; } }
  : { output: "export", images: { unoptimized: true } };

export default config;
