"use client";

import { useState } from "react";
import { api, errorMessage, type Schemas } from "@/api/client";

type Customer = Schemas["CustomerLookup"];
const newReference = () => crypto.randomUUID().slice(0, 8);

export function Staff({ slug }: { slug: string }) {
  const [email, setEmail] = useState("");
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [amount, setAmount] = useState("");
  // La referencia se conserva hasta que la compra se registra: un reintento no duplica el sello.
  const [reference, setReference] = useState(newReference);
  const [msg, setMsg] = useState<{ text: string; error?: boolean } | null>(null);

  async function lookup(e?: React.FormEvent) {
    e?.preventDefault();
    const { data, error } = await api.GET("/api/v1/b/{slug}/customer", { params: { path: { slug }, query: { q: email } } });
    setCustomer(data ?? null);
    setMsg(error ? { text: errorMessage(error), error: true } : null);
  }

  async function register(e: React.FormEvent) {
    e.preventDefault();
    const { data, error } = await api.POST("/api/v1/b/{slug}/purchases", {
      params: { path: { slug } },
      body: { customer_email: email, amount_cop: Number(amount), reference },
    });
    if (error || !data) return setMsg({ text: errorMessage(error), error: true });
    setMsg({ text: data.created ? `Compra registrada. Sellos: ${data.stamps}/${data.stamps_required}.` : "Esa compra ya estaba registrada; no se duplicó." });
    setAmount("");
    setReference(newReference());
    lookup();
  }

  async function redeem(id: number) {
    if (!confirm("¿Confirmas el canje? No se puede deshacer.")) return;
    const { error } = await api.POST("/api/v1/b/{slug}/rewards/{reward_id}/redeem", { params: { path: { slug, reward_id: id } } });
    setMsg(error ? { text: errorMessage(error), error: true } : { text: "Recompensa canjeada." });
    lookup();
  }

  return (
    <section className="card" aria-labelledby="registrar">
      <h2 id="registrar">Registrar compra o canje</h2>
      <p className="muted">Registra solo compras ya cobradas en tu caja. Esta app no cobra.</p>
      <form onSubmit={lookup}>
        <label htmlFor="cust">Correo del cliente</label>
        <input id="cust" type="email" required value={email} onChange={(e) => { setEmail(e.target.value); setCustomer(null); }} />
        <button>Buscar cliente</button>
      </form>

      {customer && (
        <>
          <p className="status">
            {customer.email}: {customer.stamps}/{customer.stamps_required} sellos
          </p>
          {customer.rewards.map((r) => (
            <p key={r.id}>
              Recompensa disponible (vence {new Date(r.expires_at).toLocaleDateString("es-CO")}){" "}
              <button type="button" onClick={() => redeem(r.id)}>Canjear</button>
            </p>
          ))}
          <form onSubmit={register}>
            <label htmlFor="amount">Valor de la compra (COP)</label>
            <input id="amount" type="number" min={1} step={1} required value={amount} onChange={(e) => setAmount(e.target.value)} />
            <label htmlFor="ref">Referencia del ticket (única)</label>
            <input id="ref" required maxLength={64} value={reference} onChange={(e) => setReference(e.target.value)} />
            <button>Registrar compra</button>
          </form>
        </>
      )}
      {msg && <p role={msg.error ? "alert" : "status"} className={`status ${msg.error ? "error" : ""}`}>{msg.text}</p>}
    </section>
  );
}
