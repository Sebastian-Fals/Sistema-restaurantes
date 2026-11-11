import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";

async function login(page: Page, email: string) {
  await page.goto("/acceso");
  await page.getByLabel("Correo electrónico", { exact: true }).fill(email);
  await page.getByRole("button", { name: "Enviar código", exact: true }).click();
  let code = "";
  await expect.poll(() => {
    const rows = readFileSync(process.env.MESA_E2E_LOG!, "utf8").split("\n");
    code = rows.filter((row) => row.includes(`Código de acceso para ${email}:`)).at(-1)?.match(/: (\d{6})$/)?.[1] ?? "";
    return code;
  }).toMatch(/^\d{6}$/);
  await page.getByLabel("Código de acceso", { exact: true }).fill(code);
  await page.getByRole("button", { name: "Verificar y entrar", exact: true }).click();
  await expect(page).not.toHaveURL(/\/acceso/);
}

async function lookup(page: Page, email: string) {
  await page.getByLabel("Código o correo del cliente").fill(email);
  await page.getByRole("button", { name: "Buscar cliente", exact: true }).click();
  await expect(page.getByText("cliente verificado", { exact: false })).toBeVisible();
}

async function purchase(page: Page, reference: string) {
  await page.getByLabel("Comprobante de compra", { exact: true }).fill(reference);
  await page.getByLabel("Total pagado (COP)", { exact: true }).fill("15000");
  await page.getByLabel("Confirmo que la compra fue pagada y no está anulada.").check();
  await page.getByRole("button", { name: "Validar y sumar 1 sello", exact: true }).click();
  await expect(page.getByText("Compra registrada", { exact: true })).toBeVisible();
  await expect(page.getByLabel("Comprobante de compra", { exact: true })).toHaveValue("");
}

test("public rules and menu remain usable from 320px to desktop", async ({ page }) => {
  for (const width of [320, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/b/cafe-olivo");
    await expect(page.getByRole("heading", { name: "Café Olivo", exact: true }).first()).toBeVisible();
    await expect(page.getByText("Una compra pagada", { exact: false })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
  }
  await page.goto("/b/cafe-olivo");
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Ir al contenido", exact: true })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main-content")).toBeFocused();
});

