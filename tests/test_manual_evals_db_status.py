import sqlite3
import unittest
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.build_manual_evals_db import build_manual_evals_db
from tools.manual_evals_db_status import (
    data_freshness_status,
    format_freshness_status,
)
from tests.test_build_manual_evals_db import _init_history_db


class ManualEvalsDbStatusTests(unittest.TestCase):
    def test_status_summarizes_current_manual_eval_db_without_mutating_sources(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            history_db = tmp / "history.db"
            output_db = tmp / "manual_evals.db"
            _init_history_db(history_db)
            build_manual_evals_db(
                history_db=history_db,
                output_db=output_db,
                include_thumbnails=False,
            )

            before_history = history_db.stat().st_mtime_ns
            before_output = output_db.stat().st_mtime_ns
            freshness = data_freshness_status(db_path=output_db)
            summary = format_freshness_status(freshness)
            after_history = history_db.stat().st_mtime_ns
            after_output = output_db.stat().st_mtime_ns

            self.assertEqual(before_history, after_history)
            self.assertEqual(before_output, after_output)
            self.assertEqual(freshness["state"], "current")
            self.assertIn("manual_evals.db status: state=current", summary)
            self.assertIn("count_scope=manual_eval_import", summary)
            self.assertIn("warnings: none", summary)

            with closing(sqlite3.connect(output_db)) as conn:
                self.assertEqual(
                    conn.execute("PRAGMA integrity_check").fetchone()[0], "ok"
                )

    def test_status_summarizes_missing_manual_eval_db(self) -> None:
        with TemporaryDirectory() as tmpdir:
            output_db = Path(tmpdir) / "missing.db"

            freshness = data_freshness_status(db_path=output_db)
            summary = format_freshness_status(freshness)

            self.assertEqual(freshness["state"], "missing")
            self.assertIn("state=missing", summary)
            self.assertIn("source history DBs: none recorded", summary)


if __name__ == "__main__":
    unittest.main()
