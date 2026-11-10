/**
 * The conversation: the designer's messages as bubbles on the right, the
 * replies on the window colour with their job caption, the reply still
 * arriving, and the working line. The column stays centred and readable.
 *
 * The thread follows its end only while the reader is there. Every way the
 * reader moves it (the wheel, the scrollbar, a key) takes it off the end the
 * moment the move happens; coming back to the end puts it back on.
 */
import { memo, useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import type { Live, Turn, Welcome } from "../types";
import { plainText } from "../markdown";
import { ReplyText } from "./Reply";
import { Menu, type Anchor, type MenuItem } from "./Menu";
import { ArrowDown, Star } from "./icons";

const AT_END_PX = 24;
const MOVE_KEYS = new Set(["PageUp", "PageDown", "ArrowUp", "ArrowDown", "Home", "End", " "]);

interface Item {
  key: string;
  role: "user" | "assistant";
  text: string;
  live: boolean;
  fromStart: boolean;
}

const Bubble = memo(function Bubble({ text, onMenu }: { text: string; onMenu: (event: React.MouseEvent, text: string) => void }) {
  return (
    <div className="turn user">
      <div className="bubble" onContextMenu={(event) => onMenu(event, text)}>
        {text}
      </div>
    </div>
  );
});

function WorkingLine({ pending, motion }: { pending: { label: string; detail: string }; motion: boolean }) {
  return (
    <div className={`working${motion ? " moving" : ""}`} role="status" aria-live="polite">
      <span className="dots" aria-hidden="true">
        <i />
        <i />
        <i />
      </span>
      <span className="working-label">{pending.label}</span>
      {pending.detail ? <span className="working-detail">{pending.detail}</span> : null}
    </div>
  );
}

function WelcomeView({ welcome, onLink }: { welcome: Welcome; onLink: (action: string) => void }) {
  return (
    <div className="welcome">
      <Star size={46} className="star welcome-star" />
      <h1 className="display">{welcome.title}</h1>
      {welcome.lines.map((line) => (
        <p key={line} className="dim">
          {line}
        </p>
      ))}
      <div className="welcome-links">
        {welcome.links.map((link) => (
          <button key={link.action} type="button" className="link" onClick={() => onLink(link.action)}>
            {link.text}
          </button>
        ))}
      </div>
      {welcome.footnote.split("\n").map((line) => (
        <p key={line} className="faint small">
          {line}
        </p>
      ))}
    </div>
  );
}

export function Thread({
  project,
  turns,
  lives,
  welcome,
  pending,
  motion,
  onLink,
  onType,
  onCopied,
}: {
  project: string | null;
  turns: Turn[];
  lives: Live[];
  welcome: Welcome | null;
  pending: { label: string; detail: string } | null;
  motion: boolean;
  onLink: (action: string) => void;
  onType: (char: string) => void;
  onCopied: (what: string) => void;
}) {
  const scroller = useRef<HTMLDivElement>(null);
  const content = useRef<HTMLDivElement>(null);
  const follow = useRef(true);
  const [behind, setBehind] = useState(false);
  const [menu, setMenu] = useState<{ anchor: Anchor; items: MenuItem[] } | null>(null);
  // What was on screen last time, so a reply that arrives now eases in and history shows at once.
  const seen = useRef<{ project: string | null; count: number }>({ project: null, count: 0 });
  const known = seen.current.project === project ? seen.current.count : turns.length;

  useLayoutEffect(() => {
    seen.current = { project, count: turns.length };
  });

  const atEnd = () => {
    const node = scroller.current;
    return !node || node.scrollHeight - node.scrollTop - node.clientHeight <= AT_END_PX;
  };

  const toEnd = useCallback(() => {
    const node = scroller.current;
    if (!node) return;
    node.scrollTop = node.scrollHeight;
    follow.current = true;
    setBehind(false);
  }, []);

  /** The reader moved the thread: it stops following until they come back to the end. */
  const moved = useCallback(() => {
    follow.current = false;
  }, []);

  // A job opened: start at its end.
  useLayoutEffect(() => {
    toEnd();
  }, [project, toEnd]);

  // Whatever makes the thread taller (a turn, a word, a bubble taking its size) keeps the end in view while following.
  useEffect(() => {
    const node = content.current;
    if (!node) return;
    const observer = new ResizeObserver(() => {
      if (follow.current) {
        const box = scroller.current;
        if (box) box.scrollTop = box.scrollHeight;
      } else {
        setBehind(true);
      }
    });
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  const onScroll = () => {
    if (atEnd()) {
      follow.current = true;
      setBehind(false);
    }
  };

  const onWheel = (event: React.WheelEvent) => {
    if (event.deltaY < 0) moved();
  };

  const onKeyDown = (event: React.KeyboardEvent) => {
    if (MOVE_KEYS.has(event.key)) {
      if (event.key !== "End" && event.key !== "PageDown" && event.key !== "ArrowDown") moved();
      return;
    }
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "a") {
      event.preventDefault();
      selectThread();
      return;
    }
    // Typing while the thread has the focus goes to the composer.
    if (!event.ctrlKey && !event.metaKey && !event.altKey && event.key.length === 1) {
      event.preventDefault();
      onType(event.key);
    }
  };

  const selectThread = () => {
    const node = content.current;
    if (!node) return;
    const range = document.createRange();
    range.selectNodeContents(node);
    const selection = window.getSelection();
    selection?.removeAllRanges();
    selection?.addRange(range);
  };

  const threadText = () =>
    turns.map((turn) => (turn.role === "user" ? `You\n${turn.text}` : plainText(turn.text))).join("\n\n");

  const copy = (text: string, what: string) => {
    void navigator.clipboard?.writeText(text).then(() => onCopied(what));
  };

  const openMenu = (event: React.MouseEvent, message?: string) => {
    event.preventDefault();
    event.stopPropagation();
    const selected = window.getSelection()?.toString() || "";
    const items: MenuItem[] = [];
    if (message !== undefined) items.push({ label: "Copy message", onSelect: () => copy(message, "Message copied.") });
    items.push({ label: "Copy", hint: "Ctrl+C", disabled: !selected, onSelect: () => copy(selected, "Copied.") });
    items.push({ label: "Select all", hint: "Ctrl+A", onSelect: selectThread });
    items.push({ label: "Copy the whole conversation", onSelect: () => copy(threadText(), "Conversation copied.") });
    setMenu({ anchor: { x: event.clientX, y: event.clientY }, items });
  };

  const bubbleMenu = useCallback((event: React.MouseEvent, text: string) => openMenu(event, text), [turns]); // eslint-disable-line react-hooks/exhaustive-deps

  // The newest turn of a job carries its live reply's key, so the words on screen carry on into it.
  const lastOfJob = new Map<string, number>();
  turns.forEach((turn, index) => {
    if (turn.job_id) lastOfJob.set(turn.job_id, index);
  });
  const items: Item[] = turns.map((turn, index) => ({
    key:
      turn.role === "assistant" && turn.job_id && lastOfJob.get(turn.job_id) === index
        ? `${project}:j${turn.job_id}`
        : `${project}:${turn.role === "user" ? "u" : "t"}${index}`,
    role: turn.role,
    text: turn.text,
    live: false,
    fromStart: index >= known,
  }));
  const shownJobs = new Set(turns.map((turn) => turn.job_id).filter(Boolean));
  for (const live of lives) {
    if (shownJobs.has(live.jobId)) continue;
    items.push({ key: `${project}:j${live.jobId}`, role: "assistant", text: live.text, live: true, fromStart: true });
  }

  return (
    <div className="thread-wrap">
      <div
        ref={scroller}
        className="thread-scroll"
        tabIndex={0}
        aria-label="Conversation"
        onScroll={onScroll}
        onWheel={onWheel}
        onPointerDown={(event) => {
          // A press on the scrollbar (outside the content) moves the thread before any release.
          if (event.target === scroller.current) moved();
        }}
        onKeyDown={onKeyDown}
        onContextMenu={(event) => openMenu(event)}
      >
        <div ref={content} className="thread-column">
          {welcome && !items.length ? <WelcomeView welcome={welcome} onLink={onLink} /> : null}
          {items.map((item) =>
            item.role === "user" ? (
              <Bubble key={item.key} text={item.text} onMenu={bubbleMenu} />
            ) : (
              <div key={item.key} className="turn assistant">
                <ReplyText text={item.text} motion={motion} fromStart={item.fromStart} live={item.live} />
              </div>
            ),
          )}
          {pending ? <WorkingLine pending={pending} motion={motion} /> : null}
        </div>
      </div>
      {behind ? (
        <button type="button" className="jump" onClick={toEnd}>
          <ArrowDown /> Latest
        </button>
      ) : null}
      {menu ? <Menu items={menu.items} anchor={menu.anchor} onClose={() => setMenu(null)} label="Thread" /> : null}
    </div>
  );
}