test("customer, staff and administrator complete the six loyalty flows", async ({ browser }) => {
  const customerContext = await browser.newContext({ viewport: { width: 320, height: 900 } });
  const staffContext = await browser.newContext({ viewport: { width: 768, height: 1024 } });
  const adminContext = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const customer = await customerContext.newPage();
  const staff = await staffContext.newPage();
  const admin = await adminContext.newPage();
  const email = "acceptance-customer@example.test";
  try {
    await login(customer, email);
    await customer.goto("/b/cafe-olivo");
    await customer.getByRole("button", { name: "Guardar mi tarjeta" }).click();
    await expect(customer).toHaveURL(/\/mis-tarjetas/);
    await customer.goto("/mis-tarjetas/cafe-olivo");
    await expect(customer.getByText("0 de 3 sellos", { exact: true })).toBeVisible();
    await login(staff, "barista@cafe-olivo.test");
    await expect(staff).toHaveURL(/\/compras/);
    await lookup(staff, email);
    for (const reference of ["ACCEPT-1", "ACCEPT-2", "ACCEPT-3"]) await purchase(staff, reference);
    await customer.reload();
    await expect(customer.getByText("Recompensa disponible", { exact: true })).toBeVisible();
    await staff.getByRole("button", { name: "Canjear", exact: true }).click();
    await expect(staff.getByRole("dialog")).toBeVisible();
    await staff.keyboard.press("Escape");
    await expect(staff.getByRole("button", { name: "Canjear", exact: true })).toBeFocused();
    await staff.getByRole("button", { name: "Canjear", exact: true }).click();
    await staff.getByRole("button", { name: "Confirmar canje", exact: true }).click();
    await expect(staff.getByText("Canje confirmado", { exact: true })).toBeVisible();
    await expect(staff.getByRole("button", { name: "Canjear", exact: true })).toHaveCount(0);
    await purchase(staff, "ACCEPT-4");
    await login(admin, "admin@cafe-olivo.test");
    await expect(admin.getByText("Recompensas disponibles", { exact: true })).toBeVisible();
    const periodRequest = admin.waitForRequest((r) => r.url().includes("/summary?") && r.url().includes("start=2020-01-01"));
    await admin.getByLabel("Desde", { exact: true }).fill("2020-01-01");
    await periodRequest;
    await admin.goto("/app/cafe-olivo/actividad");
    await admin.getByLabel("Tipo", { exact: true }).selectOption("purchase");
    const old = admin.locator("tbody tr").last();
    await old.getByRole("button", { name: "Ver detalle" }).click();
    await admin.getByLabel("Motivo obligatorio").fill("Compra antigua ya recompensada");
    await admin.getByRole("button", { name: "Confirmar reverso", exact: true }).click();
    await expect(admin.getByText("Escalar a soporte", { exact: true })).toBeVisible();
    await admin.getByRole("button", { name: "Volver al historial", exact: true }).click();
    await admin.locator("tbody tr").first().getByRole("button", { name: "Ver detalle" }).click();
    await admin.getByLabel("Motivo obligatorio").fill("Comprobante registrado por error");
    await admin.getByRole("button", { name: "Confirmar reverso", exact: true }).click();
    await expect(admin.getByText("Reverso registrado", { exact: true })).toBeVisible();
    await customer.reload();
    await expect(customer.getByText("0 de 3 sellos", { exact: true })).toBeVisible();
    expect(await customer.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
    await customer.goto("/cuenta");
    await customer.getByRole("switch").click();
    await expect(customer.getByRole("switch")).toBeChecked();
    await expect(customer.getByRole("status")).toContainText("Recibirás promociones");
    await customer.getByRole("switch").click();
    await expect(customer.getByRole("switch")).not.toBeChecked();
    await expect(customer.getByRole("status")).toContainText("Ya no recibirás");
    await customer.getByRole("link", { name: "Revisar eliminación" }).click();
    await customer.getByLabel("Escribe ELIMINAR para confirmar").fill("ELIMINAR");
    await customer.getByRole("button", { name: "Eliminar definitivamente" }).click();
    await expect(customer).toHaveURL("/");
  } finally {
    await customerContext.close();
    await staffContext.close();
    await adminContext.close();
  }
});

test("ambiguous network responses preserve purchases and recover without duplicates", async ({ page }) => {
  await login(page, "offline-admin@cafe-olivo.test");
  await page.route("**/api/v1/b/cafe-olivo/summary?*", (route) => route.abort());
  await page.reload();
  await expect(page.getByText("No se pudo cargar el resumen", { exact: true })).toBeVisible();
  await page.unroute("**/api/v1/b/cafe-olivo/summary?*");
  await page.getByRole("button", { name: "Reintentar", exact: true }).click();
  await expect(page.getByText("Compras registradas", { exact: true })).toBeVisible();
  await page.goto("/app/cafe-olivo/compras");
  // Staff accounts are also users and can receive a card in this isolated database.
  await lookup(page, "barista@cafe-olivo.test");
  await page.getByLabel("Comprobante de compra", { exact: true }).fill("LOST-RESPONSE");
  await page.getByLabel("Total pagado (COP)", { exact: true }).fill("15000");
  await page.getByLabel("Confirmo que la compra fue pagada y no está anulada.").check();
  await page.route("**/api/v1/b/cafe-olivo/purchases", async (route) => {
    await route.fetch(); // Server commits successfully, but its reply is lost.
    await route.abort();
  });
  await page.getByRole("button", { name: "Validar y sumar 1 sello", exact: true }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.getByLabel("Comprobante de compra", { exact: true })).toHaveValue("LOST-RESPONSE");
  await expect(page.getByRole("button", { name: "Validar y sumar 1 sello", exact: true })).toBeEnabled();
  await page.unroute("**/api/v1/b/cafe-olivo/purchases");
  await page.getByRole("button", { name: "Validar y sumar 1 sello", exact: true }).click();
  await expect(page.getByText("Compra ya registrada", { exact: true })).toBeVisible();
  const response = await page.request.get("/api/v1/b/cafe-olivo/customer?q=barista%40cafe-olivo.test");
  expect((await response.json()).stamps).toBe(1);
  await purchase(page, "NETWORK-2");
  await purchase(page, "NETWORK-3");
  await page.getByRole("button", { name: "Canjear", exact: true }).click();
  await page.route("**/api/v1/b/cafe-olivo/rewards/*/redeem", async (route) => {
    await route.fetch();
    await route.abort();
  });
  await page.getByRole("button", { name: "Confirmar canje", exact: true }).click();
  await expect(page.getByText("No pudimos confirmar el canje", { exact: true })).toBeVisible();
  await expect(page.getByRole("dialog")).not.toBeVisible();
  await expect(page.getByRole("button", { name: "Canjear", exact: true })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Buscar cliente", exact: true })).toBeEnabled();
  await page.unroute("**/api/v1/b/cafe-olivo/rewards/*/redeem");
  for (const route of ["/app/cafe-olivo", "/app/cafe-olivo/compras", "/app/cafe-olivo/actividad"]) {
    await page.setViewportSize({ width: 320, height: 900 });
    await page.goto(route);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
  }
});
