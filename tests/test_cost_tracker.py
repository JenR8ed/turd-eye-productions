"""Tests for scripts/cost_tracker.py (stdlib unittest, no third-party deps)."""

import csv
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import cost_tracker  # noqa: E402


class CostTrackerTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self._prev = os.environ.get("TEP_DATA_DIR")
        os.environ["TEP_DATA_DIR"] = self._tmp.name
        self.addCleanup(self._restore_env)
        self.data_dir = Path(self._tmp.name)

    def _restore_env(self):
        if self._prev is None:
            os.environ.pop("TEP_DATA_DIR", None)
        else:
            os.environ["TEP_DATA_DIR"] = self._prev

    def run_cli(self, argv):
        buffer = io.StringIO()
        with redirect_stdout(buffer), redirect_stderr(io.StringIO()):
            code = cost_tracker.main(argv)
        return code, buffer.getvalue()

    def rows(self):
        with open(self.data_dir / "costs.csv", encoding="utf-8") as f:
            return list(csv.DictReader(f))


class TestMoney(CostTrackerTestCase):
    def test_normalizes_to_two_decimals(self):
        self.assertEqual(cost_tracker.money("10"), "10.00")
        self.assertEqual(cost_tracker.money("10.5"), "10.50")
        self.assertEqual(cost_tracker.money("$1,234.567"), "1234.57")

    def test_rejects_invalid_and_negative(self):
        for bad in ("abc", "", "NaN", "-5"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    cost_tracker.money(bad)


class TestDateValidation(CostTrackerTestCase):
    def test_accepts_iso_date(self):
        self.assertEqual(cost_tracker.valid_date("2026-07-24"), "2026-07-24")

    def test_rejects_bad_format(self):
        for bad in ("07/24/2026", "2026-13-01", "yesterday"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    cost_tracker.valid_date(bad)


class TestAddEntries(CostTrackerTestCase):
    def test_creates_store_with_headers(self):
        code, _ = self.run_cli(["summary"])
        self.assertEqual(code, 0)
        with open(self.data_dir / "costs.csv", encoding="utf-8") as f:
            self.assertEqual(f.readline().strip().split(","), cost_tracker.HEADERS)

    def test_add_expense_headless(self):
        code, out = self.run_cli(
            ["add-expense", "--category", "Suno", "--amount", "10", "--description", "Pro plan", "--date", "2026-07-01"]
        )
        self.assertEqual(code, 0)
        self.assertIn("10.00", out)
        rows = self.rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["type"], "expense")
        self.assertEqual(rows[0]["category"], "Suno")
        self.assertEqual(rows[0]["amount_usd"], "10.00")
        self.assertEqual(rows[0]["date_utc"], "2026-07-01")
        self.assertTrue(rows[0]["logged_at_utc"])

    def test_add_income_headless(self):
        code, _ = self.run_cli(["add-income", "--category", "Commission", "--amount", "250.5"])
        self.assertEqual(code, 0)
        rows = self.rows()
        self.assertEqual(rows[0]["type"], "income")
        self.assertEqual(rows[0]["amount_usd"], "250.50")
        self.assertEqual(rows[0]["description"], "")

    def test_defaults_date_to_today(self):
        self.run_cli(["add-expense", "--category", "DistroKid", "--amount", "25"])
        self.assertEqual(self.rows()[0]["date_utc"], cost_tracker.today_utc())

    def test_missing_required_field_fails_cleanly(self):
        # stdin is not a TTY under the test runner, so this must error rather than hang.
        code, _ = self.run_cli(["add-expense", "--amount", "10"])
        self.assertEqual(code, 2)

    def test_invalid_amount_fails_without_writing(self):
        code, _ = self.run_cli(["add-expense", "--category", "Suno", "--amount", "ten"])
        self.assertEqual(code, 2)
        self.assertEqual(self.rows(), [])

    def test_commas_and_dollar_signs_accepted(self):
        self.run_cli(["add-income", "--category", "Commission", "--amount", "$1,500"])
        self.assertEqual(self.rows()[0]["amount_usd"], "1500.00")


class TestSummary(CostTrackerTestCase):
    def seed(self):
        self.run_cli(["add-expense", "--category", "Suno", "--amount", "10", "--description", "sub"])
        self.run_cli(["add-expense", "--category", "DistroKid", "--amount", "25", "--description", "annual"])
        self.run_cli(["add-income", "--category", "Commission", "--amount", "300", "--description", "client"])

    def test_computes_totals_and_net(self):
        self.seed()
        data = cost_tracker.compute_summary()
        self.assertEqual(data["total_income_usd"], "300.00")
        self.assertEqual(data["total_expenses_usd"], "35.00")
        self.assertEqual(data["net_profit_usd"], "265.00")
        self.assertEqual(data["entry_count"], 3)

    def test_net_by_category_signs(self):
        self.seed()
        by_cat = cost_tracker.compute_summary()["net_by_category_usd"]
        self.assertEqual(by_cat["Commission"], "300.00")
        self.assertEqual(by_cat["Suno"], "-10.00")
        self.assertEqual(by_cat["DistroKid"], "-25.00")

    def test_empty_summary_is_zeroed(self):
        data = cost_tracker.compute_summary()
        self.assertEqual(data["net_profit_usd"], "0.00")
        self.assertEqual(data["entry_count"], 0)

    def test_json_output_is_parseable(self):
        self.seed()
        code, out = self.run_cli(["summary", "--json"])
        self.assertEqual(code, 0)
        parsed = json.loads(out)
        self.assertEqual(parsed["net_profit_usd"], "265.00")

    def test_markdown_export_default_path(self):
        self.seed()
        code, _ = self.run_cli(["summary", "--markdown"])
        self.assertEqual(code, 0)
        content = (self.data_dir / "cost_summary.md").read_text(encoding="utf-8")
        self.assertIn("# Cost & Income Summary", content)
        self.assertIn("265.00", content)

    def test_markdown_export_custom_path(self):
        self.seed()
        target = self.data_dir / "nested" / "out.md"
        code, _ = self.run_cli(["summary", "--markdown", str(target)])
        self.assertEqual(code, 0)
        self.assertTrue(target.exists())

    def test_markdown_escapes_pipe_in_category(self):
        self.run_cli(["add-income", "--category", "Weird|Cat", "--amount", "5"])
        code, _ = self.run_cli(["summary", "--markdown"])
        self.assertEqual(code, 0)
        self.assertIn("Weird\\|Cat", (self.data_dir / "cost_summary.md").read_text(encoding="utf-8"))

    def test_empty_summary_prints_guidance(self):
        code, out = self.run_cli(["summary"])
        self.assertEqual(code, 0)
        self.assertIn("No data yet", out)


class TestList(CostTrackerTestCase):
    def test_empty_list(self):
        code, out = self.run_cli(["list"])
        self.assertEqual(code, 0)
        self.assertIn("No data yet", out)

    def test_limit_respected(self):
        for i in range(5):
            self.run_cli(["add-expense", "--category", f"Cat{i}", "--amount", "1"])
        code, out = self.run_cli(["list", "--limit", "2"])
        self.assertEqual(code, 0)
        self.assertIn("showing 2 of 5", out)
        self.assertIn("Cat4", out)
        self.assertNotIn("Cat0", out)

    def test_limit_zero_shows_all(self):
        for i in range(3):
            self.run_cli(["add-income", "--category", f"Cat{i}", "--amount", "1"])
        _, out = self.run_cli(["list", "--limit", "0"])
        self.assertIn("showing 3 of 3", out)

    def test_expense_and_income_signs(self):
        self.run_cli(["add-expense", "--category", "Suno", "--amount", "10"])
        self.run_cli(["add-income", "--category", "Commission", "--amount", "20"])
        _, out = self.run_cli(["list"])
        self.assertIn("-$", out)
        self.assertIn("+$", out)


class TestCLIContract(CostTrackerTestCase):
    def test_no_command_exits_nonzero(self):
        with self.assertRaises(SystemExit) as ctx:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                cost_tracker.main([])
        self.assertNotEqual(ctx.exception.code, 0)

    def test_unknown_command_exits_nonzero(self):
        with self.assertRaises(SystemExit) as ctx:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                cost_tracker.main(["bogus"])
        self.assertNotEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
