import Link from "next/link";

export default function NoEncontrada() {
  return (
    <main className="auth">
      <div className="card" style={{ textAlign: "center" }}>
        <h2>Página no encontrada</h2>
        <p className="mute" style={{ margin: "10px 0 18px" }}>La dirección no existe o cambió.</p>
        <Link className="btn" href="/">Volver al inicio</Link>
      </div>
    </main>
  );
}
