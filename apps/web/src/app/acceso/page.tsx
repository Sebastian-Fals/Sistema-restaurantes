"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { api, errorMessage } from "@/api/client";

function Access() {
  const router = useRouter();
  const next = useSearchParams().get("next");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function requestCode(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    const { error } = await api.POST("/api/v1/auth/code", { body: { email } });
    setBusy(false);
    if (error) return setError(errorMessage(error, "Revisa el correo e intenta de nuevo."));
    setSent(true);
  }

  async function verify(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    const { error } = await api.POST("/api/v1/auth/verify", { body: { email, code } });
    if (error) {
      setBusy(false);
      return setError(errorMessage(error));
    }
    const { data: me } = await api.GET("/api/v1/me");
    const staffOf = me?.memberships[0]?.business_slug;
    // Solo rutas internas como destino, para evitar redirecciones abiertas.
    router.push(next?.startsWith("/") && !next.startsWith("//") ? next : staffOf ? `/app/${staffOf}` : "/mis-tarjetas");
  }

  return (
    <>
      <h1>Ingresar</h1>
      <p className="muted">Te enviamos un código de un solo uso por correo. Si es tu primera vez, se crea tu cuenta.</p>
      <form className="card" onSubmit={sent ? verify : requestCode}>
        <label htmlFor="email">Correo electrónico</label>
        <input id="email" type="email" autoComplete="email" required value={email} readOnly={sent} onChange={(e) => setEmail(e.target.value)} />
        {sent && (
          <>
            <label htmlFor="code">Código de 6 dígitos</label>
            <input id="code" inputMode="numeric" autoComplete="one-time-code" required autoFocus value={code} onChange={(e) => setCode(e.target.value)} />
          </>
        )}
        <button disabled={busy}>{busy ? "Procesando…" : sent ? "Verificar" : "Enviar código"}</button>
        {sent && (
          <button type="button" className="secondary" style={{ marginLeft: 8 }} onClick={() => { setSent(false); setCode(""); setError(""); }}>
            Cambiar correo
          </button>
        )}
        {error && <p role="alert" className="status error">{error}</p>}
      </form>
    </>
  );
}

export default function AccessPage() {
  return (
    <Suspense>
      <Access />
    </Suspense>
  );
}
