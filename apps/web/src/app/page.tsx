import Link from "next/link";

export default function Home() {
  return (
    <>
      <p style={{ fontFamily: "var(--font-serif), serif", fontSize: 25, color: "var(--forest)", margin: "0 0 32px" }}>mesa</p>
      <h1>Tu café también te recompensa.</h1>
      <p className="muted">
        Mesa es un programa digital de sellos para cafeterías. Cada compra válida suma un sello a tu tarjeta; al completarla, el
        negocio te da una recompensa. No hay apps que instalar: solo tu correo.
      </p>
      <p>
        <Link className="btn" href="/b/cafe-olivo" style={{ display: "inline-flex", alignItems: "center", textDecoration: "none" }}>
          Ver el negocio demo: Café Olivo
        </Link>
      </p>
      <p>
        <Link href="/mis-tarjetas">Mis tarjetas</Link> · <Link href="/acceso">Ingresar</Link>
      </p>
      <p className="muted" style={{ fontSize: 13, marginTop: 48 }}>
        Piloto en desarrollo: no procesa pagos ni reemplaza tu caja.
      </p>
    </>
  );
}
