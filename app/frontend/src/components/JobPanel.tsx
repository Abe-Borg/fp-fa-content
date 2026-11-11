/**
 * The job panel, on the right of the thread: the tab the top bar chose
 * (Inputs, Results, or Team) and the edge that sizes it. The edge is dragged
 * with the pointer or moved with the arrow keys while it has the focus; Home
 * and End take it to its widest and narrowest, and a double click or Enter
 * gives the panel back its own width. While it is dragged only a CSS variable moves, so
 * the thread is not drawn again for every pixel.
 */
import { useRef, type ReactNode } from "react";
import { PANEL_MIN, TABS, panelMax, widthAfterKey, type Tab } from "../layout";

export function JobPanel({
  tab,
  width,
  stage,
  wide,
  onWidth,
  children,
}: {
  tab: Tab;
  /** The width the panel is drawn at, in CSS pixels. */
  width: number;
  /** The width of the thread and the panel together. */
  stage: number;
  /** The panel has the thread's place: there is no edge to drag. */
  wide: boolean;
  /** The designer set a width. 0 gives the panel back its own. */
  onWidth: (width: number) => void;
  children: ReactNode;
}) {
  const panel = useRef<HTMLElement>(null);
  const drag = useRef<{ x: number; width: number; now: number } | null>(null);
  const label = TABS.find((item) => item.id === tab)?.label || "";

  const holder = () => panel.current?.parentElement || null;

  const onPointerDown = (event: React.PointerEvent<HTMLDivElement>) => {
    if (event.button !== 0) return;
    event.preventDefault();
    event.currentTarget.setPointerCapture(event.pointerId);
    drag.current = { x: event.clientX, width, now: width };
    document.body.classList.add("resizing");
  };

  const onPointerMove = (event: React.PointerEvent<HTMLDivElement>) => {
    const held = drag.current;
    if (!held) return;
    const next = Math.min(Math.max(held.width + (held.x - event.clientX), PANEL_MIN), panelMax(stage));
    held.now = next;
    holder()?.style.setProperty("--panel-w", `${next}px`);
  };

  const release = () => {
    const held = drag.current;
    if (!held) return;
    drag.current = null;
    document.body.classList.remove("resizing");
    holder()?.style.removeProperty("--panel-w");
    if (Math.round(held.now) !== Math.round(held.width)) onWidth(Math.round(held.now));
  };

  return (
    <aside ref={panel} className="job-panel" aria-label={`Job panel: ${label}`}>
      {wide ? null : (
        <div
          className="panel-edge"
          role="separator"
          aria-orientation="vertical"
          aria-label="Width of the job panel"
          aria-valuemin={PANEL_MIN}
          aria-valuemax={panelMax(stage)}
          aria-valuenow={Math.round(width)}
          tabIndex={0}
          title="Drag to size the panel. Double-click, or Enter, for its own width."
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={release}
          onPointerCancel={release}
          onDoubleClick={() => onWidth(0)}
          onKeyDown={(event) => {
            const next = widthAfterKey(event.key, width, stage);
            if (next === null) return;
            event.preventDefault();
            onWidth(next);
          }}
        />
      )}
      {children}
    </aside>
  );
}
