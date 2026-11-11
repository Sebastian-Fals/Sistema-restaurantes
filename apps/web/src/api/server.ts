import createClient from "openapi-fetch";
import type { paths } from "./schema";

/** Cliente para Server Components: llama directo al backend. Solo endpoints públicos. */
export const serverApi = createClient<paths>({ baseUrl: process.env.API_URL ?? "http://localhost:8000", cache: "no-store" });
