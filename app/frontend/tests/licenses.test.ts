// The page's license list (vite.config.ts): every module in the bundle is an npm package's, whose license
// licenses.json lists, or one of the page's own sources. Any other module fails the build.
import { test } from "node:test";
import assert from "node:assert/strict";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { bundledLicenses, isPageSource, packageOf } from "../vite.config.ts";

const frontend = fileURLToPath(new URL("..", import.meta.url));
// A module id as Vite writes one for a file: its absolute path, with forward slashes on Windows too.
const file = (...parts: string[]) => join(frontend, ...parts).split("\\").join("/");

/** Runs the plugin's generateBundle over one chunk of these module ids, with a stand-in for Rollup's context. */
function generate(ids: string[]) {
  const emitted: { fileName: string; source: string }[] = [];
  const context = {
    emitFile(asset: { fileName: string; source: string }) {
      emitted.push(asset);
      return "reference";
    },
    error(message: string): never {
      throw new Error(message);
    },
  };
  const modules = Object.fromEntries(ids.map((id) => [id, { renderedLength: 1 }]));
  const bundle = { "assets/index-test.js": { type: "chunk", fileName: "assets/index-test.js", modules } };
  let failure: Error | null = null;
  try {
    (bundledLicenses().generateBundle as Function).call(context, {}, bundle, true);
  } catch (error) {
    failure = error as Error;
  }
  return { emitted, failure };
}

test("a module under node_modules is its package's, scoped or not, and wrapped by the CommonJS plugin or not", () => {
  assert.equal(packageOf(file("node_modules", "react", "index.js")), "react");
  assert.equal(packageOf(`\0${file("node_modules", "react-dom", "client.js")}?commonjs-es-import`), "react-dom");
  assert.equal(packageOf(file("node_modules", "@scope", "name", "dist", "index.js")), "@scope/name");
  assert.equal(packageOf("C:\\work\\app\\frontend\\node_modules\\scheduler\\index.js"), "scheduler");
  assert.equal(packageOf("\0vite/modulepreload-polyfill.js"), null);
  assert.equal(packageOf(file("src", "App.tsx")), null);
});

test("the page's own sources are the files the build stamp hashes, and never code a plugin writes in", () => {
  for (const id of [file("index.html"), `${file("index.html")}?html-proxy&index=0.js`, file("src", "main.tsx"),
                    file("src", "components", "Thread.tsx"), `${file("src", "styles.css")}?inline`]) {
    assert.equal(isPageSource(id), true, id);
  }
  // "src/main.tsx" is no file Vite resolved: its ids for files are absolute. npm test runs in this folder,
  // where the relative path would otherwise land on the real file.
  for (const id of ["\0vite/modulepreload-polyfill.js", "\0vite/preload-helper.js", "\0commonjsHelpers.js",
                    `\0${file("src", "App.tsx")}`, "vite/modulepreload-polyfill", "src/main.tsx",
                    file("src-old", "App.tsx"), file("tools", "shoot.mjs"), file("node_modules", "react", "index.js"),
                    file("..", "fpfa", "web", "static", "index.js")]) {
    assert.equal(isPageSource(id), false, id);
  }
});

test("a module that is neither fails the build, naming each one, and no license list is written", () => {
  const { emitted, failure } = generate([
    file("index.html"), file("src", "main.tsx"), file("node_modules", "react", "index.js"),
    "\0vite/modulepreload-polyfill.js", "\0commonjsHelpers.js",
  ]);
  assert.ok(failure, "the build went on");
  const named = failure.message.split("\n").filter((line) => line.startsWith("  ")).map((line) => line.trim());
  assert.deepEqual(named, [
    "assets/index-test.js: \\0vite/modulepreload-polyfill.js",
    "assets/index-test.js: \\0commonjsHelpers.js",
  ]);
  assert.match(failure.message, /build\.modulePreload\.polyfill/);
  assert.deepEqual(emitted, []);
});

test("a bundle of the page's own sources and npm packages lists each package once, with its license text", () => {
  const { emitted, failure } = generate([
    file("index.html"), file("src", "main.tsx"),
    `\0${file("node_modules", "react", "index.js")}?commonjs-module`, file("node_modules", "react", "index.js"),
    file("node_modules", "scheduler", "index.js"),
  ]);
  assert.equal(failure, null);
  assert.deepEqual(emitted.map((asset) => asset.fileName), ["licenses.json"]);
  const { packages } = JSON.parse(emitted[0].source);
  assert.deepEqual(packages.map((item: { name: string }) => item.name), ["react", "scheduler"]);
  for (const item of packages) assert.match(item.text, /Permission is hereby granted/, item.name);
});
