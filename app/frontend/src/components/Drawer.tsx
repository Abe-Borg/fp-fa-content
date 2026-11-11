/**
 * Zone details: the optional form behind /run, the tool-plan figures that go to
 * the export, and the team. Closed until it is wanted; the form keeps its
 * values when it closes. The fields travel to the app as they are typed.
 */
import { useState } from "react";
import type { Form, FormValues, Team } from "../types";
import { Close } from "./icons";
import { TeamPanel } from "./TeamPanel";

export type Tab = "basis" | "zone" | "results" | "team";
const TABS: { id: Tab; label: string }[] = [
  { id: "basis", label: "Basis" },
  { id: "zone", label: "Zone" },
  { id: "results", label: "Results" },
  { id: "team", label: "Team" },
];

type SetField = (name: string, value: string | boolean) => void;

function Text({ name, label, values, set, wide }: { name: string; label: string; values: FormValues; set: SetField; wide?: boolean }) {
  const id = `f-${name}`;
  return (
    <>
      <label className="field-label" htmlFor={id}>
        {label}
      </label>
      <input
        id={id}
        className={`input${wide ? " wide-field" : ""}`}
        value={String(values[name] ?? "")}
        onChange={(event) => set(name, event.target.value)}
        spellCheck={false}
      />
    </>
  );
}

function Choice({ name, label, values, set, choices }: { name: string; label: string; values: FormValues; set: SetField; choices: string[] }) {
  const id = `f-${name}`;
  return (
    <>
      <label className="field-label" htmlFor={id}>
        {label}
      </label>
      <select id={id} className="input select" value={String(values[name] ?? "")} onChange={(event) => set(name, event.target.value)}>
        {choices.map((choice) => (
          <option key={choice} value={choice}>
            {choice}
          </option>
        ))}
      </select>
    </>
  );
}

function Flag({ name, label, values, set }: { name: string; label: string; values: FormValues; set: SetField }) {
  return (
    <label className="check">
      <input type="checkbox" checked={!!values[name]} onChange={(event) => set(name, event.target.checked)} />
      <span>{label}</span>
    </label>
  );
}

