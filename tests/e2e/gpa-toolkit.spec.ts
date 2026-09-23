import { expect, test } from "@playwright/test";

test("calculates an explicitly weighted US GPA", async ({ page }) => {
  await page.goto("/tools/gpa");
  await expect(page.getByRole("heading", { name: "GPA Toolkit." })).toBeVisible();
  await page.getByLabel("Weighting method").selectOption("HONORS_0_5_ADVANCED_1_0");
  await page.getByLabel("Course", { exact: true }).fill("Calculus");
  await page.getByLabel("Course level").selectOption("AP");
  await page.getByRole("button", { name: /calculate/i }).click();
  await expect(page.getByText("5.000")).toBeVisible();
  await page.getByText("Exact formula", { exact: true }).click();
  await expect(page.getByText(/selected course-level offset/i)).toBeVisible();
});

test("preserves international results on the original scale at 360px", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto("/tools/gpa");
  await page.getByRole("tab", { name: "International", exact: true }).click();
  await page.getByLabel("Curriculum").fill("National curriculum");
  await page.getByLabel("Label").fill("Term 1");
  await page.getByRole("button", { name: /calculate/i }).click();
  await expect(page.getByText(/Conversion not applied/i)).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth)).toBe(false);
});
