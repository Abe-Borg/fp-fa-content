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
}

export interface Team {
  roster: string[];
  roster_text: string;
  blockers: string[];
  blockers_text: string;
  check_line: string;
  handoffs: Handoff[];
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
