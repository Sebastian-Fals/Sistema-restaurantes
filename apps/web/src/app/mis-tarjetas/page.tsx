"use client";

import { CustomerShell, LoadError, Loading, StampCard, styles as s, useCards } from "@/features/customer/shell";

export default function MyCards() {
  const { cards, failed } = useCards();

  return (
    <CustomerShell title={cards?.length === 0 ? "Aún no tienes tarjetas" : "Mis tarjetas"} subtitle={cards?.length ? "Tus próximos beneficios, en un solo lugar." : undefined}>
      {failed ? <LoadError /> : !cards ? <Loading /> : cards.length === 0 ? (
        <p className="muted">Escanea el QR de un establecimiento o abre el enlace de su menú para conocer su programa y activar tu primera tarjeta.</p>
      ) : (
        cards.map((c) => {
          const left = Math.max(0, c.stamps_required - c.stamps);
          return (
            <div key={c.business_slug}>
              <StampCard card={c} href={`/mis-tarjetas/${c.business_slug}`} />
              <p className={s.hint}>
                {c.rewards.length > 0
                  ? `Tienes ${c.rewards.length === 1 ? "una recompensa disponible" : `${c.rewards.length} recompensas disponibles`}. Ábrela para presentarla en caja.`
                  : left === 0 ? "Completaste tu tarjeta; tu recompensa aparecerá aquí."
                  : `Te ${left === 1 ? "falta 1 compra" : `faltan ${left} compras`} para tu ${c.reward_name.toLowerCase()}.`}
              </p>
            </div>
          );
        })
      )}
    </CustomerShell>
  );
}
