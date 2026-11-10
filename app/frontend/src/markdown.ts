/**
 * Light markdown for the thread, with the rules of app/fpfa/chat_render.py.
 *
 * Claude replies in markdown. Headings, bullets, numbered lists, fenced code,
 * tables, **bold**, and `code` are understood. Single asterisks and
 * underscores are left alone, so names such as t_total and zone_gal stay
 * intact. Every source line stays a line: a reply that puts its figures on
 * consecutive lines shows them that way. Only the markers change; the words,
 * the figures, and the ASSUMED labels are shown as written.
 *
 * The first line of a job reply is its heading (Job <id> | project | kind |
 * title). It is kept word for word and shown as a caption.
 *
 * Every piece of text keeps its offset in the source, so the page can fade in
 * the words that just arrived. Pure, so `node --test` pins every rule.
 */

export interface Inline {
  kind: "text" | "bold" | "code";
  text: string;
  /** Offset of text[0] in the source. */
  start: number;
}

export type Line =
  | { kind: "caption"; text: string; start: number }
  | { kind: "heading"; level: number; inlines: Inline[] }
  | { kind: "item"; depth: 1 | 2; marker: string; numbered: boolean; inlines: Inline[] }
  | { kind: "para"; inlines: Inline[] }
  | { kind: "blank" }
  | { kind: "rule" }
  | { kind: "pre"; lines: string[] }
  | { kind: "table"; head: string[] | null; rows: string[][]; aligns: ("left" | "right" | "center")[] };

const HEADING = /^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$/;
const BULLET = /^(\s*)[-*+]\s+(.*)$/;
const NUMBERED = /^(\s*)(\d{1,3}[.)])\s+(.*)$/;
const RULE = /^\s{0,3}([-*_])(?:\s*\1){2,}\s*$/;
const INLINE = /(\*\*[^*\n]+?\*\*|`[^`\n]+`)/g;
const JOB_HEADING = /^Job [0-9a-f]{6,} \| /;
const TABLE_RULE_CELL = /^:?-{2,}:?$/;

export function isJobHeading(line: string): boolean {
  return JOB_HEADING.test(line || "");
}

/** A chat job's heading stops at the kind: its title is the question, already on screen above. */
export function metaCaption(line: string): string {
  const parts = line.split(" | ");
  if (parts.length >= 4 && parts[2].trim() === "chat") return parts.slice(0, 3).join(" | ");
  return line;
}

/** One line split on **bold** and `code`. Other characters pass through. */
export function inlines(text: string, start: number): Inline[] {
  const out: Inline[] = [];
  let position = 0;
  INLINE.lastIndex = 0;
  for (let match = INLINE.exec(text); match; match = INLINE.exec(text)) {
    if (match.index > position) out.push({ kind: "text", text: text.slice(position, match.index), start: start + position });
    const token = match[0];
    if (token.startsWith("**")) out.push({ kind: "bold", text: token.slice(2, -2), start: start + match.index + 2 });
    else out.push({ kind: "code", text: token.slice(1, -1), start: start + match.index + 1 });
    position = match.index + token.length;
  }
  if (position < text.length) out.push({ kind: "text", text: text.slice(position), start: start + position });
  return out;
}

function indentDepth(lead: string): 1 | 2 {
  return lead.replace(/\t/g, "    ").length >= 2 ? 2 : 1;
}

/** A cell boundary is a pipe that is not escaped: "A \| B" stays in one cell. */
export function tableCells(line: string): string[] {
  let body = line.trim();
  if (body.startsWith("|")) body = body.slice(1);
  if (body.endsWith("|") && !body.endsWith("\\|")) body = body.slice(0, -1);
  const cells: string[] = [];
  let current = "";
  for (let i = 0; i < body.length; i += 1) {
    const ch = body[i];
    if (ch === "|" && body[i - 1] !== "\\") {
      cells.push(current);
      current = "";
    } else {
      current += ch;
    }
  }
  cells.push(current);
  return cells.map((cell) => cell.trim().replace(/\\\|/g, "|"));
}

/** The words of a cell without its markers. */
export function stripInline(text: string): string {
  return inlines(text, 0).map((piece) => piece.text).join("");
}

function table(rows: string[]): Line {
  const parsed = rows.map(tableCells);
  const ruleAt = parsed.findIndex((cells) => cells.length > 0 && cells.every((cell) => !cell || TABLE_RULE_CELL.test(cell)) && cells.some(Boolean));
  if (ruleAt < 0 || parsed.length < 2) return { kind: "pre", lines: rows };
  const body = parsed.filter((_cells, index) => index !== ruleAt);
  const count = Math.max(...body.map((cells) => cells.length));
  const pad = (cells: string[]) => [...cells.map(stripInline), ...Array(count - cells.length).fill("")];
  const aligns = Array.from({ length: count }, (_unused, column) => {
    const cell = parsed[ruleAt][column] || "";
    if (cell.startsWith(":") && cell.endsWith(":")) return "center" as const;
    if (cell.endsWith(":")) return "right" as const;
    return "left" as const;
  });
  if (ruleAt === 1) return { kind: "table", head: pad(body[0]), rows: body.slice(1).map(pad), aligns };
  return { kind: "table", head: null, rows: body.map(pad), aligns };
}

/**
 * The lines of a reply. start is the offset of text[0] in the whole reply;
 * caption says whether a first line that is a job heading is shown as one.
 */
export function parse(text: string, start = 0, caption = true): Line[] {
  const source = text || "";
  const lines = source.split("\n");
  const offsets: number[] = [];
  let at = start;
  for (const line of lines) {
    offsets.push(at);
    at += line.length + 1;
  }
  const out: Line[] = [];
  let fence: string[] | null = null;
  let index = 0;
  while (index < lines.length) {
    const line = lines[index];
    const offset = offsets[index];
    if (line.trim().startsWith("```")) {
      if (fence) {
        out.push({ kind: "pre", lines: fence });
        fence = null;
      } else {
        fence = [];
      }
      index += 1;
      continue;
    }
    if (fence) {
      fence.push(line);
      index += 1;
      continue;
    }
    const first = caption && index === 0 && start === 0;
    if (first && isJobHeading(line)) {
      out.push({ kind: "caption", text: metaCaption(line), start: offset });
      index += 1;
      continue;
    }
    if (line.trim().startsWith("|")) {
      const group: string[] = [];
      while (index < lines.length && lines[index].trim().startsWith("|")) {
        group.push(lines[index]);
        index += 1;
      }
      out.push(table(group));
      continue;
    }
    index += 1;
    if (line.trim() === "") {
      out.push({ kind: "blank" });
      continue;
    }
    if (RULE.test(line)) {
      out.push({ kind: "rule" });
      continue;
    }
    const heading = HEADING.exec(line);
    if (heading) {
      const body = heading[2];
      out.push({ kind: "heading", level: heading[1].length, inlines: inlines(body, offset + line.indexOf(body, heading[1].length)) });
      continue;
    }
    const bullet = BULLET.exec(line);
    if (bullet) {
      const body = bullet[2];
      out.push({ kind: "item", depth: indentDepth(bullet[1]), marker: "•", numbered: false, inlines: inlines(body, offset + line.length - body.length) });
      continue;
    }
    const numbered = NUMBERED.exec(line);
    if (numbered) {
      const body = numbered[3];
      out.push({ kind: "item", depth: indentDepth(numbered[1]), marker: numbered[2], numbered: true, inlines: inlines(body, offset + line.length - body.length) });
      continue;
    }
    out.push({ kind: "para", inlines: inlines(line, offset) });
  }
  // A fence still open at the end (a reply still arriving) shows what it has so far.
  if (fence) out.push({ kind: "pre", lines: fence });
  return out;
}

