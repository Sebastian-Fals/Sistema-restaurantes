"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api, errorMessage, type Schemas } from "@/api/client";
import { cop } from "@/api/format";
import { dateTime, errorCode, isoDay, NoPermission, usePanel } from "../context";
import s from "../panel.module.css";
import { Movements } from "./movements";

type Kind = "" | Schemas["TypeEnum"];
type Msg = { title: string; text: string; error?: boolean };

export default function Activity() {
  const { slug, role } = usePanel();
  const [start, setStart] = useState(() => isoDay(new Date(Date.now() - 30 * 864e5)));
  const [end, setEnd] = useState(() => isoDay());
  const [kind, setKind] = useState<Kind>("");
  const [events, setEvents] = useState<Schemas["Activity"][] | null>(null);
  const [forbidden, setForbidden] = useState(false);
  const [detail, setDetail] = useState<Schemas["Purchase"] | null>(null);
  const [reason, setReason] = useState("");
  const [msg, setMsg] = useState<Msg | null>(null);
  const detailRef = useRef<HTMLHeadingElement>(null);
  const trigger = useRef<HTMLElement | null>(null);

  function close() {
    setDetail(null);
    setMsg(null);
    trigger.current?.focus(); // retorno de foco al botón "Ver detalle" que abrió el panel
  }

  const load = useCallback(async () => {
    const query = { start, end, ...(kind ? { type: kind } : {}) };
    const { data, error, response } = await api.GET("/api/v1/b/{slug}/activity", { params: { path: { slug }, query } });
    if (response.status === 403) return setForbidden(true);
    setEvents(data ?? []);
    if (error) setMsg({ title: "No se pudo cargar la actividad", text: errorMessage(error), error: true });
  }, [slug, start, end, kind]);

  useEffect(() => { if (role === "admin") load(); }, [role, load]);

  async function open(id: number) {
    trigger.current = document.activeElement as HTMLElement | null;
    setMsg(null);
    setReason("");
    const { data, error } = await api.GET("/api/v1/b/{slug}/purchases/{purchase_id}", { params: { path: { slug, purchase_id: id } } });
    if (error || !data) return setMsg({ title: "Movimiento no disponible", text: errorMessage(error), error: true });
    setDetail(data);
    requestAnimationFrame(() => detailRef.current?.focus());
  }

  async function reverse(e: React.FormEvent) {
    e.preventDefault();
    if (!detail) return;
    const { error } = await api.POST("/api/v1/b/{slug}/purchases/{purchase_id}/reverse", {
      params: { path: { slug, purchase_id: detail.id } },
      body: { reason: reason.trim() },
    });
    if (error) {
      return setMsg(
        errorCode(error) === "needs_support"
          ? { title: "Escalar a soporte", text: `${errorMessage(error)} La recompensa derivada ya fue canjeada; no se modifica automáticamente.`, error: true }
          : { title: "No se pudo anular", text: errorMessage(error), error: true },
      );
    }
    const fresh = await api.GET("/api/v1/b/{slug}/purchases/{purchase_id}", { params: { path: { slug, purchase_id: detail.id } } });
    if (fresh.data) setDetail(fresh.data);
    setMsg({ title: "Reverso registrado", text: "Se conserva el evento original y se descontó el sello." });
    load();
  }

  if (role !== "admin" || forbidden) return <NoPermission />;

  return (
    <>
      <div className={s.pageHead}>
        <div>
          <h1 className={s.title}>Actividad</h1>
          <p className={s.subtitle}>Cada movimiento conserva su comprobante y responsable.</p>
        </div>
      </div>

      <form className={s.filters} onSubmit={(e) => e.preventDefault()} aria-label="Filtros de actividad">
        <div>
          <label htmlFor="start">Desde</label>
          <input id="start" type="date" value={start} max={end} onChange={(e) => e.target.value && setStart(e.target.value)} />
        </div>
        <div>
          <label htmlFor="end">Hasta</label>
          <input id="end" type="date" value={end} min={start} onChange={(e) => e.target.value && setEnd(e.target.value)} />
        </div>
        <div>
          <label htmlFor="kind">Tipo</label>
          <select id="kind" value={kind} onChange={(e) => setKind(e.target.value as Kind)}>
            <option value="">Todos los movimientos</option>
            <option value="purchase">Compras</option>
            <option value="redemption">Canjes</option>
            <option value="reversal">Reversos</option>
          </select>
        </div>
      </form>

      {events ? <Movements events={events} onDetail={open} /> : <p role="status">Cargando…</p>}

      {msg && !detail && (
        <div role="alert" className={`${s.notice} ${s.noticeError}`}>
          <b>{msg.title}</b> {msg.text}
        </div>
      )}

      {detail && (
        <section className={s.detail} aria-labelledby="detail">
          <h2 id="detail" ref={detailRef} tabIndex={-1} className={s.cardTitle}>Detalle del movimiento</h2>
          <dl className={s.facts}>
            <div><dt>Compra</dt><dd>#{detail.id} · {cop(detail.amount_cop)}</dd></div>
            <div><dt>Comprobante</dt><dd>{detail.reference}</dd></div>
            <div><dt>Cliente</dt><dd>{detail.customer_email}</dd></div>
            <div><dt>Registró</dt><dd>{detail.registered_by_email}</dd></div>
            <div><dt>Fecha</dt><dd>{dateTime(detail.created_at)}</dd></div>
            <div>
              <dt>Estado</dt>
              <dd>{detail.reversed ? `Anulada · motivo: ${detail.reversal_reason}` : detail.reward_id ? `Válida · completó la recompensa #${detail.reward_id}` : "Válida"}</dd>
            </div>
          </dl>

          {!detail.reversed && (
            <form onSubmit={reverse}>
              <h3 className={s.h3}>Anular compra</h3>
              <label htmlFor="reason">Motivo obligatorio</label>
              <input id="reason" required maxLength={300} value={reason} onChange={(e) => setReason(e.target.value)} />
              <p className={s.hint}>
                Se conserva el evento original. Si la recompensa obtenida con este sello ya fue canjeada, el caso pasa a
                soporte y no se modifica automáticamente.
              </p>
              <div className={s.actions}>
                <button className={s.dangerBtn} disabled={!reason.trim()}>Confirmar reverso</button>
                <button type="button" className={s.secondary} onClick={close}>Volver al historial</button>
              </div>
            </form>
          )}
          {detail.reversed && (
            <button type="button" className={s.secondary} onClick={close}>Volver al historial</button>
          )}
          {msg && (
            <div role={msg.error ? "alert" : "status"} className={`${s.notice} ${msg.error ? s.noticeError : ""}`}>
              <b>{msg.title}</b> {msg.text}
            </div>
          )}
        </section>
      )}
    </>
  );
}
