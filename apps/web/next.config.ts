import type { NextConfig } from "next";

// El navegador siempre habla con este origen; Next reenvía /api al backend Django (cookies de sesión del mismo origen).
const API_URL = process.env.API_URL ?? "http://localhost:8000";

const config: NextConfig = {
  output: "standalone",
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API_URL}/api/:path*` }];
  },
};

export default config;
