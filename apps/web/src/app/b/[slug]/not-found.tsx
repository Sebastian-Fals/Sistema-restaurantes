import Link from "next/link";
import { Header } from "./header";
import s from "./page.module.css";

export default function BusinessNotFound() {
  return (
    <div className={`wide ${s.page}`}>
      <Header />
      <h1 className={s.name}>No encontramos este negocio</h1>
      <p className={s.lead}>Revisa el enlace o el código QR. Puede que la página haya cambiado o ya no esté publicada.</p>
      <p className={s.section}><Link href="/">Ir al inicio de Mesa</Link></p>
    </div>
  );
}
