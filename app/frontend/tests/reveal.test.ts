// How a reply's words come onto the page (src/reveal.ts). `npm test` runs it with Node's own test runner.
import { test } from "node:test";
import assert from "node:assert/strict";
import { FADE_MS, MAX_FRAME_SECONDS, REVEAL_MIN_RATE, Reveal, alignShown, revealStep, safeCut } from "../src/reveal.ts";

test("a burst drains in about a second and the end never trickles", () => {
  assert.equal(revealStep(0, 0.016), 0);
  assert.equal(revealStep(-5, 0.016), 0);
  // A long frame cannot reveal more than is waiting.
  assert.equal(revealStep(10, 5), 10);
  // A big backlog drains by its share; a small one keeps the floor pace.
  assert.ok(Math.abs(revealStep(3000, 0.1) - 3000 * (1 - Math.exp(-0.1 / 0.3))) < 1);
  assert.ok(Math.abs(revealStep(40, 0.1) - REVEAL_MIN_RATE * 0.1) < 1e-9);
  let backlog = 800;
  let clock = 0;
  while (backlog > 0.5) {
    backlog -= revealStep(Math.floor(backlog) + 1, 1 / 60);
    clock += 1 / 60;
  }
  assert.ok(clock > 0.6 && clock < 1.6, `drained in ${clock} s`);
});

test("the pace does not depend on the frame rate", () => {
  const text = "word ".repeat(400);
  const shownAfter = (seconds: number, frame: number) => {
    const reveal = new Reveal(text, 0);
    for (let clock = 0; clock < seconds * 1000; clock += frame * 1000) reveal.advance(clock + 1);
    return reveal.shown;
  };
  const fast = shownAfter(0.5, 1 / 120);
  const slow = shownAfter(0.5, 1 / 30);
  assert.ok(Math.abs(fast - slow) < text.length * 0.12, `${fast} vs ${slow}`);
  assert.ok(fast > text.length * 0.5);
});

test("a longer text carries on from the words shown", () => {
  assert.deepEqual(alignShown("Zone total", "Zone total is 281.3 gal."), { at: 10, whole: true });
  assert.deepEqual(alignShown("", "anything"), { at: 0, whole: true });
  // The finished reply can join its parts with other spacing.
  const joined = "Trim is ASSUMED.\n\nPipe is calculated.";
  const spaced = alignShown("Trim is ASSUMED.\nPipe is", joined);
  assert.ok(spaced.whole);
  assert.equal(joined.slice(0, spaced.at), "Trim is ASSUMED.\n\nPipe is");
  // Words that are no longer there stop the match where they diverge.
  const changed = alignShown("Zone total is 300", "Zone total is 281.3 gal.");
  assert.equal(changed.whole, false);
  assert.equal("Zone total is 281.3 gal.".slice(0, changed.at), "Zone total is");
});

test("a cut never splits a surrogate pair", () => {
  const text = "a😀b";
  assert.equal(safeCut(text, 2), 3);
  assert.equal(safeCut(text, 1), 1);
  assert.equal(safeCut(text, 99), text.length);
});

test("words arrive, fade, and settle", () => {
  const reveal = new Reveal("", 0);
  assert.equal(reveal.flowing, false);
  assert.equal(reveal.advance(1), false);
  reveal.feed("Trapped volume is 276.3 gal of pipe (calculated).");
  assert.equal(reveal.flowing, true);
  assert.equal(reveal.text, "");
  let clock = 1;
  while (reveal.flowing) {
    reveal.advance(clock);
    clock += 1000 / 60;
  }
  assert.equal(reveal.text, reveal.target);
  // Pieces are still fading: their marks ascend and sit inside the text.
  assert.ok(reveal.marks.length > 0);
  assert.deepEqual([...reveal.marks].sort((a, b) => a - b), reveal.marks);
  assert.ok(reveal.marks[reveal.marks.length - 1] < reveal.target.length);
  assert.ok(reveal.active(clock));
  const later = clock + FADE_MS + 50;
  assert.equal(reveal.active(later), false);
  assert.deepEqual(reveal.marks, []);
});

test("a text the reveal starts with is shown at once", () => {
  const reveal = new Reveal("A reply from the saved thread.");
  assert.equal(reveal.text, "A reply from the saved thread.");
  assert.equal(reveal.flowing, false);
  assert.equal(reveal.advance(1000), false);
});

test("a finished reply carries on and a changed one backs up", () => {
  const streamed = "Job 1a2b3c4d | Hall | chat\nThe zone total is 281.3 gal.";
  const reveal = new Reveal(streamed, 0);
  let clock = 1;
  while (reveal.shown < 40) {
    reveal.advance(clock);
    clock += 1000 / 60;
  }
  const shown = reveal.text;
  // The saved turn adds a team summary after the same words.
  reveal.feed(streamed + "\n\n**Team**\n- fp-sprinkler recorded 2 findings.");
  assert.equal(reveal.text, shown);
  assert.equal(reveal.flowing, true);
  // A retry starts the reply over: nothing of the failed attempt stays.
  reveal.feed("Job 1a2b3c4d | Hall | chat\nA different answer.");
  assert.ok(reveal.target.startsWith(reveal.text));
  assert.ok(reveal.shown <= "Job 1a2b3c4d | Hall | chat\n".length + 2);
  assert.ok(reveal.marks.every((mark) => mark < reveal.shown || reveal.shown === 0));
  reveal.finish();
  assert.equal(reveal.text, reveal.target);
  assert.equal(reveal.active(clock), false);
});

test("a stalled page does not dump its backlog in one frame", () => {
  const text = "x".repeat(4000);
  const reveal = new Reveal(text, 0);
  reveal.advance(1);
  const first = reveal.shown;
  reveal.advance(30001);
  assert.ok(reveal.shown - first <= Math.floor(revealStep(text.length - first, MAX_FRAME_SECONDS)) + 1);
  assert.ok(reveal.shown < text.length);
});
