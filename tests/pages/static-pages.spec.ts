import { readFileSync } from "node:fs";
import { expect, test } from "@playwright/test";

const { basePath, apiOrigin } = JSON.parse(readFileSync("out/evalio-pages.json", "utf8")) as { basePath: string; apiOrigin: string };
// Synthetic API data, never production records.
const college = { id: "test-id", slug: "example-college", name: "Example College", country_code: "US", state_region: "MA", city: "Example City", institution_type: "PRIVATE_NONPROFIT", identity_confidence: "HIGH", application_platform_primary: "COMMON_APP", application_platforms: ["COMMON_APP"], official_website: null, test_policy: "OPTIONAL", need_policy: "UNKNOWN", primary_media: null };

test.beforeEach(async ({ page }) => {
  await page.route("https://*.supabase.co/**", (route) => route.fulfill({ json: { error: "Synthetic preview" }, status: 401 }));
  await page.route(`${apiOrigin}/api/v1/**`, (route) => {
    const detail = new URL(route.request().url()).pathname.endsWith("/example-college");
    return route.fulfill({ headers: { "Access-Control-Allow-Origin": "*" }, json: detail
      ? { data: { ...college, common_app_member: false, admissions: null, financial_aid: null, requirements: [], sources: [], media: [] } }
      : { data: [college], meta: { total: 1, page: 1, page_size: 12 } } });
  });
});

test("exported Pages routes hydrate, call the external API and survive refresh", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
  await page.goto(`${basePath}/`);
  await expect(page.getByRole("link", { name: "Explore Example College", exact: true })).toBeVisible();
  const icon = page.locator('img[src*="evalio-icon"]').first();
  expect(await icon.getAttribute("src")).toBe(`${basePath}/evalio-icon.png`);
  await expect.poll(() => icon.evaluate((element) => (element as HTMLImageElement).naturalWidth)).toBeGreaterThan(0);
  await page.getByRole("link", { name: "Explore Example College", exact: true }).click();
  await expect(page).toHaveURL(new RegExp(`${basePath}/colleges/view/\\?slug=example-college`));
  await expect(page.getByRole("heading", { name: "Example College", exact: true })).toBeVisible();
  await page.reload();
  await expect(page.getByRole("heading", { name: "Example College", exact: true })).toBeVisible();
  await page.goto(`${basePath}/tools/gpa/`);
  await expect(page.getByRole("heading", { name: "GPA Toolkit.", exact: true })).toBeVisible();
  expect(errors).toEqual([]);
});

test("private routes redirect guests to static sign-in and preserve the return route", async ({ page }) => {
  let profileCalls = 0;
  page.on("request", (request) => { if (request.url().includes("/api/v1/profiles")) profileCalls++; });
  await page.goto(`${basePath}/reports/view/?id=test-report`);
  await expect(page).toHaveURL(new RegExp(`${basePath}/sign-in/\\?next=`));
  expect(new URL(page.url()).searchParams.get("next")).toBe("/reports/view/?id=test-report");
  await expect(page.getByRole("heading", { name: "Sign in to Evalio" })).toBeVisible();
  expect(profileCalls).toBe(0);
});

test("password login sends the session token to FastAPI and sign-out removes private access", async ({ page }) => {
  const expires = Math.floor(Date.now() / 1000) + 3600;
  const encode = (value: object) => Buffer.from(JSON.stringify(value)).toString("base64url");
  const token = `${encode({ alg: "HS256", typ: "JWT" })}.${encode({ sub: "test-user", exp: expires, role: "authenticated" })}.test-signature`;
  await page.route("https://*.supabase.co/auth/v1/token**", (route) => route.fulfill({
    headers: { "Access-Control-Allow-Origin": "*" },
    json: { access_token: token, refresh_token: "test-refresh", token_type: "bearer", expires_in: 3600, expires_at: expires, user: { id: "test-user", email: "test@example.com", aud: "authenticated", app_metadata: {}, user_metadata: {} } },
  }));
  await page.route("https://*.supabase.co/auth/v1/logout**", (route) => route.fulfill({ status: 204, headers: { "Access-Control-Allow-Origin": "*" } }));
  const tokens: string[] = [];
  await page.route(`${apiOrigin}/api/v1/profiles`, (route) => {
    tokens.push(route.request().headers().authorization);
    return route.fulfill({ headers: { "Access-Control-Allow-Origin": "*" }, json: { data: [] } });
  });
  await page.goto(`${basePath}/sign-in/?next=%2Fdashboard`);
  await page.getByLabel("Email address").fill("test@example.com");
  await page.getByLabel("Password (for password sign-in)").fill("synthetic-password");
  await page.getByRole("button", { name: "Sign in with password", exact: true }).click();
  await expect(page).toHaveURL(new RegExp(`${basePath}/dashboard/`));
  await expect.poll(() => tokens).toEqual([`Bearer ${token}`]);
  await page.getByLabel("Open account menu").click();
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(page).toHaveURL(`${basePath ? `http://127.0.0.1:4173${basePath}` : "http://127.0.0.1:4173"}/`);
  await page.goto(`${basePath}/dashboard/`);
  await expect(page).toHaveURL(new RegExp(`${basePath}/sign-in/\\?next=`));
  expect(tokens).toHaveLength(1);
});

test("magic links return to the deployed base path", async ({ page }) => {
  let redirect: string | null = null;
  await page.route("https://*.supabase.co/auth/v1/otp**", (route) => {
    redirect = new URL(route.request().url()).searchParams.get("redirect_to");
    return route.fulfill({ headers: { "Access-Control-Allow-Origin": "*" }, json: {} });
  });
  await page.goto(`${basePath}/sign-in/?next=%2Fprofile`);
  await page.getByLabel("Email address").fill("test@example.com");
  await page.getByRole("button", { name: "Send magic link", exact: true }).click();
  await expect(page.getByText("Check your email for a secure sign-in link.", { exact: true })).toBeVisible();
  expect(redirect).toBe(`http://127.0.0.1:4173${basePath}/profile`);
});
