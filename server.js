/**
 * Minimal static file server for Railway / production SPA hosting.
 * Serves the Vite build output (dist/) with HTML5 history-mode fallback
 * so that client-side routes (e.g. /profile, /track) resolve to index.html.
 */
import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { join, extname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const DIST = resolve(join(__dirname, "dist"));
const PORT = Number(process.env.PORT || 4173);

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js":   "application/javascript; charset=utf-8",
  ".mjs":  "application/javascript; charset=utf-8",
  ".css":  "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png":  "image/png",
  ".jpg":  "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif":  "image/gif",
  ".svg":  "image/svg+xml",
  ".ico":  "image/x-icon",
  ".woff": "font/woff",
  ".woff2":"font/woff2",
  ".ttf":  "font/ttf",
  ".webp": "image/webp",
  ".webm": "video/webm",
  ".mp4":  "video/mp4",
  ".txt":  "text/plain; charset=utf-8",
};

async function tryFile(filePath) {
  try {
    const s = await stat(filePath);
    if (s.isFile()) return await readFile(filePath);
  } catch { /* not found */ }
  return null;
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url || "/", `http://localhost:${PORT}`);
  let pathname = decodeURIComponent(url.pathname);

  // Strip trailing slash (except root)
  if (pathname !== "/" && pathname.endsWith("/")) {
    pathname = pathname.slice(0, -1);
  }

  // Return 502 for /api/* so misconfigured proxy is obvious, not silent HTML
  if (pathname.startsWith("/api/") || pathname === "/api") {
    res.writeHead(502, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "No backend configured. Set VITE_API_URL or add a reverse proxy for /api." }));
    return;
  }

  // Try exact file — path traversal guard: resolved path must stay inside DIST
  let filePath = resolve(join(DIST, pathname));
  if (!filePath.startsWith(DIST)) {
    res.writeHead(400, { "Content-Type": "text/plain" });
    res.end("Bad Request");
    return;
  }
  let content = await tryFile(filePath);

  // Try with index.html for directory
  if (!content) {
    const dirIndex = resolve(join(filePath, "index.html"));
    if (dirIndex.startsWith(DIST)) {
      content = await tryFile(dirIndex);
      if (content) filePath = dirIndex;
    }
  }

  // SPA fallback: serve index.html for non-file routes
  if (!content) {
    content = await tryFile(join(DIST, "index.html"));
    filePath = join(DIST, "index.html");
  }

  if (!content) {
    res.writeHead(404, { "Content-Type": "text/plain" });
    res.end("Not Found");
    return;
  }

  const ext = extname(filePath).toLowerCase();
  const mime = MIME[ext] || "application/octet-stream";

  res.writeHead(200, {
    "Content-Type": mime,
    "Cache-Control": ext === ".html" ? "no-cache" : "public, max-age=31536000, immutable",
  });
  res.end(content);
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`Static server listening on http://0.0.0.0:${PORT}`);
});
