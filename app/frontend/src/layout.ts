/**
 * How the window is laid out: the job list shown or hidden, which tab of the
 * job panel is open, and how wide the panel is beside the thread. The page
 * owns these; the app only remembers them between runs (Desk.set_layout).
 * Pure, so `node --test` pins the arithmetic.
 */

export type Tab = "inputs" | "results" | "team";

export const TABS: { id: Tab; label: string; title: string }[] = [
  { id: "inputs", label: "Inputs", title: "The project basis, the zone, and its pipe" },
  { id: "results", label: "Results", title: "The figures of the last zone run" },
  { id: "team", label: "Team", title: "Where the job stands and what the team found" },
];

export interface Layout {
  /** The job list on the left is shown. */
  sidebar: boolean;
  /** The open tab of the job panel. "" is closed. */
  panel: Tab | "";
  /** The panel's width in CSS pixels as the designer left it. 0 is the page's own width. */
  panel_width: number;
}

export const DEFAULT_LAYOUT: Layout = { sidebar: true, panel: "", panel_width: 0 };

/** The narrowest the panel is drawn, and the narrowest it may leave the thread. */
export const PANEL_MIN = 360;
export const THREAD_MIN = 380;
/** The panel's own width never passes this, so a wide window leaves the thread its room. */
export const PANEL_OWN_MAX = 720;
/** One press of an arrow key on the panel's edge. */
export const PANEL_STEP = 32;

function clamp(value: number, low: number, high: number): number {
  return Math.min(Math.max(value, low), Math.max(low, high));
}

/** The widest the panel may be beside the thread, in a stage this wide. */
export function panelMax(stage: number): number {
  return Math.max(PANEL_MIN, Math.floor(stage - THREAD_MIN));
}

/** The panel's width when the designer has not set one: a little under half the stage. */
export function panelOwn(stage: number): number {
  return clamp(Math.round(stage * 0.44), PANEL_MIN, Math.min(PANEL_OWN_MAX, panelMax(stage)));
}

/** The width the panel is drawn at: what the designer set, held to what this stage can give. */
export function panelWidth(wanted: number, stage: number): number {
  if (!(stage > 0)) return wanted > 0 ? Math.max(PANEL_MIN, Math.round(wanted)) : PANEL_MIN;
  return wanted > 0 ? clamp(Math.round(wanted), PANEL_MIN, panelMax(stage)) : panelOwn(stage);
}

/**
 * What a key does on the panel's edge: Left widens it and Right narrows it by a step, Home
 * takes it as wide as the thread allows, End as narrow as it goes, and Enter gives the panel
 * back its own width (0, as a double click does). null for any other key.
 */
export function widthAfterKey(key: string, width: number, stage: number): number | null {
  switch (key) {
    case "ArrowLeft":
      return clamp(width + PANEL_STEP, PANEL_MIN, panelMax(stage));
    case "ArrowRight":
      return clamp(width - PANEL_STEP, PANEL_MIN, panelMax(stage));
    case "Home":
      return panelMax(stage);
    case "End":
      return PANEL_MIN;
    case "Enter":
      return 0;
    default:
      return null;
  }
}

/** A stored value as a layout. Anything that is not one of ours falls back to the default. */
export function readLayout(value: unknown): Layout {
  const raw = (value && typeof value === "object" ? value : {}) as Record<string, unknown>;
  const panel = TABS.some((tab) => tab.id === raw.panel) ? (raw.panel as Tab) : "";
  const width = typeof raw.panel_width === "number" && raw.panel_width > 0 ? Math.round(raw.panel_width) : 0;
  return {
    sidebar: raw.sidebar === undefined ? DEFAULT_LAYOUT.sidebar : !!raw.sidebar,
    panel,
    panel_width: width,
  };
}

/** A choice's stored value in words: nc_solenoid reads "NC solenoid". The value itself is not changed. */
export function choiceLabel(value: string): string {
  const words = value.replace(/_/g, " ").trim();
  if (!words) return value;
  const text = words.replace(/\bnc\b/gi, "NC");
  return text.charAt(0).toUpperCase() + text.slice(1);
}
