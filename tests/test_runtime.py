import asyncio
import os
import sqlite3
import tempfile
import unittest
from typing import Any, cast

from core.runtime import create_session


class RuntimeSessionTests(unittest.TestCase):
    def test_create_session_close_closes_all_tracked_connections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "session.db")
            session = create_session(session_id="s-runtime", db_path=db_path, limit=10)

            asyncio.run(
                session.add_items(
                    [
                        {
                            "type": "message",
                            "role": "user",
                            "content": [{"type": "input_text", "text": "hello"}],
                        }
                    ]
                )
            )

            tracked_before_close = list(cast(Any, session)._tracked_connections)
            self.assertGreaterEqual(len(tracked_before_close), 1)

            cast(Any, session).close()

            self.assertEqual(len(cast(Any, session)._tracked_connections), 0)
            for conn in tracked_before_close:
                with self.assertRaises(sqlite3.ProgrammingError):
                    conn.execute("SELECT 1;")


if __name__ == "__main__":
    unittest.main()
