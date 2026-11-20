import { expect, test } from "@playwright/test";

test("loads the Evalio foundation with a fresh nonce CSP", async ({ page }) => {
  const response = await page.goto("/");

  await expect(
    page.getByRole("heading", {
      name: "Know where your application stands.",
    }),
  ).toBeVisible();
  const csp = response?.headers()["content-security-policy"] ?? "";
  expect(csp).toContain("'strict-dynamic'");
  const scripts = csp.split(";").find((directive) => directive.trim().startsWith("script-src ")) ?? "";
  expect(scripts).not.toContain("'unsafe-inline'");
  const firstNonce = scripts.match(/'nonce-([^']+)'/)?.[1];
  expect(firstNonce).toBeTruthy();

  // A CSP nonce must not be static across responses.
  const anotherResponse = await page.request.get("/");
  const anotherCsp = anotherResponse.headers()["content-security-policy"] ?? "";
  const secondNonce = anotherCsp.match(/'nonce-([^']+)'/)?.[1];
  expect(secondNonce).toBeTruthy();
  expect(secondNonce).not.toBe(firstNonce);
});
