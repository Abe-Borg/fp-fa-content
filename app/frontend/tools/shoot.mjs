// Pictures of the window for the README and for checking a change by eye:
//   node tools/shoot.mjs <page url with ?token=…> <folder> [scheme]
// The app must be serving (python -m fpfa --demo --serve, or --demo --screenshot-dir which runs this).
import { createRequire } from "node:module";
import { mkdirSync } from "node:fs";
import { join } from "node:path";

// Playwright is not a dependency of the page: a developer machine or CI has it installed on its own.
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const [url, folder = "screenshots", scheme] = process.argv.slice(2);
if (!url) {
  console.error("usage: node tools/shoot.mjs <page url> [folder] [scheme]");
  process.exit(2);
}
mkdirSync(folder, { recursive: true });
let browser;
try {
  browser = await chromium.launch();
} catch {
  browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium" });
}
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
const address = scheme ? url.replace(/theme=[a-z]+/, `theme=${scheme}`) : url;
await page.goto(address);
await page.waitForSelector(".topbar");
await page.waitForTimeout(1500);
const suffix = scheme ? `-${scheme}` : "";
await page.screenshot({ path: join(folder, `thread${suffix}.png`) });
// The job panel's tabs are in the top bar. The demo's run may already have opened Results.
await page.locator("#tab-inputs").click();
await page.waitForSelector(".job-panel .inputs");
await page.waitForTimeout(400);
await page.screenshot({ path: join(folder, `di_zone_inputs${suffix}.png`) });
await page.locator("#tab-results").click();
await page.waitForSelector(".job-panel .results");
await page.waitForTimeout(300);
await page.screenshot({ path: join(folder, `di_zone_results${suffix}.png`) });
await browser.close();
