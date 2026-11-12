// Pictures of the window for checking a change by eye:
//   node tools/shoot.mjs <page url with ?token=…> [folder] [scheme] [scale]
// The app must be serving (python -m fpfa --demo --serve, or --demo --screenshot-dir which runs this).
// It writes thread.png, di_zone_inputs.png, and di_zone_results.png. A scheme adds its id to each name
// (thread-linen.png), and a device scale other than 1 adds the scale (thread-linen@2x.png).
//
// The page draws the scheme the app serves, whatever its address says. To shoot a scheme, serve it:
// python -m fpfa --demo --serve --theme linen. When a scheme is named, the tool reads the scheme the page
// drew before each picture and stops with exit code 1 if it is another one. It never changes the scheme
// the app has saved. A wrong argument stops it with exit code 2 before a browser opens.
import { createRequire } from "node:module";
import { mkdirSync } from "node:fs";
import { join } from "node:path";

const USAGE = "usage: node tools/shoot.mjs <page url> [folder] [scheme] [scale]";
const [url, folder = "screenshots", scheme = "", scaleText = "1"] = process.argv.slice(2);
const scale = Number(scaleText);

function refuse(problem) {
  console.error(problem ? `shoot.mjs: ${problem}\n${USAGE}` : USAGE);
  process.exit(2);
}

if (!url) refuse("");
if (scheme && !/^[a-z]+$/.test(scheme)) {
  refuse(`"${scheme}" is not a scheme id, such as linen. A scale comes after the scheme: <url> <folder> linen 2.`);
}
// Windows states its display scale in percent. A display at 150% is a device scale of 1.5, not 150.
if (!(scale >= 1 && scale <= 5)) {
  refuse(`the scale is a device scale from 1 to 5, such as 1.5 for a display at 150%, not "${scaleText}".`);
}

// Playwright is not a dependency of the page: a developer machine or CI has it installed on its own.
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

/** The page cannot give the pictures asked for. */
class Stop extends Error {}

const suffix = `${scheme ? `-${scheme}` : ""}${scale === 1 ? "" : `@${scale}x`}`;
const written = [];
let browser;
try {
  browser = await chromium.launch();
} catch {
  browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium" });
}
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: scale });

  /** One picture. Its name gives a scheme only once the page has been read as drawn in it. */
  const shot = async (name) => {
    const drawn = await page.evaluate(() => document.documentElement.dataset.theme ?? "");
    if (scheme && drawn !== scheme) {
      throw new Stop(
        `asked for ${scheme}, but the page is drawn in ${drawn || "no scheme"}. The page takes its scheme from the ` +
          `app, not from its address: serve it in ${scheme} (python -m fpfa --demo --serve --theme ${scheme}) and ` +
          `shoot the address that prints. ` +
          (written.length ? `Written before the scheme changed: ${written.join(", ")}.` : "Nothing was written."),
      );
    }
    mkdirSync(folder, { recursive: true });
    const path = join(folder, `${name}${suffix}.png`);
    await page.screenshot({ path });
    written.push(path);
  };

  /** A tab of the job panel. Its button closes the tab that is already open, so it is pressed only when shut. */
  const openTab = async (id) => {
    const tab = page.locator(`#tab-${id}`);
    if ((await tab.getAttribute("aria-pressed")) !== "true") await tab.click();
    await page.waitForSelector(`.job-panel .${id}`);
  };

  await page.goto(url);
  // The top bar is drawn once the app's state has arrived, and the page sets the scheme from that state first.
  await page.waitForSelector(".topbar");
  const ratio = await page.evaluate(() => window.devicePixelRatio);
  // Chromium holds the scale as a 32-bit float, so 1.1 reads back as 1.100000023841858.
  if (Math.abs(ratio - scale) > 1e-4) throw new Stop(`asked for a device scale of ${scale}, but the page reports ${ratio}. Nothing was written.`);
  await page.waitForTimeout(1500);
  await shot("thread");
  // The job panel's tabs are in the top bar. The demo's run, or the layout the app saved, may have one open.
  await openTab("inputs");
  await page.waitForTimeout(400);
  await shot("di_zone_inputs");
  await openTab("results");
  await page.waitForTimeout(300);
  await shot("di_zone_results");
} catch (error) {
  if (!(error instanceof Stop)) throw error;
  console.error(`shoot.mjs: ${error.message}`);
  process.exitCode = 1;
} finally {
  await browser.close();
}
