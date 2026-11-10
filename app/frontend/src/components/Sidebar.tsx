/**
 * The sidebar: the wordmark, + New chat, the jobs, the open job's team, the
 * Activity list of window jobs, and Settings. A job is renamed or deleted from
 * its right-click menu, its ⋯ button, or F2 and Delete while it has the focus.
 */
import { useState } from "react";
import type { ActivityRow, AppInfo } from "../types";
import { Menu, type Anchor } from "./Menu";
import { More, Star } from "./icons";

export function Sidebar({
  app,
  projects,
  openId,
  activity,
  roster,
  onNew,
  onOpen,
  onRename,
  onDelete,
  onTeam,
  onSettings,
}: {
  app: AppInfo;
  projects: { id: string; name: string }[];
  openId: string | null;
  activity: ActivityRow[];
  roster: string[];
  onNew: () => void;
  onOpen: (id: string) => void;
  onRename: (id: string) => void;
  onDelete: (id: string) => void;
  onTeam: () => void;
  onSettings: () => void;
}) {
  const [menu, setMenu] = useState<{ id: string; anchor: Anchor; keyboard: boolean } | null>(null);

  const jobMenu = (id: string, anchor: Anchor, keyboard: boolean) => setMenu({ id, anchor, keyboard });

  return (
    <aside className="sidebar" aria-label="Jobs">
      <div className="brand">
        <Star size={20} />
        <div>
          <div className="wordmark">
            <span className="plus">{app.name.slice(0, 1)}</span>
            {app.name.slice(1)}
          </div>
          <div className="faint small">{app.strapline}</div>
        </div>
      </div>
      <button type="button" className="button accent wide" onClick={onNew} title="Start a new chat (Ctrl+N)">
        +&nbsp;&nbsp;New chat
      </button>
      <div className="section-label">JOBS</div>
      <ul className="jobs" role="listbox" aria-label="Jobs">
        {projects.map((project) => (
          <li
            key={project.id}
            role="option"
            aria-selected={project.id === openId}
            tabIndex={0}
            className={`job${project.id === openId ? " open" : ""}`}
            title={project.name}
            onClick={() => onOpen(project.id)}
            onContextMenu={(event) => {
              event.preventDefault();
              jobMenu(project.id, { x: event.clientX, y: event.clientY }, false);
            }}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                onOpen(project.id);
              } else if (event.key === "F2") {
                event.preventDefault();
                onRename(project.id);
              } else if (event.key === "Delete") {
                event.preventDefault();
                onDelete(project.id);
              } else if (event.key === "ArrowDown" || event.key === "ArrowUp") {
                event.preventDefault();
                const sibling = (event.key === "ArrowDown"
                  ? event.currentTarget.nextElementSibling
                  : event.currentTarget.previousElementSibling) as HTMLElement | null;
                sibling?.focus();
              } else if (event.key === "ContextMenu" || (event.shiftKey && event.key === "F10")) {
                event.preventDefault();
                const rect = event.currentTarget.getBoundingClientRect();
                jobMenu(project.id, { x: rect.left + 24, y: rect.bottom }, true);
              }
            }}
          >
            <span className="job-name">{project.name}</span>
            <button
              type="button"
              className="job-more"
              tabIndex={-1}
              aria-label={`Rename or delete ${project.name}`}
              onClick={(event) => {
                event.stopPropagation();
                const rect = event.currentTarget.getBoundingClientRect();
                jobMenu(project.id, { x: rect.right, y: rect.bottom + 2, align: "right" }, event.detail === 0);
              }}
            >
              <More />
            </button>
          </li>
        ))}
      </ul>
      <div className="side-bottom">
        {roster.length ? (
          <div className="side-section">
            <div className="section-label">TEAM</div>
            <button type="button" className="lines clickable" title="Open the Team tab" onClick={onTeam}>
              {roster.map((line) => (
                <span key={line} className="line-row">
                  {line}
                </span>
              ))}
            </button>
          </div>
        ) : null}
        {activity.length ? (
          <div className="side-section">
            <div className="section-label">ACTIVITY</div>
            <ul className="lines activity" aria-label="Activity">
              {activity.map((row) => (
                <li key={row.id} className={`line-row tone-${row.tone || "plain"}`} title={row.error ? `${row.heading}\n${row.error}` : row.heading}>
                  <span className="glyph" aria-label={row.status}>
                    {row.glyph}
                  </span>
                  <span className="kind">{row.kind}</span>
                  <span className="sep">·</span>
                  <span className="name">{row.project_name}</span>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
        <button type="button" className="button side wide" onClick={onSettings}>
          Settings
        </button>
      </div>
      {menu ? (
        <Menu
          anchor={menu.anchor}
          keyboard={menu.keyboard}
          label="Job"
          onClose={() => setMenu(null)}
          items={[
            { label: "Rename…", hint: "F2", onSelect: () => onRename(menu.id) },
            { label: "Delete", hint: "Del", danger: true, onSelect: () => onDelete(menu.id) },
          ]}
        />
      ) : null}
    </aside>
  );
}
