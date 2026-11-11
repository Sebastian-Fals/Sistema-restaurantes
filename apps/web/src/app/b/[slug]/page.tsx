import { notFound } from "next/navigation";
import { serverApi } from "@/api/server";
import { cop } from "@/api/format";
import { ActivateButton } from "./activate-button";

export default async function BusinessPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const { data: b, response } = await serverApi.GET("/api/v1/public/b/{slug}", { params: { path: { slug } } });
  if (response.status === 404) notFound();
  if (!b) throw new Error("No se pudo cargar el negocio");

  const categories = [...new Set(b.menu.map((i) => i.category))];
  return (
    <>
      <h1>{b.name}</h1>
      <p className="muted">{[b.description, b.address].filter(Boolean).join(" · ")}</p>

      {b.program && (
        <section className="card" aria-labelledby="programa">
          <h2 id="programa">Programa de sellos</h2>
          <p>
            Acumula {b.program.stamps_required} sellos y recibe: <strong>{b.program.reward_name}</strong>. Cada compra pagada de{" "}
            {cop(b.program.min_purchase_cop)} o más suma un sello. La recompensa vale {b.program.reward_valid_days} días.
          </p>
          {b.program.conditions && <p className="muted">{b.program.conditions}</p>}
          <ActivateButton slug={b.slug} />
        </section>
      )}

      <section aria-labelledby="menu">
        <h2 id="menu">Menú</h2>
        {b.menu.length === 0 && <p className="muted">Aún no hay productos publicados.</p>}
        {categories.map((c) => (
          <div className="card" key={c}>
            <h3>{c}</h3>
            <table>
              <tbody>
                {b.menu.filter((i) => i.category === c).map((i) => (
                  <tr key={i.name}>
                    <td>
                      {i.name}
                      {i.description && <div className="muted">{i.description}</div>}
                      {!i.available && <div className="muted">No disponible hoy</div>}
                    </td>
                    <td style={{ textAlign: "right" }}>{cop(i.price_cop)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
        <p className="muted">Precios informativos. Este negocio participa en un piloto de software.</p>
      </section>
    </>
  );
}
