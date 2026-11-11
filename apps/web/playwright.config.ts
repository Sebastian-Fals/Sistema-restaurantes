import { defineConfig } from "@playwright/test";
import { tmpdir } from "node:os";
import path from "node:path";

// Both servers are dedicated to these tests; never reuse an operator's database.
process.env.MESA_E2E_LOG ??= path.join(tmpdir(), `mesa-e2e-${process.pid}.log`);

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  timeout: 90_000,
  expect: { timeout: 10_000 },
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:3011",
    channel: process.env.PLAYWRIGHT_CHROMIUM_CHANNEL || "chrome",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    launchOptions: { args: ["--no-sandbox"] },
  },
  webServer: [
    {
      command: "../api/.venv/bin/python e2e/serve_api.py",
      url: "http://127.0.0.1:8011/api/v1/public/b/cafe-olivo",
      reuseExistingServer: false,
      timeout: 60_000,
    },
    {
      command: "pnpm exec next dev --hostname 127.0.0.1 --port 3011",
      url: "http://127.0.0.1:3011",
      env: { API_URL: "http://127.0.0.1:8011", MESA_E2E: "1", NEXT_TELEMETRY_DISABLED: "1" },
      reuseExistingServer: false,
      timeout: 120_000,
    },
  ],
});
