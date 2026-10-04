import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/pages",
  fullyParallel: true,
  use: { baseURL: "http://127.0.0.1:4173", trace: "retain-on-failure" },
  webServer: { command: "npm run preview:pages", url: "http://127.0.0.1:4173", reuseExistingServer: false },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
