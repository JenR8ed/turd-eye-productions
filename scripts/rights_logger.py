#!/usr/bin/env python3
"""
Turd Eye Productions — Rights Logger
Simple, dependency-free CLI for logging AI music generation rights.

Usage:
  python scripts/rights_logger.py add
  python scripts/rights_logger.py list
  python scripts/rights_logger.py export
"""

import csv
import os
from datetime import datetime, timezone
from pathlib import Path

# Paths relative to repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
LOG_FILE = DATA_DIR / "rights_log.csv"

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


def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)
    if not LOG_FILE.exists():
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()


def add_entry():
    ensure_data_dir()
    print("\n=== Add Rights Log Entry ===")
    entry = {
        "track_title": input("Track title: ").strip(),
        "tool": input("Tool used (e.g. Suno, Soundraw): ").strip(),
        "plan": input("Plan at generation (e.g. Pro): ").strip(),
        "generation_datetime_utc": input("Generation datetime UTC (YYYY-MM-DD HH:MM or leave blank for now): ").strip()
        or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
        "commercial_rights": input("Commercial rights? (yes/no): ").strip().lower() or "yes",
        "human_edits": input("Human edits made (short description): ").strip(),
        "distributor": input("Distributor (e.g. DistroKid): ").strip(),
        "notes": input("Notes: ").strip(),
        "logged_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    }

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writerow(entry)

    print(f"\n✓ Logged: {entry['track_title']}")


def list_entries(limit=20):
    ensure_data_dir()
    if not LOG_FILE.exists() or LOG_FILE.stat().st_size == 0:
        print("No entries yet.")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("No entries yet.")
        return

    print(f"\n=== Rights Log (last {min(limit, len(rows))} entries) ===\n")
    for row in rows[-limit:]:
        print(f"• {row['track_title']} | {row['tool']} ({row['plan']}) | {row['generation_datetime_utc']} | Rights: {row['commercial_rights']}")


def export_markdown():
    ensure_data_dir()
    if not LOG_FILE.exists():
        print("No log file found.")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    md_path = DATA_DIR / "rights_log.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Rights Log\n\n")
        f.write("| Track Title | Tool | Plan | Generation (UTC) | Commercial | Human Edits | Distributor | Notes |\n")
        f.write("|-------------|------|------|------------------|------------|-------------|-------------|-------|\n")
        for row in rows:
            f.write(
                f"| {row['track_title']} | {row['tool']} | {row['plan']} | {row['generation_datetime_utc']} | "
                f"{row['commercial_rights']} | {row['human_edits']} | {row['distributor']} | {row['notes']} |\n"
            )

    print(f"✓ Exported to {md_path}")


def main():
    import sys
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()
    if cmd == "add":
        add_entry()
    elif cmd == "list":
        list_entries()
    elif cmd == "export":
        export_markdown()
    else:
        print("Unknown command. Use: add | list | export")


if __name__ == "__main__":
    main()
