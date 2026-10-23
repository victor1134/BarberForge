import type { Metadata } from "next";
import type { ReactNode } from "react";
import { AvisoProvider } from "@/components/Aviso";
import { ChatFlotante } from "@/components/ChatFlotante";
import { Footer } from "@/components/Footer";
import { Navbar } from "@/components/Navbar";
import { SesionProvider } from "@/components/Sesion";
import "./globals.css";

export const metadata: Metadata = {
  title: "BarberForge AI | Barberías y citas con asistente de IA",
  description: "Agenda tu cita en la barbería y pregúntale al asistente con IA local por servicios, precios y horarios.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="es">
      <body>
        <SesionProvider>
          <AvisoProvider>
            <Navbar />
            {children}
            <Footer />
            <ChatFlotante />
          </AvisoProvider>
        </SesionProvider>
      </body>
    </html>
  );
}
