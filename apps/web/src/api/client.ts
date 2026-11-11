import createClient, { type Middleware } from "openapi-fetch";
import type { components, paths } from "./schema";

export type Schemas = components["schemas"];

const cookie = (name: string) =>
  document.cookie.split("; ").find((c) => c.startsWith(`${name}=`))?.split("=")[1];

// Django exige X-CSRFToken en escrituras autenticadas con sesión.
const csrf: Middleware = {
  async onRequest({ request }) {
    if (!["GET", "HEAD"].includes(request.method)) {
      if (!cookie("csrftoken")) await fetch("/api/v1/auth/csrf");
      const token = cookie("csrftoken");
      if (token) request.headers.set("X-CSRFToken", token);
    }
    return request;
  },
};

/** Cliente del navegador (mismo origen). Solo importar desde Client Components. */
export const api = createClient<paths>({ baseUrl: "", credentials: "include" });
api.use(csrf);

/** Mensaje legible a partir del cuerpo de error de la API. */
export const errorMessage = (error: unknown, fallback = "Ocurrió un error. Intenta de nuevo.") =>
  (error as { detail?: string } | undefined)?.detail ?? fallback;
