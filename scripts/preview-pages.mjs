import { createServer } from "node:http";
import { readFileSync, statSync } from "node:fs";
import { resolve, join, extname, sep } from "node:path";

const output = resolve("out");
const { basePath } = JSON.parse(readFileSync(join(output, "evalio-pages.json"), "utf8"));
const mime = { ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8", ".json": "application/json", ".txt": "text/plain; charset=utf-8", ".png": "image/png", ".svg": "image/svg+xml", ".ico": "image/x-icon", ".webp": "image/webp", ".woff2": "font/woff2" };
const port = Number(process.env.PAGES_PREVIEW_PORT ?? 4173);
createServer((request, response) => {
  try {
    const pathname = decodeURIComponent(new URL(request.url, "http://localhost").pathname);
    if (basePath && (pathname === "/" || pathname === basePath)) {
      response.writeHead(302, { Location: `${basePath}/` }); response.end(); return;
    }
    if (basePath && !pathname.startsWith(`${basePath}/`)) { response.writeHead(404); response.end(); return; }
    const relative = pathname.slice(basePath.length).replace(/^\/+/, "");
    let target = resolve(output, relative);
    if (target !== output && !target.startsWith(output + sep)) { response.writeHead(403); response.end(); return; }
    if (statSync(target).isDirectory()) {
      if (!pathname.endsWith("/")) { response.writeHead(302, { Location: `${pathname}/${new URL(request.url, "http://localhost").search}` }); response.end(); return; }
      target = join(target, "index.html");
    }
    response.writeHead(200, { "Content-Type": mime[extname(target)] ?? "application/octet-stream", "Cache-Control": "no-store" });
    response.end(readFileSync(target));
  } catch {
    response.writeHead(404, { "Content-Type": "text/html; charset=utf-8" });
    response.end(readFileSync(join(output, "404.html")));
  }
}).listen(port, "127.0.0.1", () => console.log(`Pages preview: http://127.0.0.1:${port}${basePath}/`));
