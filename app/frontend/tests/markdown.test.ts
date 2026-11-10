// The thread's markdown (src/markdown.ts): the rules of app/fpfa/chat_render.py, which these cases mirror.
import { test } from "node:test";
import assert from "node:assert/strict";
import { inlines, isJobHeading, metaCaption, parse, plainText, settleInline, splitBlocks, tableCells, type Line } from "../src/markdown.ts";

const text = (line: Line) => ("inlines" in line ? line.inlines.map((piece) => piece.text).join("") : "");

test("markers are drawn and words are kept", () => {
  const lines = parse("## Design basis\n- **Trim** is ASSUMED\n  - nested `t_total`\n3. Confirm the AHJ\n---\nplain");
  assert.equal(lines[0].kind, "heading");
  assert.equal(text(lines[0]), "Design basis");
  assert.equal(lines[1].kind, "item");
  assert.deepEqual((lines[1] as any).inlines.map((piece: any) => piece.kind), ["bold", "text"]);
  assert.equal(text(lines[1]), "Trim is ASSUMED");
  assert.equal((lines[2] as any).depth, 2);
  assert.deepEqual((lines[2] as any).inlines.map((piece: any) => [piece.kind, piece.text]), [["text", "nested "], ["code", "t_total"]]);
  assert.equal((lines[3] as any).marker, "3.");
  assert.equal(lines[4].kind, "rule");
  assert.equal(plainText("**Trim** is ASSUMED"), "Trim is ASSUMED");
});

test("single asterisks and underscores are left alone", () => {
  for (const sample of ["t_total and zone_gal", "a * b * c", "_not italic_", "*not italic*"]) {
    assert.equal(plainText(sample), sample);
  }
});

test("every piece keeps its offset in the reply", () => {
  const reply = "Intro line\n- **bold** then `code` then text";
  for (const line of parse(reply)) {
    if (!("inlines" in line)) continue;
    for (const piece of line.inlines) assert.equal(reply.slice(piece.start, piece.start + piece.text.length), piece.text);
  }
  const pieces = inlines("a **b** `c`", 100);
  assert.deepEqual(pieces.map((piece) => [piece.kind, piece.text, piece.start]), [["text", "a ", 100], ["bold", "b", 104], ["text", " ", 107], ["code", "c", 109]]);
});

test("a job heading is a caption, and a chat caption stops at the kind", () => {
  assert.ok(isJobHeading("Job 6b34e02bf8dc | Hall | chat | Which trim?"));
  assert.equal(isJobHeading("Jobs are fun"), false);
  assert.equal(metaCaption("Job 6b34e02bf8dc | Hall | chat | Which trim?"), "Job 6b34e02bf8dc | Hall | chat");
  assert.equal(metaCaption("Job 6b34e02bf8dc | Hall | zone | Zone tool plan"), "Job 6b34e02bf8dc | Hall | zone | Zone tool plan");
  const [caption, body] = parse("Job 6b34e02bf8dc | Hall | chat | Which trim?\nEl/El.");
  assert.deepEqual(caption, { kind: "caption", text: "Job 6b34e02bf8dc | Hall | chat", start: 0 });
  assert.equal(text(body), "El/El.");
  // Only the first line of the reply is a caption.
  assert.equal(parse("x\nJob 6b34e02bf8dc | Hall | chat")[1].kind, "para");
});

test("tables have a head and body, an escaped pipe stays in its cell, and a table with no rule row is shown as written", () => {
  const [table] = parse("| Item | Value |\n| --- | ---: |\n| Zone total | **281.3** gal |\n| A \\| B | 2 |");
  assert.equal(table.kind, "table");
  assert.deepEqual((table as any).head, ["Item", "Value"]);
  assert.deepEqual((table as any).rows, [["Zone total", "281.3 gal"], ["A | B", "2"]]);
  assert.deepEqual((table as any).aligns, ["left", "right"]);
  assert.deepEqual(tableCells("| a | b \\| c |"), ["a", "b | c"]);
  const [raw] = parse("| just | a row |");
  assert.deepEqual(raw, { kind: "pre", lines: ["| just | a row |"] });
});

test("fenced code keeps its text, and an open fence shows what it has", () => {
  const [code] = parse("```\nzone_gal = 281.3\n**not bold**\n```");
  assert.deepEqual(code, { kind: "pre", lines: ["zone_gal = 281.3", "**not bold**"] });
  const [open] = parse("```python\nvalue = 1");
  assert.deepEqual(open, { kind: "pre", lines: ["value = 1"] });
});

test("a reply is cut into blocks at blank lines, and a fence stays whole", () => {
  const reply = "First paragraph.\n\nSecond\nstill second.\n\n```\nzone_gal = 281.3\n\nt_total = 38.1\n```\n\nAfter";
  const blocks = splitBlocks(reply);
  assert.deepEqual(blocks.map((block) => block.text), [
    "First paragraph.",
    "Second\nstill second.",
    "```\nzone_gal = 281.3\n\nt_total = 38.1\n```",
    "After",
  ]);
  for (const block of blocks) assert.equal(reply.slice(block.start, block.start + block.text.length), block.text);
  assert.deepEqual(splitBlocks(""), []);
});

test("drawing a reply block by block gives the lines of drawing it whole, at every length", () => {
  const reply =
    "Job 6b34e02bf8dc | Sample | chat\n## Design basis\n\nThe zone is **double-interlock**.\n\n" +
    "| Item | Value |\n| --- | --- |\n| Pipe | 276.3 gal |\n\n- First point with `t_total`\n- Second point\n\n" +
    "```\nzone_gal = 281.3\n\nmore\n```\n\n1. Confirm the trim.\n2. Confirm the AHJ.";
  const visible = (lines: Line[]) => lines.filter((line) => line.kind !== "blank").map((line) => JSON.stringify(line));
  for (let end = 0; end <= reply.length; end += 1) {
    const shown = reply.slice(0, end);
    const whole = visible(parse(shown));
    const pieces = splitBlocks(shown).flatMap((block) => visible(parse(block.text, block.start)));
    assert.deepEqual(pieces, whole, `prefix of ${end} characters`);
  }
});

test("a half-written span is drawn as it will end up", () => {
  assert.equal(settleInline("The zone is a **double-interl"), "The zone is a **double-interl**");
  assert.equal(settleInline("and `t_tot"), "and `t_tot`");
  // A marker with nothing after it yet is held back.
  assert.equal(settleInline("The zone is a **"), "The zone is a ");
  assert.equal(settleInline("The zone is a *"), "The zone is a ");
  assert.equal(settleInline("and `"), "and ");
  assert.equal(settleInline("a **bold*"), "a **bold**");
  for (const same of ["", "plain words", "a **bold** word and `code`", "**open on an earlier line\nnext line", "names such as t_total and zone_gal"]) {
    assert.equal(settleInline(same), same);
  }
  const fenced = "Intro\n```\nvalue = a ** b";
  assert.equal(settleInline(fenced), fenced);
  assert.equal(settleInline("```\ncode\n```\nthen **bol"), "```\ncode\n```\nthen **bol**");
  assert.equal(plainText(settleInline("The zone is a **double-interl")), "The zone is a double-interl");
});
