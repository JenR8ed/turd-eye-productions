#!/usr/bin/env python3
"""
Turd Eye Productions — Cost & Income Tracker
Lightweight, stdlib-only CLI for tracking expenses and income.

Headless usage (preferred for agents):
  python scripts/cost_tracker.py add-expense --category Suno --amount 10 --description "Pro plan"
  python scripts/cost_tracker.py add-income --category Commission --amount 250 --description "Client brief"
  python scripts/cost_tracker.py summary
  python scripts/cost_tracker.py summary --json
  python scripts/cost_tracker.py summary --markdown
  python scripts/cost_tracker.py list --limit 5

Interactive usage (human at a terminal):
  python scripts/cost_tracker.py add-expense

Data location defaults to <repo>/data and can be overridden with TEP_DATA_DIR.
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

HEADERS = ["date_utc", "type", "category", "amount_usd", "description", "logged_at_utc"]


def data_dir() -> Path:
    override = os.environ.get("TEP_DATA_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent.parent / "data"


def cost_file() -> Path:
    return data_dir() / "costs.csv"


def ensure_store() -> Path:
    path = cost_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=HEADERS).writeheader()
    return path


def money(value: str) -> str:
    """Normalize a currency input to a non-negative 2-decimal string."""
    try:
        amount = Decimal(str(value).strip().replace("$", "").replace(",", ""))
    except InvalidOperation:
        raise ValueError(f"not a valid amount: {value!r}")
    if amount.is_nan() or amount.is_infinite():
        raise ValueError(f"not a valid amount: {value!r}")
    if amount < 0:
        raise ValueError("amount must be non-negative; use add-expense vs add-income to set direction")
    return str(amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def valid_date(value: str) -> str:
    """Validate a YYYY-MM-DD date string."""
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError(f"date must be YYYY-MM-DD, got {value!r}")


def today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def read_rows() -> list[dict]:
    path = cost_file()
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [row for row in csv.DictReader(f) if row.get("amount_usd")]


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


def add_entry(entry_type: str, args) -> int:
    path = ensure_store()
    try:
        date = valid_date(prompt_if_missing(args.date, "Date UTC (YYYY-MM-DD, blank = today): ", default=today_utc()))
        category = prompt_if_missing(args.category, "Category (e.g. Suno, DistroKid, Commission, Streaming): ")
        amount = money(prompt_if_missing(args.amount, "Amount USD: "))
        description = prompt_if_missing(args.description, "Description: ", required=False, default="")
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    entry = {
        "date_utc": date,
        "type": entry_type,
        "category": category,
        "amount_usd": amount,
        "description": description,
        "logged_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(path, "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=HEADERS).writerow(entry)

    print(f"Logged {entry_type}: ${amount} - {category}")
    return 0


def compute_summary() -> dict:
    income = Decimal("0")
    expenses = Decimal("0")
    by_category: dict[str, Decimal] = {}

    for row in read_rows():
        try:
            amount = Decimal(row["amount_usd"])
        except InvalidOperation:
            print(f"Warning: skipping row with unreadable amount: {row['amount_usd']!r}", file=sys.stderr)
            continue
        category = row.get("category") or "(uncategorized)"
        if row.get("type") == "expense":
            expenses += amount
            by_category[category] = by_category.get(category, Decimal("0")) - amount
        else:
            income += amount
            by_category[category] = by_category.get(category, Decimal("0")) + amount

    return {
        "total_income_usd": f"{income:.2f}",
        "total_expenses_usd": f"{expenses:.2f}",
        "net_profit_usd": f"{income - expenses:.2f}",
        "net_by_category_usd": {
            cat: f"{val:.2f}"
            for cat, val in sorted(by_category.items(), key=lambda kv: abs(kv[1]), reverse=True)
        },
        "entry_count": len(read_rows()),
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    }


def summary_markdown(data: dict) -> str:
    lines = [
        "# Cost & Income Summary",
        "",
        f"Generated: {data['generated_at_utc']} UTC",
        f"Entries: {data['entry_count']}",
        "",
        "| Metric | USD |",
        "|--------|-----|",
        f"| Total Income | {data['total_income_usd']} |",
        f"| Total Expenses | {data['total_expenses_usd']} |",
        f"| **Net Profit** | **{data['net_profit_usd']}** |",
        "",
        "## Net by Category",
        "",
        "| Category | Net USD |",
        "|----------|---------|",
    ]
    for cat, val in data["net_by_category_usd"].items():
        lines.append(f"| {cat.replace('|', chr(92) + '|')} | {val} |")
    return "\n".join(lines) + "\n"


def summary(args) -> int:
    ensure_store()
    data = compute_summary()

    if args.json:
        print(json.dumps(data, indent=2))
        return 0

    if args.markdown is not None:
        out = Path(args.markdown) if args.markdown else data_dir() / "cost_summary.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(summary_markdown(data), encoding="utf-8")
        print(f"Exported summary to {out}")
        return 0

    if data["entry_count"] == 0:
        print("No data yet. Add entries with add-expense / add-income.")
        return 0

    print("\n=== Financial Summary ===")
    print(f"Total Income  : ${data['total_income_usd']}")
    print(f"Total Expenses: ${data['total_expenses_usd']}")
    print(f"Net Profit    : ${data['net_profit_usd']}")
    print("\nNet by Category:")
    for cat, val in data["net_by_category_usd"].items():
        amount = Decimal(val)
        print(f"  {cat:20} {'-' if amount < 0 else ''}${abs(amount):.2f}")
    return 0


def list_entries(args) -> int:
    ensure_store()
    rows = read_rows()
    if not rows:
        print("No data yet. Add entries with add-expense / add-income.")
        return 0

    shown = rows[-args.limit :] if args.limit > 0 else rows
    print(f"\n=== Recent Entries (showing {len(shown)} of {len(rows)}) ===\n")
    for row in shown:
        sign = "-" if row.get("type") == "expense" else "+"
        print(
            f"{row['date_utc']} | {sign}${row['amount_usd']:>10} | {row.get('type', ''):7} | "
            f"{row.get('category', '')} - {row.get('description', '')}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cost_tracker.py",
        description="Track Turd Eye Productions expenses and income (stdlib only, headless-friendly).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for name, help_text in (("add-expense", "Log an expense"), ("add-income", "Log income")):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--date", help="Date in UTC as YYYY-MM-DD (default: today)")
        p.add_argument("--category", help="Category, e.g. Suno, DistroKid, Commission")
        p.add_argument("--amount", help="Amount in USD, non-negative")
        p.add_argument("--description", help="Free-text description")

    p_sum = sub.add_parser("summary", help="Show income/expense/profit summary")
    group = p_sum.add_mutually_exclusive_group()
    group.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    group.add_argument(
        "--markdown",
        nargs="?",
        const="",
        default=None,
        metavar="PATH",
        help="Write a Markdown summary (default: data/cost_summary.md)",
    )

    p_list = sub.add_parser("list", help="List recent entries")
    p_list.add_argument("--limit", type=int, default=15, help="Number of entries to show (0 = all)")

    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "add-expense":
        return add_entry("expense", args)
    if args.command == "add-income":
        return add_entry("income", args)
    if args.command == "summary":
        return summary(args)
    return list_entries(args)


if __name__ == "__main__":
    sys.exit(main())
