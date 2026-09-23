import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL(".", import.meta.url)),
    },
  },
  test: {
    environment: "jsdom",
    exclude: ["tests/e2e/**", "node_modules/**", "node_modules.failed-*/**"],
    include: ["tests/frontend/**/*.test.{ts,tsx}"],
    setupFiles: ["./tests/frontend/setup.ts"],
  },
});
