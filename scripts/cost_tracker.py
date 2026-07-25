#!/usr/bin/env python3
"""
Turd Eye Productions — Cost & Income Tracker
Lightweight, stdlib-only CLI for tracking expenses and income.

Usage:
  python scripts/cost_tracker.py add-expense
  python scripts/cost_tracker.py add-income
  python scripts/cost_tracker.py summary
  python scripts/cost_tracker.py list
"""

import csv
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
COST_FILE = DATA_DIR / "costs.csv"

HEADERS = ["date_utc", "type", "category", "amount_usd", "description", "logged_at_utc"]


def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)
    if not COST_FILE.exists():
        with open(COST_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()


def money(value: str) -> str:
    """Normalize to 2 decimal places as string."""
    return str(Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def add_entry(entry_type: str):
    ensure_data_dir()
    print(f"\n=== Add {entry_type.upper()} ===")
    date = input("Date UTC (YYYY-MM-DD, blank = today): ").strip() or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    category = input("Category (e.g. Suno, DistroKid, Commission, Streaming): ").strip()
    amount = money(input("Amount USD: ").strip())
    description = input("Description: ").strip()

    entry = {
        "date_utc": date,
        "type": entry_type,
        "category": category,
        "amount_usd": amount,
        "description": description,
        "logged_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    }

    with open(COST_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writerow(entry)

    print(f"✓ Logged {entry_type}: ${amount} — {category}")


def summary():
    ensure_data_dir()
    if not COST_FILE.exists() or COST_FILE.stat().st_size == 0:
        print("No data yet.")
        return

    expenses = Decimal("0")
    income = Decimal("0")
    by_category = {}

    with open(COST_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            amt = Decimal(row["amount_usd"])
            cat = row["category"]
            if row["type"] == "expense":
                expenses += amt
                by_category[cat] = by_category.get(cat, Decimal("0")) - amt
            else:
                income += amt
                by_category[cat] = by_category.get(cat, Decimal("0")) + amt

    profit = income - expenses
    print("\n=== Financial Summary ===")
    print(f"Total Income  : ${income:.2f}")
    print(f"Total Expenses: ${expenses:.2f}")
    print(f"Net Profit    : ${profit:.2f}")
    print("\nBy Category:")
    for cat, val in sorted(by_category.items(), key=lambda x: abs(x[1]), reverse=True):
        print(f"  {cat:20} ${val:.2f}")


def list_entries(limit=15):
    ensure_data_dir()
    if not COST_FILE.exists():
        print("No data yet.")
        return

    with open(COST_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No data yet.")
        return

    print(f"\n=== Recent Entries (last {min(limit, len(rows))}) ===\n")
    for row in rows[-limit:]:
        sign = "-" if row["type"] == "expense" else "+"
        print(f"{row['date_utc']} | {sign}${row['amount_usd']:>8} | {row['type']:7} | {row['category']} — {row['description']}")


def main():
    import sys
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()
    if cmd == "add-expense":
        add_entry("expense")
    elif cmd == "add-income":
        add_entry("income")
    elif cmd == "summary":
        summary()
    elif cmd == "list":
        list_entries()
    else:
        print("Unknown command. Use: add-expense | add-income | summary | list")


if __name__ == "__main__":
    main()
