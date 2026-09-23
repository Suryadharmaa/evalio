import { expect, test } from "@playwright/test";

test("primary and inverse actions preserve required contrast", async ({ page }) => {
  await page.goto("/");
  const primary = page.getByRole("link", { name: /evaluate my application/i }).first();
  await expect(primary).toHaveCSS("background-color", "rgb(103, 87, 245)");
  await expect(primary).toHaveCSS("color", "rgb(255, 255, 255)");

  const inverse = page.getByRole("link", { name: /explore colleges/i });
  await inverse.scrollIntoViewIfNeeded();
  await expect(inverse).toHaveCSS("background-color", "rgb(255, 255, 255)");
  await expect(inverse).toHaveCSS("color", "rgb(40, 25, 80)");
});

for (const route of ["/", "/tools", "/colleges", "/tools/gpa"]) {
  test(`${route} has no horizontal overflow at 360px`, async ({ page }) => {
    await page.setViewportSize({ width: 360, height: 800 });
    await page.goto(route);
    expect(await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth)).toBe(false);
  });
}

test("reduced-motion preference disables decorative entrance motion", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  const duration = await page.locator("main").evaluate((element) => getComputedStyle(element).animationDuration);
  expect(["0.01ms", "1e-05s"]).toContain(duration);
});

test("landing page remains usable at 320px", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 720 });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Know where your application stands." })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth)).toBe(false);
});
