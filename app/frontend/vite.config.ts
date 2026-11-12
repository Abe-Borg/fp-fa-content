/*
 * Builds the page into ../fpfa/web/static, which the app's local server serves and the
 * PyInstaller build bundles. Besides the page it writes licenses.json: the name, version,
 * license, and license text of every npm package whose code ends up in the bundle, read
 * from node_modules. packaging/third_party_notices.py puts them in THIRD-PARTY-NOTICES.txt
 * and fails the build when one has no text. Every module in the bundle must be an npm
 * package's or one of the page's own sources: the build fails on any other, such as a helper
 * a build plugin writes in under a virtual id, because licenses.json could not list it. And
 * build.json: a hash of the sources it was built from, so tests/test_web.py fails when the
 * committed page is older than its source.
 *
 * `npm run dev` serves the page with hot reload and sends /api to a running app
 * (`python -m fpfa --serve --port 47011`, or CYNOSURE_API).
 */
import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";
import { readFileSync, readdirSync, existsSync, statSync } from "node:fs";
import { join, dirname, relative, isAbsolute } from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";

const here = dirname(fileURLToPath(import.meta.url));
const LICENSE_FILE = /^(licen[cs]e|copying|notice)(\.(md|txt))?$/i;

/**
 * The npm package a module in the bundle is from: the folder after the last node_modules in
 * its id, scoped or not. null when the id names none, as a virtual id ("\0vite/...") does.
 */
export function packageOf(id: string): string | null {
  const marker = "/node_modules/";
  const at = id.replace(/\\/g, "/").lastIndexOf(marker);
  if (at < 0) return null;
  const rest = id.replace(/\\/g, "/").slice(at + marker.length).split("/");
  return rest[0].startsWith("@") ? `${rest[0]}/${rest[1]}` : rest[0];
}

/**
 * The files the page is built from: its own sources, under +Cynosure's LICENSE.
 * tests/test_web.py hashes the same list the same way.
 */
const SOURCES = ["index.html", "package.json", "package-lock.json", "vite.config.ts", "tsconfig.json", "src"];

/**
 * Whether a module in the bundle is one of the page's own sources (SOURCES): a file Vite
 * resolved, so an absolute path, with any query a plugin added. A virtual id, such as one a
 * build plugin writes in ("\0vite/preload-helper.js"), is no path, so it is never one; nor is
 * a file outside SOURCES, which the build stamp does not hash.
 */
export function isPageSource(id: string): boolean {
  const file = id.split("?")[0];
  if (!isAbsolute(file)) return false;
  const path = relative(here, file).split("\\").join("/");
  return SOURCES.some((item) => path === item || path.startsWith(`${item}/`));
}

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

/**
 * Writes licenses.json, and fails the build when a module in the bundle is neither an npm
 * package's nor one of the page's own sources: its license could not be listed. Attributing
 * every \0vite/ id to vite instead would list Vite's LICENSE.md, about 120 KB, most of it the
 * licenses of the dependencies Vite bundles into itself, none of which is in the page.
 */
export function bundledLicenses(): Plugin {
  return {
    name: "cynosure-bundled-licenses",
    apply: "build",
    generateBundle(_options, bundle) {
      const names = new Set<string>();
      const unlisted: string[] = [];
      for (const chunk of Object.values(bundle)) {
        if (chunk.type !== "chunk") continue;
        for (const id of Object.keys(chunk.modules)) {
          const name = packageOf(id);
          if (name) names.add(name);
          else if (!isPageSource(id)) unlisted.push(`${chunk.fileName}: ${id.replace(/\0/g, "\\0")}`);
        }
      }
      if (unlisted.length) {
        this.error(
          "licenses.json cannot list the license of code in the page's bundle. Each module below is " +
            "neither an npm package's nor one of the page's own sources (SOURCES in vite.config.ts):\n" +
            unlisted.map((item) => `  ${item}\n`).join("") +
            "An id that starts with \\0 is code a build plugin writes into the page, and one under \\0vite/ " +
            "is Vite's own. Turn off what writes it in, as build.modulePreload.polyfill is, or attribute " +
            "the module to its package in packageOf so that the package and its license text are listed.",
        );
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
    // No modulepreload polyfill. It is Vite's own code, about 0.7 KB minified at the head of the
    // page's script, and it has nothing to do here: the page is one chunk with no modulepreload
    // link, and WebView2 is Chromium, which supports modulepreload natively.
    modulePreload: { polyfill: false },
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
