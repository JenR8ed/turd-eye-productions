#!/usr/bin/env python3
"""
Turd Eye Productions — Rights Logger
Dependency-free CLI for logging AI music generation rights.

Headless usage (preferred for agents):
  python scripts/rights_logger.py add --title "Neon Drift" --tool Suno --plan Pro \
      --commercial yes --human-edits "trimmed intro, remastered" --distributor DistroKid
  python scripts/rights_logger.py list --limit 5
  python scripts/rights_logger.py export
  python scripts/rights_logger.py verify

Interactive usage (human at a terminal):
  python scripts/rights_logger.py add

Data location defaults to <repo>/data and can be overridden with TEP_DATA_DIR.
"""

import argparse
import csv
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

HEADERS = [
    "track_title",
    "tool",
    "plan",
    "generation_datetime_utc",
    "commercial_rights",
    "human_edits",
    "distributor",
    "notes",
    "logged_at_utc",
]

TRUTHY = {"yes", "y", "true", "1"}
FALSEY = {"no", "n", "false", "0"}


def data_dir() -> Path:
    override = os.environ.get("TEP_DATA_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent.parent / "data"


def log_file() -> Path:
    return data_dir() / "rights_log.csv"


def ensure_store() -> Path:
    path = log_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=HEADERS).writeheader()
    return path


def normalize_yes_no(value: str) -> str:
    lowered = str(value).strip().lower()
    if lowered in TRUTHY:
        return "yes"
    if lowered in FALSEY:
        return "no"
    raise ValueError(f"expected yes or no, got {value!r}")


def valid_generation_datetime(value: str) -> str:
    """Accept YYYY-MM-DD HH:MM or YYYY-MM-DD."""
    text = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d %H:%M")
        except ValueError:
            continue
    raise ValueError(f"datetime must be 'YYYY-MM-DD HH:MM' or 'YYYY-MM-DD', got {value!r}")


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")


def read_rows() -> list[dict]:
    path = log_file()
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [row for row in csv.DictReader(f) if row.get("track_title")]


def prompt_if_missing(value, prompt_text, required=True, default=None):
    """Use the provided value, else prompt when interactive, else fail."""
    if value is not None:
        return value
    if sys.stdin.isatty():
        entered = input(prompt_text).strip()
        if entered:
            return entered
        if default is not None:
            return default
        if not required:
            return ""
        raise ValueError("a value is required")
    if default is not None:
        return default
    if not required:
        return ""
    raise ValueError(f"missing required value in non-interactive mode: {prompt_text.strip()}")


