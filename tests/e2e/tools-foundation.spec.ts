import { expect, test } from "@playwright/test";

test("tools directory and planned tool route are reachable", async ({ page }) => {
  await page.goto("/tools");
  await expect(page.getByRole("heading", { name: "Tools for a clearer application." })).toBeVisible();
  await expect(page.getByRole("link", { name: /Essay Evaluator/ }).first()).toBeVisible();

  await page.goto("/tools/essay-evaluator");
  await expect(page.getByRole("heading", { name: "College Essay Evaluator." })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Your feedback will appear here." })).toBeVisible();
});

for (const width of [360, 768, 1440]) {
  test(`tools directory has no horizontal overflow at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/tools");
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
    expect(overflow).toBe(false);
  });
}
