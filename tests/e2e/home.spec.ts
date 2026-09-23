import { expect, test } from "@playwright/test";

test("loads the Evalio foundation with a nonce CSP", async ({ page }) => {
  const response = await page.goto("/");

  await expect(
    page.getByRole("heading", {
      name: "Know where your application stands.",
    }),
  ).toBeVisible();
  const csp = response?.headers()["content-security-policy"] ?? "";
  expect(csp).toContain("'strict-dynamic'");
  expect(csp).toMatch(/'nonce-[^']+'/);
  expect(csp).not.toContain("'unsafe-inline'");
});
