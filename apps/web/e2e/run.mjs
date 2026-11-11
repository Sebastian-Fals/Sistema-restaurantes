// Next generates these files even with a separate distDir. Restore the developer's
// version when acceptance ends so test-only paths never leak into normal builds.
import { readFileSync, writeFileSync, existsSync, unlinkSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const files = ["next-env.d.ts", "tsconfig.json"];
const snapshots = files.map((name) => [name, existsSync(name) ? readFileSync(name) : null]);
let result;
try {
  result = spawnSync(process.execPath, [fileURLToPath(import.meta.resolve("@playwright/test/cli")), "test", ...process.argv.slice(2)], { stdio: "inherit" });
} finally {
  for (const [name, content] of snapshots) {
    if (content !== null) writeFileSync(name, content);
    else if (existsSync(name)) unlinkSync(name);
  }
}
if (result.error) throw result.error;
process.exitCode = result.status ?? 1;
