"""Usage and cost per job, read from the project record.

Every model context already sums its own usage. The lead turn writes a `turn`
event with the task total (lead rounds plus every delegation and check it ran),
a narrated zone run or starter writes a `narration` event, a blind check writes
its usage on the `record_check` event, and each delegation writes a `delegation`
event. This module reads those events back and prices them.

Prices are a dated snapshot, not a feed. RATES_PER_MILLION holds the Claude
Opus 5.5 list prices in dollars per million tokens as published on RATES_DATE.
Pass other rates on the command line when they change; the report always
prints the rates it used.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from fpfa.claude_client import MODEL_ID

RATES_DATE = "2026-10-06"
# Dollars per million tokens. Cache write is the 5-minute write price, 1.25 times input.
RATES_PER_MILLION = {"input": 4.00, "output": 20.00, "cache_write": 5.00, "cache_read": 0.20}
# Event kinds that carry usage, and whether the kind counts toward a job's total.
# A delegation's usage is already inside its turn's total, so it is shown but not added.
USAGE_KINDS = ("turn", "narration", "record_check", "delegation")
COUNTED_KINDS = ("turn", "narration", "record_check")


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def normalize(usage: Any) -> dict:
    """The four token counts and the round count as plain ints."""
    src = usage if isinstance(usage, dict) else {}
    return {
        "rounds": _int(src.get("rounds")),
        "input_tokens": _int(src.get("input_tokens")),
        "cache_creation_input_tokens": _int(src.get("cache_creation_input_tokens")),
        "cache_read_input_tokens": _int(src.get("cache_read_input_tokens")),
        "output_tokens": _int(src.get("output_tokens")),
    }


def add(total: dict, usage: Any) -> dict:
    for key, value in normalize(usage).items():
        total[key] = _int(total.get(key)) + value
    return total


def cost(usage: Any, rates: dict | None = None) -> dict:
    """Dollars by line and in total for one usage block, at the given rates."""
    rate = dict(RATES_PER_MILLION)
    rate.update(rates or {})
    use = normalize(usage)
    lines = {
        "input": use["input_tokens"] * rate["input"] / 1_000_000,
        "cache_write": use["cache_creation_input_tokens"] * rate["cache_write"] / 1_000_000,
        "cache_read": use["cache_read_input_tokens"] * rate["cache_read"] / 1_000_000,
        "output": use["output_tokens"] * rate["output"] / 1_000_000,
    }
    lines["total"] = sum(lines.values())
    return lines


def usage_events(record: Any, project_id: str) -> list[dict]:
    """Events on the job that carry usage, oldest first, with normalized usage attached."""
    rows = []
    for event in record.events(project_id, limit=5000):
        if event.get("kind") not in USAGE_KINDS:
            continue
        payload = event.get("payload") or {}
        usage = payload.get("usage")
        if not isinstance(usage, dict):
            continue
        row = {
            "ts": event.get("ts") or "",
            "kind": event["kind"],
            "agent": event.get("agent") or "",
            "usage": normalize(usage),
            "counted": event["kind"] in COUNTED_KINDS,
        }
        for key in ("specialist", "delegations", "checks", "cancelled", "source", "stop_reason"):
            if key in payload:
                row[key] = payload[key]
        rows.append(row)
    return rows


def job_totals(rows: list[dict]) -> dict:
    total: dict = {}
    for row in rows:
        if row.get("counted"):
            add(total, row["usage"])
    return normalize(total)


def _label(row: dict) -> str:
    kind = row["kind"]
    if kind == "turn":
        bits = ["lead turn"]
        if row.get("delegations"):
            bits.append(f"{row['delegations']} delegation{'s' if row['delegations'] != 1 else ''}")
        if row.get("checks"):
            bits.append(f"{row['checks']} check{'s' if row['checks'] != 1 else ''}")
        if row.get("cancelled"):
            bits.append("cancelled")
        return ", ".join(bits)
    if kind == "delegation":
        return f"  within the turn: {row.get('specialist') or 'specialist'}"
    if kind == "narration":
        note = "cancelled" if row.get("cancelled") else (row.get("source") or "")
        return f"narration ({row.get('agent') or 'narrator'}{', ' + note if note else ''})"
    if kind == "record_check":
        return "blind check"
    return kind


def _tokens(use: dict) -> str:
    return (
        f"{use['rounds']:>3} rd  in {use['input_tokens']:>8,}  cache+ {use['cache_creation_input_tokens']:>8,}  "
        f"cache< {use['cache_read_input_tokens']:>9,}  out {use['output_tokens']:>7,}"
    )


def report_text(record: Any, project_id: str, rates: dict | None = None, *, name: str = "") -> str:
    """Plain text: one line per model context, the job total, and the dollar estimate."""
    rate = dict(RATES_PER_MILLION)
    rate.update(rates or {})
    rows = usage_events(record, project_id)
    title = name or (record.project_row(project_id) or {}).get("name") or project_id
    lines = [f"Usage and cost for {title}", f"Model {MODEL_ID}. Rates per million tokens as of {RATES_DATE}: "
             f"input ${rate['input']:.2f}, cache write ${rate['cache_write']:.2f}, "
             f"cache read ${rate['cache_read']:.2f}, output ${rate['output']:.2f}."]
    if not rows:
        lines.append("No model usage is on this job's record yet. The tool plan alone costs nothing.")
        return "\n".join(lines)
    for row in rows:
        money = cost(row["usage"], rate)["total"]
        mark = "" if row["counted"] else "   (inside the turn above, not added)"
        lines.append(f"{row['ts'][:19]}  {_label(row):<42} {_tokens(row['usage'])}  ${money:7.4f}{mark}")
    total = job_totals(rows)
    money = cost(total, rate)
    counted = [row for row in rows if row["counted"]]
    lines.append("")
    lines.append(f"Job total over {len(counted)} model context{'s' if len(counted) != 1 else ''}: {_tokens(total)}")
    lines.append(
        f"Estimated cost ${money['total']:.4f}: input ${money['input']:.4f}, cache write ${money['cache_write']:.4f}, "
        f"cache read ${money['cache_read']:.4f}, output ${money['output']:.4f}."
    )
    in_all = total["input_tokens"] + total["cache_creation_input_tokens"] + total["cache_read_input_tokens"]
    if in_all:
        lines.append(f"Cache: {total['cache_read_input_tokens'] * 100 // in_all}% of input tokens were read from the cache.")
    lines.append("An estimate from list prices, not a bill. Thinking tokens are inside the output count.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Print the usage report for one job or every job in a record database."""
    from fpfa.record import Record, default_path

    parser = argparse.ArgumentParser(prog="python -m fpfa.usage_report", description=__doc__.split("\n\n")[0])
    parser.add_argument("--db", default="", help="Path to fpfa.db. Default: the data directory's record")
    parser.add_argument("--project", default="", help="Job id. Default: every job in the record")
    parser.add_argument("--input-rate", type=float, default=None, help="Dollars per million input tokens")
    parser.add_argument("--output-rate", type=float, default=None, help="Dollars per million output tokens")
    parser.add_argument("--cache-write-rate", type=float, default=None, help="Dollars per million cache-write tokens")
    parser.add_argument("--cache-read-rate", type=float, default=None, help="Dollars per million cache-read tokens")
    parser.add_argument("--json", action="store_true", help="Print the rows and totals as JSON instead of text")
    args = parser.parse_args(argv)
    rates = {}
    for key, value in (("input", args.input_rate), ("output", args.output_rate),
                       ("cache_write", args.cache_write_rate), ("cache_read", args.cache_read_rate)):
        if value is not None:
            rates[key] = value
    path = Path(args.db) if args.db else default_path()
    if not path.is_file():
        sys.stderr.write(f"No record at {path}\n")
        return 2
    record = Record(path)
    if args.project:
        projects = [args.project]
    else:
        projects = [row["id"] for row in record._read("SELECT id FROM projects ORDER BY created")]
    if not projects:
        sys.stdout.write("The record has no jobs.\n")
        return 0
    if args.json:
        out = {}
        for project_id in projects:
            rows = usage_events(record, project_id)
            out[project_id] = {"rows": rows, "total": job_totals(rows), "cost": cost(job_totals(rows), rates),
                               "rates": {**RATES_PER_MILLION, **rates}, "rates_date": RATES_DATE}
        sys.stdout.write(json.dumps(out, indent=2, default=str) + "\n")
        return 0
    for index, project_id in enumerate(projects):
        if index:
            sys.stdout.write("\n")
        sys.stdout.write(report_text(record, project_id, rates) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
