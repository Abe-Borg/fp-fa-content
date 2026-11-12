/**
 * What the lead filled in on the Inputs tab from the designer's own words: a
 * card under the reply, one row per field, with the value before and after and
 * the words it came from. Show opens the field; Undo puts the old value back as
 * the designer's own edit (Desk.undo_fill). Every word on the card is the app's.
 */
import type { Fill } from "../types";

function Pen() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.8 2.7l2.5 2.5-7.6 7.6-3.2.7.7-3.2z" />
      <path d="M9.4 4.1l2.5 2.5" />
    </svg>
  );
}

const STATE_WORD: Partial<Record<Fill["state"], string>> = {
  undone: "Undone",
  overtaken: "Changed since",
  skipped: "Skipped",
};

export function FillCard({
  fills,
  onShow,
  onUndo,
  onApply,
  onSkip,
  onRun,
}: {
  fills: Fill[];
  onShow: (field: string) => void;
  onUndo: (name: string) => void;
  onApply?: (name: string | null) => void;
  onSkip?: (name: string) => void;
  onRun?: () => void;
}) {
  const proposed = fills.filter((fill) => fill.state === "proposed");
  const asking = proposed.length > 0;
  const stale = fills.filter((fill) => fill.state === "applied" && fill.stale_run);
  return (
    <section className={`fill-card${asking ? " asking" : ""}`} aria-label={asking ? "Inputs waiting for your OK" : "Inputs filled in from the chat"}>
      <header className="fill-head">
        <Pen />
        <span className="fill-title">{asking ? "Fill these in on the Inputs tab?" : "Filled in on the Inputs tab"}</span>
        <span className="fill-sub">{asking ? "Nothing is on the form until you apply it." : "From your message, recorded as given by you in chat."}</span>
        {asking && onApply && proposed.length > 1 ? (
          <button type="button" className="button accent small-button" onClick={() => onApply(null)}>
            Apply all
          </button>
        ) : null}
      </header>
      <ul className="fill-rows">
        {fills.map((fill) => {
          const word = STATE_WORD[fill.state];
          const done = fill.state === "undone" || fill.state === "skipped";
          return (
            <li key={fill.name} className={`fill-row state-${fill.state}`}>
              <span className="fill-label">{fill.label}</span>
              <span className="fill-values">
                <span className={`fill-was${fill.was === "blank" ? " blank" : ""}`} title={fill.was}>
                  {fill.was || "blank"}
                </span>
                <span className="fill-arrow" aria-hidden="true">
                  →
                </span>
                <span className="visually-hidden"> becomes </span>
                <span className="fill-now">{fill.now}</span>
                {fill.why ? <span className="fill-why">{fill.why}</span> : null}
              </span>
              <span className="fill-actions">
                {word ? <span className={`fill-state${done ? " done" : ""}`}>{word}</span> : null}
                {fill.state === "applied" ? (
                  <>
                    <button type="button" className="link-button" onClick={() => onShow(fill.field)} title={`Show ${fill.label} on the Inputs tab`}>
                      Show
                    </button>
                    <button type="button" className="link-button" onClick={() => onUndo(fill.name)} title={`Put ${fill.label} back to ${fill.was || "blank"}`}>
                      Undo
                    </button>
                  </>
                ) : null}
                {fill.state === "proposed" ? (
                  <>
                    <button type="button" className="button on-card small-button" onClick={() => onApply?.(fill.name)}>
                      Apply
                    </button>
                    <button type="button" className="link-button" onClick={() => onSkip?.(fill.name)}>
                      Skip
                    </button>
                  </>
                ) : null}
              </span>
            </li>
          );
        })}
      </ul>
      {stale.length ? (
        <footer className="fill-foot">
          <span className="fill-foot-text">
            The last zone run used the old {stale.map((fill) => fill.label.toLowerCase()).join(" and ")}. Its figures on the Results tab
            no longer describe the form.
          </span>
          {onRun ? (
            <button type="button" className="button on-card small-button" onClick={onRun}>
              Run zone
            </button>
          ) : null}
        </footer>
      ) : null}
    </section>
  );
}

/** Under the working line while the turn runs: what the lead has put on the Inputs tab so far. */
export function FillsSoFar({ fills, onShow }: { fills: { label: string; now: string; field: string }[]; onShow: (field: string) => void }) {
  return (
    <div className="fills-so-far" aria-live="polite">
      <span className="fills-so-far-label">
        <Pen /> Filled in so far
      </span>
      {fills.map((fill) => (
        <button key={fill.field} type="button" className="fill-chip" onClick={() => onShow(fill.field)} title={`Show ${fill.label} on the Inputs tab`}>
          <span className="fill-chip-label">{fill.label}</span> {fill.now}
        </button>
      ))}
    </div>
  );
}
