import { expect, test } from "@playwright/test";

test("application evaluator exposes a transparent planning workflow", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto("/tools/application-evaluator");

  await expect(page.getByRole("heading", { level: 1, name: "Application Evaluator." })).toBeVisible();
  await expect(page.getByRole("heading", { name: /Fit without.*fake certainty/ })).toBeVisible();
  await expect(page.getByText(/No admission probability, guarantee, or safety classification/)).toBeVisible();

  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(1);
});
