// The README's pictures (docs/screenshots), taken from a running app:
//   node tools/shoot_docs.mjs <page url with ?token=…> <folder> <welcome|job>
// tests/docs_pictures.py starts the app twice, once empty and once on the scripted scenario's job, and runs
// this for each. The pictures show the application; the team's words in them are a script's, not a model's.
import { createRequire } from "node:module";
import { mkdirSync } from "node:fs";
import { join } from "node:path";

// Playwright is not a dependency of the page: a developer machine or CI has it installed on its own.
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const [url, folder = "screenshots", which = "job"] = process.argv.slice(2);
if (!url) {
  console.error("usage: node tools/shoot_docs.mjs <page url> [folder] [welcome|job]");
  process.exit(2);
}
mkdirSync(folder, { recursive: true });
let browser;
try {
  browser = await chromium.launch();
} catch {
  browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium" });
}
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
const shot = async (name) => {
  await page.waitForTimeout(500);
  await page.screenshot({ path: join(folder, name) });
  console.log(`wrote ${join(folder, name)}`);
};
/** One action of the app's own API, the way the page posts it. */
const post = (action, body) =>
  page.evaluate(async ([name, payload]) => {
    const token = new URLSearchParams(location.search).get("token");
    await fetch(`/api/${name}`, { method: "POST", headers: { "X-Cynosure-Token": token, "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  }, [action, body]);

await page.goto(url);
await page.waitForSelector(".composer textarea");
await page.waitForTimeout(1500);

if (which === "welcome") {
  await page.waitForSelector(".welcome-card");
  await shot("welcome-warm-clay.png");
  await page.click(".side-link");
  await page.waitForSelector(".settings");
  await shot("settings-appearance.png");
} else {
  // The whole window: the job list, the lead's reply, and the run's figures beside it.
  await page.click("#tab-results");
  await page.waitForSelector(".job-panel .tiles");
  await shot("window-warm-clay.png");
  // The Team tab beside the thread: the question waiting, then where the job stands.
  await page.click("#tab-team");
  await page.waitForSelector(".job-panel .team");
  await shot("team-warm-clay.png");
  // Linen, the light scheme: the inputs, then the team's work with the panel in the thread's place.
  await post("scheme", { id: "linen" });
  await page.waitForFunction(() => document.documentElement.getAttribute("data-theme") === "linen");
  await page.click("#tab-inputs");
  await page.waitForSelector(".job-panel .inputs");
  await shot("inputs-linen.png");
  await page.click("#tab-team");
  await page.click("button[aria-label='Panel across the window']");
  await page.waitForSelector(".stage.panel-wide");
  await page.locator(".tier[open] .finding > summary").first().click();
  // The findings, with the one just opened, come to the top of what is drawn.
  await page.$$eval(".team .section-label", (labels) => labels.find((label) => label.textContent.startsWith("FINDINGS"))?.scrollIntoView({ block: "start" }));
  await shot("team-across-linen.png");
}
await browser.close();
