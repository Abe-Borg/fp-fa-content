/**
 * Settings: Appearance (the five colour schemes and Reduce motion), the
 * Anthropic API key, the content pack, and About with the license.
 */
import { useState } from "react";
import type { AppInfo, SchemeInfo, Settings as SettingsState } from "../types";
import { Modal } from "./Dialog";

/** A card shows its scheme in that scheme's own colours, whatever scheme the window is in. */
function SchemeCard({ scheme, chosen, onChoose }: { scheme: SchemeInfo; chosen: boolean; onChoose: () => void }) {
  const c = scheme.colors;
  return (
    <button type="button" className={`scheme-card${chosen ? " chosen" : ""}`} aria-pressed={chosen} onClick={onChoose}>
      <svg className="scheme-preview" viewBox="0 0 160 60" aria-hidden="true" preserveAspectRatio="none">
        <rect width="160" height="60" fill={c.bg} />
        <rect width="34" height="60" fill={c.surface} />
        <rect x="8" y="10" width="18" height="4" rx="1" fill={c.accent} />
        {[0, 1, 2].map((row) => (
          <rect key={row} x="8" y={22 + row * 8} width="18" height="3" rx="1" fill={c.edge} />
        ))}
        <rect x="44" y="12" width="52" height="3" rx="1" fill={c.ink} />
        <rect x="44" y="22" width="40" height="3" rx="1" fill={c.ink_dim} />
        <rect x="44" y="32" width="28" height="3" rx="1" fill={c.ink_faint} />
        <rect x="106" y="8" width="54" height="52" rx="3" fill={c.paper} />
        <rect x="114" y="18" width="26" height="3" rx="1" fill={c.paper_ink} />
        <rect x="114" y="28" width="20" height="3" rx="1" fill={c.accent} />
      </svg>
      <span className="scheme-name">{scheme.name}</span>
      <span className="small dim">{scheme.blurb}</span>
    </button>
  );
}

export function SettingsDialog({
  app,
  settings,
  onClose,
  act,
  onText,
}: {
  app: AppInfo;
  settings: SettingsState;
  onClose: () => void;
  act: (action: string, body?: Record<string, unknown>) => Promise<unknown>;
  onText: (which: "about" | "license" | "notices") => void;
}) {
  const [key, setKey] = useState("");
  const [feed, setFeed] = useState(settings.feed_url);
  const [folder, setFolder] = useState(settings.content_root);
  const [advanced, setAdvanced] = useState(false);

  const saveKey = async () => {
    await act("key-save", { key });
    setKey("");
  };

  return (
    <Modal title="Settings" onClose={onClose} wide className="settings" initialFocus=".scheme-card.chosen">
      <section className="panel">
        <h3 className="display">Appearance</h3>
        <p className="dim small">The window's colour scheme. It changes at once and is remembered.</p>
        <div className="schemes">
          {settings.schemes.map((scheme) => (
            <SchemeCard key={scheme.id} scheme={scheme} chosen={scheme.id === settings.scheme} onChoose={() => void act("scheme", { id: scheme.id })} />
          ))}
        </div>
        <label className="check">
          <input
            type="checkbox"
            checked={settings.reduce_motion}
            disabled={settings.reduce_motion_forced}
            onChange={(event) => void act("motion", { reduce: event.target.checked })}
          />
          <span>
            Reduce motion: show each reply at once instead of easing it in
            {settings.reduce_motion_forced ? " (FPFA_REDUCE_MOTION is set for this run)" : ""}
          </span>
        </label>
      </section>

      <section className="panel">
        <h3 className="display">Anthropic API key</h3>
        <p className="dim small">
          Your own key, used with {app.model}. It stays on this machine and is never written into a job, the chat, or an export.
        </p>
        <form
          className="row"
          onSubmit={(event) => {
            event.preventDefault();
            void saveKey();
          }}
        >
          <input
            className="input grow"
            type="password"
            autoComplete="off"
            placeholder={settings.key_saved ? "A key is saved. Paste a new one to replace it." : "Paste your key"}
            aria-label="Anthropic API key"
            value={key}
            onChange={(event) => setKey(event.target.value)}
          />
          <button type="submit" className="button accent">
            Save key
          </button>
        </form>
        <p className="key-message" role="status">
          {settings.key_message}
        </p>
        <div className="row">
          <button type="button" className="button side" onClick={() => void act("key-check", { key })}>
            Check key
          </button>
          <button type="button" className="button danger-ghost" disabled={!settings.key_saved} onClick={() => void act("key-clear")}>
            Clear key
          </button>
        </div>
        <p className="faint small">{settings.key_help}</p>
      </section>

      <section className="panel">
        <h3 className="display">Content pack</h3>
        <p className="dim small">{settings.content_version}</p>
        <div className="row">
          <button
            type="button"
            className="button side"
            disabled={settings.checking_content}
            onClick={() => void act("content-check", { feed })}
          >
            {settings.checking_content ? "Checking…" : "Check for updates"}
          </button>
          <span className="dim small" role="status">
            {settings.content_line}
          </span>
        </div>
        <p className="faint small">A newer pack is used only after its sha256 matches. Your API key and jobs stay on this machine.</p>
        <div className="section-label">WHAT'S NEW</div>
        <pre className="well changelog">{settings.changelog}</pre>
        <label className="check">
          <input type="checkbox" checked={advanced} onChange={(event) => setAdvanced(event.target.checked)} />
          <span>Advanced: content feed and content pack folder</span>
        </label>
        {advanced ? (
          <div className="advanced">
            <label className="field-label" htmlFor="feed-url">
              Content feed URL
            </label>
            <input id="feed-url" className="input" value={feed} onChange={(event) => setFeed(event.target.value)} spellCheck={false} />
            <label className="field-label" htmlFor="pack-folder">
              Content pack folder (skills/, roles/, modes/, and calcs/ at the top level)
            </label>
            <div className="row">
              <input id="pack-folder" className="input grow" value={folder} onChange={(event) => setFolder(event.target.value)} spellCheck={false} />
              <button type="button" className="button side" onClick={() => void act("content-root", { folder })}>
                Save content pack
              </button>
            </div>
          </div>
        ) : null}
      </section>

      <section className="panel">
        <h3 className="display">About {app.name}</h3>
        <p className="dim small">
          {app.name} {app.version}. {app.copyright}.
        </p>
        <p className="faint small">
          {app.license_summary} {app.use_notice}
        </p>
        <div className="row">
          <button type="button" className="button side" onClick={() => onText("license")}>
            License
          </button>
          <button type="button" className="button side" onClick={() => onText("notices")}>
            Third-party notices
          </button>
          <button type="button" className="button side" onClick={() => onText("about")}>
            About and versions
          </button>
        </div>
      </section>
    </Modal>
  );
}
