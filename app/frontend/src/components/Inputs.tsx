/**
 * The Inputs tab: the project basis, the zone, and its pipe, in the groups a
 * designer thinks in, with Run zone always in reach under them. Every field
 * starts blank and travels to the app as it is typed; the form keeps its
 * values when the panel closes. A unit sits inside its field. A blank field
 * shows the app's hint for it (form.hints), labeled as a hint; a hint is an
 * input only when the designer accepts it with Use hints, and the app records
 * it ASSUMED (form.assumed marks those fields). The page labels and groups the
 * fields and nothing more: what a blank one means is said by the app
 * (form.assumptions) and by the run.
 */
import { useState } from "react";
import type { Form, FormValues, Mark } from "../types";
import { choiceLabel } from "../layout";
import { Close } from "./icons";

type SetField = (name: string, value: string | boolean) => void;
type AcceptHints = (names: string[]) => void;

interface FieldSpec {
  name: string;
  label: string;
  kind?: "text" | "choice" | "flag" | "notes";
  unit?: string;
  /** "all": the field takes the whole row. */
  span?: "all";
  /** Said when the pointer rests on the field, and read with it. */
  hint?: string;
}

interface Group {
  id: string;
  title: string;
  fields: FieldSpec[];
  note?: string;
}

/** The basis and the zone, in the order a zone is described. The names are the app's (Desk.patch_form). */
const GROUPS: Group[] = [
  {
    id: "basis",
    title: "Project basis",
    fields: [
      { name: "ahj", label: "AHJ", span: "all" },
      { name: "insurer", label: "Insurer" },
      { name: "nfpa_13", label: "NFPA 13 edition" },
      { name: "nfpa_72", label: "NFPA 72 edition" },
      { name: "hazard_notes", label: "Hazard notes", kind: "notes", span: "all" },
    ],
    note: "Scope: wet, dry, and double-interlock preaction, plus the detection and releasing that trip them.",
  },
  {
    id: "zone",
    title: "Zone",
    fields: [
      { name: "zone_id", label: "Zone" },
      { name: "system_label", label: "System", kind: "choice" },
      { name: "hazard", label: "Hazard", kind: "choice" },
      { name: "delivery_basis", label: "Time basis", kind: "choice" },
    ],
  },
  {
    id: "demand",
    title: "Sprinkler demand",
    fields: [
      { name: "density", label: "Density", unit: "gpm/ft²" },
      { name: "base_area", label: "Base area", unit: "ft²" },
      { name: "area_increase", label: "Area increase", unit: "fraction", hint: "A fraction: 0.30 is a 30 percent increase." },
      { name: "hose", label: "Hose", unit: "gpm" },
      { name: "supervised", label: "Supervised waterflow", kind: "choice" },
    ],
  },
  {
    id: "delivery",
    title: "Water delivery",
    fields: [
      { name: "q_fill", label: "Fill flow", unit: "gpm" },
      { name: "t_detect", label: "Detection time", unit: "s" },
      { name: "t_release", label: "Releasing time", unit: "s" },
      { name: "t_exhaust", label: "Exhaust time", unit: "s" },
      { name: "qod", label: "Quick-opening device", kind: "choice" },
    ],
  },
  {
    id: "trim",
    title: "Trim and supervisory gas",
    fields: [
      { name: "medium", label: "Medium", kind: "choice" },
      { name: "prime", label: "Prime held by", kind: "choice" },
      { name: "supervisory_psi", label: "Low-air supervisory", unit: "psi" },
      { name: "supervisory_psig", label: "Supervisory fill", unit: "psig" },
      { name: "fill_minutes", label: "Fill time", unit: "min" },
      { name: "manual_station", label: "Manual station", kind: "choice" },
      { name: "failsafe", label: "Failsafe on total power loss", kind: "choice" },
    ],
  },
];

const PIPE_FIELDS: FieldSpec[] = [
  { name: "length_label", label: "Lengths", kind: "choice" },
  { name: "fittings", label: "Fittings", unit: "%" },
  { name: "trim_gal", label: "Trim", unit: "gal" },
];

