import { createHash } from "node:crypto";
import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { resolve, join, relative, sep } from "node:path";
import { spawnSync } from "node:child_process";

const require = createRequire(import.meta.url);
require("@next/env").loadEnvConfig(process.cwd(), false);
const result = spawnSync(process.execPath, [require.resolve("next/dist/bin/next"), "build"], {
  stdio: "inherit",
  env: { ...process.env, EVALIO_STATIC_EXPORT: "1" },
});
if (result.error) throw result.error;
if (result.status !== 0) process.exit(result.status ?? 1);

// GitHub Pages cannot send custom HTTP headers. Hash the exported inline scripts
// and styles and apply a CSP meta policy to each generated HTML document.
const apiOrigin = new URL(process.env.NEXT_PUBLIC_API_ORIGIN).origin;
const authOrigin = new URL(process.env.NEXT_PUBLIC_SUPABASE_URL).origin;
const authSocketOrigin = authOrigin.replace(/^https:/, "wss:");
const output = resolve("out");
const hash = (value) => `'sha256-${createHash("sha256").update(value).digest("base64")}'`;
function files(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => entry.isDirectory() ? files(join(directory, entry.name)) : [join(directory, entry.name)]);
}
const exportedFiles = files(output);
// Next's Windows export can emit segment payloads in nested directories while
// the browser requests flattened names. Publish aliases; no server rewrite needed.
for (const path of exportedFiles) {
  if (!path.endsWith(".txt")) continue;
  const parts = relative(output, path).split(sep);
  const segment = parts.findIndex((part) => part.startsWith("__next."));
  if (segment >= 0 && segment < parts.length - 1) {
    writeFileSync(join(output, ...parts.slice(0, segment), parts.slice(segment).join(".")), readFileSync(path));
  }
}
const attributes = new Set();
for (const path of exportedFiles.filter((path) => path.endsWith(".html"))) {
  for (const match of readFileSync(path, "utf8").matchAll(/\bstyle="([^"]*)"/g)) {
    attributes.add(hash(match[1].replace(/&quot;/g, '"').replace(/&#x27;/g, "'").replace(/&amp;/g, "&")));
  }
}
function finalize(directory) {
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) { finalize(path); continue; }
    if (!entry.name.endsWith(".html")) continue;
    const html = readFileSync(path, "utf8");
    const scripts = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].filter((match) => match[1]).map((match) => hash(match[1]));
    const styles = [...html.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/gi)].map((match) => hash(match[1]));
    const policy = [
      "default-src 'self'",
      `script-src 'self' ${[...new Set(scripts)].join(" ")}`,
      `style-src 'self' ${[...new Set(styles)].join(" ")}`,
      `style-src-attr 'unsafe-hashes' ${[...attributes].join(" ")}`,
      "img-src 'self' data: blob: https://commons.wikimedia.org https://upload.wikimedia.org",
      `connect-src 'self' ${apiOrigin} ${authOrigin} ${authSocketOrigin}`,
      "font-src 'self'", "object-src 'none'", "base-uri 'self'", "form-action 'self'",
      "upgrade-insecure-requests",
    ].join("; ");
    writeFileSync(path, html.replace("<head>", `<head><meta http-equiv="Content-Security-Policy" content="${policy}">`));
  }
}
finalize(output);
writeFileSync(join(output, ".nojekyll"), "");
writeFileSync(join(output, "evalio-pages.json"), JSON.stringify({ basePath: process.env.NEXT_PUBLIC_BASE_PATH ?? "", apiOrigin }));
console.log("GitHub Pages export ready in out/ (including script hashes and .nojekyll).");
