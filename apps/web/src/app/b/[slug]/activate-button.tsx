"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { api, errorMessage } from "@/api/client";

export function ActivateButton({ slug, className }: { slug: string; className?: string }) {
  const router = useRouter();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function activate() {
    setBusy(true);
    setError("");
    let res;
    try {
      res = await api.POST("/api/v1/b/{slug}/card", { params: { path: { slug } } });
    } catch {
      setBusy(false);
      return setError("No pudimos conectar. Revisa tu conexión e intenta de nuevo.");
    }
    setBusy(false);
    const { response, error } = res;
    if (response.status === 401 || response.status === 403) return router.push(`/acceso?next=${encodeURIComponent(`/b/${slug}`)}`);
    if (error) return setError(errorMessage(error));
    router.push("/mis-tarjetas");
  }

  return (
    <>
      <button className={className} onClick={activate} disabled={busy} aria-busy={busy}>
        {busy ? "Activando…" : "Guardar mi tarjeta"}
      </button>
      {error && <p role="alert" className="status error">{error}</p>}
    </>
  );
}
