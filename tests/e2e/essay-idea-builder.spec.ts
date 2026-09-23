import { expect, test } from "@playwright/test";

test("anonymous user builds grounded essay directions", async ({ page }) => {
  await page.goto("/tools/essay-idea-builder");
  await expect(page.getByRole("heading", { name: "Essay Idea Builder." })).toBeVisible();
  await page.getByLabel("Specific moments").fill("The 3 AM server outage\nThe failed field test\nThe team meeting");
  await page.getByLabel("Challenges or tensions").fill("Responsibility versus being unprepared");
  await page.getByLabel("Responsibility").check();
  await page.getByLabel("Lessons or changes").fill("I learned to test assumptions before scaling");
  await page.getByRole("button", { name: "Build idea directions" }).click();

  await expect(page.getByRole("heading", { name: "3 grounded directions" })).toBeVisible();
  await expect(page.getByText("The 3 AM server outage").first()).toBeVisible();
  await expect(page.getByText("Responsibility versus being unprepared").first()).toBeVisible();
  await expect(page.getByText("Questions to explore").first()).toBeVisible();
});

test("essay idea builder has no overflow at 360px", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto("/tools/essay-idea-builder");
  await expect(page.getByLabel("Specific moments")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth)).toBe(false);
});