/** What the thread shows for a reply, as plain text. The same words chat_render.plain_text gives. */
export function plainText(text: string): string {
  return parse(text)
    .map((line) => {
      switch (line.kind) {
        case "caption":
          return line.text;
        case "heading":
        case "para":
          return line.inlines.map((piece) => piece.text).join("");
        case "item":
          return `${line.numbered ? line.marker + " " : "• "}${line.inlines.map((piece) => piece.text).join("")}`;
        case "pre":
          return line.lines.join("\n");
        case "table":
          return [...(line.head ? [line.head] : []), ...line.rows].map((cells) => cells.join("  ").trimEnd()).join("\n");
        case "rule":
        case "blank":
          return "";
      }
    })
    .join("\n");
}

/** One block of a reply: the slice of the text from `start`. */
export interface Block {
  start: number;
  text: string;
}

const FENCE_OPEN = /^\s*```/;

/**
 * The reply cut at its blank lines into blocks that render the same apart as
 * together: a fenced code block stays whole, and a table never holds a blank
 * line. A settled block is parsed and drawn once; only the growing one is
 * drawn again as words arrive.
 */
export function splitBlocks(text: string): Block[] {
  const blocks: Block[] = [];
  let start = -1;
  let end = 0;
  let inFence = false;
  let pos = 0;
  for (;;) {
    const nl = text.indexOf("\n", pos);
    const lineEnd = nl === -1 ? text.length : nl;
    const line = text.slice(pos, lineEnd);
    if (FENCE_OPEN.test(line)) {
      if (start < 0) start = pos;
      inFence = !inFence;
      end = lineEnd;
    } else if (inFence) {
      end = lineEnd;
    } else if (line.trim() === "") {
      if (start >= 0) {
        blocks.push({ start, text: text.slice(start, end) });
        start = -1;
      }
    } else {
      if (start < 0) start = pos;
      end = lineEnd;
    }
    if (nl === -1) break;
    pos = nl + 1;
  }
  if (start >= 0) blocks.push({ start, text: text.slice(start, end) });
  return blocks;
}

/**
 * The growing end of a reply with a half-written bold or code span closed, so
 * "the **double-interl" is drawn bold already instead of jumping when the
 * closing pair lands. A marker with nothing after it yet is held back. Text
 * in an open code fence is left alone. Only for text still flowing.
 */
export function settleInline(text: string): string {
  if (!text) return text;
  const lines = text.split("\n");
  if (lines.filter((line) => line.trim().startsWith("```")).length % 2) return text;
  let last = lines[lines.length - 1];
  const trailing = last.length - last.replace(/\*+$/, "").length;
  if (trailing % 2) last = last.slice(0, -1);
  if ((last.match(/\*\*/g) || []).length % 2) last = last.endsWith("**") ? last.slice(0, -2) : last + "**";
  if ((last.match(/`/g) || []).length % 2) last = last.endsWith("`") ? last.slice(0, -1) : last + "`";
  lines[lines.length - 1] = last;
  return lines.join("\n");
}
