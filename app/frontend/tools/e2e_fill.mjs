// Drives the chat's fill of the Inputs tab in Chromium against a running app whose lead is a script
// (tests/test_web.py, BrowserTests.test_the_chat_filling_the_inputs_in_a_browser):
//   node tools/e2e_fill.mjs <page url with ?token=…>
// Turn one fills the AHJ and the insurer; turn two, in ask-first mode, proposes the hazard notes.
// Prints one JSON line {ok, checks, failures, errors}; exits 1 on a failure.
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
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const errors = [];
page.on("pageerror", (error) => errors.push(String(error)));
page.on("console", (message) => message.type() === "error" && errors.push(message.text()));

const send = async (text) => {
  await page.click(".composer textarea");
  await page.keyboard.insertText(text);
  await page.keyboard.press("Enter");
};
const row = (label) => page.locator(".fill-row", { hasText: label });

try {
  await page.goto(url);
  await page.waitForSelector(".composer textarea");

  // Turn one: the lead fills in two basis fields. The panel is closed, so the Inputs tab says so.
  await send("New job. The AHJ is the City of Irvine, and the insurer is FM Global.");
  await page.waitForSelector(".fill-card");
  check("the card names the fields in the form's words", (await page.textContent(".fill-card")).includes("AHJ"));
  check("the card shows before and after", (await row("Insurer").textContent()).includes("FM Global"));
  check("a reason found in the message is the designer's words", (await row("AHJ").textContent()).includes("You said:"));
  check("the Inputs tab is marked while the panel is closed", (await page.$("#tab-inputs .fill-dot")) !== null);

  // Show opens the tab on the field, with the focus in it.
  await row("AHJ").getByRole("button", { name: "Show" }).click();
  await page.waitForSelector(".job-panel .inputs");
  await page.waitForFunction(() => document.activeElement?.id === "f-ahj");
  check("Show puts the focus in the field", true);
  check("the field holds the value", (await page.inputValue("#f-ahj")) === "City of Irvine");
  check("the field is marked as filled from the chat", (await page.$(".field.filled #f-ahj")) !== null);
  check("the open tab carries no mark", (await page.$("#tab-inputs .fill-dot")) === null);

  // The tag opens where the value came from, and Escape closes it.
  const tag = page.locator(".field.filled", { has: page.locator("#f-ahj") }).locator(".from-chat");
  await tag.click();
  await page.waitForSelector(".from-chat-pop");
  check("the tag says what the designer said", (await page.textContent(".from-chat-pop")).includes("City of Irvine"));
  check("the tag says what the field held before", (await page.textContent(".from-chat-pop")).includes("Before: blank"));
  await page.keyboard.press("Escape");
  check("Escape closes it", (await page.$(".from-chat-pop")) === null);

  // Undo puts the insurer back.
  await row("Insurer").getByRole("button", { name: "Undo" }).click();
  await page.waitForSelector(".fill-row.state-undone");
  await page.waitForFunction(() => document.querySelector("#f-insurer")?.value === "FM");
  check("Undo puts the old value back on the form", true);
  check("the undone field is no longer marked", (await page.$(".field.filled #f-insurer")) === null);
  check("the row says it was undone", (await row("Insurer").textContent()).includes("Undone"));

  // Settings: ask first.
  await page.click(".side-link");
  await page.waitForSelector(".settings");
  await page.getByLabel("Ask me first. Nothing goes on the form until I apply it on the card.").click();
  await page.waitForFunction(() => document.querySelector("input[name='fill-from-chat']:checked")?.closest("label")?.textContent?.startsWith("Ask me first"));
  check("the setting is kept", true);
  await page.keyboard.press("Escape");
  await page.waitForSelector(".settings", { state: "detached" });

  // Turn two: the hazard notes wait for Apply.
  await send("Hazard notes: single-story hall, hot-aisle containment.");
  await page.waitForSelector(".fill-card.asking");
  check("the proposal says nothing is on the form yet", (await page.textContent(".fill-card.asking")).includes("until you apply it"));
  check("the form does not have it yet", (await page.inputValue("#f-hazard_notes")) === "");
  await page.locator(".fill-card.asking .fill-row", { hasText: "Hazard notes" }).getByRole("button", { name: "Apply" }).click();
  await page.waitForFunction(() => document.querySelector("#f-hazard_notes")?.value === "Single-story hall, hot-aisle containment.");
  check("Apply puts it on the form", true);
  check("an applied row can be undone", (await page.locator(".fill-row", { hasText: "Hazard notes" }).last().getByRole("button", { name: "Undo" }).count()) === 1);
  check("the applied field is marked", (await page.$(".field.filled #f-hazard_notes")) !== null);
} catch (error) {
  failures.push(`stopped: ${error.message}`);
}
await browser.close();
const report = { ok: failures.length === 0 && errors.length === 0, checks: checks.length, failures, errors };
console.log(JSON.stringify(report));
process.exit(report.ok ? 0 : 1);
