import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

import tools.build_eval_relationship_graph as eval_relationship_graph


class BuildEvalRelationshipGraphTests(unittest.TestCase):
    def test_markdown_contains_navigation_and_session_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = self._create_db(Path(tmpdir))
            markdown = eval_relationship_graph.build_eval_relationship_markdown(
                db_path=db_path
            )
            self.assertIn("# Eval Relationship Graph", markdown)
            self.assertIn("## Quick Navigation", markdown)
            self.assertIn("## Session Directory", markdown)
            self.assertIn("[session-alpha](#session-session-alpha)", markdown)
            self.assertIn("### Session session-alpha", markdown)
            self.assertIn("tag:grounded", markdown)

    def test_session_filter_limits_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = self._create_db(Path(tmpdir))
            markdown = eval_relationship_graph.build_eval_relationship_markdown(
                db_path=db_path,
                session_filter={"session-beta"},
            )
            self.assertIn("[session-beta](#session-session-beta)", markdown)
            self.assertNotIn("[session-alpha](#session-session-alpha)", markdown)
            self.assertIn("### Session session-beta", markdown)
            self.assertNotIn("### Session session-alpha", markdown)

    def test_writer_creates_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            db_path = self._create_db(tmp)
            output = tmp / "visuals" / "eval_relationship_graph.md"
            eval_relationship_graph.build_eval_relationship_graph(
                db_path=db_path,
                output=output,
            )
            self.assertTrue(output.exists())
            text = output.read_text(encoding="utf-8")
            self.assertIn("## Tag Frequency", text)

    def _create_db(self, root: Path) -> Path:
        db_path = root / "history.db"
        conn = sqlite3.connect(db_path)
        conn.execute(
            """
            CREATE TABLE chats (
              session_id TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              created_at INTEGER NOT NULL,
              updated_at INTEGER NOT NULL,
              status TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE chat_messages (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id TEXT NOT NULL,
              role TEXT NOT NULL,
              content TEXT NOT NULL,
              created_at INTEGER NOT NULL,
              message_id TEXT,
              parent_message_id TEXT
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE message_feedback (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id TEXT NOT NULL,
              message_id TEXT NOT NULL,
              outcome TEXT NOT NULL,
              tags_json TEXT NOT NULL,
              note TEXT,
              status TEXT NOT NULL,
              created_at INTEGER NOT NULL,
              updated_at INTEGER NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE eval_checkpoints (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              checkpoint_id TEXT NOT NULL,
              session_id TEXT NOT NULL,
              total_count INTEGER NOT NULL,
              pass_count INTEGER NOT NULL,
              fail_count INTEGER NOT NULL,
              other_count INTEGER NOT NULL,
              created_at INTEGER NOT NULL
            );
            """
        )

        now = 1_710_000_000_000
        conn.executemany(
            """
            INSERT INTO chats(session_id, title, created_at, updated_at, status)
            VALUES (?, ?, ?, ?, ?);
            """,
            [
                ("session-alpha", "Alpha chat", now, now + 1000, "active"),
                ("session-beta", "Beta chat", now + 2000, now + 3000, "active"),
            ],
        )
        conn.executemany(
            """
            INSERT INTO chat_messages(session_id, role, content, created_at, message_id, parent_message_id)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            [
                ("session-alpha", "user", "hello", now + 10, "m-alpha-u", None),
                ("session-alpha", "assistant", "hi", now + 20, "m-alpha-a", "m-alpha-u"),
                ("session-beta", "user", "need review", now + 30, "m-beta-u", None),
                ("session-beta", "assistant", "reviewed", now + 40, "m-beta-a", "m-beta-u"),
            ],
        )
        conn.executemany(
            """
            INSERT INTO message_feedback(session_id, message_id, outcome, tags_json, note, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            [
                (
                    "session-alpha",
                    "m-alpha-a",
                    "pass",
                    json.dumps({"positive": ["grounded"], "negative": [], "all": ["grounded"]}),
                    "clean",
                    "closed",
                    now + 50,
                    now + 60,
                ),
                (
                    "session-beta",
                    "m-beta-a",
                    "fail",
                    json.dumps({"positive": [], "negative": ["hallucination_risk"], "all": ["hallucination_risk"]}),
                    "needs fix",
                    "open",
                    now + 70,
                    now + 80,
                ),
            ],
        )
        conn.executemany(
            """
            INSERT INTO eval_checkpoints(checkpoint_id, session_id, total_count, pass_count, fail_count, other_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            [
                ("cp-alpha", "session-alpha", 1, 1, 0, 0, now + 90),
                ("cp-beta", "session-beta", 1, 0, 1, 0, now + 100),
            ],
        )
        conn.commit()
        conn.close()
        return db_path


if __name__ == "__main__":
    unittest.main()
