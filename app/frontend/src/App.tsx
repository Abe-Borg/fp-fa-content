/**
 * The +Cynosure window: the sidebar of jobs, the thread with its composer, and
 * the Zone details drawer, closed until it is wanted. Everything shown comes
 * from the app's state (app/fpfa/desk.py) over the event stream; everything
 * done is one POST. The page keeps only what is its own: which panel is open,
 * the words in the composer, and the fields being typed.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { connect, getState, getText, post } from "./api";
import { mergeForm, PatchQueue } from "./form";
import type { FormValues, Live, State, Turn } from "./types";
import { Sidebar } from "./components/Sidebar";
import { Thread } from "./components/Thread";
import { Composer, type ComposerHandle } from "./components/Composer";
import { Drawer, type Tab } from "./components/Drawer";
import { SettingsDialog } from "./components/Settings";
import { ConfirmDialog, MessageDialog, PromptDialog, TextDialog } from "./components/Dialog";
import { MenuButton, type MenuItem } from "./components/Menu";
import { Chevron, Close, More, Panel } from "./components/icons";

type Dialog =
  | { kind: "delete"; id: string; name: string }
  | { kind: "rename"; id: string; name: string }
  | { kind: "text"; which: "about" | "license" | "notices"; text: string | null }
  | { kind: "error"; message: string };

/** What draws the window: WebView2 reports itself as Edge in its user agent. */
function windowEngine(): string {
  const agent = navigator.userAgent;
  const edge = /Edg\/([\d.]+)/.exec(agent);
  if (edge) return `Edge engine ${edge[1]} (WebView2 in the app window)`;
  const chrome = /Chrome\/([\d.]+)/.exec(agent);
  if (chrome) return `a browser (Chromium ${chrome[1]})`;
  return `a browser (${agent})`;
}

function usePrefersReducedMotion(): boolean {
  const query = typeof window !== "undefined" ? window.matchMedia?.("(prefers-reduced-motion: reduce)") : undefined;
  const [reduced, setReduced] = useState(!!query?.matches);
  useEffect(() => {
    if (!query) return;
    const change = () => setReduced(query.matches);
    query.addEventListener?.("change", change);
    return () => query.removeEventListener?.("change", change);
  }, [query]);
  return reduced;
}

