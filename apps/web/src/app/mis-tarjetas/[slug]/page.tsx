"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { cop } from "@/api/format";
import { CustomerShell, LoadError, Loading, shortDate, StampCard, styles as s, useCards } from "@/features/customer/shell";

export default function CardDetail() {
  const { slug } = useParams<{ slug: string }>();
  const { cards, failed } = useCards();
  const card = cards?.find((c) => c.business_slug === slug);

  if (failed || !cards || !card)
    return (
      <CustomerShell title="Tu tarjeta">
        {failed ? <LoadError /> : !cards ? <Loading /> : (
          <p className="muted">No tienes una tarjeta en este negocio. <Link href={`/b/${slug}`}>Ver su programa</Link></p>
        )}
      </CustomerShell>
    );

  return (
    <CustomerShell title="Tu tarjeta" subtitle={card.business_name}>
      {card.rewards.map((r) => (
        <section key={r.id} className={s.reward} aria-labelledby={`r-${r.id}`}>
          <p className={s.badge}>Recompensa disponible</p>
          <h2 id={`r-${r.id}`}>{card.reward_name}</h2>
          <p>Válida hasta el {shortDate(r.expires_at)}</p>
          <p className={s.small}>Preséntala en caja con tu código de cliente. Solo se descuenta cuando el personal confirma el canje.</p>
        </section>
      ))}

      <StampCard card={card} />

      <section className={s.codeBox} aria-labelledby="code-title">
        <h2 id="code-title" className={s.label}>Mi código de cliente</h2>
        <p className={s.code}>{card.customer_code}</p>
        <p className="muted">Muéstralo al personal al pagar. El personal valida la compra para sumar el sello.</p>
      </section>

      <h2>Actividad reciente</h2>
      {card.recent_purchases.length === 0 ? (
        <p className="muted">Aún no hay compras registradas en esta tarjeta.</p>
      ) : (
        <ul className={s.activity}>
          {card.recent_purchases.map((p) => (
            <li key={p.id} className={p.reversed ? s.reversed : undefined}>
              <span>{shortDate(p.created_at)} · {cop(p.amount_cop)}</span>
              {p.reversed ? <span><strong>+1 sello</strong> · Reversada</span> : <strong>+1 sello</strong>}
            </li>
          ))}
        </ul>
      )}

      <div className={s.actions}>
        <Link href={`/b/${card.business_slug}`} className={`btn ${s.btnLink} ${s.secondaryLink}`}>Ver menú y reglas</Link>
      </div>
    </CustomerShell>
  );
}
