/**
 * The Results tab: the last run as the figures a designer looks for first,
 * each with the label it carries, then what the run assumed, its flags, the
 * narrative, and the tool transcript for whoever wants to trace a number.
 *
 * The page formats nothing here. Every number, label, and sentence is the
 * app's (app/fpfa/results_panel.py), which prints what the calc tools
 * returned in the words the narrative uses.
 */
import type { Figure, ResultsView } from "../types";

function Tile({ figure }: { figure: Figure }) {
  return (
    <div className={`tile${figure.tone ? ` tone-${figure.tone}` : ""}${figure.code ? " span-all" : ""}`} data-figure={figure.key}>
      <div className="tile-head">
        <span className="tile-title">{figure.title}</span>
        {figure.label ? <span className={`label-chip${figure.label.includes("ASSUMED") ? " assumed" : ""}`}>{figure.label}</span> : null}
      </div>
      {figure.value ? (
        <div className="tile-value">
          <span className="display">{figure.value}</span>
          {figure.unit ? <span className="tile-unit">{figure.unit}</span> : null}
        </div>
      ) : null}
      {figure.code ? <code className="tile-code">{figure.code}</code> : null}
      {figure.verdict ? <p className="tile-verdict">{figure.verdict}</p> : null}
      {figure.lines.map((line) => (
        <p key={line} className="tile-line">
          {line}
        </p>
      ))}
    </div>
  );
}

function Lines({ title, lines, className = "" }: { title: string; lines: string[]; className?: string }) {
  if (!lines.length) return null;
  return (
    <section className={`group ${className}`}>
      <h3 className="group-title">{title}</h3>
      <ul className="evidence">
        {lines.map((line) => (
          <li key={line}>{line}</li>
        ))}
      </ul>
    </section>
  );
}

export function Results({
  view,
  text,
  note,
  onRun,
  onInputs,
  onSample,
  onCopied,
}: {
  view: ResultsView;
  /** The run as plain text, for the clipboard. */
  text: string;
  /** Said above the figures when the form changed after the run they are from. */
  note: string;
  onRun: () => void;
  onInputs: () => void;
  onSample: () => void;
  onCopied: (what: string) => void;
}) {
  if (!view.kind) {
    return (
      <div className="pane results">
        <div className="pane-scroll">
          <div className="empty">
            <h2 className="display">{view.title}</h2>
            {(view.lines || []).map((line) => (
              <p key={line} className="dim">
                {line}
              </p>
            ))}
            <div className="row empty-actions">
              <button type="button" className="button accent" onClick={onInputs}>
                Open Inputs
              </button>
              <button type="button" className="button" onClick={onSample}>
                Load the sample zone
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }
  const figures = view.figures || [];
  return (
    <div className="pane results">
      <div className="pane-scroll">
        {note ? (
          <div className="card callout warn" role="status">
            <p>{note}</p>
            <div className="right">
              <button type="button" className="button on-card" onClick={onRun}>
                Run zone again
              </button>
            </div>
          </div>
        ) : null}
        <header className="results-head">
          <div>
            <h2 className="display">{view.title}</h2>
            <p className="small dim">{view.source}</p>
          </div>
          <button
            type="button"
            className="button quiet"
            title="Copy this run as plain text"
            onClick={() => void navigator.clipboard?.writeText(text).then(() => onCopied("Results copied."))}
          >
            Copy as text
          </button>
        </header>
        {figures.length ? (
          <div className="tiles">
            {figures.map((figure) => (
              <Tile key={figure.key} figure={figure} />
            ))}
          </div>
        ) : null}
        <div className="results-columns">
          <Lines title="Governing figures" lines={view.governing || []} />
          <Lines title="Assumed and calculated" lines={view.notes || []} />
          <Lines title="Warnings" lines={view.warnings || []} className="warnings" />
          <Lines title="Flags" lines={view.flags || []} />
        </div>
        {view.narrative ? (
          <section className="group">
            <h3 className="group-title">Narrative</h3>
            <p className="narrative pre-line">{view.narrative}</p>
          </section>
        ) : null}
        {view.transcript ? (
          <details className="disclosure">
            <summary>Tool transcript</summary>
            <p className="small faint">Each tool the plan ran, with what it was given and what it returned.</p>
            <pre className="paper sheet" tabIndex={0}>
              {view.transcript}
            </pre>
          </details>
        ) : null}
        {view.heading ? <p className="small faint run-heading">{view.heading}</p> : null}
      </div>
    </div>
  );
}
