import Link from "next/link";

export default function Home() {
  return (
    <>
      <h1>Mesa</h1>
      <p>Programa digital de sellos para cafeterías. Piloto en desarrollo: no procesa pagos ni reemplaza tu caja.</p>
      <p>
        <Link href="/acceso">Ingresar</Link> · <Link href="/mis-tarjetas">Mis tarjetas</Link>
      </p>
    </>
  );
}
