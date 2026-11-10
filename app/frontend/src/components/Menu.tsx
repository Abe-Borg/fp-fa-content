/**
 * A drop-down menu in the window's own colours. What the pointer can work, the
 * keyboard can: a menu button opens on a click, Space, Enter, or Down (from the
 * keyboard with the first row chosen); Up and Down move over the rows that can
 * be chosen, Home and End go to the ends, Enter or Space chooses, Esc and Tab
 * close it, and closing puts the focus back on the button that opened it.
 */
import { useEffect, useLayoutEffect, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { Check } from "./icons";

export type MenuItem =
  | { kind: "separator" }
  | {
      kind?: "item" | "check" | "radio";
      label: string;
      hint?: string;
      checked?: boolean;
      disabled?: boolean;
      danger?: boolean;
      onSelect: () => void;
    };

export interface Anchor {
  x: number;
  y: number;
  /** "right": the menu's right edge sits at x. */
  align?: "left" | "right";
}

function choosable(item: MenuItem): boolean {
  return item.kind !== "separator" && !item.disabled;
}

export function Menu({
  items,
  anchor,
  onClose,
  keyboard = false,
  label,
}: {
  items: MenuItem[];
  anchor: Anchor;
  onClose: (chose: boolean) => void;
  keyboard?: boolean;
  label?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState(() => (keyboard ? items.findIndex(choosable) : -1));
  const [place, setPlace] = useState<{ left: number; top: number }>({ left: anchor.x, top: anchor.y });

  useLayoutEffect(() => {
    const menu = ref.current;
    if (!menu) return;
    const rect = menu.getBoundingClientRect();
    let left = anchor.align === "right" ? anchor.x - rect.width : anchor.x;
    let top = anchor.y;
    left = Math.max(8, Math.min(left, window.innerWidth - rect.width - 8));
    if (top + rect.height > window.innerHeight - 8) top = Math.max(8, window.innerHeight - rect.height - 8);
    setPlace({ left, top });
    menu.focus();
  }, [anchor.x, anchor.y, anchor.align]);

  useEffect(() => {
    const away = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) onClose(false);
    };
    const blur = () => onClose(false);
    document.addEventListener("mousedown", away, true);
    window.addEventListener("blur", blur);
    window.addEventListener("resize", blur);
    return () => {
      document.removeEventListener("mousedown", away, true);
      window.removeEventListener("blur", blur);
      window.removeEventListener("resize", blur);
    };
  }, [onClose]);

  const choose = (index: number) => {
    const item = items[index];
    if (!item || item.kind === "separator" || item.disabled) return;
    onClose(true);
    item.onSelect();
  };

  const move = (from: number, step: number) => {
    const count = items.length;
    for (let i = 1; i <= count; i += 1) {
      const next = (from + step * i + count * 4) % count;
      if (choosable(items[next])) return next;
    }
    return from;
  };

  const onKeyDown = (event: React.KeyboardEvent) => {
    switch (event.key) {
      case "ArrowDown":
        setActive((index) => move(index < 0 ? -1 : index, 1));
        break;
      case "ArrowUp":
        setActive((index) => move(index < 0 ? items.length : index, -1));
        break;
      case "Home":
        setActive(items.findIndex(choosable));
        break;
      case "End": {
        let last = -1;
        items.forEach((item, index) => {
          if (choosable(item)) last = index;
        });
        setActive(last);
        break;
      }
      case "Enter":
      case " ":
        if (active >= 0) choose(active);
        break;
      case "Escape":
      case "Tab":
        onClose(false);
        break;
      default:
        return;
    }
    event.preventDefault();
    event.stopPropagation();
  };

  return createPortal(
    <div
      ref={ref}
      className="menu"
      role="menu"
      aria-label={label}
      tabIndex={-1}
      style={{ left: place.left, top: place.top }}
      onKeyDown={onKeyDown}
    >
      {items.map((item, index) =>
        item.kind === "separator" ? (
          <div key={`s${index}`} className="menu-sep" role="separator" />
        ) : (
          <div
            key={`i${index}`}
            role={item.kind === "check" ? "menuitemcheckbox" : item.kind === "radio" ? "menuitemradio" : "menuitem"}
            aria-checked={item.kind === "check" || item.kind === "radio" ? !!item.checked : undefined}
            aria-disabled={item.disabled || undefined}
            className={`menu-item${index === active ? " active" : ""}${item.disabled ? " disabled" : ""}${item.danger ? " danger" : ""}`}
            onMouseEnter={() => !item.disabled && setActive(index)}
            onMouseLeave={() => setActive(-1)}
            onClick={() => choose(index)}
          >
            <span className="menu-mark">{item.kind === "check" || item.kind === "radio" ? item.checked ? <Check /> : null : null}</span>
            <span className="menu-label">{item.label}</span>
            {item.hint ? <span className="menu-hint">{item.hint}</span> : null}
          </div>
        ),
      )}
    </div>,
    document.body,
  );
}

/** A button that opens a menu under itself, from the pointer or the keyboard. */
export function MenuButton({
  items,
  className,
  title,
  align = "left",
  children,
  label,
}: {
  items: () => MenuItem[];
  className?: string;
  title?: string;
  align?: "left" | "right";
  children: ReactNode;
  label: string;
}) {
  const button = useRef<HTMLButtonElement>(null);
  const [open, setOpen] = useState<{ anchor: Anchor; keyboard: boolean } | null>(null);

  const show = (keyboard: boolean) => {
    const rect = button.current!.getBoundingClientRect();
    setOpen({ anchor: { x: align === "right" ? rect.right : rect.left, y: rect.bottom + 4, align }, keyboard });
  };

  return (
    <>
      <button
        ref={button}
        type="button"
        className={className}
        title={title}
        aria-label={label}
        aria-haspopup="menu"
        aria-expanded={open !== null}
        onClick={(event) => (open ? setOpen(null) : show(event.detail === 0))}
        onKeyDown={(event) => {
          if (event.key === "ArrowDown" && !open) {
            event.preventDefault();
            show(true);
          }
        }}
      >
        {children}
      </button>
      {open ? (
        <Menu
          items={items()}
          anchor={open.anchor}
          keyboard={open.keyboard}
          label={label}
          onClose={() => {
            setOpen(null);
            button.current?.focus({ preventScroll: true });
          }}
        />
      ) : null}
    </>
  );
}
