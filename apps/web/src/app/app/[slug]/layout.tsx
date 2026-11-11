"use client";

import Link from "next/link";
import { useParams, usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/api/client";
import { type Panel, PanelContext } from "./context";
import s from "./panel.module.css";

const ROLE = { admin: "Administrador", staff: "Personal" } as const;

export default function BusinessLayout({ children }: { children: React.ReactNode }) {
  const { slug } = useParams<{ slug: string }>();
  const pathname = usePathname();
  const router = useRouter();
  const [panel, setPanel] = useState<Panel | "none" | null>(null);
  const [menu, setMenu] = useState(false);

  useEffect(() => {
    Promise.all([api.GET("/api/v1/me"), api.GET("/api/v1/public/b/{slug}", { params: { path: { slug } } })]).then(
      ([me, pub]) => {
        if (!me.data) return router.replace(`/acceso?next=${encodeURIComponent(window.location.pathname)}`);
        const role = me.data.memberships.find((m) => m.business_slug === slug)?.role;
        setPanel(role ? { slug, role, business: pub.data ?? null } : "none");
      },
    );
  }, [slug, router]);

  async function logout() {
    await api.POST("/api/v1/auth/logout");
    router.push("/acceso");
  }

  if (!panel) return <p role="status">Cargando…</p>;
  if (panel === "none") return <p role="alert" className="status error">No tienes permiso en este negocio.</p>;

  const base = `/app/${slug}`;
  const nav = [
    { href: base, label: "Resumen", admin: true },
    { href: `${base}/compras`, label: "Compras y canjes", admin: false },
    { href: `${base}/actividad`, label: "Actividad", admin: true },
  ].filter((i) => !i.admin || panel.role === "admin");
  const name = panel.business?.name ?? slug;

  return (
    <div className={`wide ${s.shell}`}>
      <aside className={s.sidebar}>
        <div className={s.brandRow}>
          <span className={s.brand}>mesa</span>
          <button
            type="button"
            className={s.menuButton}
            aria-expanded={menu}
            aria-controls="panel-nav"
            onClick={() => setMenu(!menu)}
          >
            Menú
          </button>
        </div>
        <div id="panel-nav" className={s.navWrap} data-open={menu}>
          <p className={s.business}>
            <b>{name}</b>
            <span>{ROLE[panel.role]}</span>
          </p>
          <nav aria-label="Panel del negocio">
            {nav.map((i) => (
              <Link
                key={i.href}
                href={i.href}
                className={s.navLink}
                aria-current={pathname === i.href ? "page" : undefined}
                onClick={() => setMenu(false)}
              >
                {i.label}
              </Link>
            ))}
          </nav>
          <button type="button" className={s.logout} onClick={logout}>Cerrar sesión</button>
        </div>
      </aside>
      <div className={s.main}>
        <header className={s.header}>{name}</header>
        <div className={s.content}>
          <PanelContext.Provider value={panel}>{children}</PanelContext.Provider>
        </div>
      </div>
    </div>
  );
}
