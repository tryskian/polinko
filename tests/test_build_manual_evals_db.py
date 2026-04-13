import base64
import sqlite3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.build_manual_evals_db import HistorySource, build_manual_evals_db


_PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+lmR8AAAAASUVORK5CYII="
)


def _init_history_db(
    path: Path,
    *,
    session_id: str = "chat-1",
    title: str = "Manual OCR",
    run_id: str = "ocr-1",
    source_name: str = "file-abc123-image1.png",
    feedback_outcome: str | None = None,
) -> None:
    with sqlite3.connect(path) as conn:
        conn.executescript(
            """
            CREATE TABLE chats (
              session_id TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              created_at INTEGER NOT NULL,
              updated_at INTEGER NOT NULL,
              status TEXT NOT NULL DEFAULT 'active',
              deprecated_at INTEGER
            );
            CREATE TABLE chat_messages (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id TEXT NOT NULL,
              role TEXT NOT NULL,
              content TEXT NOT NULL,
              created_at INTEGER NOT NULL,
              message_id TEXT,
              parent_message_id TEXT
            );
            CREATE TABLE message_feedback (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id TEXT NOT NULL,
              message_id TEXT NOT NULL,
              outcome TEXT NOT NULL,
              tags_json TEXT NOT NULL DEFAULT '[]',
              note TEXT,
              recommended_action TEXT,
              action_taken TEXT,
              status TEXT NOT NULL DEFAULT 'logged',
              created_at INTEGER NOT NULL,
              updated_at INTEGER NOT NULL
            );
            CREATE TABLE eval_checkpoints (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              checkpoint_id TEXT UNIQUE NOT NULL,
              session_id TEXT NOT NULL,
              total_count INTEGER NOT NULL,
              pass_count INTEGER NOT NULL,
              fail_count INTEGER NOT NULL,
              other_count INTEGER NOT NULL,
              created_at INTEGER NOT NULL
            );
            CREATE TABLE ocr_runs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              run_id TEXT UNIQUE NOT NULL,
              session_id TEXT NOT NULL,
              source_name TEXT,
              mime_type TEXT,
              source_message_id TEXT,
              result_message_id TEXT,
              status TEXT NOT NULL,
              extracted_text TEXT NOT NULL,
              created_at INTEGER NOT NULL
            );
            """
        )
        conn.execute(
            """
            INSERT INTO chats (session_id, title, created_at, updated_at, status, deprecated_at)
            VALUES (?, ?, 100, 200, 'active', NULL)
            """,
            (session_id, title),
        )
        conn.execute(
            """
            INSERT INTO ocr_runs (
              run_id, session_id, source_name, mime_type, source_message_id, result_message_id,
              status, extracted_text, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                session_id,
                source_name,
                "image/png",
                "m-source-1",
                "m-result-1",
                "ok",
                "hello world",
                150,
            ),
        )
        if feedback_outcome is not None:
            conn.execute(
                """
                INSERT INTO message_feedback (
                  session_id, message_id, outcome, tags_json, note, recommended_action,
                  action_taken, status, created_at, updated_at
                ) VALUES (?, 'm-result-1', ?, '[]', 'manual note', NULL, NULL, 'logged', 160, 170)
                """,
                (session_id, feedback_outcome),
            )
        conn.commit()


class BuildManualEvalsDbTests(unittest.TestCase):
    def test_build_includes_resolved_image_asset(self) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            history_db = tmp / "history.db"
            output_db = tmp / "manual_evals.db"
            image_dir = tmp / "images"
            image_dir.mkdir(parents=True, exist_ok=True)
            (image_dir / "image1.png").write_bytes(_PNG_1X1)
            _init_history_db(history_db)

            result = build_manual_evals_db(
                history_db=history_db,
                output_db=output_db,
                image_roots=[image_dir],
                include_thumbnails=False,
            )

            self.assertEqual(result["sessions"], 1)
            self.assertEqual(result["ocr_runs"], 1)
            self.assertEqual(result["image_assets"], 1)

            with sqlite3.connect(output_db) as conn:
                conn.row_factory = sqlite3.Row
                asset = conn.execute(
                    "SELECT resolved_path, status, thumbnail_png FROM image_assets LIMIT 1"
                ).fetchone()
                assert asset is not None
                self.assertEqual(Path(str(asset["resolved_path"])).name, "image1.png")
                self.assertEqual(str(asset["status"]), "resolved")
                self.assertIsNone(asset["thumbnail_png"])

    def test_build_can_generate_thumbnail_preview(self) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            history_db = tmp / "history.db"
            output_db = tmp / "manual_evals.db"
            image_dir = tmp / "images"
            image_dir.mkdir(parents=True, exist_ok=True)
            (image_dir / "image1.png").write_bytes(_PNG_1X1)
            _init_history_db(history_db)

            result = build_manual_evals_db(
                history_db=history_db,
                output_db=output_db,
                image_roots=[image_dir],
                include_thumbnails=True,
                thumbnail_size=96,
            )

            with sqlite3.connect(output_db) as conn:
                conn.row_factory = sqlite3.Row
                asset = conn.execute(
                    """
                    SELECT status, thumbnail_png, thumbnail_data_url, thumbnail_width, thumbnail_height
                    FROM image_assets
                    LIMIT 1
                    """
                ).fetchone()
                assert asset is not None
                status = str(asset["status"])
                self.assertIn(status, {"thumbnail_ready", "resolved_no_pillow", "thumbnail_error"})
                if status == "thumbnail_ready":
                    self.assertGreater(len(bytes(asset["thumbnail_png"])), 0)
                    self.assertTrue(str(asset["thumbnail_data_url"]).startswith("data:image/png;base64,"))
                    self.assertGreater(int(asset["thumbnail_width"]), 0)
                    self.assertGreater(int(asset["thumbnail_height"]), 0)
                    self.assertGreater(result["thumbnails_ready"], 0)

    def test_build_combines_multiple_history_sources_with_provenance(self) -> None:
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            beta_history = tmp / "beta-history.db"
            current_history = tmp / "current-history.db"
            output_db = tmp / "manual_evals.db"
            _init_history_db(beta_history, feedback_outcome="PASS")
            _init_history_db(current_history)

            result = build_manual_evals_db(
                history_db=current_history,
                output_db=output_db,
                history_sources=[
                    HistorySource(era="beta_1_0", history_db=beta_history),
                    HistorySource(era="current", history_db=current_history),
                ],
                include_thumbnails=False,
            )

            self.assertEqual(result["sessions"], 2)
            self.assertEqual(result["feedback"], 1)
            self.assertEqual(result["ocr_runs"], 2)

            with sqlite3.connect(output_db) as conn:
                conn.row_factory = sqlite3.Row
                sessions = conn.execute(
                    "SELECT session_id, era, source_session_id FROM sessions ORDER BY era"
                ).fetchall()
                self.assertEqual([str(row["source_session_id"]) for row in sessions], ["chat-1", "chat-1"])
                self.assertEqual([str(row["era"]) for row in sessions], ["beta_1_0", "current"])
                self.assertEqual(str(sessions[0]["session_id"]), "beta_1_0:chat-1")
                self.assertEqual(str(sessions[1]["session_id"]), "current:chat-1")

                runs = conn.execute(
                    "SELECT run_id, source_run_id, era FROM ocr_runs ORDER BY era"
                ).fetchall()
                self.assertEqual([str(row["source_run_id"]) for row in runs], ["ocr-1", "ocr-1"])
                self.assertEqual(str(runs[0]["run_id"]), "beta_1_0:ocr-1")
                self.assertEqual(str(runs[1]["run_id"]), "current:ocr-1")


if __name__ == "__main__":
    unittest.main()
