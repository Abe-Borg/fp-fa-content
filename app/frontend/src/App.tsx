/**
 * The +Cynosure window: the job list on the left, the thread with its
 * composer in the middle, and the job panel on the right, which the top bar
 * opens on Inputs, Results, or Team. Everything shown comes from the app's
 * state (app/fpfa/desk.py) over the event stream; everything done is one
 * POST. The page keeps only what is its own: how the window is laid out
 * (src/layout.ts, which the app remembers between runs), the words in the
 * composer, and the fields being typed.
 */
import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { connect, getState, getText, post } from "./api";
import { mergeForm, PatchQueue } from "./form";
import type { FormValues, Live, State, Turn } from "./types";
import { DEFAULT_LAYOUT, TABS, panelWidth, readLayout, type Layout, type Tab } from "./layout";
import { Sidebar } from "./components/Sidebar";
import { Thread } from "./components/Thread";
import { Composer, type ComposerHandle } from "./components/Composer";
import { JobPanel } from "./components/JobPanel";
import { Inputs } from "./components/Inputs";
import { Results } from "./components/Results";
import { TeamPanel } from "./components/TeamPanel";
import { SettingsDialog } from "./components/Settings";
import { ConfirmDialog, MessageDialog, PromptDialog, TextDialog } from "./components/Dialog";
import { MenuButton, type MenuItem } from "./components/Menu";
import { Close, More, SidePane, Widen } from "./components/icons";

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
  // How the window is laid out. The app's state gives it once, at launch; after that it is the page's.
  const [layout, setLayoutState] = useState<Layout>(DEFAULT_LAYOUT);
  const layoutRead = useRef(false);
  const layoutUnsent = useRef<Partial<Layout>>({});
  const layoutTimer = useRef<number | null>(null);
  const runRev = useRef<number | null>(null);
  const stage = useRef<HTMLDivElement>(null);
  const [stageWidth, setStageWidth] = useState(0);
  // The panel in the thread's place. It is for the moment, so a launch always opens on the thread.
  const [across, setAcross] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [dialog, setDialog] = useState<Dialog | null>(null);
  const [flash, setFlash] = useState("");
  const composer = useRef<ComposerHandle>(null);
  const reduced = usePrefersReducedMotion();

  const queue = useMemo(() => new PatchQueue((patch) => post("form", { values: patch }).then(() => undefined)), []);
  const unsent = useRef(new Set<string>());

  /** A change to the layout: drawn at once, and told to the app a moment later so it is there next launch. */
  const changeLayout = useCallback((patch: Partial<Layout>) => {
    setLayoutState((current) => ({ ...current, ...patch }));
    layoutUnsent.current = { ...layoutUnsent.current, ...patch };
    if (layoutTimer.current !== null) window.clearTimeout(layoutTimer.current);
    layoutTimer.current = window.setTimeout(() => {
      const values = layoutUnsent.current;
      layoutUnsent.current = {};
      layoutTimer.current = null;
      post("layout", { values }).catch(() => undefined);
    }, 250);
  }, []);

  // A change made a moment before the window closes still reaches the app.
  useEffect(() => {
    const flush = () => {
      if (layoutTimer.current === null) return;
      window.clearTimeout(layoutTimer.current);
      layoutTimer.current = null;
      const values = layoutUnsent.current;
      layoutUnsent.current = {};
      post("layout", { values }, true).catch(() => undefined);
    };
    window.addEventListener("pagehide", flush);
    return () => window.removeEventListener("pagehide", flush);
  }, []);

  const apply = useCallback((next: State) => {
    if (next.thread.turns) setTurns(next.thread.turns);
    if (!layoutRead.current) {
      layoutRead.current = true;
      setLayoutState(readLayout(next.settings.layout));
    }
    // A run landed on the open job: its figures are shown, unless a field of the panel is being typed in.
    if (runRev.current !== null && next.run_rev > runRev.current) {
      const typing = document.activeElement?.closest(".job-panel") && /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
      if (!typing) changeLayout({ panel: "results" });
    }
    runRev.current = next.run_rev;
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
  }, [changeLayout]);

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
          throw new Error(`The fields of the Inputs tab did not reach the app, so nothing was done. Your edits are kept; try again. (${why})`);
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

  const openTab = useCallback((tab: Tab) => changeLayout({ panel: tab }), [changeLayout]);

  /** A new chat is typed into: the thread comes back if the panel had its place. */
  const newChat = useCallback(() => {
    setAcross(false);
    void act("new").then(() => composer.current?.focus());
  }, [act]);

  // Ctrl+S saves the open job, Ctrl+N starts a new chat, and Ctrl+B hides or shows the job list, wherever the focus is.
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (!(event.ctrlKey || event.metaKey) || event.altKey) return;
      const key = event.key.toLowerCase();
      if (key === "s") {
        event.preventDefault();
        void act("save");
      } else if (key === "n") {
        event.preventDefault();
        newChat();
      } else if (key === "b") {
        event.preventDefault();
        changeLayout({ sidebar: !layout.sidebar });
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [act, newChat, changeLayout, layout.sidebar]);

  // The thread is the main surface: the cursor starts in the composer once the window has drawn.
  const ready = state !== null;
  useEffect(() => {
    if (ready) composer.current?.focus();
  }, [ready]);

  // The thread and the panel share the stage. Its width says how wide the panel may be, and it is
  // measured before the first paint so a panel left open is drawn at its width at once.
  useLayoutEffect(() => {
    const node = stage.current;
    if (!node) return;
    const measure = () => setStageWidth(node.clientWidth);
    const observer = new ResizeObserver(measure);
    observer.observe(node);
    measure();
    return () => observer.disconnect();
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

  const tab = layout.panel;
  const wide = tab !== "" && across;
  const width = panelWidth(layout.panel_width, stageWidth);
  const run = () => void act("run");

  const moreItems = (): MenuItem[] => [
    { label: "Sample DI zone", hint: "/sample-di", onSelect: () => void act("sample-di") },
    { label: "Sample BESS room", hint: "/sample-bess", onSelect: () => void act("sample-bess") },
    { kind: "separator" },
    { label: "Run zone", hint: "/run", onSelect: run },
    { label: `Export draft Section ${app.draft_section}…`, onSelect: () => void act("export-section") },
    { label: `Export ${app.design_basis_title}…`, onSelect: () => void act("export-basis") },
    { label: "Team panel", onSelect: () => openTab("team") },
    { label: "Where this job stands", hint: "/status", onSelect: () => void act("status") },
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

  const projectName = (id: string) => state.projects.find((project) => project.id === id)?.name || "this job";

  /** A start card or a link of the welcome: three are the page's own, the rest are the server's. */
  const follow = (action: string) => {
    if (action === "settings") setSettingsOpen(true);
    else if (action === "ask") {
      setAcross(false);
      requestAnimationFrame(() => composer.current?.focus());
    }
    else if (action === "inputs") openTab("inputs");
    else void act(action);
  };

  /** The arrow keys walk the three tab buttons of the top bar. */
  const onViewKey = (event: React.KeyboardEvent, index: number) => {
    const step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
    if (!step) return;
    event.preventDefault();
    document.getElementById(`tab-${TABS[(index + step + TABS.length) % TABS.length].id}`)?.focus();
  };

  return (
    <div className="window">
      {state.banner ? (
        <div className="banner-row">
          <button type="button" className="banner" onClick={() => void act("banner-dismiss")} title="Dismiss">
            <span className="pre-line">{state.banner}</span>
            <Close />
          </button>
        </div>
      ) : null}
      <div className={`body${layout.sidebar ? "" : " no-side"}`}>
        {layout.sidebar ? (
          <Sidebar
            app={app}
            projects={state.projects}
            openId={openId}
            activity={state.activity}
            keySaved={state.settings.key_saved}
            contentStatus={state.content_status}
            onNew={newChat}
            onOpen={(id) => void act("open", { id })}
            onRename={(id) => setDialog({ kind: "rename", id, name: projectName(id) })}
            onDelete={(id) => setDialog({ kind: "delete", id, name: projectName(id) })}
            onSettings={() => setSettingsOpen(true)}
          />
        ) : null}
        <div className="work">
          <header className="topbar">
            <button
              type="button"
              className={`icon-button${layout.sidebar ? " on" : ""}`}
              aria-label="Job list"
              aria-pressed={layout.sidebar}
              title={layout.sidebar ? "Hide the job list (Ctrl+B)" : "Show the job list (Ctrl+B)"}
              onClick={() => changeLayout({ sidebar: !layout.sidebar })}
            >
              <SidePane />
            </button>
            <h1 className="job-title display" title={state.title}>
              {state.title}
            </h1>
            {state.team.strip ? (
              <button
                type="button"
                className={`team-strip${state.team.attention ? " waiting" : ""}`}
                onClick={() => openTab("team")}
                title="What the team has done on this job. Opens the Team tab."
              >
                <span className="strip-dot" aria-hidden="true" />
                <span className="visually-hidden">Team: </span>
                <span className="strip-text">{state.team.strip}</span>
              </button>
            ) : (
              <span className="grow" />
            )}
            <div className="views" role="toolbar" aria-label="Job panel">
              {TABS.map((item, index) => (
                <button
                  key={item.id}
                  id={`tab-${item.id}`}
                  type="button"
                  className={`view${tab === item.id ? " on" : ""}`}
                  aria-pressed={tab === item.id}
                  tabIndex={(tab || TABS[0].id) === item.id ? 0 : -1}
                  title={tab === item.id ? `${item.title}. Press again to close the panel.` : item.title}
                  onClick={() => changeLayout({ panel: tab === item.id ? "" : item.id })}
                  onKeyDown={(event) => onViewKey(event, index)}
                >
                  {item.label}
                  {item.id === "team" && state.team.attention ? (
                    <span className="count" title={`${state.team.attention} waiting on someone`}>
                      {state.team.attention}
                      <span className="visually-hidden"> waiting</span>
                    </span>
                  ) : null}
                </button>
              ))}
            </div>
            {tab ? (
              <button
                type="button"
                className={`icon-button${wide ? " on" : ""}`}
                aria-label="Panel across the window"
                aria-pressed={wide}
                title={wide ? "Bring the thread back beside the panel" : "Give the panel the thread's place"}
                onClick={() => setAcross(!wide)}
              >
                <Widen on={wide} />
              </button>
            ) : null}
            <MenuButton items={moreItems} className="icon-button more" label="More" title="Samples, exports, usage, settings" align="right">
              <More />
            </MenuButton>
          </header>
          <div
            ref={stage}
            className={`stage${tab ? " with-panel" : ""}${wide ? " panel-wide" : ""}`}
            style={tab && !wide ? ({ "--panel-want": `${width}px` } as React.CSSProperties) : undefined}
          >
            <main className="chat">
              <Thread
                project={state.thread.project}
                turns={turns}
                lives={shownLives}
                welcome={state.welcome}
                pending={state.pending}
                motion={motion}
                onLink={follow}
                onType={(char) => composer.current?.type(char)}
                onCopied={say}
              />
              <Composer
                ref={composer}
                placeholder={app.placeholder}
                hint={app.composer_hint}
                status={!connected ? "Reconnecting to the app…" : flash || state.status}
                statusTitle={state.status_full}
                chips={state.chips}
                running={state.running_here}
                onSend={(text) => void act("send", { text })}
                onStop={() => void act("cancel")}
              />
            </main>
            {tab ? (
              <JobPanel tab={tab} width={width} stage={stageWidth} wide={wide} onWidth={(next) => changeLayout({ panel_width: next })}>
                {tab === "inputs" ? (
                  <Inputs
                    form={state.form}
                    values={values}
                    set={setField}
                    runNote={state.results_note}
                    onRun={run}
                    onAddSegment={async (row) => {
                      const reply = await act("segment-add", row);
                      return !!(reply && reply.result);
                    }}
                    onRemoveSegment={(index) => void act("segment-remove", { index })}
                  />
                ) : null}
                {tab === "results" ? (
                  <Results
                    view={state.results_view}
                    text={state.results}
                    note={state.results_note}
                    onRun={run}
                    onInputs={() => openTab("inputs")}
                    onSample={() => void act("sample-di")}
                    onCopied={say}
                  />
                ) : null}
                {tab === "team" ? (
                  <TeamPanel
                    team={state.team}
                    running={state.running_here}
                    onCancel={() => void act("cancel")}
                    onCheck={() => void act("check-record")}
                    onExportBasis={() => void act("export-basis")}
                    onStatus={() => void act("status")}
                    onAnswer={async (id, answer) => (await act("answer", { id, answer })) !== null}
                  />
                ) : null}
              </JobPanel>
            ) : null}
          </div>
        </div>
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
