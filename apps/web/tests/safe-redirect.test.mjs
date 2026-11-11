import assert from "node:assert/strict";
import test from "node:test";
import { safeRedirectPath } from "../src/features/auth/safe-redirect.ts";

const origin = "https://mesa.example";

test("keeps legitimate local paths, queries and fragments", () => {
  for (const path of ["/", "/mis-tarjetas", "/b/cafe-olivo", "/app/cafe-olivo/actividad?start=2026-11-01#detalle", "/buscar?q=caf%C3%A9", "/buscar?q=100%25"]) {
    assert.equal(safeRedirectPath(path, origin), path);
  }
  assert.equal(safeRedirectPath("/cuenta/../mis-tarjetas", origin), "/mis-tarjetas");
});

test("rejects external URLs, schemes, protocol-relative paths and backslashes", () => {
  for (const path of ["https://attacker.example", "https://mesa.example/cuenta", "javascript:alert(1)", "data:text/html,test", "//attacker.example", "/\\attacker.example", "\\\\attacker.example", "/%5cattacker.example", "/%255cattacker.example", "/%2fattacker.example", "/%252fattacker.example", "/cuenta/..//attacker.example"]) {
    assert.equal(safeRedirectPath(path, origin), null, JSON.stringify(path));
  }
});

test("rejects raw and encoded URL-normalized control characters", () => {
  for (const control of ["\t", "\n", "\r", "\u0000", "\u001f", "\u007f"]) {
    const encoded = encodeURIComponent(control);
    for (const path of [`/${control}/attacker.example`, `/${encoded}/attacker.example`, `/${encodeURIComponent(encoded)}/attacker.example`, `/mis-tarjetas?value=${encoded}`]) {
      assert.equal(safeRedirectPath(path, origin), null, JSON.stringify(path));
    }
  }
});

test("checks values after the outer next parameter is decoded", () => {
  for (const search of ["next=%2F%09%2Fattacker.example", "next=%2F%0A%2Fattacker.example", "next=%2F%250D%2Fattacker.example"]) {
    assert.equal(safeRedirectPath(new URLSearchParams(search).get("next"), origin), null);
  }
  assert.equal(safeRedirectPath(new URLSearchParams("next=%2Fapp%2Fcafe-olivo").get("next"), origin), "/app/cafe-olivo");
});

test("malformed percent escapes cannot hide encoded controls", () => {
  for (const path of ["/%09/attacker.example?x=%ZZ", "/%2509/attacker.example?x=%ZZ", "/%ZZ%0a/attacker.example"]) {
    assert.equal(safeRedirectPath(path, origin), null, path);
  }
});

test("fails closed on absent paths, invalid origin or excessive decoding", () => {
  for (const path of [null, "", "cuenta", "/%2525252525252525252509/attacker.example"]) {
    assert.equal(safeRedirectPath(path, origin), null);
  }
  assert.equal(safeRedirectPath("/cuenta", "not an origin"), null);
  assert.equal(safeRedirectPath("/cuenta", "javascript:alert(1)"), null);
});
