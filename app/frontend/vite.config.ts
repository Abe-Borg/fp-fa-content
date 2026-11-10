/*
 * Builds the page into ../fpfa/web/static, which the app's local server serves and the
 * PyInstaller build bundles. Besides the page it writes licenses.json: the name, version,
 * license, and license text of every npm package whose code ends up in the bundle, read
 * from node_modules. packaging/third_party_notices.py puts them in THIRD-PARTY-NOTICES.txt
 * and fails the build when one has no text. And build.json: a hash of the sources it was
 * built from, so tests/test_web.py fails when the committed page is older than its source.
 *
 * `npm run dev` serves the page with hot reload and sends /api to a running app
 * (`python -m fpfa --serve --port 47011`, or CYNOSURE_API).
 */
import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";
import { readFileSync, readdirSync, existsSync, statSync } from "node:fs";
import { join, dirname, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";

const here = dirname(fileURLToPath(import.meta.url));
const LICENSE_FILE = /^(licen[cs]e|copying|notice)(\.(md|txt))?$/i;

function packageOf(id: string): string | null {
  const marker = "/node_modules/";
  const at = id.replace(/\\/g, "/").lastIndexOf(marker);
  if (at < 0) return null;
  const rest = id.replace(/\\/g, "/").slice(at + marker.length).split("/");
  return rest[0].startsWith("@") ? `${rest[0]}/${rest[1]}` : rest[0];
}

/** The files the page is built from. tests/test_web.py hashes the same list the same way. */
const SOURCES = ["index.html", "package.json", "package-lock.json", "vite.config.ts", "tsconfig.json", "src"];

function sourceFiles(): string[] {
  const out: string[] = [];
  const walk = (path: string) => {
    if (statSync(path).isDirectory()) readdirSync(path).sort().forEach((entry) => walk(join(path, entry)));
    else out.push(path);
  };
  SOURCES.forEach((item) => walk(join(here, item)));
  return out.map((path) => relative(here, path).split("\\").join("/")).sort();
}

/** sha256 over each source's path and bytes, with Windows line endings read as Unix ones. */
function sourceHash(): string {
  const hash = createHash("sha256");
  for (const name of sourceFiles()) {
    const text = readFileSync(join(here, name), "utf8").replace(/\r\n/g, "\n");
    hash.update(name + "\0" + text + "\0");
  }
  return hash.digest("hex");
}

function buildStamp(): Plugin {
  return {
    name: "cynosure-build-stamp",
    apply: "build",
    generateBundle() {
      this.emitFile({ type: "asset", fileName: "build.json", source: JSON.stringify({ sources: sourceHash() }, null, 2) + "\n" });
    },
  };
}

function bundledLicenses(): Plugin {
  return {
    name: "cynosure-bundled-licenses",
    apply: "build",
    generateBundle(_options, bundle) {
      const names = new Set<string>();
      for (const chunk of Object.values(bundle)) {
        if (chunk.type !== "chunk") continue;
        for (const id of Object.keys(chunk.modules)) {
          const name = packageOf(id);
          if (name) names.add(name);
        }
      }
      const packages = [...names].sort().map((name) => {
        const folder = join(here, "node_modules", name);
        const meta = JSON.parse(readFileSync(join(folder, "package.json"), "utf8"));
        const file = existsSync(folder) ? readdirSync(folder).find((entry) => LICENSE_FILE.test(entry)) : undefined;
        return {
          name,
          version: String(meta.version || ""),
          license: String(meta.license || ""),
          homepage: String(meta.homepage || ""),
          text: file ? readFileSync(join(folder, file), "utf8") : "",
        };
      });
      this.emitFile({ type: "asset", fileName: "licenses.json", source: JSON.stringify({ packages }, null, 2) + "\n" });
    },
  };
}

const api = process.env.CYNOSURE_API || "http://127.0.0.1:47011";

export default defineConfig({
  plugins: [react(), bundledLicenses(), buildStamp()],
  base: "/",
  build: {
    outDir: "../fpfa/web/static",
    emptyOutDir: true,
    target: "es2022",
    sourcemap: false,
    chunkSizeWarningLimit: 800,
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: api,
        changeOrigin: true,
        // The app refuses a cross-site Origin; the dev server's own is not the app's.
        configure: (proxy) => proxy.on("proxyReq", (request) => request.removeHeader("origin")),
      },
    },
  },
});
