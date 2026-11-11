"use client";

import { useCallback, useEffect, useState } from "react";
import { api, errorMessage, type Schemas } from "@/api/client";
import { cop } from "@/api/format";

type Kind = "" | "purchase" | "reversal" | "redemption";
const LABEL = { purchase: "Compra", reversal: "Reverso", redemption: "Canje" } as const;

export function Admin({ slug }: { slug: string }) {
  const [summary, setSummary] = useState<Schemas["Summary"] | null>(null);
  const [events, setEvents] = useState<Schemas["Activity"][]>([]);
  const [kind, setKind] = useState<Kind>("");
  const [reversing, setReversing] = useState<number | null>(null);
  const [reason, setReason] = useState("");
  const [msg, setMsg] = useState<{ text: string; error?: boolean } | null>(null);

  const load = useCallback(async () => {
    const path = { slug };
    const [s, a] = await Promise.all([
      api.GET("/api/v1/b/{slug}/summary", { params: { path } }),
      api.GET("/api/v1/b/{slug}/activity", { params: { path, query: kind ? { type: kind } : {} } }),
    ]);
    setSummary(s.data ?? null);
    setEvents(a.data ?? []);
  }, [slug, kind]);
  useEffect(() => { load(); }, [load]);

  async function reverse(e: React.FormEvent) {
    e.preventDefault();
    const { error } = await api.POST("/api/v1/b/{slug}/purchases/{purchase_id}/reverse", {
      params: { path: { slug, purchase_id: reversing! } },
      body: { reason },
    });
    setMsg(error ? { text: errorMessage(error), error: true } : { text: "Reverso registrado." });
    if (!error) { setReversing(null); setReason(""); load(); }
  }

  const kpis: [string, number | undefined][] = [
    ["Clientes", summary?.customers], ["Compras (30 días)", summary?.purchases], ["Sellos acreditados", summary?.stamps_credited],
    ["Recompensas obtenidas", summary?.rewards_earned], ["Canjeadas", summary?.rewards_redeemed], ["Disponibles", summary?.rewards_available],
  ];

  return (
    <section className="card" aria-labelledby="resumen">
      <h2 id="resumen">Resumen y actividad</h2>
      <div className="grid">{kpis.map(([l, v]) => <div className="kpi" key={l}><b>{v ?? "–"}</b>{l}</div>)}</div>
      <p className="muted">Actividad observada; no mide el efecto del programa sobre las ventas.</p>

      <label htmlFor="kind">Filtrar por tipo</label>
      <select id="kind" value={kind} onChange={(e) => setKind(e.target.value as Kind)}>
        <option value="">Todos</option><option value="purchase">Compras</option><option value="reversal">Reversos</option><option value="redemption">Canjes</option>
      </select>

      {events.length === 0 ? <p className="muted">Sin actividad en el periodo.</p> : (
        <table>
          <thead><tr><th>Fecha</th><th>Tipo</th><th>Cliente</th><th>Registró</th><th>Valor / motivo</th><th /></tr></thead>
          <tbody>
            {events.map((ev, i) => (
              <tr key={i}>
                <td>{new Date(ev.at).toLocaleString("es-CO")}</td><td>{LABEL[ev.type]}</td><td>{ev.customer_email}</td><td>{ev.actor_email}</td>
                <td>{ev.amount_cop != null ? cop(ev.amount_cop) : ""} {ev.detail}</td>
                <td>{ev.type === "purchase" && <button className="secondary" style={{ margin: 0, minHeight: 44 }} onClick={() => setReversing(ev.purchase_id)}>Reversar</button>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {reversing != null && (
        <form onSubmit={reverse} aria-label="Reversar compra">
          <label htmlFor="reason">Motivo del reverso (compra #{reversing})</label>
          <input id="reason" required maxLength={300} autoFocus value={reason} onChange={(e) => setReason(e.target.value)} />
          <button className="danger">Confirmar reverso</button>{" "}
          <button type="button" className="secondary" onClick={() => setReversing(null)}>Cancelar</button>
        </form>
      )}
      {msg && <p role={msg.error ? "alert" : "status"} className={`status ${msg.error ? "error" : ""}`}>{msg.text}</p>}
    </section>
  );
}
