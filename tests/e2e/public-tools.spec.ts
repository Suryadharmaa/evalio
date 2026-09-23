import { expect, test } from "@playwright/test";

test("anonymous essay review validates draft length", async ({ page }) => {
  await page.goto("/essay");
  await page.getByLabel("Essay text").fill("I built a solar cart for 12 students. After three failed tests, I learned why measured iteration matters. I revised the wheel mount and documented the result.");
  await page.getByRole("button", { name: "Analyze essay" }).click();
  await expect(page.getByText("Essay must contain between 50 and 5,000 words.")).toBeVisible();
});

test("legacy essay URL redirects to the current evaluator", async ({ page }) => {
  await page.goto("/essay");
  await expect(page).toHaveURL(/\/tools\/essay-evaluator$/);
  await expect(page.getByRole("heading", { name: "College Essay Evaluator." })).toBeVisible();
});

test("activity analyzer returns component feedback", async ({ page }) => {
  await page.goto("/activity-analyzer");
  await page.getByLabel("Description").fill("Led 12 students through weekly workshops");
  await page.getByRole("button", { name: "Analyze description" }).click();
  await expect(page.getByText("Description score")).toBeVisible();
  await expect(page.getByText("Confidence: HIGH")).toBeVisible();
});

for (const viewport of [
  { width: 360, height: 800 },
  { width: 390, height: 844 },
  { width: 768, height: 1024 },
  { width: 1024, height: 768 },
  { width: 1440, height: 900 },
]) {
  test(`homepage has no horizontal overflow at ${viewport.width}x${viewport.height}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto("/");
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
    expect(overflow).toBe(false);
  });
}
