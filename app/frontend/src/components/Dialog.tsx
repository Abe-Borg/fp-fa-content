/**
 * Dialogs in the window's own colours: a message, a question, a name to type,
 * and a long text on a paper sheet (the license, the notices, the versions).
 * Each holds the focus while it is open, Tab stays inside it, and Esc closes it.
 */
import { useEffect, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { Close } from "./icons";

const FOCUSABLE = 'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

export function Modal({
  title,
  onClose,
  children,
  wide = false,
  className = "",
  initialFocus,
}: {
  title: string;
  onClose: () => void;
  children: ReactNode;
  wide?: boolean;
  className?: string;
  initialFocus?: string;
}) {
  const box = useRef<HTMLDivElement>(null);
  const opener = useRef<Element | null>(document.activeElement);

  useEffect(() => {
    const node = box.current;
    const first = (initialFocus && node?.querySelector<HTMLElement>(initialFocus)) || node?.querySelector<HTMLElement>(FOCUSABLE);
    (first || node)?.focus();
    const back = opener.current;
    return () => {
      if (back instanceof HTMLElement) back.focus({ preventScroll: true });
    };
  }, [initialFocus]);

  const onKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === "Escape") {
      event.stopPropagation();
      onClose();
      return;
    }
    if (event.key !== "Tab" || !box.current) return;
    const items = [...box.current.querySelectorAll<HTMLElement>(FOCUSABLE)].filter((item) => item.offsetParent !== null);
    if (!items.length) return;
    const first = items[0];
    const last = items[items.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };

  return createPortal(
    <div className="overlay" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <div
        ref={box}
        className={`dialog${wide ? " wide" : ""} ${className}`}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        tabIndex={-1}
        onKeyDown={onKeyDown}
      >
        <div className="dialog-head">
          <h2>{title}</h2>
          <button type="button" className="icon-button" aria-label="Close" title="Close" onClick={onClose}>
            <Close />
          </button>
        </div>
        {children}
      </div>
    </div>,
    document.body,
  );
}

export function MessageDialog({ title, message, onClose, tone }: { title: string; message: string; onClose: () => void; tone?: string }) {
  return (
    <Modal title={title} onClose={onClose} initialFocus=".dialog-actions .accent">
      <p className={`dialog-text${tone === "error" ? " err" : ""}`}>{message}</p>
      <div className="dialog-actions">
        <button type="button" className="button accent" onClick={onClose}>
          OK
        </button>
      </div>
    </Modal>
  );
}

export function ConfirmDialog({
  title,
  message,
  yes,
  danger,
  onAnswer,
}: {
  title: string;
  message: string;
  yes: string;
  danger?: boolean;
  onAnswer: (yes: boolean) => void;
}) {
  return (
    <Modal title={title} onClose={() => onAnswer(false)} initialFocus=".dialog-actions .ghost">
      <p className="dialog-text">{message}</p>
      <div className="dialog-actions">
        <button type="button" className="button ghost" onClick={() => onAnswer(false)}>
          Cancel
        </button>
        <button type="button" className={`button ${danger ? "danger" : "accent"}`} onClick={() => onAnswer(true)}>
          {yes}
        </button>
      </div>
    </Modal>
  );
}

export function PromptDialog({
  title,
  label,
  initial,
  ok,
  onAnswer,
}: {
  title: string;
  label: string;
  initial: string;
  ok: string;
  onAnswer: (value: string | null) => void;
}) {
  const [value, setValue] = useState(initial);
  return (
    <Modal title={title} onClose={() => onAnswer(null)} initialFocus="input">
      <form
        onSubmit={(event) => {
          event.preventDefault();
          onAnswer(value);
        }}
      >
        <label className="field-label" htmlFor="prompt-value">
          {label}
        </label>
        <input
          id="prompt-value"
          className="input"
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onFocus={(event) => event.target.select()}
        />
        <div className="dialog-actions">
          <button type="button" className="button ghost" onClick={() => onAnswer(null)}>
            Cancel
          </button>
          <button type="submit" className="button accent" disabled={!value.trim()}>
            {ok}
          </button>
        </div>
      </form>
    </Modal>
  );
}

export function TextDialog({
  title,
  heading,
  note,
  text,
  onClose,
}: {
  title: string;
  heading?: string;
  note?: string;
  text: string | null;
  onClose: () => void;
}) {
  return (
    <Modal title={title} onClose={onClose} wide className="text-dialog" initialFocus=".dialog-actions .accent">
      {heading ? <h3 className="display">{heading}</h3> : null}
      {note ? <p className="dim small">{note}</p> : null}
      <pre className="paper sheet" tabIndex={0}>
        {text === null ? "Reading…" : text}
      </pre>
      <div className="dialog-actions">
        <button
          type="button"
          className="button ghost"
          disabled={!text}
          onClick={() => text && void navigator.clipboard?.writeText(text)}
        >
          Copy
        </button>
        <button type="button" className="button accent" onClick={onClose}>
          Close
        </button>
      </div>
    </Modal>
  );
}
