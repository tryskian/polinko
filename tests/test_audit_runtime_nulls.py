import sqlite3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.audit_runtime_nulls import build_report


class AuditRuntimeNullsTests(unittest.TestCase):
    def test_build_report_counts_expected_null_surfaces(self) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            history_db = tmp / "history.db"
            vector_db = tmp / "vector.db"

            with sqlite3.connect(history_db) as conn:
                conn.execute(
                    "CREATE TABLE ocr_runs (run_id TEXT, source_message_id TEXT, result_message_id TEXT)"
                )
                conn.execute("INSERT INTO ocr_runs VALUES ('r1', 'm1', 'm2')")
                conn.execute("INSERT INTO ocr_runs VALUES ('r2', NULL, NULL)")
                conn.execute("INSERT INTO ocr_runs VALUES ('r3', '', 'm3')")
                conn.commit()

            with sqlite3.connect(vector_db) as conn:
                conn.execute(
                    "CREATE TABLE message_vectors (message_id TEXT, source_type TEXT)"
                )
                conn.execute("INSERT INTO message_vectors VALUES ('m1', 'chat')")
                conn.execute("INSERT INTO message_vectors VALUES ('', 'attachment')")
                conn.execute("INSERT INTO message_vectors VALUES (NULL, 'attachment')")
                conn.execute("INSERT INTO message_vectors VALUES ('att:1', 'attachment')")
                conn.commit()

            report = build_report(history_db=history_db, vector_db=vector_db)

            self.assertEqual(report["history"]["ocr_runs_total"], 3)
            self.assertEqual(report["history"]["source_message_id_null"], 2)
            self.assertEqual(report["history"]["result_message_id_null"], 1)
            self.assertEqual(report["history"]["both_message_ids_null"], 1)

            self.assertEqual(report["vector"]["message_vectors_total"], 4)
            self.assertEqual(report["vector"]["message_id_null"], 2)
            self.assertEqual(report["vector"]["non_chat_total"], 3)
            self.assertEqual(report["vector"]["non_chat_message_id_null"], 2)


if __name__ == "__main__":
    unittest.main()
