/**
 * Where the designer types. Enter sends, Shift+Enter starts a new line, and the
 * box grows with what is typed. One-tap suggestions sit above it while there
 * are any, and Stop sits under it while a job on this job is running. A running
 * job never locks the composer.
 */
import { forwardRef, useImperativeHandle, useLayoutEffect, useRef, useState } from "react";

export interface ComposerHandle {
  focus: () => void;
  type: (text: string) => void;
}

const MIN_ROWS = 2;
const MAX_ROWS = 8;

export const Composer = forwardRef<ComposerHandle, {
  placeholder: string;
  hint: string;
  chips: { label: string; action: string }[];
  running: boolean;
  onSend: (text: string) => void;
  onStop: () => void;
}>(function Composer({ placeholder, hint, chips, running, onSend, onStop }, handle) {
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

  // The box grows with its text, from two lines to eight, then scrolls.
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
      <div className="composer">
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
        <button type="button" className="button accent send" onClick={send} disabled={!text.trim()}>
          Send
        </button>
      </div>
      <div className="composer-foot">
        <span className="faint small">{hint}</span>
        {running ? (
          <button type="button" className="chip stop" title="Stop the running job before its next model round" onClick={onStop}>
            Stop
          </button>
        ) : null}
      </div>
    </div>
  );
});
