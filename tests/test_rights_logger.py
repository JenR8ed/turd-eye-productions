"""Tests for scripts/rights_logger.py (stdlib unittest, no third-party deps)."""

import csv
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import rights_logger  # noqa: E402


class RightsLoggerTestCase(unittest.TestCase):
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
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = rights_logger.main(argv)
        return code, out.getvalue(), err.getvalue()

    def add_track(self, title="Neon Drift", **overrides):
        argv = ["add", "--title", title, "--tool", "Suno", "--plan", "Pro", "--human-edits", "trimmed intro"]
        for key, value in overrides.items():
            flag = "--" + key.replace("_", "-")
            if flag in argv:
                argv[argv.index(flag) + 1] = value
            else:
                argv += [flag, value]
        return self.run_cli(argv)

    def rows(self):
        with open(self.data_dir / "rights_log.csv", encoding="utf-8") as f:
            return list(csv.DictReader(f))


class TestNormalizers(RightsLoggerTestCase):
    def test_yes_no_normalization(self):
        for value in ("yes", "Y", "TRUE", "1"):
            self.assertEqual(rights_logger.normalize_yes_no(value), "yes")
        for value in ("no", "N", "false", "0"):
            self.assertEqual(rights_logger.normalize_yes_no(value), "no")

    def test_yes_no_rejects_garbage(self):
        with self.assertRaises(ValueError):
            rights_logger.normalize_yes_no("maybe")

    def test_generation_datetime_accepts_both_formats(self):
        self.assertEqual(rights_logger.valid_generation_datetime("2026-07-24 13:45"), "2026-07-24 13:45")
        self.assertEqual(rights_logger.valid_generation_datetime("2026-07-24"), "2026-07-24 00:00")

    def test_generation_datetime_rejects_bad_input(self):
        for bad in ("24/07/2026", "now", "2026-07-24T13:45"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    rights_logger.valid_generation_datetime(bad)


class TestAdd(RightsLoggerTestCase):
    def test_creates_store_with_headers(self):
        self.run_cli(["list"])
        with open(self.data_dir / "rights_log.csv", encoding="utf-8") as f:
            self.assertEqual(f.readline().strip().split(","), rights_logger.HEADERS)

    def test_add_headless_writes_row(self):
        code, out, _ = self.add_track(distributor="DistroKid", notes="first release")
        self.assertEqual(code, 0)
        self.assertIn("Neon Drift", out)
        rows = self.rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["tool"], "Suno")
        self.assertEqual(rows[0]["plan"], "Pro")
        self.assertEqual(rows[0]["commercial_rights"], "yes")
        self.assertEqual(rows[0]["distributor"], "DistroKid")
        self.assertTrue(rows[0]["generation_datetime_utc"])
        self.assertTrue(rows[0]["logged_at_utc"])

    def test_commercial_rights_defaults_to_yes(self):
        self.add_track()
        self.assertEqual(self.rows()[0]["commercial_rights"], "yes")

    def test_missing_required_field_fails_cleanly(self):
        code, _, _ = self.run_cli(["add", "--title", "Orphan"])
        self.assertEqual(code, 2)

    def test_invalid_commercial_value_rejected(self):
        code, _, _ = self.add_track(commercial="perhaps")
        self.assertEqual(code, 2)
        self.assertEqual(self.rows(), [])

    def test_warns_when_no_commercial_rights(self):
        code, _, err = self.add_track(commercial="no")
        self.assertEqual(code, 0)
        self.assertIn("no commercial rights", err)

    def test_warns_when_no_human_edits(self):
        code, _, err = self.run_cli(["add", "--title", "Raw", "--tool", "Suno", "--plan", "Pro"])
        self.assertEqual(code, 0)
        self.assertIn("no human edits", err)

    def test_clean_entry_produces_no_warnings(self):
        _, _, err = self.add_track()
        self.assertEqual(err.strip(), "")


class TestVerify(RightsLoggerTestCase):
    def test_empty_log_is_ok(self):
        code, out, _ = self.run_cli(["verify"])
        self.assertEqual(code, 0)
        self.assertIn("Nothing to verify", out)

    def test_clean_log_passes(self):
        self.add_track()
        code, out, _ = self.run_cli(["verify"])
        self.assertEqual(code, 0)
        self.assertIn("satisfy", out)

    def test_reports_violations(self):
        self.add_track(title="Bad", commercial="no")
        code, out, _ = self.run_cli(["verify"])
        self.assertEqual(code, 0)
        self.assertIn("no commercial rights", out)
        self.assertIn("1 issue(s) found", out)

    def test_strict_mode_exits_nonzero(self):
        self.add_track(title="Bad", commercial="no")
        code, _, _ = self.run_cli(["verify", "--strict"])
        self.assertEqual(code, 1)

    def test_strict_mode_passes_on_clean_log(self):
        self.add_track()
        code, _, _ = self.run_cli(["verify", "--strict"])
        self.assertEqual(code, 0)


class TestExport(RightsLoggerTestCase):
    def test_export_default_path(self):
        self.add_track()
        code, out, _ = self.run_cli(["export"])
        self.assertEqual(code, 0)
        content = (self.data_dir / "rights_log.md").read_text(encoding="utf-8")
        self.assertIn("# Rights Log", content)
        self.assertIn("Neon Drift", content)
        self.assertIn("Entries: 1", content)

    def test_export_custom_path(self):
        self.add_track()
        target = self.data_dir / "nested" / "log.md"
        code, _, _ = self.run_cli(["export", "--output", str(target)])
        self.assertEqual(code, 0)
        self.assertIn("Neon Drift", target.read_text(encoding="utf-8"))

    def test_export_empty_log_still_writes_table(self):
        code, _, _ = self.run_cli(["export"])
        self.assertEqual(code, 0)
        self.assertIn("Entries: 0", (self.data_dir / "rights_log.md").read_text(encoding="utf-8"))

    def test_export_escapes_pipes_and_newlines(self):
        self.add_track(title="A|B", notes="line1\nline2")
        self.run_cli(["export"])
        content = (self.data_dir / "rights_log.md").read_text(encoding="utf-8")
        self.assertIn("A\\|B", content)
        self.assertNotIn("line1\nline2", content)
        self.assertIn("line1 line2", content)
        # One header row, one separator row, one data row.
        table_rows = [line for line in content.splitlines() if line.startswith("|")]
        self.assertEqual(len(table_rows), 3)


class TestList(RightsLoggerTestCase):
    def test_empty_list_gives_guidance(self):
        code, out, _ = self.run_cli(["list"])
        self.assertEqual(code, 0)
        self.assertIn("No entries yet", out)

    def test_limit_respected(self):
        for i in range(4):
            self.add_track(title=f"Track{i}")
        code, out, _ = self.run_cli(["list", "--limit", "2"])
        self.assertEqual(code, 0)
        self.assertIn("showing 2 of 4", out)
        self.assertIn("Track3", out)
        self.assertNotIn("Track0", out)

    def test_limit_zero_shows_all(self):
        for i in range(3):
            self.add_track(title=f"Track{i}")
        _, out, _ = self.run_cli(["list", "--limit", "0"])
        self.assertIn("showing 3 of 3", out)


class TestCLIContract(RightsLoggerTestCase):
    def test_no_command_exits_nonzero(self):
        with self.assertRaises(SystemExit) as ctx:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                rights_logger.main([])
        self.assertNotEqual(ctx.exception.code, 0)

    def test_unknown_command_exits_nonzero(self):
        with self.assertRaises(SystemExit) as ctx:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                rights_logger.main(["bogus"])
        self.assertNotEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
