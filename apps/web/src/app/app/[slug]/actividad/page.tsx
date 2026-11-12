"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api, errorMessage, offline, type Schemas } from "@/api/client";
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
  const [loadError, setLoadError] = useState("");
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const loadVersion = useRef(0);
  const detailRef = useRef<HTMLHeadingElement>(null);
  const trigger = useRef<HTMLElement | null>(null);

  function close() {
    setDetail(null);
    setMsg(null);
    trigger.current?.focus(); // retorno de foco al botón "Ver detalle" que abrió el panel
  }

  const load = useCallback(async () => {
    const version = ++loadVersion.current;
    setLoading(true);
    setLoadError("");
    setEvents(null);
    const query = { start, end, ...(kind ? { type: kind } : {}) };
    const { data, error, response } = await api.GET("/api/v1/b/{slug}/activity", { params: { path: { slug }, query } }).catch(offline);
    if (version !== loadVersion.current) return;
    setLoading(false);
    if (response.status === 403) return setForbidden(true);
    if (error || !data) return setLoadError(errorMessage(error));
    setEvents(data);
  }, [slug, start, end, kind]);

  useEffect(() => {
    if (role === "admin") load();
    return () => { loadVersion.current += 1; };
  }, [role, load]);

  async function open(id: number) {
    if (busy) return;
    setBusy(true);
    trigger.current = document.activeElement as HTMLElement | null;
    setMsg(null);
    setReason("");
    try {
      const { data, error } = await api.GET("/api/v1/b/{slug}/purchases/{purchase_id}", { params: { path: { slug, purchase_id: id } } }).catch(offline);
      if (error || !data) return setMsg({ title: "Movimiento no disponible", text: errorMessage(error), error: true });
      setDetail(data);
      requestAnimationFrame(() => detailRef.current?.focus());
    } finally {
      setBusy(false);
    }
  }

  async function reverse(e: React.FormEvent) {
    e.preventDefault();
    if (!detail || busy) return;
    setBusy(true);
    setMsg(null);
    try {
      const { error, response } = await api.POST("/api/v1/b/{slug}/purchases/{purchase_id}/reverse", {
        params: { path: { slug, purchase_id: detail.id } },
        body: { reason: reason.trim() },
      }).catch(offline);
      // A lost response can follow a committed reversal. Read its state before asking to retry.
      const fresh = !error || response.status === 0 || errorCode(error) === "already_reversed"
        ? await api.GET("/api/v1/b/{slug}/purchases/{purchase_id}", { params: { path: { slug, purchase_id: detail.id } } }).catch(offline)
        : null;
      if (fresh?.data) setDetail(fresh.data);
      if (fresh?.data?.reversed) {
        setMsg({ title: "Reverso registrado", text: "La compra está anulada y se conserva el evento original con su motivo y responsable." });
        await load();
        return;
      }
      if (error) {
        return setMsg(
          errorCode(error) === "needs_support"
            ? { title: "Escalar a soporte", text: `${errorMessage(error)} No se modifica automáticamente. Contacta a soporte con el número de compra.`, error: true }
            : { title: "No se pudo confirmar el reverso", text: `${errorMessage(error)} Puedes consultar de nuevo el detalle o reintentar sobre esta misma compra.`, error: true },
        );
      }
      // The server confirmed the write even if the following read failed.
      setDetail({ ...detail, reversed: true, reversal_reason: reason.trim() });
      setMsg({ title: "Reverso registrado", text: "Se conserva el evento original. No se pudo actualizar el detalle; vuelve a cargar la actividad." });
      await load();
    } finally {
      setBusy(false);
    }
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

      {loading && <p role="status">Cargando actividad…</p>}
      {busy && !detail && <p role="status">Cargando detalle…</p>}
      {loadError && <div role="alert" className={`${s.notice} ${s.noticeError}`}><b>No se pudo cargar la actividad</b><span>{loadError}</span><button type="button" className={s.secondary} onClick={load}>Reintentar</button></div>}
      {events && <Movements events={events} onDetail={open} disabled={busy} />}

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
              <input id="reason" required maxLength={300} disabled={busy} value={reason} onChange={(e) => setReason(e.target.value)} />
              <p className={s.hint}>
                Se conserva el evento original. Si la recompensa obtenida con este sello ya fue canjeada, el caso pasa a
                soporte y no se modifica automáticamente.
              </p>
              <div className={s.actions}>
                <button className={s.dangerBtn} disabled={!reason.trim() || busy}>{busy ? "Registrando reverso…" : "Confirmar reverso"}</button>
                <button type="button" className={s.secondary} disabled={busy} onClick={close}>Volver al historial</button>
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