function SegmentAdd({ roles, onAdd }: { roles: string[]; onAdd: (row: { role: string; nps: string; schedule: string; length: string }) => Promise<boolean> }) {
  const [row, setRow] = useState({ role: roles[0] || "branch", nps: "", schedule: "", length: "" });
  const change = (key: keyof typeof row) => (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setRow({ ...row, [key]: event.target.value });
  const add = async () => {
    if (await onAdd(row)) setRow({ ...row, nps: "", schedule: "", length: "" });
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
      <label className="small dim" htmlFor="seg-role">Role</label>
      <label className="small dim" htmlFor="seg-nps">NPS</label>
      <label className="small dim" htmlFor="seg-schedule">Schedule</label>
      <label className="small dim" htmlFor="seg-length">Length ft</label>
      <span />
      <select id="seg-role" className="input select well" value={row.role} onChange={change("role")}>
        {roles.map((role) => (
          <option key={role}>{role}</option>
        ))}
      </select>
      <input id="seg-nps" className="input well" value={row.nps} onChange={change("nps")} spellCheck={false} />
      <input id="seg-schedule" className="input well" value={row.schedule} onChange={change("schedule")} spellCheck={false} />
      <input id="seg-length" className="input well" value={row.length} onChange={change("length")} spellCheck={false} />
      <button type="button" className="button on-card" onClick={() => void add()}>
        Add segment
      </button>
    </div>
  );
}

export function Drawer({
  tab,
  setTab,
  form,
  values,
  set,
  results,
  resultsNote,
  team,
  running,
  onClose,
  onRun,
  onAddSegment,
  onRemoveSegment,
  onCancel,
  onCheck,
  onExportBasis,
  onStatus,
  onAnswer,
}: {
  tab: Tab;
  setTab: (tab: Tab) => void;
  form: Form;
  values: FormValues;
  set: SetField;
  results: string;
  resultsNote: string;
  team: Team;
  running: boolean;
  onClose: () => void;
  onRun: () => void;
  onAddSegment: (row: { role: string; nps: string; schedule: string; length: string }) => Promise<boolean>;
  onRemoveSegment: (index: number) => void;
  onCancel: () => void;
  onCheck: () => void;
  onExportBasis: () => void;
  onStatus: () => void;
  onAnswer: (id: string, answer: string) => Promise<boolean>;
}) {
  const choices = form.choices;

  const onTabKey = (event: React.KeyboardEvent, index: number) => {
    const step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
    if (!step) return;
    event.preventDefault();
    const next = TABS[(index + step + TABS.length) % TABS.length];
    setTab(next.id);
    requestAnimationFrame(() => document.getElementById(`tab-${next.id}`)?.focus());
  };

  return (
    <aside className="drawer" aria-label="Zone details">
      <div className="drawer-head">
        <h2 className="display">Zone details</h2>
        <button type="button" className="icon-button" aria-label="Close Zone details" title="Close the drawer. The form keeps its values." onClick={onClose}>
          <Close />
        </button>
      </div>
      <p className="small dim">Optional. Chat works without it. /run and Run zone use these inputs.</p>
      <div className="tabs" role="tablist" aria-label="Zone details">
        {TABS.map((item, index) => (
          <button
            key={item.id}
            id={`tab-${item.id}`}
            type="button"
            role="tab"
            aria-selected={tab === item.id}
            tabIndex={tab === item.id ? 0 : -1}
            className={`tab${tab === item.id ? " on" : ""}`}
            onClick={() => setTab(item.id)}
            onKeyDown={(event) => onTabKey(event, index)}
          >
            {item.label}
            {item.id === "team" && team.attention ? (
              <span className="count" title={`${team.attention} waiting on someone`}>
                {team.attention}
                <span className="visually-hidden"> waiting</span>
              </span>
            ) : null}
          </button>
        ))}
      </div>
      <div className="drawer-body" role="tabpanel" aria-labelledby={`tab-${tab}`}>
        {tab === "basis" ? (
          <div className="form-grid basis">
            <Text name="ahj" label="AHJ" values={values} set={set} wide />
            <Text name="nfpa_13" label="NFPA 13 edition" values={values} set={set} />
            <Text name="nfpa_72" label="NFPA 72 edition" values={values} set={set} />
            <Text name="insurer" label="Insurer" values={values} set={set} />
            <label className="field-label top" htmlFor="f-hazard_notes">
              Hazard notes
            </label>
            <textarea
              id="f-hazard_notes"
              className="input notes"
              rows={8}
              value={String(values.hazard_notes ?? "")}
              onChange={(event) => set("hazard_notes", event.target.value)}
            />
            <p className="small dim span2">Scope: wet, dry, and double-interlock preaction, plus the detection and releasing that trip them.</p>
          </div>
        ) : null}
        {tab === "zone" ? (
          <div className="zone">
            <p className="small dim pre-line">{form.assumptions}</p>
            <div className="form-grid four">
              <Text name="zone_id" label="Zone" values={values} set={set} />
              <Choice name="system_label" label="System" values={values} set={set} choices={choices.system_label || []} />
              <Choice name="hazard" label="Hazard" values={values} set={set} choices={choices.hazard || []} />
              <Choice name="delivery_basis" label="Time basis" values={values} set={set} choices={choices.delivery_basis || []} />
              <Text name="density" label="Density" values={values} set={set} />
              <Text name="base_area" label="Base area ft²" values={values} set={set} />
              <Text name="area_increase" label="Area increase" values={values} set={set} />
              <Text name="hose" label="Hose gpm" values={values} set={set} />
              <Text name="q_fill" label="Fill gpm" values={values} set={set} />
              <Text name="trim_gal" label="Trim gal" values={values} set={set} />
              <Text name="t_detect" label="t detect s" values={values} set={set} />
              <Text name="t_release" label="t release s" values={values} set={set} />
              <Text name="t_exhaust" label="t exhaust s" values={values} set={set} />
              <Text name="fittings" label="Fittings %" values={values} set={set} />
              <Choice name="medium" label="Medium" values={values} set={set} choices={choices.medium || []} />
              <Choice name="prime" label="Prime held by" values={values} set={set} choices={choices.prime || []} />
              <Text name="supervisory_psi" label="Low-air supervisory psi" values={values} set={set} />
              <Text name="supervisory_psig" label="Supervisory psig" values={values} set={set} />
              <Choice name="length_label" label="Lengths" values={values} set={set} choices={choices.length_label || []} />
              <Text name="fill_minutes" label="Fill minutes" values={values} set={set} />
            </div>
            <div className="checks">
              <Flag name="supervised" label="Supervised waterflow" values={values} set={set} />
              <Flag name="qod" label="Quick-opening device" values={values} set={set} />
              <Flag name="manual_station" label="Manual station" values={values} set={set} />
              <Flag name="failsafe" label="Failsafe on total power loss" values={values} set={set} />
            </div>
            <div className="section-label">PIPE SEGMENTS</div>
            <div className="card">
              <table className="grid-table">
                <thead>
                  <tr>
                    <th>ROLE</th>
                    <th>NPS</th>
                    <th>SCHEDULE</th>
                    <th>LENGTH FT</th>
                    <th>ID IN</th>
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
                        <td>{String(segment.length_ft)}</td>
                        <td>{segment.d_in}</td>
                        <td>
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
                        No segments yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
              <SegmentAdd roles={form.roles} onAdd={onAddSegment} />
            </div>
            <p className="small dim">
              Blank schedule uses the shop default (branch and under 2 in = sch 40, mains and cross 2 in and up = sch 10). The ID comes
              from the calc pack. Blank fittings follow the length basis. Blank trim is ASSUMED 5 gal (no valve data sheet), not
              calculated.
            </p>
            <div className="right">
              <button type="button" className="button accent" onClick={onRun}>
                Run zone
              </button>
            </div>
          </div>
        ) : null}
        {tab === "results" ? (
          <div className="results">
            {resultsNote ? (
              <div className="card callout warn" role="status">
                <p>{resultsNote}</p>
                <div className="right">
                  <button type="button" className="button on-card" onClick={onRun}>
                    Run zone again
                  </button>
                </div>
              </div>
            ) : null}
            <p className="small dim">
              Tool-plan figures for export. Pipe gallons and t_total are calculated. Blank trim and the screen-limit seconds are marked
              ASSUMED. A delivery time here is an optimistic screen, not a listed water-delivery-time calculation.
            </p>
            <pre className="paper sheet" tabIndex={0}>
              {results}
            </pre>
          </div>
        ) : null}
        {tab === "team" ? (
          <TeamPanel
            team={team}
            running={running}
            onCancel={onCancel}
            onCheck={onCheck}
            onExportBasis={onExportBasis}
            onStatus={onStatus}
            onAnswer={onAnswer}
          />
        ) : null}
      </div>
    </aside>
  );
}
