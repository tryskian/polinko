from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass


DEFAULT_CHAT_TITLE = "New chat"


@dataclass(frozen=True)
class ChatSummary:
    session_id: str
    title: str
    created_at: int
    updated_at: int
    message_count: int
    status: str
    deprecated_at: int | None


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str
    created_at: int


def _now_ms() -> int:
    return int(time.time() * 1000)


def derive_chat_title(text: str, max_len: int = 42) -> str:
    compact = " ".join(text.split()).strip()
    if not compact:
        return DEFAULT_CHAT_TITLE
    if len(compact) <= max_len:
        return compact
    return f"{compact[:max_len].rstrip()}..."


class ChatHistoryStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chats (
                  session_id TEXT PRIMARY KEY,
                  title TEXT NOT NULL,
                  created_at INTEGER NOT NULL,
                  updated_at INTEGER NOT NULL,
                  status TEXT NOT NULL DEFAULT 'active',
                  deprecated_at INTEGER
                );
                """
            )
            self._ensure_chats_columns(conn)
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_messages (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT NOT NULL,
                  role TEXT NOT NULL,
                  content TEXT NOT NULL,
                  created_at INTEGER NOT NULL,
                  FOREIGN KEY(session_id) REFERENCES chats(session_id) ON DELETE CASCADE
                );
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id_id
                ON chat_messages(session_id, id);
                """
            )

    def _ensure_chats_columns(self, conn: sqlite3.Connection) -> None:
        columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(chats);").fetchall()
        }
        if "status" not in columns:
            conn.execute(
                "ALTER TABLE chats ADD COLUMN status TEXT NOT NULL DEFAULT 'active';"
            )
        if "deprecated_at" not in columns:
            conn.execute("ALTER TABLE chats ADD COLUMN deprecated_at INTEGER;")

    def ensure_chat(self, session_id: str, title: str | None = None) -> ChatSummary:
        now = _now_ms()
        safe_title = (title or DEFAULT_CHAT_TITLE).strip() or DEFAULT_CHAT_TITLE
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO chats(session_id, title, created_at, updated_at, status, deprecated_at)
                VALUES (?, ?, ?, ?, 'active', NULL)
                ON CONFLICT(session_id) DO NOTHING;
                """,
                (session_id, safe_title, now, now),
            )
            row = conn.execute(
                """
                SELECT session_id, title, created_at, updated_at, status, deprecated_at
                FROM chats
                WHERE session_id = ?;
                """,
                (session_id,),
            ).fetchone()
            if row is None:
                raise RuntimeError("Failed to create or load chat.")
            count_row = conn.execute(
                """
                SELECT COUNT(*) AS message_count
                FROM chat_messages
                WHERE session_id = ? AND role IN ('user', 'assistant');
                """,
                (session_id,),
            ).fetchone()
        return ChatSummary(
            session_id=str(row["session_id"]),
            title=str(row["title"]),
            created_at=int(row["created_at"]),
            updated_at=int(row["updated_at"]),
            message_count=int(count_row["message_count"]) if count_row is not None else 0,
            status=str(row["status"]),
            deprecated_at=int(row["deprecated_at"]) if row["deprecated_at"] is not None else None,
        )

    def list_chats(self, *, include_deprecated: bool = False) -> list[ChatSummary]:
        with self._connect() as conn:
            where_clause = "" if include_deprecated else "WHERE c.status = 'active'"
            rows = conn.execute(
                """
                SELECT
                  c.session_id,
                  c.title,
                  c.created_at,
                  c.updated_at,
                  c.status,
                  c.deprecated_at,
                  COALESCE(m.message_count, 0) AS message_count
                FROM chats c
                LEFT JOIN (
                  SELECT session_id, COUNT(*) AS message_count
                  FROM chat_messages
                  WHERE role IN ('user', 'assistant')
                  GROUP BY session_id
                ) m ON m.session_id = c.session_id
                """ + where_clause + """
                ORDER BY c.updated_at DESC, c.created_at DESC;
                """
            ).fetchall()
        return [
            ChatSummary(
                session_id=str(row["session_id"]),
                title=str(row["title"]),
                created_at=int(row["created_at"]),
                updated_at=int(row["updated_at"]),
                message_count=int(row["message_count"]),
                status=str(row["status"]),
                deprecated_at=int(row["deprecated_at"]) if row["deprecated_at"] is not None else None,
            )
            for row in rows
        ]

    def get_chat(self, session_id: str) -> ChatSummary | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                  c.session_id,
                  c.title,
                  c.created_at,
                  c.updated_at,
                  c.status,
                  c.deprecated_at,
                  COALESCE(m.message_count, 0) AS message_count
                FROM chats c
                LEFT JOIN (
                  SELECT session_id, COUNT(*) AS message_count
                  FROM chat_messages
                  WHERE role IN ('user', 'assistant')
                  GROUP BY session_id
                ) m ON m.session_id = c.session_id
                WHERE c.session_id = ?;
                """,
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return ChatSummary(
            session_id=str(row["session_id"]),
            title=str(row["title"]),
            created_at=int(row["created_at"]),
            updated_at=int(row["updated_at"]),
            message_count=int(row["message_count"]),
            status=str(row["status"]),
            deprecated_at=int(row["deprecated_at"]) if row["deprecated_at"] is not None else None,
        )

    def rename_chat(self, session_id: str, title: str) -> ChatSummary:
        safe_title = title.strip() or DEFAULT_CHAT_TITLE
        now = _now_ms()
        with self._connect() as conn:
            updated = conn.execute(
                """
                UPDATE chats
                SET title = ?, updated_at = ?
                WHERE session_id = ?;
                """,
                (safe_title, now, session_id),
            )
            if updated.rowcount == 0:
                raise KeyError(session_id)
            row = conn.execute(
                """
                SELECT session_id, title, created_at, updated_at, status, deprecated_at
                FROM chats
                WHERE session_id = ?;
                """,
                (session_id,),
            ).fetchone()
            count_row = conn.execute(
                """
                SELECT COUNT(*) AS message_count
                FROM chat_messages
                WHERE session_id = ? AND role IN ('user', 'assistant');
                """,
                (session_id,),
            ).fetchone()
        if row is None:
            raise KeyError(session_id)
        return ChatSummary(
            session_id=str(row["session_id"]),
            title=str(row["title"]),
            created_at=int(row["created_at"]),
            updated_at=int(row["updated_at"]),
            message_count=int(count_row["message_count"]) if count_row is not None else 0,
            status=str(row["status"]),
            deprecated_at=int(row["deprecated_at"]) if row["deprecated_at"] is not None else None,
        )

    def delete_chat(self, session_id: str) -> None:
        with self._connect() as conn:
            deleted = conn.execute("DELETE FROM chats WHERE session_id = ?;", (session_id,))
            if deleted.rowcount == 0:
                raise KeyError(session_id)

    def list_messages(self, session_id: str) -> list[ChatMessage]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT role, content, created_at
                FROM chat_messages
                WHERE session_id = ? AND role IN ('user', 'assistant')
                ORDER BY id ASC;
                """,
                (session_id,),
            ).fetchall()
        return [
            ChatMessage(role=str(row["role"]), content=str(row["content"]), created_at=int(row["created_at"]))
            for row in rows
        ]

    def append_message(self, session_id: str, role: str, content: str) -> None:
        if role not in {"user", "assistant", "note"}:
            raise ValueError(f"Unsupported role: {role}")
        now = _now_ms()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO chats(session_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(session_id) DO NOTHING;
                """,
                (session_id, DEFAULT_CHAT_TITLE, now, now),
            )
            conn.execute(
                """
                INSERT INTO chat_messages(session_id, role, content, created_at)
                VALUES (?, ?, ?, ?);
                """,
                (session_id, role, content, now),
            )
            conn.execute(
                "UPDATE chats SET updated_at = ? WHERE session_id = ?;",
                (now, session_id),
            )

    def deprecate_chat(self, session_id: str) -> ChatSummary:
        now = _now_ms()
        with self._connect() as conn:
            updated = conn.execute(
                """
                UPDATE chats
                SET status = 'deprecated', deprecated_at = ?, updated_at = ?
                WHERE session_id = ?;
                """,
                (now, now, session_id),
            )
            if updated.rowcount == 0:
                raise KeyError(session_id)
        chat = self.get_chat(session_id)
        if chat is None:
            raise KeyError(session_id)
        return chat

    def list_notes(self, session_id: str, limit: int = 8) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT content
                FROM chat_messages
                WHERE session_id = ? AND role = 'note'
                ORDER BY id DESC
                LIMIT ?;
                """,
                (session_id, limit),
            ).fetchall()
        # Preserve oldest->newest order for deterministic prompt construction.
        return [str(row["content"]) for row in reversed(rows)]

    def maybe_set_title_from_first_user_message(self, session_id: str, user_message: str) -> None:
        candidate = derive_chat_title(user_message)
        now = _now_ms()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE chats
                SET title = ?, updated_at = ?
                WHERE session_id = ? AND title = ?;
                """,
                (candidate, now, session_id, DEFAULT_CHAT_TITLE),
            )

    def clear_messages(self, session_id: str) -> None:
        now = _now_ms()
        with self._connect() as conn:
            conn.execute("DELETE FROM chat_messages WHERE session_id = ?;", (session_id,))
            conn.execute("UPDATE chats SET updated_at = ? WHERE session_id = ?;", (now, session_id))
