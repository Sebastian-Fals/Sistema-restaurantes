"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, errorMessage } from "@/api/client";
import { CustomerShell, LoadError, Loading, offline, styles as s, useCards } from "@/features/customer/shell";

export default function Account() {
  const router = useRouter();
  const { cards, setCards, failed } = useCards();
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<{ text: string; error?: boolean } | null>(null);
  const [busy, setBusy] = useState("");

  useEffect(() => {
    api.GET("/api/v1/me").then(({ data }) => data && setEmail(data.email));
  }, []);

  async function consent(slug: string, name: string, granted: boolean) {
    setBusy(slug);
    const { error } = await api.PUT("/api/v1/b/{slug}/consent", { params: { path: { slug } }, body: { granted } }).catch(offline);
    setBusy("");
    if (error) return setMessage({ text: errorMessage(error), error: true });
    setCards((cs) => cs && cs.map((c) => (c.business_slug === slug ? { ...c, marketing_consent: granted } : c)));
    setMessage({ text: granted ? `Recibirás promociones de ${name} por correo.` : `Ya no recibirás promociones de ${name}.` });
  }

  async function logout() {
    await api.POST("/api/v1/auth/logout");
    router.push("/acceso");
  }

  return (
    <CustomerShell title="Mi cuenta" subtitle={email || " "}>
      <h2>Preferencias de comunicación</h2>
      {failed ? <LoadError /> : !cards ? <Loading /> : cards.length === 0 ? (
        <p className="muted">Cuando actives una tarjeta podrás elegir aquí si quieres recibir promociones de ese negocio.</p>
      ) : (
        cards.map((c) => (
          <label key={c.business_slug} className={s.prefRow} htmlFor={`consent-${c.business_slug}`}>
            <span>
              <strong>{c.business_name}</strong>
              <span className="muted" style={{ display: "block", fontSize: 14 }}>
                Promociones por correo · {c.marketing_consent ? "activadas" : "desactivadas"}
              </span>
            </span>
            <input
              id={`consent-${c.business_slug}`} type="checkbox" role="switch" className={s.switch}
              checked={c.marketing_consent} disabled={busy === c.business_slug}
              onChange={(e) => consent(c.business_slug, c.business_name, e.target.checked)}
            />
          </label>
        ))
      )}
      <p className="muted" style={{ fontSize: 14 }}>
        Cada permiso es opcional y se cambia por separado. Los correos de acceso y servicio no son promociones.
      </p>
      {message && <p role={message.error ? "alert" : "status"} className={`status ${message.error ? "error" : ""}`}>{message.text}</p>}

      <h2 style={{ marginTop: 40 }}>Privacidad y mis datos</h2>
      <p className="muted">Cada negocio ve únicamente tu relación con su programa. No puede consultar tus compras en otros locales.</p>
      <div className={s.actions}>
        <button className="secondary" onClick={logout}>Cerrar sesión</button>
      </div>

      <h2 className={s.dangerTitle}>Eliminar tu cuenta</h2>
      <p className="muted">Perderás el acceso a tus tarjetas. Antes de confirmar podrás revisar qué ocurre con tus beneficios y registros.</p>
      <div className={s.actions}>
        <Link href="/cuenta/eliminar" className={`btn ${s.btnLink} ${s.secondaryLink}`}>Revisar eliminación</Link>
      </div>
    </CustomerShell>
  );
}
