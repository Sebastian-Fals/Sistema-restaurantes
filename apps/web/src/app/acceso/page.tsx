"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { api, errorMessage } from "@/api/client";
import { CustomerShell, offline, styles as s } from "@/features/customer/shell";
import { safeRedirectPath } from "@/features/auth/safe-redirect";

const COOLDOWN = 60; // segundos; igual a RESEND_COOLDOWN del backend
const codeOf = (error: unknown) => (error as { code?: string } | undefined)?.code;

function Access() {
  const router = useRouter();
  const next = useSearchParams().get("next");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [step, setStep] = useState<"email" | "code">("email");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [verified, setVerified] = useState(false);
  const [wait, setWait] = useState(0);

  useEffect(() => {
    if (wait <= 0) return;
    const t = setTimeout(() => setWait(wait - 1), 1000);
    return () => clearTimeout(t);
  }, [wait]);

  async function requestCode(e?: React.FormEvent) {
    e?.preventDefault();
    if (busy) return;
    setBusy(true);
    setError("");
    setNotice("");
    const { error } = await api.POST("/api/v1/auth/code", { body: { email } }).catch(offline);
    setBusy(false);
    if (error && codeOf(error) !== "too_many_requests") return setError(errorMessage(error, "Revisa el correo e intenta de nuevo."));
    // Con espera activa, el último código enviado sigue sirviendo: pasamos al paso 2 igualmente.
    if (error) setNotice("Ya te enviamos un código hace poco. Usa el del último correo o espera para pedir otro.");
    else if (step === "code") setNotice("Te enviamos un código nuevo.");
    setStep("code");
    setCode("");
    setWait(COOLDOWN);
    setVerified(false);
  }

  async function verify(e: React.FormEvent) {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      if (!verified) {
        const { error, response } = await api.POST("/api/v1/auth/verify", { body: { email, code } }).catch(offline);
        if (error) {
          // A response may be lost after the server has created the session.
          const session = response.status === 0 ? await api.GET("/api/v1/me").catch(offline) : null;
          if (session?.data?.email !== email.trim().toLowerCase()) {
            return setError(
              codeOf(error) === "invalid_code"
                ? "El código no es válido o ya venció. Revisa el último correo o pide uno nuevo."
                : errorMessage(error),
            );
          }
        }
        setVerified(true);
      }
      const { data: me, error: profileError, response } = await api.GET("/api/v1/me").catch(offline);
      if (response.status === 401 || response.status === 403) {
        setVerified(false);
        setStep("email");
        return setError("Tu sesión no está activa. Solicita un código nuevo para entrar.");
      }
      if (!me) return setError(`No pudimos abrir tu cuenta. ${errorMessage(profileError)} Pulsa Continuar para reintentar sin pedir otro código.`);
      const staffOf = me.memberships[0]?.business_slug;
      const destination = safeRedirectPath(next, window.location.origin);
      router.push(destination ?? (staffOf ? `/app/${staffOf}` : "/mis-tarjetas"));
    } finally {
      setBusy(false);
    }
  }

  const mmss = `${String(Math.floor(wait / 60)).padStart(2, "0")}:${String(wait % 60).padStart(2, "0")}`;
  const alert = error && <p role="alert" className="status error">{error}</p>;

  if (step === "email")
    return (
      <CustomerShell title="Guarda tus beneficios" subtitle="Una cuenta para todas tus tarjetas." nav={false}>
        <form onSubmit={requestCode}>
          <label htmlFor="email">Correo electrónico</label>
          <input id="email" type="email" autoComplete="email" disabled={busy} required autoFocus value={email} onChange={(e) => setEmail(e.target.value)} />
          <p className="muted">
            Te enviaremos un código para entrar. No necesitas contraseña: si es tu primera vez creamos tu cuenta, y si ya la tienes,
            entras con el mismo paso.
          </p>
          {alert}
          <div className={s.actions}>
            <button disabled={busy}>{busy ? "Enviando…" : "Enviar código"}</button>
          </div>
        </form>
      </CustomerShell>
    );

  return (
    <CustomerShell title="Revisa tu correo" subtitle={<>Enviamos un código a <strong>{email}</strong></>} nav={false}>
      <form onSubmit={verify} className={s.field}>
        <label htmlFor="code">Código de acceso</label>
        <input
          id="code" className={s.codeInput} inputMode="numeric" autoComplete="one-time-code" pattern="\d{6}" maxLength={6} required autoFocus
          disabled={verified || busy}
          aria-invalid={!!error} aria-describedby="code-help" value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
        />
        <p id="code-help" className="muted">Son 6 dígitos. El código vence en 10 minutos.</p>
        {alert}
        {notice && <p role="status" className="status">{notice}</p>}
        <div className={s.actions}>
          <button disabled={busy || (!verified && code.length !== 6)}>{busy ? "Verificando…" : verified ? "Continuar" : "Verificar y entrar"}</button>
          <button type="button" className="secondary" disabled={busy} onClick={() => { setStep("email"); setCode(""); setError(""); setNotice(""); setVerified(false); }}>
            Cambiar correo
          </button>
        </div>
        {!verified && (wait > 0 ? (
          <p className="muted" aria-live="off">Reenviar código disponible en {mmss}</p>
        ) : (
          <button type="button" className="secondary" disabled={busy} onClick={() => requestCode()}>Reenviar código</button>
        ))}
      </form>
    </CustomerShell>
  );
}

export default function AccessPage() {
  return (
    <Suspense>
      <Access />
    </Suspense>
  );
}
