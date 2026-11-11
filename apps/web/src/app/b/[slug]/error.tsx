"use client";

import { Header } from "./header";
import s from "./page.module.css";

export default function BusinessError() {
  return (
    <div className={`wide ${s.page}`}>
      <Header />
      <h1 className={s.name}>No pudimos cargar esta página</h1>
      <p className={s.lead}>Puede ser un problema temporal de conexión. Intenta de nuevo en unos segundos.</p>
      <button onClick={() => location.reload()}>Reintentar</button>
    </div>
  );
}
