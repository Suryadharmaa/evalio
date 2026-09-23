import { expect, test } from "@playwright/test";

test("LOR builder is transparent and usable at 360px", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto("/tools/lor-builder");

  await expect(page.getByRole("heading", { level: 1, name: "LOR Builder." })).toBeVisible();
  await expect(page.getByText(/reviewed and owned by the recommender/i)).toBeVisible();
  await page.getByLabel("Recommender role").fill("Mathematics teacher");
  await page.getByLabel("Student name").fill("Jordan Lee");
  await page.getByLabel("Relationship context").fill("Advanced calculus class and math club");
  await page.getByLabel("Relationship duration").fill("Two academic years");
  await page.getByLabel("Observed qualities").fill("Analytical curiosity\nCollaborative leadership");
  await page.getByLabel("Specific examples").fill("Tested three modeling approaches\nLed weekly peer review");
  await page.getByRole("button", { name: /build letter framework/i }).click();
  await expect(page.getByRole("heading", { name: "Editable letter framework" })).toBeVisible();
  await expect(page.getByLabel("Opening — editable framework")).toHaveValue(/source: student_name/);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(1);
});
