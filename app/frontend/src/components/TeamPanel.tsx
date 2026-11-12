/**
 * The Team tab: where the job stands and what the team did, drawn from the
 * record as the app reads it (app/fpfa/team_panel.py). What is waiting on
 * someone comes first: a question for the designer, work an input change
 * left out of date, a disagreement not yet settled. Then what was asked and
 * how far it got, what each specialist found and how far each finding was
 * taken, and what passed between them. Where the panel is wide the history
 * sits beside the findings instead of under them.
 *
 * The page decides nothing here. Every row is a row of the state. The only
 * thing it keeps is the answer being typed and which rows are open.
 */
import { useState } from "react";
import type { FindingRow, Team } from "../types";

/** The words beside a tier's dot. The colour is never the only signal. */
const TIER_SHORT: Record<string, string> = {
  source: "checked against a source",
  checker: "a source, on the checker's reading only",
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
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [sending, setSending] = useState<string | null>(null);
  // Which groups of findings the reader opened or closed. Until they choose, the group that needs
  // attention is open, and every group is on a short list.
  const [tierOpen, setTierOpen] = useState<Record<string, boolean>>({});
  const quiet = !team.plan && !team.people.length && !team.findings.length;
  // A job the team has not touched shows one card that says so, and nothing to press that would do nothing.
  const untouched = quiet && !team.handoffs.length && !team.rfis.length && !team.answered.length && !team.settled.length;
  const unsettled = team.disagreements.length + team.conflicts.length + team.alternatives.length;
  const outOfDate = team.stale.length || team.changes.length;
  const waiting = team.asks.length || outOfDate || unsettled;

  const answer = async (id: string) => {
    const text = (answers[id] || "").trim();
    if (!text || sending) return;
    setSending(id);
    const ok = await onAnswer(id, text);
    setSending(null);
    if (ok) setAnswers((current) => ({ ...current, [id]: "" }));
  };

  return (
    <div className="pane team">
      <div className="pane-scroll">
        <div className="team-grid">
          {waiting ? (
            <div className="team-area waiting">
              {team.asks.length ? (
                <section className="team-block">
                  <h3 className="section-label attention">NEEDS YOUR ANSWER ({team.asks.length})</h3>
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
                      <div className="ask-foot">
                        <span className="small faint">Ctrl+Enter</span>
                        <button
                          type="button"
                          className="button accent"
                          disabled={!(answers[ask.id] || "").trim() || sending === ask.id}
                          onClick={() => void answer(ask.id)}
                        >
                          Answer
                        </button>
                      </div>
                    </div>
                  ))}
                  <p className="small faint block-note">
                    An answer goes on the record. The lead reads it at its next turn, so answer what you can and then say continue.
                  </p>
                </section>
              ) : null}

              {outOfDate ? (
                <section className="team-block">
                  <h3 className="section-label attention">OUT OF DATE ({team.stale.length})</h3>
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
                    <p className="small dim">
                      These rest on a value that changed. They are not exported as current. Run the zone again, or ask the lead to bring
                      them up to date.
                    </p>
                  </div>
                </section>
              ) : null}

              {unsettled ? (
                <section className="team-block">
                  <h3 className="section-label attention">NOT YET RECONCILED ({unsettled})</h3>
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
                </section>
              ) : null}
            </div>
          ) : null}

          <div className="team-area main">
            <section className="team-block">
              <h3 className="section-label">WHERE THINGS STAND</h3>
              <div className="card stand">
                {quiet ? (
                  <p className="dim">{team.roster_text}</p>
                ) : (
                  <>
                    {team.plan && team.plan.objective ? <p className="stand-objective">{team.plan.objective}</p> : null}
                    <div className="stand-columns">
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
                    </div>
                  </>
                )}
                <p className="small dim stand-line">{team.check_line}</p>
                {team.export ? (
                  <p className="small dim stand-line">
                    {team.export.ready
                      ? team.findings.length && team.coverage.gaps.length
                        ? "Design Basis export: ready, as an incomplete draft. It opens with what is missing."
                        : "Design Basis export: ready."
                      : `Design Basis export waits: ${team.export.reason}`}
                  </p>
                ) : null}
                {team.partial.map((line) => (
                  <p key={line} className="small warn-ink stand-line">
                    {line}
                  </p>
                ))}
                {team.retry_line ? <p className="small dim stand-line">{team.retry_line}</p> : null}
                {team.unchecked.map((line) => (
                  <p key={line} className="small warn-ink stand-line">
                    Not reconciled by the app: {line}
                  </p>
                ))}
                {team.unconfirmed_line ? <p className="small warn-ink stand-line">{team.unconfirmed_line}</p> : null}
                <div className="row-buttons" hidden={untouched}>
                  <button type="button" className="button on-card" onClick={onCheck} title="Check each finding against the rows it cites. It does not open the standards.">
                    Run trace check
                  </button>
                  <button type="button" className="button on-card" onClick={onExportBasis}>
                    Export basis…
                  </button>
                  <button type="button" className="button on-card" onClick={onStatus} title="Post where this job stands into the thread (/status)">
                    Status to thread
                  </button>
                  {running ? (
                    <button type="button" className="button danger-ghost" onClick={onCancel}>
                      Cancel running job
                    </button>
                  ) : null}
                </div>
              </div>
            </section>

            {team.findings.length && team.coverage.gaps.length ? (
              <section className="team-block" id="team-coverage">
                <h3 className="section-label attention">A DESIGN BASIS WOULD BE INCOMPLETE ({team.coverage.gaps.length})</h3>
                <div className="card callout">
                  <ul className="evidence">
                    {team.coverage.gaps.map((gap) => (
                      <li key={gap}>{gap}</li>
                    ))}
                  </ul>
                  <p className="small dim">The export is still allowed. It opens with this list and says it is incomplete.</p>
                </div>
              </section>
            ) : null}

            <section className="team-block" hidden={untouched}>
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
            </section>
          </div>

          <div className="team-area history" hidden={untouched}>
            {team.ladder.length ? (
              <section className="team-block" id="team-assurance">
                <h3 className="section-label">WHAT KIND OF CHECKING THIS IS</h3>
                <div className="card ladder">
                  <details className="assurance">
                    <summary>
                      <span className="assurance-brief">
                        The trace check is a consistency check on the team's own record. Two kinds of assurance were not
                        performed.
                      </span>
                    </summary>
                    <ul className="evidence">
                      {team.ladder.map((row) => (
                        <li key={row.name}>
                          <strong>{row.name}.</strong> {row.what} <span className="dim">{row.where}</span>
                        </li>
                      ))}
                    </ul>
                  </details>
                </div>
              </section>
            ) : null}

            <section className="team-block" id="team-methods">
              <h3 className="section-label">METHODS READ ({team.skills_used.length})</h3>
              <div className="card">
                {team.skills_used.length ? (
                  <ul className="evidence">
                    {team.skills_used.map((row) => (
                      <li key={`${row.agent}-${row.slug}`}>{row.line}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="faint">No contributor has read a skill on this job.</p>
                )}
                <p className="small dim">
                  A read shows the method was in front of the contributor, not that it was followed.
                  {team.content.content_fingerprint
                    ? ` Content ${team.content.content_version || "unlabeled"}, fingerprint ${team.content.content_fingerprint}.`
                    : ""}
                </p>
              </div>
            </section>

            <section className="team-block">
              <h3 className="section-label">EXCHANGES BETWEEN AGENTS</h3>
              <div className="card exchanges">
                {team.handoffs.length ? (
                  team.handoffs.map((row) => (
                    <details key={row.id} className="exchange">
                      <summary>
                        <span className="exchange-kind">{row.kind_word}</span>
                        <span className="exchange-who">
                          {row.from} → {row.to}
                        </span>
                        <span className="exchange-status">{row.status}</span>
                        <span className="exchange-when">{row.when}</span>
                        <span className="exchange-brief">{row.brief}</span>
                      </summary>
                      <pre className="text-card detail">{row.detail}</pre>
                    </details>
                  ))
                ) : (
                  <p className="faint exchange-none">Nothing has passed between agents yet.</p>
                )}
              </div>
            </section>

            {team.settled.length ? (
              <section className="team-block">
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
              </section>
            ) : null}

            {team.rfis.length ? (
              <section className="team-block">
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
              </section>
            ) : null}

            {team.answered.length ? (
              <section className="team-block">
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
              </section>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
