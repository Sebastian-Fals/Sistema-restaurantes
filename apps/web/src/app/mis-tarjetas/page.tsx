"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { api, errorMessage, type Schemas } from "@/api/client";
import { cop } from "@/api/format";

type Card = Schemas["Card"];

function StampGrid({ stamps, total }: { stamps: number; total: number }) {
  return (
    <div className="stamps" role="img" aria-label={`${stamps} de ${total} sellos`}>
      {Array.from({ length: total }, (_, i) => (
        <div key={i} className={`stamp ${i < stamps ? "on" : ""}`}>{i < stamps ? "✓" : i + 1}</div>
      ))}
    </div>
  );
}

export default function MyCards() {
  const router = useRouter();
  const [cards, setCards] = useState<Card[] | null>(null);
  const [message, setMessage] = useState("");

  const load = useCallback(async () => {
    const { data, response } = await api.GET("/api/v1/me/cards");
    if (response.status === 401 || response.status === 403) return router.push("/acceso?next=/mis-tarjetas");
    setCards(data ?? []);
  }, [router]);
  useEffect(() => { load(); }, [load]);

  async function consent(slug: string, granted: boolean) {
    const { error } = await api.PUT("/api/v1/b/{slug}/consent", { params: { path: { slug } }, body: { granted } });
    setMessage(error ? errorMessage(error) : granted ? "Aceptaste recibir comunicaciones." : "Revocaste las comunicaciones.");
    load();
  }

  async function logout() {
    await api.POST("/api/v1/auth/logout");
    router.push("/");
  }

  async function deleteAccount() {
    if (!confirm("Esto elimina tu cuenta y tus datos personales. ¿Continuar?")) return;
    await api.DELETE("/api/v1/me");
    router.push("/");
  }

  if (!cards) return <p role="status">Cargando…</p>;
  return (
    <>
      <h1>Mis tarjetas</h1>
      {cards.length === 0 && (
        <p className="card">Aún no tienes tarjetas. Abre la página de tu cafetería y activa tu tarjeta.</p>
      )}
      {cards.map((c) => (
        <section className="card" key={c.business_slug} aria-labelledby={`t-${c.business_slug}`}>
          <h2 id={`t-${c.business_slug}`}>{c.business_name}</h2>
          <p>
            {c.stamps} de {c.stamps_required} sellos · Recompensa: <strong>{c.reward_name}</strong>
          </p>
          <StampGrid stamps={c.stamps} total={c.stamps_required} />
          {c.rewards.map((r) => (
            <p key={r.id} className="status">
              🎉 Recompensa disponible hasta {new Date(r.expires_at).toLocaleDateString("es-CO")}. Muéstrala al personal.
            </p>
          ))}
          {c.recent_purchases.length > 0 && (
            <>
              <h3>Actividad reciente</h3>
              <table>
                <tbody>
                  {c.recent_purchases.map((p) => (
                    <tr key={p.id}>
                      <td>{new Date(p.created_at).toLocaleDateString("es-CO")}</td>
                      <td>{cop(p.amount_cop)}</td>
                      <td>{p.reversed ? "Anulada" : "+1 sello"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
          <label style={{ display: "flex", gap: 8, alignItems: "center", fontWeight: 400 }}>
            <input type="checkbox" style={{ width: 24, minHeight: 24 }} checked={c.marketing_consent} onChange={(e) => consent(c.business_slug, e.target.checked)} />
            Quiero recibir novedades comerciales de este negocio por correo (opcional)
          </label>
          <p><Link href={`/b/${c.business_slug}`}>Ver menú y reglas</Link></p>
        </section>
      ))}
      {message && <p role="status" className="status">{message}</p>}
      <button className="secondary" onClick={logout}>Cerrar sesión</button>{" "}
      <button className="danger" onClick={deleteAccount}>Eliminar mi cuenta</button>
    </>
  );
}
