"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, type Schemas } from "@/api/client";
import { cop } from "@/api/format";
import { Movements } from "./actividad/movements";
import { isoDay, NoPermission, usePanel } from "./context";
import s from "./panel.module.css";

export default function Summary() {
  const { slug, role, business } = usePanel();
  const router = useRouter();
  const [summary, setSummary] = useState<Schemas["Summary"] | null>(null);
  const [events, setEvents] = useState<Schemas["Activity"][]>([]);
  const [forbidden, setForbidden] = useState(false);

  useEffect(() => {
    // El personal entra directo a su tarea; el resumen es solo para administración.
    if (role !== "admin") return router.replace(`/app/${slug}/compras`);
    const path = { slug };
    Promise.all([
      api.GET("/api/v1/b/{slug}/summary", { params: { path } }),
      api.GET("/api/v1/b/{slug}/activity", { params: { path } }),
    ]).then(([sum, act]) => {
      if (sum.response.status === 403) return setForbidden(true);
      setSummary(sum.data ?? null);
      setEvents((act.data ?? []).slice(0, 5));
    });
  }, [slug, role, router]);

  if (forbidden) return <NoPermission />;
  if (role !== "admin") return null;

  const today = isoDay();
  const max = Math.max(1, ...(summary?.daily.map((d) => d.stamps) ?? []));
  const program = business?.program;
  const metrics: [string, number | undefined, string][] = [
    ["Clientes inscritos", summary?.customers, "Participan en este programa"],
    ["Clientes que regresaron", summary?.returning_customers, "Con 2+ compras en el periodo"],
    ["Sellos entregados", summary?.stamps_credited, "Compras válidas registradas"],
    ["Recompensas canjeadas", summary?.rewards_redeemed, `De ${summary?.rewards_earned ?? "–"} obtenidas en el periodo`],
  ];

  return (
    <>
      <div className={s.pageHead}>
        <div>
          <h1 className={s.title}>Hoy en {business?.name ?? slug}</h1>
          <p className={s.subtitle}>
            {new Date().toLocaleDateString("es-CO", { weekday: "long", day: "numeric", month: "long" })} · Actividad de
            fidelización (últimos 30 días)
          </p>
        </div>
        <Link className={s.primary} href={`/app/${slug}/compras`}>Registrar compra</Link>
      </div>

      <dl className={s.metrics}>
        {metrics.map(([label, value, hint]) => (
          <div key={label} className={s.metric}>
            <dt>{label}</dt>
            <dd className={s.metricValue}>{value ?? "–"}</dd>
            <dd className={s.hint}>{hint}</dd>
          </div>
        ))}
      </dl>

      <div className={s.split}>
        <section aria-labelledby="week">
          <h2 id="week" className={s.h2}>Actividad de los últimos 7 días</h2>
          <p className={s.hint}>Sellos entregados · registros observados, no miden el efecto sobre las ventas</p>
          <ol className={s.chart}>
            {summary?.daily.map((d) => {
              const day = new Date(`${d.date}T12:00:00`).toLocaleDateString("es-CO", { weekday: "short" });
              return (
                <li key={d.date} className={s.barCol} aria-current={d.date === today ? "date" : undefined}>
                  <span className={s.barValue}>
                    {d.stamps}
                    <span className={s.srOnly}> sellos el {day}</span>
                  </span>
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
            <p>
              {program.reward_name} al completar {program.stamps_required} sellos
              <br />
              Compra mínima: {cop(program.min_purchase_cop)}
              {program.reward_valid_days ? <><br />Recompensa vigente {program.reward_valid_days} días</> : null}
            </p>
          </section>
        )}
      </div>

      <section aria-labelledby="latest">
        <h2 id="latest" className={s.h2}>Últimos movimientos</h2>
        <Movements events={events} />
      </section>
    </>
  );
}
