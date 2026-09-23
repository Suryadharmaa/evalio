import { expect, test } from "@playwright/test";

// Synthetic test fixture only; production components always request the API.
const college = { id: "test-college", slug: "example-college", name: "Example College", country_code: "US", state_region: "MA", city: "Example City", institution_type: "PRIVATE_NONPROFIT", identity_confidence: "HIGH", application_platform_primary: "COMMON_APP", application_platforms: ["COMMON_APP"], official_website: null, test_policy: "OPTIONAL", need_policy: "UNKNOWN", primary_media: null };

test.beforeEach(async ({ page }) => {
  await page.route("**/api/v1/colleges**", async (route) => {
    if (new URL(route.request().url()).pathname.endsWith("/example-college")) return route.fulfill({ json: { data: { ...college, common_app_member: false, admissions: null, financial_aid: null, requirements: [], sources: [], media: [] } } });
    return route.fulfill({ json: { data: [college, { ...college, id: "test-second", slug: "second-example", name: "Second Example College" }, { ...college, id: "test-third", slug: "third-example", name: "Third Example College" }], meta: { page: 1, page_size: 12, total: 3 } } });
  });
});

for (const width of [360, 390, 768, 1024, 1440]) {
  test(`redesigned surfaces fit ${width}px and have no browser exceptions`, async ({ page }, testInfo) => {
    test.setTimeout(120000);
    await page.setViewportSize({ width, height: 900 });
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("console", (message) => {
      const text = message.text();
      // Next's development runtime injects transient style attributes that the
      // production nonce CSP intentionally blocks. Application source has no
      // inline style attributes; retain every other warning/error here.
      if ((message.type() === "error" || message.type() === "warning") && !text.includes("Applying inline style violates")) errors.push(text);
    });
    for (const route of ["/", "/colleges", "/colleges/example-college", "/tools/essay-evaluator", "/tools/writing-pattern-checker", "/tools/application-evaluator", "/tools/gpa", "/tools/coursework-evaluator", "/tools/lor-builder", "/tools/lor-evaluator", "/tools/scholarships", "/dashboard"]) {
      await page.goto(route);
      await expect(page.locator("main")).toBeVisible();
      if (route === "/") await expect(page.getByRole("link", { name: "Explore Example College", exact: true })).toBeVisible();
      expect(await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth), route).toBeLessThanOrEqual(1);
      if (route === "/" || (width === 1440 && route === "/tools/essay-evaluator") || (width === 390 && route === "/colleges/example-college")) await page.screenshot({ path: testInfo.outputPath(`${route === "/" ? "home" : "product"}-${width}.png`), fullPage: true, caret: "initial" });
      if (route === "/") await page.screenshot({ path: testInfo.outputPath(`hero-${width}.png`), caret: "initial" });
    }
    expect(errors).toEqual([]);
  });
}

test("hero evidence, mobile disclosures, focus and reduced motion work", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  const evidence = page.getByRole("button", { name: "View evidence", exact: true });
  await evidence.focus();
  await expect(evidence).toHaveCSS("outline-style", "solid");
  await page.keyboard.press("Enter");
  await expect(page.getByRole("button", { name: "Hide evidence", exact: true })).toHaveAttribute("aria-expanded", "true");
  await expect(page.getByText("ACAD-003", { exact: true }).first()).toBeVisible();
  const menu = page.getByLabel("Open navigation menu");
  await menu.click();
  await page.getByRole("navigation", { name: "Mobile navigation" }).getByText("Essays", { exact: true }).click();
  await expect(page.getByRole("navigation", { name: "Mobile navigation" }).getByRole("link", { name: "Essay Evaluator", exact: true })).toBeVisible();
  await menu.focus(); await page.keyboard.press("Escape");
  await expect(menu.locator("..")).not.toHaveAttribute("open");
  const duration = await page.locator("main").evaluate((element) => getComputedStyle(element).animationDuration);
  expect(["1e-05s", "0.00001s", "0.01ms"]).toContain(duration);
});

test("every primary CTA retains white text in pointer and keyboard states", async ({ page }) => {
  await page.goto("/");
  const primary = page.locator('a[data-variant="primary"]').first();
  await expect(primary).toHaveCSS("color", "rgb(255, 255, 255)");
  await primary.hover(); await expect(primary).toHaveCSS("color", "rgb(255, 255, 255)");
  await primary.focus(); await expect(primary).toHaveCSS("color", "rgb(255, 255, 255)");
  await page.goto("/tools/essay-evaluator");
  const disabled = page.getByRole("button", { name: "Analyze essay", exact: true });
  await expect(disabled).toBeDisabled(); await expect(disabled).toHaveCSS("color", "rgb(255, 255, 255)");
});
