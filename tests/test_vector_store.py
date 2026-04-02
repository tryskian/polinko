import os
import sqlite3
import tempfile
import unittest

from core.vector_store import VectorStore


class VectorStoreTests(unittest.TestCase):
    def test_non_chat_vectors_get_derived_message_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "vectors.db")
            store = VectorStore(db_path)

            source_ref = "ocr-abc123:1/2"
            store.upsert_message_vector(
                session_id="s-ocr",
                role="assistant",
                content="extracted ocr text",
                embedding=[0.1, 0.2, 0.3],
                message_id=None,
                source_type="ocr",
                source_ref=source_ref,
                metadata={"source": "ocr"},
                created_at=1_700_000_000_000,
            )

            with sqlite3.connect(db_path) as conn:
                row = conn.execute(
                    "SELECT message_id FROM message_vectors WHERE source_ref = ? LIMIT 1;",
                    (source_ref,),
                ).fetchone()

            self.assertIsNotNone(row)
            self.assertEqual(row[0], f"ocr:{source_ref}")

    def test_initialize_backfills_legacy_non_chat_message_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "vectors-legacy.db")
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE message_vectors (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      vector_id TEXT NOT NULL UNIQUE,
                      session_id TEXT NOT NULL,
                      role TEXT NOT NULL,
                      message_id TEXT,
                      source_type TEXT NOT NULL DEFAULT 'chat',
                      source_ref TEXT,
                      metadata_json TEXT,
                      content TEXT NOT NULL,
                      embedding_json TEXT NOT NULL,
                      created_at INTEGER NOT NULL,
                      active INTEGER NOT NULL DEFAULT 1
                    );
                    """
                )
                conn.execute(
                    """
                    INSERT INTO message_vectors(
                      vector_id, session_id, role, message_id, source_type, source_ref,
                      metadata_json, content, embedding_json, created_at, active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        "vec-legacy-1",
                        "s-legacy",
                        "assistant",
                        None,
                        "ocr",
                        "ocr-legacy:1/1",
                        "{}",
                        "legacy row",
                        "[0.1,0.2]",
                        1_700_000_000_000,
                        1,
                    ),
                )
                conn.execute(
                    """
                    INSERT INTO message_vectors(
                      vector_id, session_id, role, message_id, source_type, source_ref,
                      metadata_json, content, embedding_json, created_at, active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        "vec-legacy-chat",
                        "s-chat",
                        "assistant",
                        None,
                        "chat",
                        "msg_legacy",
                        "{}",
                        "chat row",
                        "[0.2,0.3]",
                        1_700_000_000_001,
                        1,
                    ),
                )

            # Reopening through VectorStore runs schema ensure + backfill.
            VectorStore(db_path)

            with sqlite3.connect(db_path) as conn:
                ocr_row = conn.execute(
                    "SELECT message_id FROM message_vectors WHERE vector_id = 'vec-legacy-1';"
                ).fetchone()
                chat_row = conn.execute(
                    "SELECT message_id FROM message_vectors WHERE vector_id = 'vec-legacy-chat';"
                ).fetchone()

            self.assertIsNotNone(ocr_row)
            self.assertEqual(ocr_row[0], "ocr:ocr-legacy:1/1")
            self.assertIsNotNone(chat_row)
            self.assertIsNone(chat_row[0])


if __name__ == "__main__":
    unittest.main()