/** The mark of a field the lead filled in from the chat: a tag that opens what it came from. */
function FromChat({ id, mark }: { id: string; mark: Mark }) {
  const [open, setOpen] = useState(false);
  return (
    <span className="from-chat-wrap">
      <button
        type="button"
        className="from-chat"
        aria-expanded={open}
        aria-controls={`${id}-from`}
        onClick={(event) => {
          // Inside a checkbox's label, the press is the tag's and does not tick the box.
          event.preventDefault();
          setOpen(!open);
        }}
        onBlur={() => setOpen(false)}
        onKeyDown={(event) => {
          if (event.key === "Escape" && open) {
            event.stopPropagation();
            setOpen(false);
          }
        }}
        title="Filled in from the chat. Press for where it came from."
      >
        <svg width="10" height="10" viewBox="0 0 16 16" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <path d="M10.8 2.7l2.5 2.5-7.6 7.6-3.2.7.7-3.2z" />
        </svg>
        <span className="word">from chat</span>
        <span className="visually-hidden word-short">from chat</span>
      </button>
      {open ? (
        <span id={`${id}-from`} className="from-chat-pop" role="note">
          <span className="pop-line">Filled in from the chat.</span>
          {mark.why && mark.quoted ? <span className="pop-quote">{mark.why}</span> : null}
          {mark.why && !mark.quoted ? <span className="pop-line dim">The lead's note: {mark.why}</span> : null}
          {mark.was ? <span className="pop-line dim">Before: {mark.was}</span> : null}
          <span className="pop-line dim">Type over it to make it yours; the record keeps both.</span>
        </span>
      ) : null}
    </span>
  );
}

/** The blank fields of a list that show a hint. */
function hinted(fields: FieldSpec[], form: Form, values: FormValues): string[] {
  return fields
    .filter((spec) => (form.hints || {})[spec.name] && !String(values[spec.name] ?? "").trim())
    .map((spec) => spec.name);
}

/** The blank fields of a list Use hints would fill: one hint each. */
export function hintable(fields: FieldSpec[], form: Form, values: FormValues): string[] {
  return hinted(fields, form, values).filter((name) => (form.accept || []).includes(name));
}

function Field({ spec, form, values, set, seen }: { spec: FieldSpec; form: Form; values: FormValues; set: SetField; seen: number }) {
  const id = `f-${spec.name}`;
  const span = spec.span === "all" ? " span-all" : "";
  const mark = form.marks?.[spec.name];
  // A field filled in since the designer last looked at the tab is drawn with a moment's highlight.
  const marked = mark ? ` filled${mark.fill > seen ? " fresh-fill" : ""}` : "";
  const hint = (form.hints || {})[spec.name] || "";
  const assumed = (form.assumed || []).includes(spec.name);
  const blank = !String(values[spec.name] ?? "").trim();
  // Under the field: its hint while it is blank, or ASSUMED while it holds a hint the designer used.
  const note = blank && hint ? "hint" : assumed ? "assumed" : "";
  // The app writes the hint whole: the value, what it is for, its cite and edition, and VERIFY.
  const hintText = hint;
  const described = [spec.hint ? `${id}-hint` : "", note ? `${id}-note` : ""].filter(Boolean).join(" ") || undefined;
  if (spec.kind === "flag") {
    return (
      <label className={`check field-flag${marked}`}>
        <input id={id} type="checkbox" checked={!!values[spec.name]} onChange={(event) => set(spec.name, event.target.checked)} />
        <span>{spec.label}</span>
        {mark ? <FromChat id={id} mark={mark} /> : null}
      </label>
    );
  }
  const value = String(values[spec.name] ?? "");
  return (
    <div className={`field${span}${marked}`} title={spec.hint}>
      <span className="field-head">
        <label className="field-label" htmlFor={id}>
          {spec.label}
        </label>
        {mark ? <FromChat id={id} mark={mark} /> : null}
      </span>
      {spec.kind === "notes" ? (
        <textarea id={id} className="input notes" rows={3} value={value} onChange={(event) => set(spec.name, event.target.value)} />
      ) : spec.kind === "choice" ? (
        <select
          id={id}
          className="input select"
          value={value}
          aria-describedby={described}
          onChange={(event) => set(spec.name, event.target.value)}
        >
          {(form.choices[spec.name] || []).map((choice) => (
            <option key={choice} value={choice}>
              {choice ? choiceLabel(choice) : "—"}
            </option>
          ))}
        </select>
      ) : (
        <div className={`control${spec.unit ? " with-unit" : ""}`}>
          <input
            id={id}
            className="input"
            value={value}
            aria-describedby={described}
            onChange={(event) => set(spec.name, event.target.value)}
            spellCheck={false}
          />
          {spec.unit ? (
            <span className="unit" aria-hidden="true">
              {spec.unit}
            </span>
          ) : null}
        </div>
      )}
      {spec.hint ? (
        <span id={`${id}-hint`} className="visually-hidden">
          {spec.hint}
        </span>
      ) : null}
      {note === "hint" ? (
        <span id={`${id}-note`} className="field-note hint-note small dim">
          hint: {hintText}
        </span>
      ) : null}
      {note === "assumed" ? (
        <span id={`${id}-note`} className="field-note small dim" title="A hint you used. It is recorded ASSUMED, not as a design value.">
          <span className="tag">ASSUMED</span>
          <span className="visually-hidden">a hint you used</span>
        </span>
      ) : null}
    </div>
  );
}

/** Fill this group's blank fields with their hints. The app records each one ASSUMED. */
function UseHints({ names, onAccept }: { names: string[]; onAccept: AcceptHints }) {
  if (!names.length) return null;
  return (
    <div className="hint-row">
      <button
        type="button"
        className="button on-card"
        onClick={() => onAccept(names)}
        title="Fill the blank fields in this group with their hints. Each is recorded ASSUMED, not a design value."
      >
        Use hints ({names.length})
      </button>
    </div>
  );
}

function Fields({ fields, form, values, set, seen }: { fields: FieldSpec[]; form: Form; values: FormValues; set: SetField; seen: number }) {
  const flags = fields.filter((spec) => spec.kind === "flag");
  return (
    <>
      <div className="fields">
        {fields
          .filter((spec) => spec.kind !== "flag")
          .map((spec) => (
            <Field key={spec.name} spec={spec} form={form} values={values} set={set} seen={seen} />
          ))}
      </div>
      {flags.length ? (
        <div className="flags">
          {flags.map((spec) => (
            <Field key={spec.name} spec={spec} form={form} values={values} set={set} seen={seen} />
          ))}
        </div>
      ) : null}
    </>
  );
}

type SegmentRow = { role: string; nps: string; schedule: string; length: string };

function SegmentAdd({ roles, onAdd }: { roles: string[]; onAdd: (row: SegmentRow) => Promise<boolean> }) {
  const [row, setRow] = useState<SegmentRow>({ role: roles[0] || "branch", nps: "", schedule: "", length: "" });
  const change = (key: keyof SegmentRow) => (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setRow({ ...row, [key]: event.target.value });
  const add = async () => {
    if (await onAdd(row)) {
      setRow({ ...row, nps: "", schedule: "", length: "" });
      document.getElementById("seg-nps")?.focus();
    }
  };
  return (
    <div
      className="segment-add"
      onKeyDown={(event) => {
        if (event.key === "Enter" && (event.target as HTMLElement).tagName === "INPUT") {
          event.preventDefault();
          void add();
        }
      }}
    >
      <div className="field">
        <label className="field-label" htmlFor="seg-role">
          Role
        </label>
        <select id="seg-role" className="input select well" value={row.role} onChange={change("role")}>
          {roles.map((role) => (
            <option key={role}>{role}</option>
          ))}
        </select>
      </div>
      <div className="field">
        <label className="field-label" htmlFor="seg-nps">
          NPS
        </label>
        <input id="seg-nps" className="input well" value={row.nps} onChange={change("nps")} spellCheck={false} />
      </div>
      <div className="field">
        <label className="field-label" htmlFor="seg-schedule">
          Schedule
        </label>
        <input id="seg-schedule" className="input well" value={row.schedule} placeholder="default" onChange={change("schedule")} spellCheck={false} />
      </div>
      <div className="field">
        <label className="field-label" htmlFor="seg-length">
          Length
        </label>
        <div className="control with-unit">
          <input id="seg-length" className="input well" value={row.length} onChange={change("length")} spellCheck={false} />
          <span className="unit" aria-hidden="true">
            ft
          </span>
        </div>
      </div>
      <button type="button" className="button on-card" onClick={() => void add()}>
        Add segment
      </button>
    </div>
  );
}

export function Inputs({
  form,
  values,
  set,
  runNote,
  onRun,
  onAcceptHints,
  onAddSegment,
  onRemoveSegment,
  seen = 0,
}: {
  form: Form;
  values: FormValues;
  set: SetField;
  /** The newest fill the designer has seen on this tab; a newer one is highlighted. */
  seen?: number;
  /** Accept the hints of these blank fields. The app fills them and records each ASSUMED. */
  onAcceptHints: AcceptHints;
  /** Said beside Run zone when the form has moved past the run the Results tab shows. */
  runNote: string;
  onRun: () => void;
  onAddSegment: (row: SegmentRow) => Promise<boolean>;
  onRemoveSegment: (index: number) => void;
}) {
  return (
    <div className="pane inputs">
      <div className="pane-scroll">
        <div className="inputs-columns">
          <div className="inputs-column">
            {hinted([...GROUPS.flatMap((group) => group.fields), ...PIPE_FIELDS], form, values).length ? (
              <p className="small dim hints-note">
                Every field starts blank. Some show a hint: a value the content pack pins, with its cite and edition,
                to VERIFY. A hint is not an input until you use it. A hint you use is recorded ASSUMED, not as a design
                value, and an edition you take from a hint is still not pinned until you type it.
              </p>
            ) : null}
            {GROUPS.map((group) => (
              <section key={group.id} className="group" aria-labelledby={`group-${group.id}`}>
                <h3 id={`group-${group.id}`} className="group-title">
                  {group.title}
                </h3>
                <Fields fields={group.fields} form={form} values={values} set={set} seen={seen} />
                <UseHints names={hintable(group.fields, form, values)} onAccept={onAcceptHints} />
                {group.note ? <p className="small faint group-note">{group.note}</p> : null}
              </section>
            ))}
          </div>
          <div className="inputs-column">
            <section className="group" aria-labelledby="group-pipe">
              <h3 id="group-pipe" className="group-title field-head">
                Pipe
                {form.marks?.segments ? <FromChat id="f-segments" mark={form.marks.segments} /> : null}
              </h3>
              <Fields fields={PIPE_FIELDS} form={form} values={values} set={set} seen={seen} />
              <UseHints names={hintable(PIPE_FIELDS, form, values)} onAccept={onAcceptHints} />
              <div
                id="f-segments"
                tabIndex={-1}
                aria-label="Pipe segments"
                className={`card segments${form.marks?.segments ? ` filled${form.marks.segments.fill > seen ? " fresh-fill" : ""}` : ""}`}
              >
                <table className="grid-table">
                  <thead>
                    <tr>
                      <th>Role</th>
                      <th>NPS</th>
                      <th>Schedule</th>
                      <th className="num">Length ft</th>
                      <th className="num">ID in</th>
                      <th aria-label="Remove" />
                    </tr>
                  </thead>
                  <tbody>
                    {form.segments.length ? (
                      form.segments.map((segment, index) => (
                        <tr key={`${index}-${segment.role}-${segment.nps}-${segment.length_ft}`}>
                          <td>{segment.role}</td>
                          <td>{String(segment.nps)}</td>
                          <td>{segment.schedule}</td>
                          <td className="num">{String(segment.length_ft)}</td>
                          <td className="num">{segment.d_in}</td>
                          <td className="end">
                            <button
                              type="button"
                              className="icon-button small-x"
                              aria-label={`Remove segment ${index + 1}`}
                              title="Remove this segment"
                              onClick={() => onRemoveSegment(index)}
                            >
                              <Close />
                            </button>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={6} className="faint">
                          No segments yet. A zone needs at least one to run.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
                <SegmentAdd roles={form.roles} onAdd={onAddSegment} />
              </div>
              <p className="small faint group-note">
                Blank schedule uses the shop default (branch and under 2 in = sch 40, mains and cross 2 in and up = sch 10). The ID
                comes from the calc pack. Blank fittings follow the length basis. Blank trim is ASSUMED 5 gal (no valve data sheet),
                not calculated.
              </p>
            </section>
            {form.assumptions ? (
              <section className="group" aria-labelledby="group-assumed">
                <h3 id="group-assumed" className="group-title">
                  What a run takes as given
                </h3>
                <p className="small dim pre-line assumptions">{form.assumptions}</p>
              </section>
            ) : null}
          </div>
        </div>
      </div>
      <div className="action-bar">
        <span className={`small action-note${runNote ? " warn-ink" : " faint"}`} role="status">
          {runNote || "Every figure of a run comes from the calc tools."}
        </span>
        <button type="button" className="button accent" onClick={onRun} title="Run the zone tool plan on these inputs (/run)">
          Run zone
        </button>
      </div>
    </div>
  );
}
