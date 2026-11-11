"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { api, errorMessage } from "@/api/client";

export function ActivateButton({ slug }: { slug: string }) {
  const router = useRouter();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function activate() {
    setBusy(true);
    setError("");
    const { response, error } = await api.POST("/api/v1/b/{slug}/card", { params: { path: { slug } } });
    setBusy(false);
    if (response.status === 401 || response.status === 403) return router.push(`/acceso?next=/b/${slug}`);
    if (error) return setError(errorMessage(error));
    router.push("/mis-tarjetas");
  }

  return (
    <>
      <button onClick={activate} disabled={busy}>
        {busy ? "Activando…" : "Activar mi tarjeta"}
      </button>
      {error && <p role="alert" className="status error">{error}</p>}
    </>
  );
}
