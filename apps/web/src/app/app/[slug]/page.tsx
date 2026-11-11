"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, errorMessage, offline, type Schemas } from "@/api/client";
import { cop } from "@/api/format";
import { Movements } from "./actividad/movements";
import { isoDay, NoPermission, usePanel } from "./context";
import s from "./panel.module.css";

export default function Summary() {
  const { slug, role, business } = usePanel();
  const router = useRouter();
  const [start, setStart] = useState(() => isoDay(new Date(Date.now() - 30 * 864e5)));
  const [end, setEnd] = useState(() => isoDay());
  const [summary, setSummary] = useState<Schemas["Summary"] | null>(null);
  const [events, setEvents] = useState<Schemas["Activity"][]>([]);
  const [forbidden, setForbidden] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (role !== "admin") return router.replace(`/app/${slug}/compras`);
    let active = true;
    setLoading(true);
    setError("");
    setSummary(null);
    const params = { path: { slug }, query: { start, end } };
    Promise.all([
      api.GET("/api/v1/b/{slug}/summary", { params }).catch(offline),
      api.GET("/api/v1/b/{slug}/activity", { params }).catch(offline),
    ]).then(([sum, act]) => {
      if (!active) return;
      setLoading(false);
      if (sum.response.status === 403 || act.response.status === 403) return setForbidden(true);
      if (!sum.data || !act.data) return setError(errorMessage(sum.error ?? act.error, "No pudimos cargar el resumen. Intenta de nuevo."));
      setSummary(sum.data);
      setEvents(act.data.slice(0, 5));
    });
    return () => { active = false; };
  }, [slug, role, router, start, end, attempt]);

  if (forbidden) return <NoPermission />;
  if (role !== "admin") return null;

  const today = isoDay();
  const max = Math.max(1, ...(summary?.daily.map((d) => d.stamps) ?? []));
  const program = business?.program;
  const metrics: [string, number | undefined, string][] = [
    ["Clientes inscritos", summary?.customers, "Total del programa"],
    ["Compras registradas", summary?.purchases, "Compras válidas en el periodo"],
    ["Sellos entregados", summary?.stamps_credited, "Un sello por compra válida"],
    ["Recompensas disponibles", summary?.rewards_available, "Vigentes para canjear ahora"],
    ["Recompensas canjeadas", summary?.rewards_redeemed, `De ${summary?.rewards_earned ?? "–"} obtenidas en el periodo`],
    ["Clientes que regresaron", summary?.returning_customers, "Con 2+ compras en el periodo"],
  ];

  return (
    <>
      <div className={s.pageHead}>
        <div>
          <h1 className={s.title}>Resumen de {business?.name ?? slug}</h1>
          <p className={s.subtitle}>Actividad de fidelización · fechas del negocio en Colombia</p>
        </div>
        <Link className={s.primary} href={`/app/${slug}/compras`}>Registrar compra</Link>
      </div>

      <form className={s.filters} onSubmit={(e) => e.preventDefault()} aria-label="Periodo del resumen">
        <div>
          <label htmlFor="summary-start">Desde</label>
          <input id="summary-start" type="date" required value={start} max={end} onChange={(e) => e.target.value && setStart(e.target.value)} />
        </div>
        <div>
          <label htmlFor="summary-end">Hasta</label>
          <input id="summary-end" type="date" required value={end} min={start} onChange={(e) => e.target.value && setEnd(e.target.value)} />
        </div>
      </form>

      {loading && <p role="status">Cargando el resumen…</p>}
      {error && (
        <div role="alert" className={`${s.notice} ${s.noticeError}`}>
          <b>No se pudo cargar el resumen</b><span>{error}</span>
          <button type="button" className={s.secondary} onClick={() => setAttempt((n) => n + 1)}>Reintentar</button>
        </div>
      )}

      {summary && (
        <>
          <dl className={s.metrics}>
            {metrics.map(([label, value, hint]) => (
              <div key={label} className={s.metric}>
                <dt>{label}</dt><dd className={s.metricValue}>{value ?? "–"}</dd><dd className={s.hint}>{hint}</dd>
              </div>
            ))}
          </dl>

          <div className={s.split}>
            <section aria-labelledby="week">
              <h2 id="week" className={s.h2}>Actividad al cierre del periodo</h2>
              <p className={s.hint}>Sellos de los 7 días hasta {end}. Registros observados; no miden el efecto sobre las ventas.</p>
              <ol className={s.chart}>
                {summary.daily.map((d) => {
                  const day = new Date(`${d.date}T12:00:00`).toLocaleDateString("es-CO", { weekday: "short" });
                  return (
                    <li key={d.date} className={s.barCol} aria-current={d.date === today ? "date" : undefined}>
                      <span className={s.barValue}>{d.stamps}<span className={s.srOnly}> sellos el {d.date}</span></span>
                      <span className={s.bar} style={{ height: `${Math.max(4, (d.stamps / max) * 140)}px` }} aria-hidden />
                      <span className={s.barDay} aria-hidden>{day.replace(".", "")}</span>
                    </li>
                  );
                })}
              </ol>
            </section>

            {program && (
              <section className={s.programCard} aria-labelledby="program">
                <h2 id="program" className={s.h2}>Tu programa está activo</h2>
                <p>{program.reward_name} al completar {program.stamps_required} sellos<br />Compra mínima: {cop(program.min_purchase_cop)}
                  {program.reward_valid_days ? <><br />Recompensa vigente {program.reward_valid_days} días</> : null}
                </p>
              </section>
            )}
          </div>

          <section aria-labelledby="latest">
            <h2 id="latest" className={s.h2}>Últimos movimientos del periodo</h2>
            <Movements events={events} />
            {events.length > 0 && <Link className={s.link} href={`/app/${slug}/actividad`}>Ver actividad y detalles</Link>}
          </section>
        </>
      )}
    </>
  );
}
