import { expect, test } from "@playwright/test";

test("evaluates coursework without penalizing unavailable advanced courses", async ({ page }) => {
  await page.goto("/tools/coursework-evaluator");
  await expect(page.getByRole("heading", { name: "Coursework Evaluator." })).toBeVisible();
  await page.getByLabel("Curriculum type").fill("National curriculum");
  await page.getByLabel("Intended major", { exact: true }).fill("Economics");
  await page.getByLabel("Course name").fill("English Literature");
  await page.getByLabel("School context notes").fill("No advanced courses are offered by the school.");
  await page.getByRole("button", { name: /evaluate coursework/i }).click();
  await expect(page.getByText("No penalty applied")).toBeVisible();
  await expect(page.getByText("ACAD-005", { exact: true })).toBeVisible();
});

test("coursework evaluator has no overflow at 360px", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto("/tools/coursework-evaluator");
  await expect(page.getByLabel("Curriculum type")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth)).toBe(false);
});
