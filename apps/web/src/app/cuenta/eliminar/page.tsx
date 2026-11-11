"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api, errorMessage } from "@/api/client";
import { CustomerShell, offline, styles as s } from "@/features/customer/shell";

const WORD = "ELIMINAR";

export default function DeleteAccount() {
  const router = useRouter();
  const [typed, setTyped] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function remove(e: React.FormEvent) {
    e.preventDefault();
    if (typed.trim().toUpperCase() !== WORD) return setError(`Escribe ${WORD} para confirmar.`);
    setBusy(true);
    setError("");
    const { error, response } = await api.DELETE("/api/v1/me").catch(offline);
    if (response.status === 401 || response.status === 403) return router.replace("/acceso?next=/cuenta/eliminar");
    if (error) {
      setBusy(false);
      return setError(errorMessage(error));
    }
    router.replace("/");
  }

  return (
    <CustomerShell title="Eliminar mi cuenta" subtitle="Revisa lo que pasará antes de continuar.">
      <div className={s.warning}>
        <p style={{ margin: 0 }}>
          Perderás el acceso a tus tarjetas, sellos y recompensas, y dejarás de recibir comunicaciones. Esto no se puede deshacer.
        </p>
        <p style={{ marginBottom: 0 }}>
          Los negocios conservan el registro de las compras que hiciste (fecha, valor y referencia) sin tu correo ni otros datos personales.
        </p>
      </div>
      <form onSubmit={remove}>
        <label htmlFor="confirm">Escribe {WORD} para confirmar</label>
        <input id="confirm" autoComplete="off" value={typed} aria-invalid={!!error} onChange={(e) => setTyped(e.target.value)} />
        {error && <p role="alert" className="status error">{error}</p>}
        <div className={s.actions}>
          <button className="danger" disabled={busy}>{busy ? "Eliminando…" : "Eliminar definitivamente"}</button>
          <Link href="/cuenta" className={`btn ${s.btnLink} ${s.secondaryLink}`}>Conservar mi cuenta</Link>
        </div>
      </form>
    </CustomerShell>
  );
}
