// Drives the real page in Chromium against a running app and checks what a designer would do:
//   node tools/e2e.mjs <page url with ?token=…>
// tests/test_web.py starts the app (with a scripted, streaming Claude) and runs this when Node and
// Playwright are installed. Prints one JSON line {ok, checks, failures, errors}; exits 1 on a failure.
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const url = process.argv[2];
const checks = [];
const failures = [];
const check = (name, ok, detail = "") => {
  checks.push(name);
  if (!ok) failures.push(`${name}${detail ? `: ${detail}` : ""}`);
};

let browser;
try {
  browser = await chromium.launch();
} catch {
  browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium" });
}
const page = await browser.newPage({ viewport: { width: 1280, height: 820 } });
const errors = [];
page.on("pageerror", (error) => errors.push(String(error)));
page.on("console", (message) => message.type() === "error" && errors.push(message.text()));

try {
  await page.goto(url);
  await page.waitForSelector(".composer textarea");
  check("the welcome is on an empty thread", await page.isVisible("text=What are we working on?"));
  check("the composer has the focus at launch", await page.evaluate(() => document.activeElement?.tagName === "TEXTAREA"));
  check("the drawer is closed at launch", (await page.$(".drawer")) === null);

  // A chip sends exactly the message it stands for.
  await page.click(".chip:has-text('Load the sample zone')");
  await page.waitForSelector("text=Sample loaded");
  // The reply eases in at a reading pace; wait for its last words.
  await page.waitForFunction(() => document.querySelector(".thread-column")?.textContent?.includes("Draft export is Section"), null, { timeout: 15000 });
  const thread = await page.textContent(".thread-column");
  check("the sample run is posted with its labels", thread.includes("5.0 gal trim ASSUMED") && thread.includes("/sample-di"));
  check("the job caption is drawn", (await page.$$(".caption")).length >= 1);

  // The ⋯ menu, from the keyboard.
  await page.focus("button[aria-label=More]");
  await page.keyboard.press("Enter");
  await page.waitForSelector(".menu");
  const labels = await page.$$eval(".menu .menu-label", (nodes) => nodes.map((node) => node.textContent));
  for (const label of ["Sample DI zone", "Sample BESS room", "Run zone from Zone details", "Export draft Section 21 13 19…",
    "Team panel", "Usage and cost", "Narrate zone runs with Claude", "Rename job…", "Settings…", "Commands", "About and versions"]) {
    check(`the ⋯ menu has ${label}`, labels.includes(label), JSON.stringify(labels));
  }
  check("Enter opens the menu with the first row chosen", (await page.textContent(".menu-item.active .menu-label")) === "Sample DI zone");
  await page.keyboard.press("End");
  check("End goes to the last row", (await page.textContent(".menu-item.active .menu-label")) === "About and versions");
  await page.keyboard.press("Escape");
  check("Esc closes the menu", (await page.$(".menu")) === null);
  check("closing puts the keys back on the button", await page.evaluate(() => document.activeElement?.getAttribute("aria-label") === "More"));

  // Mode, from the keyboard: Down opens it.
  await page.focus("button[aria-label=Mode]");
  await page.keyboard.press("ArrowDown");
  await page.waitForSelector(".menu");
  const modes = await page.$$eval(".menu .menu-label", (nodes) => nodes.map((node) => node.textContent));
  check("the Mode menu lists the modes", ["Brainstorm", "Calculator", "Synthesis", "Mixed"].every((mode) => modes.includes(mode)), JSON.stringify(modes));
  await page.click(".menu-item:has-text('Calculator')");
  await page.waitForFunction(() => document.querySelector("button[aria-label=Mode]")?.textContent?.includes("calculator"));
  check("choosing a mode shows it on the button", true);

  // Zone details: the drawer, its tabs, and the figures on the Results tab.
  await page.click("button:has-text('Zone details')");
  await page.waitForSelector(".drawer");
  check("the Zone tab is open first", (await page.getAttribute("#tab-zone", "aria-selected")) === "true");
  check("the sample's four segments are listed", (await page.$$(".zone .grid-table tbody tr")).length === 4);
  await page.focus("#tab-zone");
  await page.keyboard.press("ArrowRight");
  await page.waitForSelector(".sheet");
  check("the arrow keys move between tabs", (await page.getAttribute("#tab-results", "aria-selected")) === "true");
  check("Results carries the tool-plan figures", (await page.textContent(".sheet")).includes("281.3"));
  await page.click("#tab-zone");
  await page.fill("#f-zone_id", "DH-9");
  await page.click("#tab-basis");
  await page.click("#tab-zone");
  check("a typed field keeps its value across tabs", (await page.inputValue("#f-zone_id")) === "DH-9");

  // Settings: a scheme card recolours the window at once.
  await page.click(".side-bottom >> text=Settings");
  await page.waitForSelector(".settings");
  await page.click(".scheme-card:has-text('Linen')");
  await page.waitForFunction(() => document.documentElement.getAttribute("data-theme") === "linen");
  check("a scheme card recolours the window", true);
  const background = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  check("Linen's window colour is drawn", background === "rgb(245, 241, 234)", background);
  await page.keyboard.press("Escape");
  check("Esc closes Settings", (await page.$(".settings")) === null);

  // Rename from the job's own menu, and delete with a question first.
  await page.click(".job.open .job-more");
  await page.click(".menu-item:has-text('Rename…')");
  await page.fill("#prompt-value", "Hall 2 zoning");
  await page.keyboard.press("Enter");
  await page.waitForSelector(".job:has-text('Hall 2 zoning')");
  check("rename shows in the sidebar and the top bar", (await page.textContent(".job-title")) === "Hall 2 zoning");

  // A question streams in: words while the turn runs, a caret, the working line, Stop.
  await page.fill(".composer textarea", "Give me the design basis for zone DH-1.");
  await page.keyboard.press("Enter");
  await page.waitForSelector(".working");
  check("the working line names what the app is doing", (await page.textContent(".working")).includes("Working on it"));
  check("Stop sits under the composer while the job runs", await page.isVisible(".chip.stop"));
  await page.waitForSelector(".turn.assistant .caret", { timeout: 15000 });
  await page.waitForFunction(() => document.querySelector(".thread-column")?.textContent?.includes("Design basis for zone DH-1"), null, { timeout: 15000 });
  const midway = await page.textContent(".thread-column");
  check("a half-written bold span shows no markers", !midway.includes("**"));
  // The reader scrolls up: the thread stays where they put it while words keep arriving.
  await page.mouse.move(640, 300);
  await page.mouse.wheel(0, -2000);
  await page.waitForTimeout(400);
  const before = await page.$eval(".thread-scroll", (node) => node.scrollTop);
  await page.waitForTimeout(900);
  const after = await page.$eval(".thread-scroll", (node) => node.scrollTop);
  check("a reader who scrolled up is left where they are", Math.abs(after - before) < 2, `${before} -> ${after}`);
  await page.waitForFunction(() => !document.querySelector(".working"), null, { timeout: 30000 });
  await page.waitForTimeout(2500);
  const done = await page.textContent(".thread-column");
  const newest = await page.$$eval(".turn.assistant", (nodes) => nodes[nodes.length - 1].textContent || "");
  const drawn = (newest.match(/Design basis for zone DH-1/g) || []).length;
  check("the finished reply is drawn once", drawn === 1 && newest.includes("Confirm the AHJ"), `${drawn} times`);
  check("no caret is left", (await page.$$(".caret")).length === 0);
  check("the table is a table on paper", (await page.$$(".block-table table")).length >= 1);
  const jump = await page.$(".jump");
  if (jump) await jump.click();
  const end = await page.$eval(".thread-scroll", (node) => node.scrollHeight - node.scrollTop - node.clientHeight);
  check("Latest brings the thread back to its end", end <= 24, String(end));

  // Delete, with the question first.
  await page.click(".job.open .job-more");
  await page.click(".menu-item:has-text('Delete')");
  await page.waitForSelector("text=Delete job");
  await page.click(".dialog .button.danger");
  await page.waitForFunction(() => !document.querySelector(".job"));
  check("delete clears the thread back to the welcome", await page.isVisible("text=What are we working on?"));
} catch (error) {
  failures.push(`stopped: ${error && error.message ? error.message.split("\n")[0] : error}`);
}
await browser.close();
const ok = failures.length === 0 && errors.length === 0;
console.log(JSON.stringify({ ok, checks: checks.length, failures, errors }));
process.exit(ok ? 0 : 1);
