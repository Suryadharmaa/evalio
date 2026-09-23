import { expect, test } from "@playwright/test";

test("anonymous user receives transparent writing-pattern evidence", async ({ page }) => {
  await page.goto("/tools/writing-pattern-checker");
  await expect(page.getByRole("heading", { name: "Writing Pattern Checker." })).toBeVisible();
  await expect(page.getByText("This tool identifies measurable writing patterns. It cannot determine who or what wrote a text.").first()).toBeVisible();
  await page.getByLabel("Writing sample").fill("I learned through measured practice. ".repeat(24));
  await page.getByRole("button", { name: "Check patterns" }).click();
  await expect(page.getByText("Writing Pattern Risk")).toBeVisible();
  await expect(page.getByText("WP-004")).toBeVisible();
  const repeatedSignal = page.locator("details").filter({ hasText: "WP-004" });
  await repeatedSignal.locator("summary").click();
  await expect(repeatedSignal.getByText(/i learned through/i)).toBeVisible();
});

test("writing pattern checker has no overflow at 360px", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto("/tools/writing-pattern-checker");
  await expect(page.getByLabel("Writing sample")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth)).toBe(false);
});
