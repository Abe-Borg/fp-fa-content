/**
 * The Team tab: where the job stands and what the team did, drawn from the
 * record as the app reads it (app/fpfa/team_panel.py). In the order a person
 * coming back to a job asks: what was asked and how far it got, what the team
 * needs from me, what changed, where the specialists disagree, what each of
 * them found and how far each finding was taken, and what passed between them.
 *
 * The page decides nothing here. Every row is a row of the state. The only
 * thing it keeps is the answer being typed and which rows are open.
 */
import { useState } from "react";
import type { FindingRow, Team } from "../types";

/** The words beside a tier's dot. The colour is never the only signal. */
const TIER_SHORT: Record<string, string> = {
  source: "checked against a source",
  reviewed: "reviewed, author's cite only",
  stated: "not reviewed",
  open: "needs evidence or review",
};

function plural(count: number, word: string): string {
  return `${count} ${word}${count === 1 ? "" : "s"}`;
}

function clip(text: string, limit: number): string {
  return text.length <= limit ? text : `${text.slice(0, limit - 1)}…`;
}

function Finding({ row }: { row: FindingRow }) {
  return (
    <details className="finding">
      <summary>
        <span className={`dot tier-${row.tier}`} aria-hidden="true" />
        <span className="finding-text">{row.text}</span>
        <span className="finding-meta">
          {row.by} · {row.label}
          {row.verdict ? ` · trace check: ${row.verdict}` : " · not checked"}
        </span>
        {row.tier === "open" && row.why.length ? <span className="finding-why">{clip(row.why[0], 150)}</span> : null}
      </summary>
      <div className="finding-body">
        <p className="evidence-head">Rests on</p>
        {row.rests_on.length ? (
          <ul className="evidence">
            {row.rests_on.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        ) : (
          <p className="dim">Nothing cited.</p>
        )}
        <p className="evidence-head">How far it was taken</p>
        <p>
          {row.tier_title}.{row.verdict ? ` Trace check: ${row.verdict}.` : " No trace check has judged it."}
        </p>
        {row.checked_against.length ? (
          <ul className="evidence">
            {row.checked_against.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        ) : null}
        {row.why.map((line) => (
          <p key={line} className="why">
            {line}
          </p>
        ))}
        {row.reviews.length ? (
          <>
            <p className="evidence-head">Reviewed by</p>
            <ul className="evidence">
              {row.reviews.map((review) => (
                <li key={`${review.by}-${review.position}`}>
                  {review.by} {review.position}
                  {review.note ? `: ${review.note}` : ""}
                  {review.how ? ` — ${review.how}` : ""}
                </li>
              ))}
            </ul>
          </>
        ) : null}
        <p className="faint small">Record id {row.id}</p>
      </div>
    </details>
  );
}

export function TeamPanel({
  team,
  running,
  onCancel,
  onCheck,
  onExportBasis,
  onStatus,
  onAnswer,
}: {
  team: Team;
  running: boolean;
  onCancel: () => void;
  onCheck: () => void;
  onExportBasis: () => void;
  onStatus: () => void;
  onAnswer: (id: string, answer: string) => Promise<boolean>;
}) {
  const [handoff, setHandoff] = useState<string | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [sending, setSending] = useState<string | null>(null);
  // Which groups of findings the reader opened or closed. Until they choose, the group that needs
  // attention is open, and every group is on a short list.
  const [tierOpen, setTierOpen] = useState<Record<string, boolean>>({});
  const selected = team.handoffs.find((row) => row.id === handoff);
  const quiet = !team.plan && !team.people.length && !team.findings.length;
  const unsettled = team.disagreements.length + team.conflicts.length + team.alternatives.length;

  const answer = async (id: string) => {
    const text = (answers[id] || "").trim();
    if (!text || sending) return;
    setSending(id);
    const ok = await onAnswer(id, text);
    setSending(null);
    if (ok) setAnswers((current) => ({ ...current, [id]: "" }));
  };

  return (
    <div className="team">
      <div className="row-buttons">
        <button type="button" className="button side" onClick={onCheck} title="Check each finding against the rows it cites. It does not open the standards.">
          Run trace check
        </button>
        <button type="button" className="button side" onClick={onExportBasis}>
          Export basis…
        </button>
        <button type="button" className="button side" onClick={onStatus} title="Post where this job stands into the thread (/status)">
          Status to thread
        </button>
        <button type="button" className="button danger-ghost" disabled={!running} onClick={onCancel}>
          Cancel running job
        </button>
      </div>

      <h3 className="section-label">WHERE THINGS STAND</h3>
      <div className="card stand">
        {quiet ? (
          <p className="dim">{team.roster_text}</p>
        ) : (
          <>
            {team.plan && team.plan.objective ? <p className="stand-objective">{team.plan.objective}</p> : null}
            {team.plan && team.plan.steps.length ? (
              <ul className="steps">
                {team.plan.steps.map((step) => (
                  <li key={`${step.title}-${step.owner}`} className={`step ${step.status}`}>
                    <span className="step-mark" aria-hidden="true">
                      {step.mark}
                    </span>
                    <span>
                      {step.title}
                      {step.owner ? <span className="dim"> · {step.owner}</span> : null}
                      <span className="visually-hidden"> ({step.status})</span>
                    </span>
                  </li>
                ))}
              </ul>
            ) : null}
            {team.people.length ? (
              <ul className="people">
                {team.people.map((person) => (
                  <li key={person.slug}>
                    <span className="step-mark" aria-hidden="true">
                      {person.glyph}
                    </span>
                    <span>
                      {person.name} <span className="dim">· {person.status}</span>
                      {person.findings ? <span className="dim"> · {plural(person.findings, "finding")}</span> : null}
                      {person.reviews ? <span className="dim"> · reviewed {person.reviews}</span> : null}
                    </span>
                  </li>
                ))}
              </ul>
            ) : null}
          </>
        )}
        <p className="small dim stand-line">{team.check_line}</p>
        {team.export ? (
          <p className="small dim stand-line">{team.export.ready ? "Design Basis export: ready." : `Design Basis export waits: ${team.export.reason}`}</p>
        ) : null}
        {team.interrupted.length ? (
          <p className="small warn-ink stand-line">
            Interrupted before it finished: {team.interrupted.join(", ")}. What it recorded is kept. Ask again to finish; calcs replay.
          </p>
        ) : null}
      </div>

      {team.asks.length ? (
        <>
          <h3 className="section-label">NEEDS YOUR ANSWER ({team.asks.length})</h3>
          {team.asks.map((ask) => (
            <div key={ask.id} className="card ask">
              <label htmlFor={`answer-${ask.id}`} className="ask-text">
                {ask.text}
              </label>
              <p className="small dim">Asked by {ask.by}</p>
              <textarea
                id={`answer-${ask.id}`}
                className="input well answer"
                rows={2}
                value={answers[ask.id] || ""}
                placeholder="Your answer"
                onChange={(event) => setAnswers((current) => ({ ...current, [ask.id]: event.target.value }))}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
                    event.preventDefault();
                    void answer(ask.id);
                  }
                }}
              />
              <div className="right">
                <button type="button" className="button on-card" disabled={!(answers[ask.id] || "").trim() || sending === ask.id} onClick={() => void answer(ask.id)}>
                  Answer
                </button>
              </div>
            </div>
          ))}
          <p className="small dim">An answer goes on the record. The lead reads it at its next turn, so answer what you can and then say continue.</p>
        </>
      ) : null}

      {team.stale.length || team.changes.length ? (
        <>
          <h3 className="section-label">OUT OF DATE ({team.stale.length})</h3>
          <div className="card callout warn">
            {team.changes.map((line) => (
              <p key={line} className="change">
                {line}
              </p>
            ))}
            <ul className="evidence">
              {team.stale.map((row) => (
                <li key={row.id}>
                  {row.kind} by {row.by}: {row.text}
                </li>
              ))}
            </ul>
            <p className="small dim">These rest on a value that changed. They are not exported as current. Run the zone again, or ask the lead to bring them up to date.</p>
          </div>
        </>
      ) : null}

      {unsettled ? (
        <>
          <h3 className="section-label">NOT YET RECONCILED ({unsettled})</h3>
          <div className="card callout">
            {team.disagreements.map((row) => (
              <div key={row.id} className="dispute">
                <p>
                  <strong>{row.by}</strong> objects to a finding by <strong>{row.author}</strong>
                  {row.status === "escalated" ? <span className="tag">escalated</span> : null}
                </p>
                <p className="quote">{row.finding}</p>
                <p>{row.note}</p>
                {row.resolution ? <p className="small dim">{row.resolution}</p> : null}
              </div>
            ))}
            {team.conflicts.map((row) => (
              <div key={row.key} className="dispute">
                <p>
                  Two values for <strong>{row.key}</strong>
                </p>
                <p>{row.values.map((value) => `${value.by}: ${value.value}`).join(" · ")}</p>
              </div>
            ))}
            {team.alternatives.map((row) => (
              <div key={row.id} className="dispute">
                <p>
                  A finding by <strong>{row.by}</strong> rests on a value other than the project input
                </p>
                <p className="quote">{row.finding}</p>
                <p className="small dim">{row.why}</p>
              </div>
            ))}
          </div>
        </>
      ) : null}

      <h3 className="section-label">FINDINGS ({team.findings.length})</h3>
      {team.findings.length ? (
        <div className="card tiers">
          {team.tiers.map((tier) => {
            const rows = team.findings.filter((row) => row.tier === tier.tier);
            if (!rows.length) return null;
            return (
              <details
                key={tier.tier}
                className="tier"
                open={tierOpen[tier.tier] ?? (tier.tier === "open" || team.findings.length <= 6)}
                onToggle={(event) => {
                  const now = event.currentTarget.open;
                  setTierOpen((current) => (current[tier.tier] === now ? current : { ...current, [tier.tier]: now }));
                }}
              >
                <summary title={tier.note}>
                  <span className={`dot tier-${tier.tier}`} aria-hidden="true" />
                  <span className="tier-title">{tier.title}</span>
                  <span className="tier-count">{rows.length}</span>
                </summary>
                <p className="small dim tier-note">{tier.note}</p>
                {rows.map((row) => (
                  <Finding key={row.id} row={row} />
                ))}
              </details>
            );
          })}
          <p className="small dim legend">
            {Object.entries(TIER_SHORT).map(([tier, words]) => (
              <span key={tier} className="legend-item">
                <span className={`dot tier-${tier}`} aria-hidden="true" /> {words}
              </span>
            ))}
          </p>
          <p className="small dim">{team.not_standard}</p>
        </div>
      ) : (
        <div className="card">
          <p className="dim">No findings on this job's record yet.</p>
        </div>
      )}

      {team.settled.length ? (
        <>
          <h3 className="section-label">HOW DISAGREEMENTS ENDED ({team.settled.length})</h3>
          <div className="card">
            {team.settled.map((row) => (
              <div key={row.id} className="dispute">
                <p>
                  <strong>{row.by}</strong> objected to a finding by <strong>{row.author}</strong>
                </p>
                <p className="quote">{row.finding}</p>
                <p>{row.note}</p>
                <p className="small dim">{row.how}</p>
              </div>
            ))}
          </div>
        </>
      ) : null}

      <h3 className="section-label">EXCHANGES BETWEEN AGENTS</h3>
      <div className="card">
        <table className="grid-table selectable">
          <thead>
            <tr>
              <th>WHEN</th>
              <th>KIND</th>
              <th>FROM</th>
              <th>TO</th>
              <th>STATUS</th>
              <th>BRIEF</th>
            </tr>
          </thead>
          <tbody>
            {team.handoffs.length ? (
              team.handoffs.map((row) => (
                <tr
                  key={row.id}
                  tabIndex={0}
                  aria-selected={row.id === handoff}
                  className={row.id === handoff ? "on" : ""}
                  onClick={() => setHandoff(row.id)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      setHandoff(row.id);
                    }
                  }}
                >
                  <td>{row.when}</td>
                  <td>{row.kind_word}</td>
                  <td>{row.from}</td>
                  <td>{row.to}</td>
                  <td>{row.status}</td>
                  <td className="brief">{row.brief}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={6} className="faint">
                  Nothing has passed between agents yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      {team.handoffs.length ? <pre className="card text-card detail">{selected ? selected.detail : "Select a row to read the brief and what came back."}</pre> : null}

      {team.rfis.length ? (
        <>
          <h3 className="section-label">OPEN FOR THE ENGINEER OF RECORD ({team.rfis.length})</h3>
          <div className="card">
            <ol className="rfis">
              {team.rfis.map((row) => (
                <li key={row.id}>
                  {row.text} <span className="dim">· {row.by}</span>
                </li>
              ))}
            </ol>
          </div>
        </>
      ) : null}

      {team.answered.length ? (
        <>
          <h3 className="section-label">ANSWERED ({team.answered.length})</h3>
          <div className="card">
            <ul className="evidence">
              {team.answered.map((row) => (
                <li key={row.id}>
                  {row.text} <strong>{row.answer}</strong>
                  {row.by ? <span className="dim"> · {row.by}</span> : null}
                </li>
              ))}
            </ul>
          </div>
        </>
      ) : null}
    </div>
  );
}
