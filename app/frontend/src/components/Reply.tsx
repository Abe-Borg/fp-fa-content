/**
 * A reply on the page: markdown drawn block by block (a settled block is drawn
 * once and skipped after that), the words that just arrived fading in from the
 * window colour, and a caret after the last word while the reply is arriving.
 */
import { memo, useEffect, useRef, useState, type ReactNode } from "react";
import { parse, settleInline, splitBlocks, type Inline, type Line } from "../markdown";
import { Reveal } from "../reveal";

/** The text cut at the pieces still fading in. marks are absolute offsets, ascending. */
function pieces(inline: Inline, marks: readonly number[], keyBase: string): ReactNode[] {
  const start = inline.start;
  const end = start + inline.text.length;
  if (!marks.length || end <= marks[0]) return [inline.text];
  const out: ReactNode[] = [];
  let at = start;
  // The piece that holds `start`, if one is still fading.
  let index = 0;
  while (index < marks.length && marks[index] <= start) index += 1;
  let current = index > 0 ? marks[index - 1] : -1;
  while (at < end) {
    const next = index < marks.length && marks[index] < end ? marks[index] : end;
    const text = inline.text.slice(at - start, next - start);
    if (text) {
      out.push(current >= 0 ? <span key={`${keyBase}f${current}_${at}`} className="fresh">{text}</span> : text);
    }
    at = next;
    if (index < marks.length && marks[index] === next) {
      current = marks[index];
      index += 1;
    }
  }
  return out;
}

function inlineNodes(list: Inline[], marks: readonly number[]): ReactNode[] {
  return list.map((inline, index) => {
    const content = pieces(inline, marks, `${index}`);
    if (inline.kind === "bold") return <strong key={index}>{content}</strong>;
    if (inline.kind === "code") return <code key={index}>{content}</code>;
    return <span key={index}>{content}</span>;
  });
}

function lineNode(line: Line, index: number, marks: readonly number[], caret: ReactNode): ReactNode {
  switch (line.kind) {
    case "caption":
      return (
        <div key={index} className="caption">
          {line.text}
          {caret}
        </div>
      );
    case "heading":
      return (
        <div key={index} className={`heading h${Math.min(line.level, 4)}`} role="heading" aria-level={Math.min(line.level + 2, 6)}>
          {inlineNodes(line.inlines, marks)}
          {caret}
        </div>
      );
    case "item":
      return (
        <div key={index} className={`item depth${line.depth}`}>
          <span className="marker">{line.marker}</span>
          <span className="item-body">
            {inlineNodes(line.inlines, marks)}
            {caret}
          </span>
        </div>
      );
    case "para":
      return (
        <div key={index} className="line">
          {inlineNodes(line.inlines, marks)}
          {caret}
        </div>
      );
    case "blank":
      return <div key={index} className="blank" />;
    case "rule":
      return <hr key={index} />;
    case "pre":
      return (
        <pre key={index} className="paper block-pre">
          {line.lines.join("\n")}
          {caret}
        </pre>
      );
    case "table":
      return (
        <div key={index} className="paper block-table">
          <table>
            {line.head ? (
              <thead>
                <tr>
                  {line.head.map((cell, column) => (
                    <th key={column} style={{ textAlign: line.aligns[column] }}>
                      {cell}
                    </th>
                  ))}
                </tr>
              </thead>
            ) : null}
            <tbody>
              {line.rows.map((cells, row) => (
                <tr key={row}>
                  {cells.map((cell, column) => (
                    <td key={column} style={{ textAlign: line.aligns[column] }}>
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {caret}
        </div>
      );
  }
}

const Block = memo(
  function Block({ text, start, marks, caret }: { text: string; start: number; marks: readonly number[]; caret: ReactNode }) {
    const lines = parse(text, start);
    const last = lines.length - 1;
    return <div className="block">{lines.map((line, index) => lineNode(line, index, marks, index === last ? caret : null))}</div>;
  },
  (a, b) => a.text === b.text && a.start === b.start && a.caret === b.caret && sameMarks(a.marks, b.marks),
);

function sameMarks(a: readonly number[], b: readonly number[]): boolean {
  if (a === b) return true;
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i += 1) if (a[i] !== b[i]) return false;
  return true;
}

const NO_MARKS: number[] = [];

/** The markdown of one reply. marks are the pieces still fading in; caret ends the last line. */
export function Markdown({ text, marks = NO_MARKS, caret = null }: { text: string; marks?: readonly number[]; caret?: ReactNode }) {
  const blocks = splitBlocks(text);
  if (!blocks.length) return caret ? <div className="block">{caret}</div> : null;
  const last = blocks.length - 1;
  return (
    <>
      {blocks.map((block, index) => {
        const end = block.start + block.text.length;
        let carried: readonly number[] = NO_MARKS;
        if (marks.length && marks[marks.length - 1] >= 0) {
          // A piece that began in an earlier block and is still fading carries into this one.
          let before = -1;
          const inside: number[] = [];
          for (const mark of marks) {
            if (mark < block.start) before = mark;
            else if (mark < end) inside.push(mark);
          }
          carried = before >= 0 ? [before, ...inside] : inside;
        }
        return <Block key={block.start} text={block.text} start={block.start} marks={carried} caret={index === last ? caret : null} />;
      })}
    </>
  );
}

/**
 * The text as it comes onto the page. A reply drawn from history shows at
 * once; one that arrives (or grows) while the designer watches is revealed at
 * a reading pace. A reply that changes under the words already shown carries
 * on from where those words end in it.
 */
export function useReveal(target: string, { motion, fromStart }: { motion: boolean; fromStart: boolean }): Reveal {
  const ref = useRef<Reveal | null>(null);
  if (ref.current === null) ref.current = new Reveal(target, motion && fromStart ? 0 : undefined);
  const reveal = ref.current;
  reveal.feed(target);
  if (!motion) reveal.finish();
  const [, setFrame] = useState(0);

  useEffect(() => {
    if (!motion) return;
    let frame = 0;
    let flowing = reveal.flowing;
    const tick = (now: number) => {
      const moved = reveal.advance(now);
      const active = reveal.active(now);
      if (moved || flowing !== reveal.flowing || !active) setFrame((count) => count + 1);
      flowing = reveal.flowing;
      frame = active ? requestAnimationFrame(tick) : 0;
    };
    if (reveal.active(performance.now())) frame = requestAnimationFrame(tick);
    return () => {
      if (frame) cancelAnimationFrame(frame);
    };
  }, [target, motion, reveal]);

  return reveal;
}

/** One assistant reply: its caption and markdown, revealed at a reading pace, with a caret while it arrives. */
export const ReplyText = memo(function ReplyText({
  text,
  motion,
  fromStart,
  live,
}: {
  text: string;
  motion: boolean;
  fromStart: boolean;
  live: boolean;
}) {
  const reveal = useReveal(text, { motion, fromStart });
  const flowing = reveal.flowing;
  const shown = reveal.text;
  const drawn = flowing ? settleInline(shown) : shown;
  const caret = live || flowing ? <span className={`caret${flowing ? "" : " blink"}`} aria-hidden="true" /> : null;
  return (
    <div className="reply" aria-busy={live || flowing || undefined}>
      <Markdown text={drawn} marks={motion ? reveal.marks : NO_MARKS} caret={caret} />
    </div>
  );
});
