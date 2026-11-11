// Drives the Team panel in Chromium against a running app whose open job already has a team's work on its
// record (tests/team_fixture.py), and checks what a designer coming back to that job would do:
//   node tools/e2e_team.mjs <page url with ?token=…>
// tests/test_web.py seeds the job and runs this when Node and Playwright are installed.
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

try {
  await page.goto(url);
  await page.waitForSelector(".composer textarea");

  // One line on the team sits beside the job's name, with what is waiting first. The keyboard opens the panel from it.
  await page.waitForSelector(".team-strip");
  const strip = await page.textContent(".team-strip .strip-text");
  check("the strip leads with what is waiting", strip.startsWith("1 needs your answer · 1 disagreement open · 7 findings"), strip);
  check("the job panel is closed until it is wanted", (await page.$(".job-panel")) === null);
  check("the Team tab counts what is waiting before it is opened", (await page.textContent("#tab-team .count")).startsWith("2"));
  await page.focus(".team-strip");
  await page.keyboard.press("Enter");
  await page.waitForSelector(".team");
  check("the strip opens the Team tab", (await page.getAttribute("#tab-team", "aria-pressed")) === "true");
  const first = await page.$eval(".team .section-label", (node) => node.textContent);
  check("what is waiting on the designer comes first", first === "NEEDS YOUR ANSWER (1)", first);
  check("the tab counts what is waiting", (await page.textContent("#tab-team .count")).startsWith("2"));

  // Where things stand: the plan the lead set, and who did what.
  const stand = await page.textContent(".card.stand");
  check("the objective is shown", stand.includes("Design basis for zone DH-1, with the releasing sequence that trips it"));
  check("the plan's four steps are listed", (await page.$$(".steps li")).length === 4);
  check("each contributor is listed with what it did", stand.includes("Sprinkler specialist") && stand.includes("5 findings") && stand.includes("reviewed 3"), stand);
  check("the check line says what the check is", stand.includes("Trace check:") && stand.includes("The standards were not opened."));
  // The fixture's team left calculations with no finding, so the export is ready as an incomplete draft and
  // the panel lists what is missing. Neither line may read as a finished design basis.
  check("the export's readiness is said", stand.includes("Design Basis export: ready"), stand);
  const coverage = await page.$("#team-coverage");
  check("what a design basis would be missing is listed", coverage !== null
    && (await coverage.innerText()).includes("A DESIGN BASIS WOULD BE INCOMPLETE"));
  check("an incomplete draft is not called simply ready",
    coverage === null || stand.includes("Design Basis export: ready, as an incomplete draft."), stand);
  check("the kinds of checking are on the panel", (await page.$("#team-assurance")) !== null);
  check("the methods read are on the panel", (await page.$("#team-methods")) !== null);

  // Findings: the group that needs attention is open; the others wait to be opened.
  const tiers = await page.$$eval(".tier", (nodes) => nodes.map((node) => [node.querySelector(".tier-title").textContent, node.open]));
  check("findings are grouped by how far each was taken", tiers.length === 3 && tiers[2][0] === "Needs further evidence or engineering review", JSON.stringify(tiers));
  check("only the group that needs attention starts open", JSON.stringify(tiers.map((tier) => tier[1])) === "[false,false,true]", JSON.stringify(tiers));
  const whys = await page.$$eval(".tier[open] .finding-why", (nodes) => nodes.map((node) => node.textContent));
  check("an open finding says why on its row", whys.some((text) => text.startsWith("fa-releasing objects:")) && whys.some((text) => text.startsWith("It is an assumption.")), JSON.stringify(whys));
  await page.focus(".tier:first-of-type > summary");
  await page.keyboard.press("Enter");
  check("Enter opens a group", await page.$eval(".tier:first-of-type", (node) => node.open));
  await page.focus(".tier:first-of-type .finding > summary");
  await page.keyboard.press("Space");
  const evidence = await page.textContent(".tier:first-of-type .finding[open] .finding-body");
  check("a finding opens to what it rests on", evidence.includes("calculation zone_trapped_volume") && evidence.includes("cite NFPA 13-2025 §8.3.2.3.1.1"), evidence);
  check("and to what the check read", evidence.includes("content-pack note: NFPA 13-2025 §8.3.2.3.1.1 (corpus/"), evidence);
  check("the panel says the standards were not opened", (await page.textContent(".tiers")).includes("The standards were not opened. Engineer-of-record review still applies."));

  // What is not settled, and what was.
  const open = await page.textContent(".team .callout:not(.warn)");
  check("the open objection is shown with both sides", open.includes("fa-releasing objects to a finding by fp-sprinkler") && open.includes("has no stated basis"), open);
  const team = await page.textContent(".team");
  check("how an earlier disagreement ended is kept", team.includes("HOW DISAGREEMENTS ENDED (1)") && team.includes("The finding was revised by fp-sprinkler"));
  check("questions for the engineer are apart from the designer's", team.includes("OPEN FOR THE ENGINEER OF RECORD (2)") && team.includes("NEEDS YOUR ANSWER (1)"));

  // Exchanges: a row is opened from the keyboard and shows the brief and what came back.
  const kinds = await page.$$eval(".exchange .exchange-kind", (nodes) => nodes.map((node) => node.textContent));
  check("exchanges are listed by kind", JSON.stringify(kinds) === '["brief","question","brief"]', JSON.stringify(kinds));
  await page.focus(".exchange:nth-of-type(2) > summary");
  await page.keyboard.press("Enter");
  const detail = await page.textContent(".exchange[open] .detail");
  check("a consult shows its question and its answer", detail.includes("What releasing time does the sequence carry") && detail.includes("Carry it as ASSUMED"), detail);

  // The designer answers the team's question on the panel. Nothing runs; the answer goes on the record.
  const ask = page.locator(".card.ask");
  check("the question is shown with who asked", (await ask.textContent()).includes("What is the trim volume on the elected valve's data sheet?") && (await ask.textContent()).includes("Asked by fp-sprinkler"));
  check("Answer waits for something to be typed", await ask.locator("button").isDisabled());
  await ask.locator("textarea").fill("6.5 gallons, from the submittal.");
  await page.keyboard.press("Control+Enter");
  await page.waitForFunction(() => !document.querySelector(".card.ask"));
  check("the answered question leaves the list", true);
  await page.waitForFunction(() => document.querySelector(".thread-column")?.textContent?.includes("6.5 gallons, from the submittal."));
  // The app's note eases in at a reading pace; wait for its last words.
  await page.waitForFunction(() => document.querySelector(".thread-column")?.textContent?.includes("or say so in your own words."), null, { timeout: 15000 });
  const thread = await page.textContent(".thread-column");
  check("the answer is in the thread as the designer's", thread.includes("Answer to the team's question") && thread.includes("Recorded. The lead reads it at the start of its next turn."));
  check("the next step is offered", await page.isVisible(".chip:has-text('Continue with my answers')"));
  check("the count drops", (await page.textContent("#tab-team .count")).startsWith("1"));
  check("the group the reader opened is still open after the page redrew", await page.$eval(".tier:first-of-type", (node) => node.open));
  check("the answer is listed as answered", (await page.textContent(".team")).includes("ANSWERED (1)"));

  // Status goes to the thread from the panel and from the menu, with no model call.
  await page.click(".team .button:has-text('Status to thread')");
  await page.waitForFunction(() => document.querySelector(".thread-column")?.textContent?.includes("Where Sample data hall DI zone stands"));
  check("status is posted into the thread", true);
  await page.focus("button[aria-label=More]");
  await page.keyboard.press("Enter");
  await page.waitForSelector(".menu");
  const labels = await page.$$eval(".menu .menu-label", (nodes) => nodes.map((node) => node.textContent));
  check("the ⋯ menu has the status", labels.includes("Where this job stands"), JSON.stringify(labels));
  await page.keyboard.press("Escape");

  // A field changed after the run: the Results tab and the panel both say the run is behind.
  await page.click("#tab-results");
  check("a current run carries no warning", (await page.$(".results .callout")) === null);
  await page.click("#tab-inputs");
  await page.fill("#f-q_fill", "750");
  await page.waitForFunction(() => document.querySelector(".action-note")?.textContent?.includes("q_fill_gpm"));
  check("Inputs says the run is behind beside Run zone", true);
  await page.click("#tab-results");
  await page.waitForSelector(".results .callout");
  const note = await page.textContent(".results .callout");
  check("Results says the run is behind the form", note.includes("These figures are from a run before the form changed (q_fill_gpm)."), note);
  check("and offers the run", await page.isVisible(".results .callout .button:has-text('Run zone again')"));
  await page.keyboard.press("Control+s");
  await page.click("#tab-team");
  await page.waitForSelector(".team .callout.warn");
  const stale = await page.textContent(".team .callout.warn");
  check("the panel lists what the change left out of date", stale.includes("q_fill_gpm changed from 600 gpm to 750 gpm") && stale.includes("finding by fp-sprinkler"), stale);
  const waiting = await page.textContent(".team-strip .strip-text");
  check("the strip counts it", /\d+ out of date/.test(waiting), waiting);
  check("bringing it up to date is offered", await page.isVisible(".chip:has-text('Bring it up to date')"));

  // Given the thread's place, the panel lays the team's work out side by side. The thread comes back as it was.
  await page.click("button[aria-label='Panel across the window']");
  check("the panel can take the thread's place", !(await page.isVisible(".thread-scroll")));
  const columns = await page.$eval(".team-grid", (node) => getComputedStyle(node).gridTemplateColumns.split(" ").length);
  check("a wide panel sets the findings beside the history", columns === 2, String(columns));
  await page.click("button[aria-label='Panel across the window']");
  check("and gives it back", await page.isVisible(".thread-scroll"));
} catch (error) {
  failures.push(`stopped: ${error && error.message ? error.message.split("\n")[0] : error}`);
}
await browser.close();
const ok = failures.length === 0 && errors.length === 0;
console.log(JSON.stringify({ ok, checks: checks.length, failures, errors }));
process.exit(ok ? 0 : 1);
