"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, type Schemas } from "@/api/client";
import s from "./customer.module.css";

export { s as styles };

const icon = { width: 24, height: 24, fill: "none", stroke: "currentColor", strokeWidth: 1.6, "aria-hidden": true } as const;
const CardIcon = () => (
  <svg viewBox="0 0 24 24" {...icon}><rect x="3" y="5" width="18" height="14" rx="2" /><path d="M3 10h18M7 15h4" /></svg>
);
const UserIcon = () => (
  <svg viewBox="0 0 24 24" {...icon}><circle cx="12" cy="8" r="4" /><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7" /></svg>
);

/** Encabezado con marca, título y navegación inferior del cliente. */
export function CustomerShell({ title, subtitle, children, nav = true }: { title: string; subtitle?: React.ReactNode; children: React.ReactNode; nav?: boolean }) {
  const path = usePathname();
  const current = (href: string) => (path.startsWith(href) ? "page" : undefined);
  return (
    <div className={nav ? s.shell : undefined}>
      <header className={s.top}>
        <Link href="/" className={s.brand}>mesa</Link>
        {nav && <Link href="/cuenta" className={s.iconLink} aria-label="Mi cuenta"><UserIcon /></Link>}
      </header>
      <h1>{title}</h1>
      {subtitle && <p className={s.subtitle}>{subtitle}</p>}
      {children}
      {nav && (
        <nav className={s.nav} aria-label="Cliente">
          <Link href="/mis-tarjetas" aria-current={current("/mis-tarjetas")}><CardIcon />Mis tarjetas</Link>
          <Link href="/cuenta" aria-current={current("/cuenta")}><UserIcon />Mi cuenta</Link>
        </nav>
      )}
    </div>
  );
}

/** Tarjetas del cliente; sin sesión redirige a /acceso?next=<ruta actual>. */
export function useCards() {
  const router = useRouter();
  const path = usePathname();
  const [cards, setCards] = useState<Schemas["Card"][] | null>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    api.GET("/api/v1/me/cards").then(({ data, response }) => {
      if (response.status === 401 || response.status === 403) return router.replace(`/acceso?next=${encodeURIComponent(path)}`);
      if (!data) return setFailed(true);
      setCards(data);
    }, () => setFailed(true));
  }, [router, path]);
  return { cards, setCards, failed };
}

/** Respuesta sustituta cuando fetch falla por red (openapi-fetch lanza en ese caso). */
export const offline = () => ({ data: undefined, error: { detail: "Sin conexión. Revisa tu red e intenta de nuevo." }, response: { status: 0 } as Response });

export const Loading = () => <p role="status" className="muted">Cargando…</p>;
export const LoadError = () => <p role="alert" className="status error">No pudimos cargar tus tarjetas. Revisa tu conexión y recarga la página.</p>;

/** Tarjeta verde con la cuadrícula de sellos. El estado se comunica con check/número y texto, no solo color. */
export function StampCard({ card, href }: { card: Schemas["Card"]; href?: string }) {
  const { stamps, stamps_required: total } = card;
  const body = (
    <>
      <h2>{card.business_name}</h2>
      <p className={s.small}>Cada compra válida suma un sello.</p>
      <div className={s.stamps} role="img" aria-label={`${stamps} de ${total} sellos`}>
        {Array.from({ length: total }, (_, i) => (
          <span key={i} className={`${s.stamp} ${i < stamps ? s.on : ""}`}>
            {i < stamps ? <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2"><path d="m5 12 5 5 9-10" /></svg> : i + 1}
          </span>
        ))}
      </div>
      <p className={s.count}>{stamps} de {total} sellos</p>
      <p className={s.small}>{total} compras válidas = {card.reward_name}</p>
    </>
  );
  return href ? <Link href={href} className={s.stampCard}>{body}</Link> : <section className={s.stampCard}>{body}</section>;
}

export const shortDate = (iso: string) => new Date(iso).toLocaleDateString("es-CO", { day: "numeric", month: "long" });