def add_entry(args) -> int:
    path = ensure_store()
    try:
        entry = {
            "track_title": prompt_if_missing(args.title, "Track title: "),
            "tool": prompt_if_missing(args.tool, "Tool used (e.g. Suno, Soundraw): "),
            "plan": prompt_if_missing(args.plan, "Plan at generation (e.g. Pro): "),
            "generation_datetime_utc": valid_generation_datetime(
                prompt_if_missing(
                    args.generated_at,
                    "Generation datetime UTC (YYYY-MM-DD HH:MM, blank = now): ",
                    default=now_utc(),
                )
            ),
            "commercial_rights": normalize_yes_no(
                prompt_if_missing(args.commercial, "Commercial rights? (yes/no): ", default="yes")
            ),
            "human_edits": prompt_if_missing(
                args.human_edits, "Human edits made (short description): ", required=False, default=""
            ),
            "distributor": prompt_if_missing(
                args.distributor, "Distributor (e.g. DistroKid): ", required=False, default=""
            ),
            "notes": prompt_if_missing(args.notes, "Notes: ", required=False, default=""),
            "logged_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        }
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    with open(path, "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=HEADERS).writerow(entry)

    print(f"Logged: {entry['track_title']}")
    for warning in compliance_warnings(entry):
        print(f"Warning: {warning}", file=sys.stderr)
    return 0


def compliance_warnings(row: dict) -> list[str]:
    """AGENTS.md safety rules: commercial rights required, human edits expected."""
    warnings = []
    if row.get("commercial_rights") != "yes":
        warnings.append(
            f"{row.get('track_title', '(untitled)')}: no commercial rights recorded - "
            "do not release until generated on a paid commercial plan (AGENTS.md rule 1)"
        )
    if not (row.get("human_edits") or "").strip():
        warnings.append(
            f"{row.get('track_title', '(untitled)')}: no human edits recorded - "
            "add light editing before release (AGENTS.md rule 3)"
        )
    return warnings


def verify(args) -> int:
    """Report entries that violate the AGENTS.md release rules."""
    ensure_store()
    rows = read_rows()
    if not rows:
        print("No entries yet. Nothing to verify.")
        return 0

    warnings = [w for row in rows for w in compliance_warnings(row)]
    print(f"Checked {len(rows)} entr{'y' if len(rows) == 1 else 'ies'}.")
    if not warnings:
        print("All entries satisfy the commercial-rights and human-edit rules.")
        return 0

    for warning in warnings:
        print(f"  - {warning}")
    print(f"\n{len(warnings)} issue(s) found.")
    return 1 if args.strict else 0


def escape_cell(value: str) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def export_markdown(args) -> int:
    ensure_store()
    rows = read_rows()
    out = Path(args.output) if args.output else data_dir() / "rights_log.md"
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Rights Log",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC",
        f"Entries: {len(rows)}",
        "",
        "| Track Title | Tool | Plan | Generation (UTC) | Commercial | Human Edits | Distributor | Notes |",
        "|-------------|------|------|------------------|------------|-------------|-------------|-------|",
    ]
    for row in rows:
        cells = [
            escape_cell(row.get(key))
            for key in (
                "track_title",
                "tool",
                "plan",
                "generation_datetime_utc",
                "commercial_rights",
                "human_edits",
                "distributor",
                "notes",
            )
        ]
        lines.append("| " + " | ".join(cells) + " |")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Exported {len(rows)} entr{'y' if len(rows) == 1 else 'ies'} to {out}")
    return 0


def list_entries(args) -> int:
    ensure_store()
    rows = read_rows()
    if not rows:
        print("No entries yet. Add one with: rights_logger.py add --title ... --tool ... --plan ...")
        return 0

    shown = rows[-args.limit :] if args.limit > 0 else rows
    print(f"\n=== Rights Log (showing {len(shown)} of {len(rows)}) ===\n")
    for row in shown:
        print(
            f"* {row['track_title']} | {row.get('tool', '')} ({row.get('plan', '')}) | "
            f"{row.get('generation_datetime_utc', '')} | Rights: {row.get('commercial_rights', '')}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rights_logger.py",
        description="Log AI music generation rights (stdlib only, headless-friendly).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a rights log entry")
    p_add.add_argument("--title", help="Track title")
    p_add.add_argument("--tool", help="Generator used, e.g. Suno, Soundraw")
    p_add.add_argument("--plan", help="Plan active at generation time, e.g. Pro")
    p_add.add_argument("--generated-at", help="Generation datetime UTC 'YYYY-MM-DD HH:MM' (default: now)")
    p_add.add_argument("--commercial", help="Commercial rights: yes or no (default: yes)")
    p_add.add_argument("--human-edits", help="Short description of human edits applied")
    p_add.add_argument("--distributor", help="Distributor, e.g. DistroKid")
    p_add.add_argument("--notes", help="Free-text notes")

    p_list = sub.add_parser("list", help="List recent entries")
    p_list.add_argument("--limit", type=int, default=20, help="Number of entries to show (0 = all)")

    p_export = sub.add_parser("export", help="Export the log to Markdown")
    p_export.add_argument("--output", help="Output path (default: data/rights_log.md)")

    p_verify = sub.add_parser("verify", help="Check entries against AGENTS.md release rules")
    p_verify.add_argument("--strict", action="store_true", help="Exit non-zero if any issue is found")

    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "add":
        return add_entry(args)
    if args.command == "list":
        return list_entries(args)
    if args.command == "export":
        return export_markdown(args)
    return verify(args)


if __name__ == "__main__":
    sys.exit(main())
