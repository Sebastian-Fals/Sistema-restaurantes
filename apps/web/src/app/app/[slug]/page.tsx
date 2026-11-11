"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/api/client";
import { Admin } from "./admin";
import { Staff } from "./staff";

export default function BusinessApp() {
  const { slug } = useParams<{ slug: string }>();
  const router = useRouter();
  const [role, setRole] = useState<string | null>(null);

  useEffect(() => {
    api.GET("/api/v1/me").then(({ data, response }) => {
      if (!data || response.status === 401 || response.status === 403) return router.push(`/acceso?next=/app/${slug}`);
      setRole(data.memberships.find((m) => m.business_slug === slug)?.role ?? "none");
    });
  }, [slug, router]);

  async function logout() {
    await api.POST("/api/v1/auth/logout");
    router.push("/acceso");
  }

  if (!role) return <p role="status">Cargando…</p>;
  if (role === "none") return <p role="alert" className="status error">No tienes permiso en este negocio.</p>;
  return (
    <>
      <h1>Operación · {slug}</h1>
      <Staff slug={slug} />
      {role === "admin" && <Admin slug={slug} />}
      <button className="secondary" onClick={logout}>Cerrar sesión</button>
    </>
  );
}
