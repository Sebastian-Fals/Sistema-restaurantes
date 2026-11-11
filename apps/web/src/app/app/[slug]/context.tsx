"use client";

import Link from "next/link";
import { createContext, useContext } from "react";
import type { Schemas } from "@/api/client";
import s from "./panel.module.css";

export type Panel = { slug: string; role: Schemas["RoleEnum"]; business: Schemas["PublicBusiness"] | null };

export const PanelContext = createContext<Panel>({ slug: "", role: "staff", business: null });
export const usePanel = () => useContext(PanelContext);

/** Fecha local YYYY-MM-DD (la API trabaja con días del negocio). */
export const isoDay = (d = new Date()) => d.toLocaleDateString("en-CA");
export const dateTime = (iso: string) =>
  new Date(iso).toLocaleString("es-CO", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
export const errorCode = (error: unknown) => (error as { code?: string } | undefined)?.code;

/** Estado "No tienes este permiso": el servidor responde 403 a quien no es administrador. */
export function NoPermission() {
  const { slug } = usePanel();
  return (
    <section className={s.forbidden} aria-labelledby="forbidden">
      <h1 id="forbidden" className={s.title}>No tienes este permiso</h1>
      <p className={s.subtitle}>
        Tu rol permite registrar compras y validar recompensas. Para consultar el resumen, la actividad o anular una
        compra, contacta al administrador del negocio.
      </p>
      <Link className={s.primary} href={`/app/${slug}/compras`}>Ir a compras y canjes</Link>
    </section>
  );
}
