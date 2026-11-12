/**
 * Where the designer types. Enter sends, Shift+Enter starts a new line, and the
 * box grows with what is typed. One-tap suggestions sit above it while there
 * are any. Under the words, inside the box: Send on the right, with Stop beside
 * it while a job on this job is running. A running job never locks the
 * composer. One line under the box says what the app last did.
 */
import { forwardRef, useImperativeHandle, useLayoutEffect, useRef, useState } from "react";
import { ArrowUp, Square } from "./icons";

export interface ComposerHandle {
  focus: () => void;
  type: (text: string) => void;
}

const MIN_ROWS = 1;
const MAX_ROWS = 8;

export const Composer = forwardRef<ComposerHandle, {
  placeholder: string;
  hint: string;
  status: string;
  statusTitle: string;
  chips: { label: string; action: string }[];
  running: boolean;
  onSend: (text: string) => void;
  onStop: () => void;
}>(function Composer({ placeholder, hint, status, statusTitle, chips, running, onSend, onStop }, handle) {
  const [text, setText] = useState("");
  const box = useRef<HTMLTextAreaElement>(null);

  useImperativeHandle(handle, () => ({
    focus: () => box.current?.focus(),
    type: (char: string) => {
      const node = box.current;
      if (!node) return;
      node.focus();
      const start = node.selectionStart ?? text.length;
      const end = node.selectionEnd ?? text.length;
      const next = text.slice(0, start) + char + text.slice(end);
      setText(next);
      requestAnimationFrame(() => node.setSelectionRange(start + char.length, start + char.length));
    },
  }), [text]);

  // The box grows with its text, from one line to eight, then scrolls.
  useLayoutEffect(() => {
    const node = box.current;
    if (!node) return;
    const style = getComputedStyle(node);
    const line = parseFloat(style.lineHeight) || 22;
    const padding = parseFloat(style.paddingTop) + parseFloat(style.paddingBottom);
    node.style.height = "auto";
    const wanted = Math.min(Math.max(node.scrollHeight, line * MIN_ROWS + padding), line * MAX_ROWS + padding);
    node.style.height = `${wanted}px`;
    node.style.overflowY = node.scrollHeight > wanted + 1 ? "auto" : "hidden";
  }, [text]);

  const send = () => {
    const value = text.trim();
    if (!value) return;
    setText("");
    onSend(value);
  };

  return (
    <div className="composer-row">
      {chips.length ? (
        <div className="chips" role="group" aria-label="Suggestions">
          {chips.map((chip) => (
            <button key={chip.label} type="button" className="chip" title={chip.action} onClick={() => onSend(chip.action)}>
              {chip.label}
            </button>
          ))}
        </div>
      ) : null}
      <div className="composer" onClick={(event) => event.target === event.currentTarget && box.current?.focus()}>
        <textarea
          ref={box}
          rows={MIN_ROWS}
          value={text}
          placeholder={placeholder}
          aria-label="Message"
          spellCheck
          onChange={(event) => setText(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
              event.preventDefault();
              send();
            }
          }}
        />
        <div className="composer-bar">
          <span className="grow" />
          {running ? (
            <button type="button" className="button stop" title="Stop the running job before its next model round" onClick={onStop}>
              <Square /> Stop
            </button>
          ) : null}
          <button type="button" className="button accent send" onClick={send} disabled={!text.trim()} title="Send (Enter)">
            <ArrowUp /> Send
          </button>
        </div>
      </div>
      <div className="composer-foot">
        <span className="status" role="status" title={statusTitle}>
          {status}
        </span>
        <span className="hint">{hint}</span>
      </div>
    </div>
  );
});
