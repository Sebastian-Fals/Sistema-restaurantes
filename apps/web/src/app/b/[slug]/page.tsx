import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { cache } from "react";
import { serverApi } from "@/api/server";
import { cop } from "@/api/format";
import { SupportContact } from "@/components/support-contact";
import { ActivateButton } from "./activate-button";
import { Header } from "./header";
import s from "./page.module.css";

type Props = { params: Promise<{ slug: string }> };

// cache: generateMetadata y la página comparten una sola llamada por request.
const load = cache(async (slug: string) => {
  const { data, response } = await serverApi.GET("/api/v1/public/b/{slug}", { params: { path: { slug } } });
  if (response.status === 404) notFound();
  if (!data) throw new Error("No se pudo cargar el negocio");
  return data;
});

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const b = await load(slug);
  return { title: `${b.name} — Mesa`, description: b.description };
}

export default async function BusinessPage({ params }: Props) {
  const { slug } = await params;
  const b = await load(slug);
  const p = b.program;
  const categories = [...new Set(b.menu.map((i) => i.category))];

  return (
    <div className={`wide ${s.page}`}>
      <Header />
      <div className={s.layout}>
        <div className={s.intro}>
          <h1 className={s.name}>{b.name}</h1>
          {b.description && <p className={s.lead}>{b.description}</p>}
          {b.address && <p className={s.lead}>{b.address}</p>}
          <span className={s.chip}>Menú público</span>
        </div>

        {p && (
          <section className={s.aside} aria-labelledby="programa">
            <div className={s.card}>
              <h2 id="programa" className={s.cardName}>{b.name}</h2>
              <p className={s.cardLead}>Tu próximo café empieza aquí.</p>
              <ol className={s.stamps} aria-hidden="true">
                {Array.from({ length: p.stamps_required }, (_, i) => <li key={i}>{i + 1}</li>)}
              </ol>
              <p className={s.count}>0 de {p.stamps_required} sellos</p>
              <p className={s.cardNote}>{p.stamps_required} compras válidas = {p.reward_name}</p>
            </div>

            <div className={s.section}>
              <h3 className={s.h3}>Así acumulas</h3>
              <p className={s.rules}>
                Una compra pagada de {cop(p.min_purchase_cop)} o más suma un sello. Al completar {p.stamps_required}, recibes{" "}
                <strong>{p.reward_name}</strong>.
              </p>
              <p className={s.fine}>
                {p.reward_valid_days != null ? `Tienes ${p.reward_valid_days} días para canjear la recompensa. ` : ""}
                {p.conditions}
              </p>
              <ActivateButton slug={b.slug} className={s.cta} />
            </div>
          </section>
        )}

        <section className={`${s.section} ${s.menu}`} aria-labelledby="menu">
          <h2 id="menu" className={s.h2}>Menú</h2>
          {b.menu.length === 0 ? (
            <p className={s.lead}>Aún no hay productos publicados.</p>
          ) : (
            categories.length > 1 && (
              <nav aria-label="Categorías del menú">
                <ul className={s.tabs}>
                  {categories.map((c, n) => <li key={c}><a href={`#cat-${n}`}>{c}</a></li>)}
                </ul>
              </nav>
            )
          )}
          {categories.map((c, n) => (
            <div className={s.cat} id={`cat-${n}`} key={c}>
              <h3>{c}</h3>
              <ul className={s.items}>
                {b.menu.filter((i) => i.category === c).map((i) => (
                  <li key={i.name} className={`${s.item} ${i.available === false ? s.off : ""}`}>
                    <div>
                      <span className={s.itemName}>{i.name}</span>
                      {i.description && <p className={s.itemDesc}>{i.description}</p>}
                      {i.available === false && <span className={s.badge}>No disponible hoy</span>}
                    </div>
                    <span className={s.price}>{cop(i.price_cop)}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
          <p className={s.foot}>Precios en COP, informativos. Consulta ingredientes al personal.</p>
        </section>
      </div>
      <footer className={s.support}><SupportContact /></footer>
    </div>
  );
}
