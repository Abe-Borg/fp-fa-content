/** The shape of Desk.snapshot() (app/fpfa/desk.py). The page draws only this. */

export interface Turn {
  role: "user" | "assistant";
  text: string;
  job_id?: string;
}

export interface ActivityRow {
  id: string;
  kind: string;
  status: string;
  project_id: string;
  project_name: string;
  glyph: string;
  tone: string;
  line: string;
  heading: string;
  error: string;
}

export interface Handoff {
  id: string;
  when: string;
  from: string;
  to: string;
  status: string;
  brief: string;
  detail: string;
  /** delegation, consult, or handoff, and the word the panel shows for it. */
  kind: string;
  kind_word: string;
}

export interface PlanStep {
  title: string;
  owner: string;
  status: string;
  mark: string;
}

export interface Person {
  slug: string;
  name: string;
  status: string;
  glyph: string;
  findings: number;
  reviews: number;
}

export interface TeamQuestion {
  id: string;
  text: string;
  by: string;
}

export interface FindingReview {
  by: string;
  position: string;
  note: string;
  status: string;
  how: string;
}

/** One finding with what it rests on and how far the trace check took it. */
export interface FindingRow {
  id: string;
  text: string;
  label: string;
  by: string;
  tier: string;
  tier_title: string;
  verdict: string;
  rests_on: string[];
  checked_against: string[];
  why: string[];
  reviews: FindingReview[];
}

export interface Disagreement {
  id: string;
  finding_id: string;
  by: string;
  author: string;
  finding: string;
  note: string;
  status: string;
  resolution: string;
}

export interface Team {
  roster: string[];
  roster_text: string;
  blockers: string[];
  blockers_text: string;
  check_line: string;
  handoffs: Handoff[];
  /** One line on the job for the main view. Empty before any team work. */
  strip: string;
  /** How many things are waiting on someone. */
  attention: number;
  plan: { objective: string; steps: PlanStep[] } | null;
  people: Person[];
  asks: TeamQuestion[];
  rfis: TeamQuestion[];
  answered: { id: string; text: string; answer: string; by: string }[];
  stale: { kind: string; id: string; by: string; text: string; why: string }[];
  changes: string[];
  disagreements: Disagreement[];
  conflicts: { key: string; values: { by: string; value: string }[] }[];
  alternatives: { id: string; by: string; finding: string; why: string }[];
  settled: { id: string; by: string; author: string; finding: string; note: string; how: string }[];
  tiers: { tier: string; title: string; note: string; count: number }[];
  findings: FindingRow[];
  inputs: { id: string; name: string; text: string; source: string; unconfirmed: boolean; blank: boolean }[];
  interrupted: string[];
  export: { ready: boolean; reason: string } | null;
  not_standard: string;
  unseen_answers?: number;
}

export interface Segment {
  role: string;
  nps: string | number;
  schedule: string;
  length_ft: string | number;
  d_in: string;
}

export type FormValues = Record<string, string | boolean>;

export interface Form {
  rev: number;
  values: FormValues;
  segments: Segment[];
  assumptions: string;
  choices: Record<string, string[]>;
  roles: string[];
}

export interface SchemeInfo {
  id: string;
  name: string;
  blurb: string;
  dark: boolean;
  colors: Record<string, string>;
}

export interface Settings {
  scheme: string;
  schemes: SchemeInfo[];
  reduce_motion: boolean;
  reduce_motion_forced: boolean;
  key_saved: boolean;
  key_status: string;
  key_message: string;
  key_help: string;
  content_version: string;
  content_line: string;
  changelog: string;
  feed_url: string;
  content_root: string;
  checking_content: boolean;
}

export interface Notice {
  id: number;
  title: string;
  message: string;
  kind: string;
}

export interface Welcome {
  title: string;
  lines: string[];
  links: { text: string; action: string }[];
  footnote: string;
}

export interface AppInfo {
  name: string;
  strapline: string;
  tagline: string;
  version: string;
  copyright: string;
  license_name: string;
  license_summary: string;
  use_notice: string;
  model: string;
  draft_section: string;
  design_basis_title: string;
  placeholder: string;
  composer_hint: string;
}

export interface LiveItem {
  job_id: string;
  gen: number;
  text: string;
}

export interface State {
  revision: number;
  app: AppInfo;
  status: string;
  status_full: string;
  content_status: string;
  banner: string;
  projects: { id: string; name: string }[];
  open: { id: string; name: string } | null;
  title: string;
  mode: { slug: string; choices: string[] };
  narrate: boolean;
  activity: ActivityRow[];
  pending: { label: string; detail: string } | null;
  running_here: boolean;
  chips: { label: string; action: string }[];
  welcome: Welcome | null;
  team: Team;
  form: Form;
  results: string;
  /** Said above the Results tab when the form changed after the run it shows. Empty when the run is current. */
  results_note: string;
  run_changes: string[];
  notices: Notice[];
  settings: Settings;
  live_rev: number;
  thread: { rev: number; project: string | null; turns?: Turn[] };
  lives?: LiveItem[];
}

/** A reply still arriving, as the page keeps it. */
export interface Live {
  jobId: string;
  projectId: string | null;
  gen: number;
  text: string;
}
