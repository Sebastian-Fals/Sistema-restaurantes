"use client";

import Link from "next/link";
import { useRef, useState } from "react";
import { api, errorMessage, type Schemas } from "@/api/client";
import { cop } from "@/api/format";
import { errorCode, usePanel } from "../context";
import s from "../panel.module.css";

type Customer = Schemas["CustomerLookup"];
type Msg = { title: string; text: string; error?: boolean };

const ERROR_TITLE: Record<string, string> = {
  reference_conflict: "Comprobante ya usado",
  below_minimum: "Compra bajo el mínimo",
  reward_not_redeemable: "Recompensa no disponible",
  reward_not_found: "Recompensa no encontrada",
  unknown_customer: "Cliente no encontrado",
};
const fail = (error: unknown): Msg => ({
  title: ERROR_TITLE[errorCode(error) ?? ""] ?? "No se pudo completar",
  text: errorMessage(error),
  error: true,
});
const longDate = (iso: string) => new Date(iso).toLocaleDateString("es-CO", { day: "numeric", month: "long", year: "numeric" });

export default function Purchases() {
  const { slug, role, business } = usePanel();
  const program = business?.program;
  const [q, setQ] = useState("");
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [reference, setReference] = useState("");
  const [amount, setAmount] = useState("");
  const [paid, setPaid] = useState(false);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<Msg | null>(null);
  const [reward, setReward] = useState<Schemas["Reward"] | null>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  const trigger = useRef<HTMLButtonElement | null>(null);
  const result = useRef<HTMLDivElement>(null);

  function show(m: Msg) {
    setMsg(m);
    requestAnimationFrame(() => result.current?.focus());
  }

  async function lookup(query = q) {
    const { data, error } = await api.GET("/api/v1/b/{slug}/customer", { params: { path: { slug }, query: { q: query } } });
    setCustomer(data ?? null);
    return error;
  }

  async function search(e: React.FormEvent) {
    e.preventDefault();
    setMsg(null);
    const error = await lookup();
    if (error) show(fail(error));
  }

  function reset() {
    setCustomer(null);
    setReference("");
    setAmount("");
    setPaid(false);
  }

  async function register(e: React.FormEvent) {
    e.preventDefault();
    if (!customer) return;
    setBusy(true);
    const { data, error, response } = await api.POST("/api/v1/b/{slug}/purchases", {
      params: { path: { slug } },
      body: { customer_email: customer.email, amount_cop: Number(amount), reference: reference.trim() },
    });
    setBusy(false);
    if (error || !data) return show(fail(error));
    const p = data.purchase;
    const head = `Comprobante ${p.reference} · ${cop(p.amount_cop)} · ${p.customer_email}.`;
    // Al completar la tarjeta el contador vuelve a 0 y nace una recompensa.
    const credited = p.reward_id != null
      ? "Se acreditó 1 sello y completó la tarjeta: ganó una recompensa disponible para canjear."
      : `Se acreditó 1 sello. Ahora tiene ${data.stamps} de ${data.stamps_required}.`;
    show(
      response.status === 201
        ? { title: "Compra registrada", text: `${head} ${credited}` }
        : { title: "Compra ya registrada", text: `${head} Esta referencia ya estaba registrada: no se sumó otro sello. Tiene ${data.stamps} de ${data.stamps_required}.` },
    );
    setReference("");
    setAmount("");
    setPaid(false);
    await lookup(customer.email);
  }

  function ask(r: Schemas["Reward"], button: HTMLButtonElement) {
    trigger.current = button;
    setReward(r);
    dialog.current?.showModal();
  }

  function closeDialog() {
    dialog.current?.close();
  }

  async function redeem() {
    if (!reward || !customer) return;
    setBusy(true);
    const { error } = await api.POST("/api/v1/b/{slug}/rewards/{reward_id}/redeem", { params: { path: { slug, reward_id: reward.id } } });
    setBusy(false);
    closeDialog();
    show(error ? fail(error) : { title: "Canje confirmado", text: `${program?.reward_name ?? "Recompensa"} entregada a ${customer.email}. No puede volver a usarse.` });
    await lookup(customer.email);
  }

  const next = customer ? customer.stamps + 1 : 0;

  return (
    <>
      <div className={s.pageHead}>
        <div>
          <h1 className={s.title}>Compras y canjes</h1>
          <p className={s.subtitle}>Identifica al cliente y verifica el comprobante antes de acreditar. Esta app no cobra.</p>
        </div>
        {role === "admin" && <Link className={s.secondary} href={`/app/${slug}/actividad`}>Ver movimientos</Link>}
      </div>

      <form className={s.search} onSubmit={search} role="search">
        <div>
          <label htmlFor="q">Código o correo del cliente</label>
          <input
            id="q"
            required
            placeholder="CAF · 482 916 o correo"
            autoComplete="off"
            value={q}
            onChange={(e) => { setQ(e.target.value); reset(); }}
          />
        </div>
        <button className={s.primaryBtn}>Buscar cliente</button>
      </form>

      <div ref={result} tabIndex={-1} className={s.live}>
        {msg && (
          <div role={msg.error ? "alert" : "status"} className={`${s.notice} ${msg.error ? s.noticeError : ""}`}>
            <b>{msg.title}</b>
            <span>{msg.text}</span>
          </div>
        )}
      </div>

      {customer && (
        <>
          <p className={s.chip}>
            {customer.email}
            {customer.customer_code && ` · ${customer.customer_code}`} · cliente verificado
          </p>

          <div className={s.split}>
            <form onSubmit={register} aria-labelledby="register">
              <h2 id="register" className={s.h2}>Registrar compra válida</h2>
              <div className={s.pair}>
                <div>
                  <label htmlFor="ref">Comprobante de compra</label>
                  <input id="ref" required maxLength={64} value={reference} onChange={(e) => setReference(e.target.value)} />
                </div>
                <div>
                  <label htmlFor="amount">Total pagado (COP)</label>
                  <input
                    id="amount"
                    type="number"
                    inputMode="numeric"
                    min={1}
                    step={1}
                    required
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                  />
                </div>
              </div>
              <label className={s.check}>
                <input type="checkbox" required checked={paid} onChange={(e) => setPaid(e.target.checked)} />
                Confirmo que la compra fue pagada y no está anulada.
              </label>
              <div className={s.actions}>
                <button className={s.primaryBtn} disabled={busy}>Validar y sumar 1 sello</button>
                <button type="button" className={s.secondary} onClick={() => { setQ(""); reset(); setMsg(null); }}>
                  Cancelar registro
                </button>
              </div>
            </form>

            <aside className={s.programCard} aria-labelledby="validation">
              <h2 id="validation" className={s.h2}>Resumen de validación</h2>
              <dl className={s.facts}>
                <div><dt>Cliente</dt><dd>{customer.email}</dd></div>
                {program && <div><dt>Programa</dt><dd>{program.reward_name} · mínimo {cop(program.min_purchase_cop)}</dd></div>}
                <div>
                  <dt>Resultado previsto</dt>
                  <dd>
                    {customer.stamps} → {next} sellos
                    {next >= customer.stamps_required && " · completa la recompensa"}
                  </dd>
                </div>
              </dl>
              <p className={s.hint}>
                El comprobante no puede repetirse en este negocio. El resultado se confirma después de registrar la operación.
              </p>
            </aside>
          </div>

          <section aria-labelledby="rewards" className={s.rewards}>
            <h2 id="rewards" className={s.h2}>Validar recompensa</h2>
            {customer.rewards.length === 0 ? (
              <p className={s.hint}>Sin recompensas disponibles. Lleva {customer.stamps} de {customer.stamps_required} sellos.</p>
            ) : (
              <ul className={s.rewardList}>
                {customer.rewards.map((r) => (
                  <li key={r.id} className={s.rewardItem}>
                    <div>
                      <span className={s.okChip}>Disponible · no utilizada</span>
                      <p className={s.rewardName}>{program?.reward_name ?? "Recompensa"}</p>
                      <p className={s.hint}>Vence el {longDate(r.expires_at)} · Emisión #{r.id}</p>
                    </div>
                    <button type="button" className={s.primaryBtn} onClick={(e) => ask(r, e.currentTarget)}>
                      Canjear
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}

      <dialog ref={dialog} className={s.dialog} aria-labelledby="confirm" onClose={() => { setReward(null); trigger.current?.focus(); }}>
        <h2 id="confirm" className={s.h2}>¿Confirmar canje?</h2>
        <p>
          {program?.reward_name ?? "Recompensa"} para {customer?.email}
          {reward && <> · vence el {longDate(reward.expires_at)}</>}
        </p>
        <p className={s.warning}>Confirma cuando entregues el producto. Esta acción consumirá la recompensa una sola vez.</p>
        <div className={s.actions}>
          <button type="button" className={s.primaryBtn} disabled={busy} onClick={redeem}>Confirmar canje</button>
          <button type="button" className={s.secondary} onClick={closeDialog} autoFocus>Volver sin canjear</button>
        </div>
      </dialog>
    </>
  );
}
