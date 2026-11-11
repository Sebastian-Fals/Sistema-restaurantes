"use client";

import type { Schemas } from "@/api/client";
import { cop } from "@/api/format";
import { dateTime } from "../context";
import s from "../panel.module.css";

const LABEL = { purchase: "+1 sello", reversal: "Sello revertido", redemption: "Canje confirmado" } as const;

/** Tabla de movimientos; en pantallas angostas cada fila se muestra como bloque con etiquetas. */
export function Movements({ events, onDetail }: { events: Schemas["Activity"][]; onDetail?: (purchaseId: number) => void }) {
  if (events.length === 0) return <p className={s.hint}>Sin movimientos en el periodo.</p>;
  return (
    <table className={s.table}>
      <thead>
        <tr>
          <th scope="col">Fecha</th>
          <th scope="col">Cliente</th>
          <th scope="col">Movimiento</th>
          <th scope="col">Compra</th>
          <th scope="col">Responsable</th>
          {onDetail && <th scope="col"><span className={s.srOnly}>Acciones</span></th>}
        </tr>
      </thead>
      <tbody>
        {events.map((ev) => (
          <tr key={`${ev.type}-${ev.purchase_id}-${ev.at}`}>
            <td data-label="Fecha" className={s.strong}>{dateTime(ev.at)}</td>
            <td data-label="Cliente">{ev.customer_email}</td>
            <td data-label="Movimiento">
              {LABEL[ev.type]}
              {ev.amount_cop != null && ev.type === "purchase" ? ` · ${cop(ev.amount_cop)}` : ""}
              {ev.detail && <span className={s.hint}> · {ev.detail}</span>}
            </td>
            <td data-label="Compra">#{ev.purchase_id}</td>
            <td data-label="Responsable">{ev.actor_email}</td>
            {onDetail && (
              <td>
                <button type="button" className={s.link} onClick={() => onDetail(ev.purchase_id)}>
                  Ver detalle<span className={s.srOnly}> de la compra #{ev.purchase_id}</span>
                </button>
              </td>
            )}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