export function App() {
  const [state, setState] = useState<State | null>(null);
  const [turns, setTurns] = useState<Turn[]>([]);
  const lives = useRef(new Map<string, Live>());
  const [, setLiveTick] = useState(0);
  const [connected, setConnected] = useState(true);
  const [values, setValues] = useState<FormValues>({});
  const formRev = useRef(-1);
  const [drawer, setDrawer] = useState(false);
  const [tab, setTab] = useState<Tab>("zone");
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [dialog, setDialog] = useState<Dialog | null>(null);
  const [flash, setFlash] = useState("");
  const composer = useRef<ComposerHandle>(null);
  const reduced = usePrefersReducedMotion();

  const queue = useMemo(() => new PatchQueue((patch) => post("form", { values: patch }).then(() => undefined)), []);
  const unsent = useRef(new Set<string>());

  const apply = useCallback((next: State) => {
    if (next.thread.turns) setTurns(next.thread.turns);
    if (next.lives) {
      lives.current = new Map(next.lives.map((item) => [item.job_id, { jobId: item.job_id, projectId: next.open?.id ?? null, gen: item.gen, text: item.text }]));
      setLiveTick((count) => count + 1);
    }
    if (next.form.rev !== formRev.current) {
      formRev.current = next.form.rev;
      setValues((local) => mergeForm(next.form.values, local, unsent.current));
    }
    document.documentElement.setAttribute("data-theme", next.settings.scheme);
    setState(next);
  }, []);

  const resync = useCallback(() => {
    getState().then(apply).catch(() => setConnected(false));
  }, [apply]);

  useEffect(() => {
    resync();
    return connect({
      state: apply,
      connected: setConnected,
      live: (event) => {
        const current = lives.current.get(event.job_id);
        let text: string;
        if (event.start === 0) text = event.text;
        else if (current && current.gen === event.gen && current.text.length === event.start) text = current.text + event.text;
        else {
          resync();
          return;
        }
        lives.current.set(event.job_id, { jobId: event.job_id, projectId: event.project_id, gen: event.gen, text });
        setLiveTick((count) => count + 1);
      },
      liveEnd: (event) => {
        lives.current.delete(event.job_id);
        setLiveTick((count) => count + 1);
      },
    });
  }, [apply, resync]);

  /** One action: the fields being typed reach the app first, then the action runs there. */
  const act = useCallback(
    async (action: string, body: Record<string, unknown> = {}) => {
      try {
        try {
          await queue.flush();
        } catch (error) {
          const why = error instanceof Error ? error.message : String(error);
          throw new Error(`The Zone details fields did not reach the app, so nothing was done. Your edits are kept; try again. (${why})`);
        }
        unsent.current.clear();
        return await post(action, body);
      } catch (error) {
        setDialog({ kind: "error", message: error instanceof Error ? error.message : String(error) });
        return null;
      }
    },
    [queue],
  );

  const setField = useCallback(
    (name: string, value: string | boolean) => {
      setValues((current) => ({ ...current, [name]: value }));
      unsent.current.add(name);
      queue.set(name, value);
    },
    [queue],
  );

  const say = useCallback((text: string) => {
    setFlash(text);
    window.setTimeout(() => setFlash((current) => (current === text ? "" : current)), 2500);
  }, []);

  const showText = useCallback((which: "about" | "license" | "notices") => {
    setDialog({ kind: "text", which, text: null });
    getText(which)
      .then((text) => (which === "about" ? `${text}\nWindow ${windowEngine()}` : text))
      .then((text) => setDialog((current) => (current && current.kind === "text" && current.which === which ? { ...current, text } : current)))
      .catch((error) => setDialog({ kind: "error", message: String(error.message || error) }));
  }, []);

  const openTeam = useCallback(() => {
    setDrawer(true);
    setTab("team");
  }, []);

  // Ctrl+S saves the open job and Ctrl+N starts a new chat, wherever the focus is.
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (!(event.ctrlKey || event.metaKey) || event.altKey) return;
      const key = event.key.toLowerCase();
      if (key === "s") {
        event.preventDefault();
        void act("save");
      } else if (key === "n") {
        event.preventDefault();
        void act("new").then(() => composer.current?.focus());
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [act]);

  // The thread is the main surface: the cursor starts in the composer once the window has drawn.
  const ready = state !== null;
  useEffect(() => {
    if (ready) composer.current?.focus();
  }, [ready]);

  if (!state) {
    return (
      <div className="loading" role="status">
        {connected ? "Opening +Cynosure…" : "The app is not answering. It may have closed."}
      </div>
    );
  }

  const motion = !state.settings.reduce_motion && !reduced;
  const openId = state.open?.id ?? null;
  const shownLives = [...lives.current.values()].filter((live) => live.projectId === openId && live.text);
  const app = state.app;
  const notice = state.notices[0];

  const moreItems = (): MenuItem[] => [
    { label: "Sample DI zone", hint: "/sample-di", onSelect: () => void act("sample-di") },
    { label: "Sample BESS room", hint: "/sample-bess", onSelect: () => void act("sample-bess") },
    { kind: "separator" },
    { label: "Run zone from Zone details", hint: "/run", onSelect: () => void act("run") },
    { label: `Export draft Section ${app.draft_section}…`, onSelect: () => void act("export-section") },
    { label: `Export ${app.design_basis_title}…`, onSelect: () => void act("export-basis") },
    { label: "Team panel", onSelect: openTeam },
    { label: "Usage and cost", hint: "/usage", onSelect: () => void act("usage") },
    { kind: "separator" },
    { kind: "check", label: "Narrate zone runs with Claude", checked: state.narrate, onSelect: () => void act("narrate", { on: !state.narrate }) },
    { kind: "separator" },
    {
      label: "Rename job…",
      disabled: !state.open,
      onSelect: () => state.open && setDialog({ kind: "rename", id: state.open.id, name: state.open.name }),
    },
    { label: "Settings…", onSelect: () => setSettingsOpen(true) },
    { label: "Commands", hint: "/help", onSelect: () => void act("help") },
    { label: "About and versions", onSelect: () => showText("about") },
  ];

  const modeItems = (): MenuItem[] =>
    state.mode.choices.map((slug) => ({
      kind: "radio" as const,
      label: slug.charAt(0).toUpperCase() + slug.slice(1),
      checked: slug === state.mode.slug,
      onSelect: () => void act("mode", { slug }),
    }));

  const projectName = (id: string) => state.projects.find((project) => project.id === id)?.name || "this job";

  return (
    <div className={`window${drawer ? " with-drawer" : ""}`}>
      {state.banner ? (
        <div className="banner-row">
          <button type="button" className="banner" onClick={() => void act("banner-dismiss")} title="Dismiss">
            <span className="pre-line">{state.banner}</span>
            <Close />
          </button>
        </div>
      ) : null}
      <div className="body">
        <Sidebar
          app={app}
          projects={state.projects}
          openId={openId}
          activity={state.activity}
          roster={state.team.roster}
          onNew={() => void act("new").then(() => composer.current?.focus())}
          onOpen={(id) => void act("open", { id })}
          onRename={(id) => setDialog({ kind: "rename", id, name: projectName(id) })}
          onDelete={(id) => setDialog({ kind: "delete", id, name: projectName(id) })}
          onTeam={openTeam}
          onSettings={() => setSettingsOpen(true)}
        />
        <main className="chat">
          <header className="topbar">
            <h1 className="job-title display" title={state.title}>
              {state.title}
            </h1>
            <MenuButton
              items={modeItems}
              className="button toolbar"
              label="Mode"
              title="How the assistant answers: brainstorm, calculator, synthesis, or mixed"
            >
              Mode: {state.mode.slug} <Chevron />
            </MenuButton>
            <button
              type="button"
              className={`button toolbar${drawer ? " on" : ""}`}
              aria-pressed={drawer}
              title="Zone inputs, results, and the team"
              onClick={() => setDrawer(!drawer)}
            >
              <Panel /> Zone details
            </button>
            <MenuButton items={moreItems} className="icon-button more" label="More" title="Samples, exports, usage, settings" align="right">
              <More />
            </MenuButton>
          </header>
          <Thread
            project={state.thread.project}
            turns={turns}
            lives={shownLives}
            welcome={state.welcome}
            pending={state.pending}
            motion={motion}
            onLink={(action) => (action === "settings" ? setSettingsOpen(true) : void act(action))}
            onType={(char) => composer.current?.type(char)}
            onCopied={say}
          />
          <Composer
            ref={composer}
            placeholder={app.placeholder}
            hint={app.composer_hint}
            chips={state.chips}
            running={state.running_here}
            onSend={(text) => void act("send", { text })}
            onStop={() => void act("cancel")}
          />
          <footer className="footer">
            <span className="status" role="status" title={state.status_full}>
              {!connected ? "Reconnecting to the app…" : flash || state.status}
            </span>
            <span className="content-status">{state.content_status}</span>
          </footer>
        </main>
        {drawer ? (
          <Drawer
            tab={tab}
            setTab={setTab}
            form={state.form}
            values={values}
            set={setField}
            results={state.results}
            team={state.team}
            running={state.running_here}
            onClose={() => setDrawer(false)}
            onRun={() => void act("run")}
            onAddSegment={async (row) => {
              const reply = await act("segment-add", row);
              return !!(reply && reply.result);
            }}
            onRemoveSegment={(index) => void act("segment-remove", { index })}
            onCancel={() => void act("cancel")}
            onCheck={() => void act("check-record")}
            onExportBasis={() => void act("export-basis")}
          />
        ) : null}
      </div>
      {settingsOpen ? (
        <SettingsDialog app={app} settings={state.settings} onClose={() => setSettingsOpen(false)} act={act} onText={showText} />
      ) : null}
      {dialog?.kind === "delete" ? (
        <ConfirmDialog
          title="Delete job"
          message={`Delete “${dialog.name}” and its chat from this machine?`}
          yes="Delete"
          danger
          onAnswer={(yes) => {
            setDialog(null);
            if (yes) void act("delete", { id: dialog.id });
          }}
        />
      ) : null}
      {dialog?.kind === "rename" ? (
        <PromptDialog
          title="Rename job"
          label="Job name"
          initial={dialog.name}
          ok="Rename"
          onAnswer={(name) => {
            setDialog(null);
            if (name && name.trim()) void act("rename", { id: dialog.id, name });
          }}
        />
      ) : null}
      {dialog?.kind === "text" ? (
        <TextDialog
          title={dialog.which === "about" ? `About ${app.name}` : dialog.which === "license" ? `${app.name} license` : "Third-party notices"}
          heading={dialog.which === "notices" ? "Third-party notices" : dialog.which === "license" ? app.license_name : app.name}
          note={
            dialog.which === "about"
              ? `${app.tagline} for hyperscale data centers. Licensed under the ${app.license_name}.`
              : dialog.which === "license"
                ? `${app.license_summary} ${app.use_notice}`
                : `${app.name} is built on these open-source projects. Each keeps its own license.`
          }
          text={dialog.text}
          onClose={() => setDialog(null)}
        />
      ) : null}
      {dialog?.kind === "error" ? <MessageDialog title="Something went wrong" message={dialog.message} tone="error" onClose={() => setDialog(null)} /> : null}
      {!dialog && notice ? (
        <MessageDialog title={notice.title} message={notice.message} tone={notice.kind} onClose={() => void act("notice-dismiss", { id: notice.id })} />
      ) : null}
    </div>
  );
}
