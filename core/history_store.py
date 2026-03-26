from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any


DEFAULT_CHAT_TITLE = "New chat"
_CANONICAL_FEEDBACK_OUTCOMES = {"pass", "fail"}


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
    message_id: str
    parent_message_id: str | None
    role: str
    content: str
    created_at: int


@dataclass(frozen=True)
class OcrRun:
    run_id: str
    session_id: str
    source_name: str | None
    mime_type: str | None
    source_message_id: str | None
    result_message_id: str | None
    status: str
    extracted_text: str
    created_at: int


@dataclass(frozen=True)
class CollaborationState:
    session_id: str
    active_agent_id: str
    active_role: str
    objective: str | None
    updated_at: int
    updated_by: str | None


@dataclass(frozen=True)
class CollaborationHandoff:
    handoff_id: str
    session_id: str
    from_agent_id: str | None
    from_role: str | None
    to_agent_id: str
    to_role: str
    objective: str | None
    reason: str | None
    created_at: int
    created_by: str | None


@dataclass(frozen=True)
class PersonalizationSettings:
    session_id: str
    memory_scope: str
    updated_at: int
    updated_by: str | None


@dataclass(frozen=True)
class MessageFeedback:
    session_id: str
    message_id: str
    outcome: str
    positive_tags: list[str]
    negative_tags: list[str]
    tags: list[str]
    note: str | None
    recommended_action: str | None
    action_taken: str | None
    status: str
    created_at: int
    updated_at: int


@dataclass(frozen=True)
class EvalCheckpoint:
    checkpoint_id: str
    session_id: str
    total_count: int
    pass_count: int
    fail_count: int
    non_binary_count: int
    created_at: int


def _now_ms() -> int:
    return int(time.time() * 1000)


def _normalize_feedback_outcome(outcome: str) -> str:
    normalized = outcome.strip().lower()
    if normalized in _CANONICAL_FEEDBACK_OUTCOMES:
        return normalized
    raise ValueError("feedback outcome must be pass or fail")


def _build_message_id(
    *,
    session_id: str,
    row_id: int,
    role: str,
    created_at: int,
    content: str,
) -> str:
    payload = f"{session_id}:{row_id}:{role}:{created_at}:{content}".encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()[:24]
    return f"msg_{digest}"


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

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        conn = self._connect()
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def _initialize(self) -> None:
        with self._connection() as conn:
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
                  message_id TEXT,
                  parent_message_id TEXT,
                  FOREIGN KEY(session_id) REFERENCES chats(session_id) ON DELETE CASCADE
                );
                """
            )
            self._ensure_chat_messages_columns(conn)
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id_id
                ON chat_messages(session_id, id);
                """
            )
            conn.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_chat_messages_message_id_unique
                ON chat_messages(message_id)
                WHERE message_id IS NOT NULL;
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ocr_runs (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  run_id TEXT UNIQUE NOT NULL,
                  session_id TEXT NOT NULL,
                  source_name TEXT,
                  mime_type TEXT,
                  source_message_id TEXT,
                  result_message_id TEXT,
                  status TEXT NOT NULL,
                  extracted_text TEXT NOT NULL,
                  created_at INTEGER NOT NULL,
                  FOREIGN KEY(session_id) REFERENCES chats(session_id) ON DELETE CASCADE
                );
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_ocr_runs_session_created
                ON ocr_runs(session_id, created_at DESC);
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ingest_dedup (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  dedup_key TEXT UNIQUE NOT NULL,
                  operation TEXT NOT NULL,
                  session_id TEXT NOT NULL,
                  response_json TEXT NOT NULL,
                  created_at INTEGER NOT NULL,
                  FOREIGN KEY(session_id) REFERENCES chats(session_id) ON DELETE CASCADE
                );
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_ingest_dedup_operation_created
                ON ingest_dedup(operation, created_at DESC);
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_collaboration_state (
                  session_id TEXT PRIMARY KEY,
                  active_agent_id TEXT NOT NULL,
                  active_role TEXT NOT NULL,
                  objective TEXT,
                  updated_at INTEGER NOT NULL,
                  updated_by TEXT,
                  FOREIGN KEY(session_id) REFERENCES chats(session_id) ON DELETE CASCADE
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_handoffs (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT NOT NULL,
                  from_agent_id TEXT,
                  from_role TEXT,
                  to_agent_id TEXT NOT NULL,
                  to_role TEXT NOT NULL,
                  objective TEXT,
                  reason TEXT,
                  created_at INTEGER NOT NULL,
                  created_by TEXT,
                  FOREIGN KEY(session_id) REFERENCES chats(session_id) ON DELETE CASCADE
                );
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_chat_handoffs_session_created
                ON chat_handoffs(session_id, created_at DESC, id DESC);
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_personalization (
                  session_id TEXT PRIMARY KEY,
                  memory_scope TEXT NOT NULL,
                  updated_at INTEGER NOT NULL,
                  updated_by TEXT,
                  FOREIGN KEY(session_id) REFERENCES chats(session_id) ON DELETE CASCADE
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS message_feedback (
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
                  updated_at INTEGER NOT NULL,
                  FOREIGN KEY(session_id) REFERENCES chats(session_id) ON DELETE CASCADE,
                  UNIQUE(session_id, message_id)
                );
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_message_feedback_session_updated
                ON message_feedback(session_id, updated_at DESC, id DESC);
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS eval_checkpoints (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  checkpoint_id TEXT UNIQUE NOT NULL,
                  session_id TEXT NOT NULL,
                  total_count INTEGER NOT NULL,
                  pass_count INTEGER NOT NULL,
                  fail_count INTEGER NOT NULL,
                  other_count INTEGER NOT NULL,
                  created_at INTEGER NOT NULL,
                  FOREIGN KEY(session_id) REFERENCES chats(session_id) ON DELETE CASCADE
                );
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_eval_checkpoints_session_created
                ON eval_checkpoints(session_id, created_at ASC, id ASC);
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

    def _ensure_chat_messages_columns(self, conn: sqlite3.Connection) -> None:
        columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(chat_messages);").fetchall()
        }
        if "message_id" not in columns:
            conn.execute("ALTER TABLE chat_messages ADD COLUMN message_id TEXT;")
        if "parent_message_id" not in columns:
            conn.execute("ALTER TABLE chat_messages ADD COLUMN parent_message_id TEXT;")
        self._backfill_message_lineage(conn)

    def _backfill_message_lineage(self, conn: sqlite3.Connection) -> None:
        rows = conn.execute(
            """
            SELECT id, session_id, role, content, created_at, message_id, parent_message_id
            FROM chat_messages
            ORDER BY id ASC;
            """
        ).fetchall()

        latest_visible_message_by_session: dict[str, str] = {}
        for row in rows:
            row_id = int(row["id"])
            session_id = str(row["session_id"])
            role = str(row["role"])
            content = str(row["content"])
            created_at = int(row["created_at"])

            current_message_id = (
                str(row["message_id"]) if row["message_id"] is not None else None
            )
            current_parent_id = (
                str(row["parent_message_id"]) if row["parent_message_id"] is not None else None
            )

            next_message_id = current_message_id or _build_message_id(
                session_id=session_id,
                row_id=row_id,
                role=role,
                created_at=created_at,
                content=content,
            )
            next_parent_id = current_parent_id
            if role in {"user", "assistant"} and next_parent_id is None:
                next_parent_id = latest_visible_message_by_session.get(session_id)

            if current_message_id != next_message_id or current_parent_id != next_parent_id:
                conn.execute(
                    """
                    UPDATE chat_messages
                    SET message_id = ?, parent_message_id = ?
                    WHERE id = ?;
                    """,
                    (next_message_id, next_parent_id, row_id),
                )

            if role in {"user", "assistant"}:
                latest_visible_message_by_session[session_id] = next_message_id

    def ensure_chat(self, session_id: str, title: str | None = None) -> ChatSummary:
        now = _now_ms()
        safe_title = (title or DEFAULT_CHAT_TITLE).strip() or DEFAULT_CHAT_TITLE
        with self._connection() as conn:
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
        with self._connection() as conn:
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
        with self._connection() as conn:
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
        with self._connection() as conn:
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
        with self._connection() as conn:
            deleted = conn.execute("DELETE FROM chats WHERE session_id = ?;", (session_id,))
            if deleted.rowcount == 0:
                raise KeyError(session_id)

    def list_messages(self, session_id: str) -> list[ChatMessage]:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT message_id, parent_message_id, role, content, created_at
                FROM chat_messages
                WHERE session_id = ? AND role IN ('user', 'assistant')
                ORDER BY id ASC;
                """,
                (session_id,),
            ).fetchall()
        return [
            ChatMessage(
                message_id=str(row["message_id"]),
                parent_message_id=(
                    str(row["parent_message_id"])
                    if row["parent_message_id"] is not None
                    else None
                ),
                role=str(row["role"]),
                content=str(row["content"]),
                created_at=int(row["created_at"]),
            )
            for row in rows
        ]

    def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        *,
        parent_message_id_override: str | None = None,
    ) -> ChatMessage:
        if role not in {"user", "assistant", "note"}:
            raise ValueError(f"Unsupported role: {role}")
        now = _now_ms()
        with self._connection() as conn:
            parent_message_id: str | None = None
            if role in {"user", "assistant"}:
                if parent_message_id_override is not None:
                    parent_message_id = parent_message_id_override
                else:
                    parent_row = conn.execute(
                        """
                        SELECT message_id
                        FROM chat_messages
                        WHERE session_id = ? AND role IN ('user', 'assistant')
                        ORDER BY id DESC
                        LIMIT 1;
                        """,
                        (session_id,),
                    ).fetchone()
                    if parent_row is not None and parent_row["message_id"] is not None:
                        parent_message_id = str(parent_row["message_id"])
            conn.execute(
                """
                INSERT INTO chats(session_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(session_id) DO NOTHING;
                """,
                (session_id, DEFAULT_CHAT_TITLE, now, now),
            )
            insert_result = conn.execute(
                """
                INSERT INTO chat_messages(
                  session_id,
                  role,
                  content,
                  created_at,
                  message_id,
                  parent_message_id
                )
                VALUES (?, ?, ?, ?, NULL, ?);
                """,
                (session_id, role, content, now, parent_message_id),
            )
            if insert_result.lastrowid is None:
                raise RuntimeError("Failed to persist chat message row id.")
            row_id = int(insert_result.lastrowid)
            message_id = _build_message_id(
                session_id=session_id,
                row_id=row_id,
                role=role,
                created_at=now,
                content=content,
            )
            conn.execute(
                "UPDATE chat_messages SET message_id = ? WHERE id = ?;",
                (message_id, row_id),
            )
            conn.execute(
                "UPDATE chats SET updated_at = ? WHERE session_id = ?;",
                (now, session_id),
            )
        return ChatMessage(
            message_id=message_id,
            parent_message_id=parent_message_id,
            role=role,
            content=content,
            created_at=now,
        )

    def message_exists(self, session_id: str, message_id: str) -> bool:
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT 1
                FROM chat_messages
                WHERE session_id = ? AND message_id = ?
                LIMIT 1;
                """,
                (session_id, message_id),
            ).fetchone()
        return row is not None

    def get_message_role(self, session_id: str, message_id: str) -> str | None:
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT role
                FROM chat_messages
                WHERE session_id = ? AND message_id = ?
                LIMIT 1;
                """,
                (session_id, message_id),
            ).fetchone()
        if row is None:
            return None
        return str(row["role"])

    def upsert_message_feedback(
        self,
        *,
        session_id: str,
        message_id: str,
        outcome: str,
        positive_tags: list[str] | None = None,
        negative_tags: list[str] | None = None,
        note: str | None,
        recommended_action: str | None,
        action_taken: str | None,
        status: str,
    ) -> MessageFeedback:
        normalized_outcome = _normalize_feedback_outcome(outcome)
        normalized_positive_tags = [
            tag.strip() for tag in (positive_tags or []) if tag.strip()
        ]
        normalized_negative_tags = [
            tag.strip() for tag in (negative_tags or []) if tag.strip()
        ]
        normalized_tags = list(dict.fromkeys(normalized_positive_tags + normalized_negative_tags))
        normalized_note = note.strip() if note is not None and note.strip() else None
        normalized_recommended_action = (
            recommended_action.strip() if recommended_action is not None and recommended_action.strip() else None
        )
        normalized_action_taken = (
            action_taken.strip() if action_taken is not None and action_taken.strip() else None
        )
        normalized_status = status.strip().upper() if status.strip() else "LOGGED"
        now = _now_ms()
        serialized_tags = json.dumps(
            {
                "positive": normalized_positive_tags,
                "negative": normalized_negative_tags,
                "all": normalized_tags,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO message_feedback(
                  session_id,
                  message_id,
                  outcome,
                  tags_json,
                  note,
                  recommended_action,
                  action_taken,
                  status,
                  created_at,
                  updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id, message_id) DO UPDATE SET
                  outcome = excluded.outcome,
                  tags_json = excluded.tags_json,
                  note = excluded.note,
                  recommended_action = excluded.recommended_action,
                  action_taken = excluded.action_taken,
                  status = excluded.status,
                  updated_at = excluded.updated_at;
                """,
                (
                    session_id,
                    message_id,
                    normalized_outcome,
                    serialized_tags,
                    normalized_note,
                    normalized_recommended_action,
                    normalized_action_taken,
                    normalized_status,
                    now,
                    now,
                ),
            )
            row = conn.execute(
                """
                SELECT
                  session_id,
                  message_id,
                  outcome,
                  tags_json,
                  note,
                  recommended_action,
                  action_taken,
                  status,
                  created_at,
                  updated_at
                FROM message_feedback
                WHERE session_id = ? AND message_id = ?
                LIMIT 1;
                """,
                (session_id, message_id),
            ).fetchone()
        if row is None:
            raise RuntimeError("Failed to upsert message feedback.")
        return _message_feedback_from_row(row)

    def list_message_feedback(self, session_id: str) -> list[MessageFeedback]:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT
                  session_id,
                  message_id,
                  outcome,
                  tags_json,
                  note,
                  recommended_action,
                  action_taken,
                  status,
                  created_at,
                  updated_at
                FROM message_feedback
                WHERE session_id = ?
                ORDER BY updated_at DESC, id DESC;
                """,
                (session_id,),
            ).fetchall()
        return [_message_feedback_from_row(row) for row in rows]

    def record_eval_checkpoint(
        self,
        *,
        checkpoint_id: str,
        session_id: str,
        total_count: int,
        pass_count: int,
        fail_count: int,
        non_binary_count: int,
    ) -> EvalCheckpoint:
        now = _now_ms()
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO eval_checkpoints(
                  checkpoint_id,
                  session_id,
                  total_count,
                  pass_count,
                  fail_count,
                  other_count,
                  created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    checkpoint_id,
                    session_id,
                    int(total_count),
                    int(pass_count),
                    int(fail_count),
                    int(non_binary_count),
                    now,
                ),
            )
            conn.execute(
                "UPDATE chats SET updated_at = ? WHERE session_id = ?;",
                (now, session_id),
            )
        return EvalCheckpoint(
            checkpoint_id=checkpoint_id,
            session_id=session_id,
            total_count=int(total_count),
            pass_count=int(pass_count),
            fail_count=int(fail_count),
            non_binary_count=int(non_binary_count),
            created_at=now,
        )

    def list_eval_checkpoints(self, session_id: str, limit: int = 200) -> list[EvalCheckpoint]:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT
                  checkpoint_id,
                  session_id,
                  total_count,
                  pass_count,
                  fail_count,
                  other_count,
                  created_at
                FROM eval_checkpoints
                WHERE session_id = ?
                ORDER BY created_at ASC, id ASC
                LIMIT ?;
                """,
                (session_id, limit),
            ).fetchall()
        return [
            EvalCheckpoint(
                checkpoint_id=str(row["checkpoint_id"]),
                session_id=str(row["session_id"]),
                total_count=int(row["total_count"]),
                pass_count=int(row["pass_count"]),
                fail_count=int(row["fail_count"]),
                non_binary_count=int(row["other_count"]),
                created_at=int(row["created_at"]),
            )
            for row in rows
        ]

    def record_ocr_run(
        self,
        *,
        run_id: str,
        session_id: str,
        source_name: str | None,
        mime_type: str | None,
        source_message_id: str | None,
        result_message_id: str | None,
        status: str,
        extracted_text: str,
    ) -> OcrRun:
        now = _now_ms()
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO ocr_runs(
                  run_id,
                  session_id,
                  source_name,
                  mime_type,
                  source_message_id,
                  result_message_id,
                  status,
                  extracted_text,
                  created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    run_id,
                    session_id,
                    source_name,
                    mime_type,
                    source_message_id,
                    result_message_id,
                    status,
                    extracted_text,
                    now,
                ),
            )
            conn.execute(
                "UPDATE chats SET updated_at = ? WHERE session_id = ?;",
                (now, session_id),
            )
        return OcrRun(
            run_id=run_id,
            session_id=session_id,
            source_name=source_name,
            mime_type=mime_type,
            source_message_id=source_message_id,
            result_message_id=result_message_id,
            status=status,
            extracted_text=extracted_text,
            created_at=now,
        )

    def list_ocr_runs(self, session_id: str, limit: int = 100) -> list[OcrRun]:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT
                  run_id,
                  session_id,
                  source_name,
                  mime_type,
                  source_message_id,
                  result_message_id,
                  status,
                  extracted_text,
                  created_at
                FROM ocr_runs
                WHERE session_id = ?
                ORDER BY created_at ASC, id ASC
                LIMIT ?;
                """,
                (session_id, limit),
            ).fetchall()
        return [
            OcrRun(
                run_id=str(row["run_id"]),
                session_id=str(row["session_id"]),
                source_name=str(row["source_name"]) if row["source_name"] is not None else None,
                mime_type=str(row["mime_type"]) if row["mime_type"] is not None else None,
                source_message_id=(
                    str(row["source_message_id"]) if row["source_message_id"] is not None else None
                ),
                result_message_id=(
                    str(row["result_message_id"]) if row["result_message_id"] is not None else None
                ),
                status=str(row["status"]),
                extracted_text=str(row["extracted_text"]),
                created_at=int(row["created_at"]),
            )
            for row in rows
        ]

    def get_ingest_dedup_response(
        self,
        *,
        dedup_key: str,
        operation: str,
    ) -> dict[str, Any] | None:
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT response_json
                FROM ingest_dedup
                WHERE dedup_key = ? AND operation = ?
                LIMIT 1;
                """,
                (dedup_key, operation),
            ).fetchone()
        if row is None:
            return None
        try:
            payload = json.loads(str(row["response_json"]))
        except (TypeError, ValueError):
            return None
        return payload if isinstance(payload, dict) else None

    def record_ingest_dedup_response(
        self,
        *,
        dedup_key: str,
        operation: str,
        session_id: str,
        response_payload: dict[str, Any],
    ) -> None:
        now = _now_ms()
        serialized = json.dumps(response_payload, ensure_ascii=False, separators=(",", ":"))
        with self._connection() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO ingest_dedup(
                  dedup_key,
                  operation,
                  session_id,
                  response_json,
                  created_at
                )
                VALUES (?, ?, ?, ?, ?);
                """,
                (dedup_key, operation, session_id, serialized, now),
            )

    def deprecate_chat(self, session_id: str) -> ChatSummary:
        now = _now_ms()
        with self._connection() as conn:
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
        with self._connection() as conn:
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
        with self._connection() as conn:
            conn.execute(
                """
                UPDATE chats
                SET title = ?, updated_at = ?
                WHERE session_id = ? AND title = ?;
                """,
                (candidate, now, session_id, DEFAULT_CHAT_TITLE),
            )

    def get_collaboration_state(self, session_id: str) -> CollaborationState | None:
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT
                  session_id,
                  active_agent_id,
                  active_role,
                  objective,
                  updated_at,
                  updated_by
                FROM chat_collaboration_state
                WHERE session_id = ?;
                """,
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return CollaborationState(
            session_id=str(row["session_id"]),
            active_agent_id=str(row["active_agent_id"]),
            active_role=str(row["active_role"]),
            objective=str(row["objective"]) if row["objective"] is not None else None,
            updated_at=int(row["updated_at"]),
            updated_by=str(row["updated_by"]) if row["updated_by"] is not None else None,
        )

    def list_handoffs(self, session_id: str, limit: int = 20) -> list[CollaborationHandoff]:
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT
                  id,
                  session_id,
                  from_agent_id,
                  from_role,
                  to_agent_id,
                  to_role,
                  objective,
                  reason,
                  created_at,
                  created_by
                FROM chat_handoffs
                WHERE session_id = ?
                ORDER BY created_at DESC, id DESC
                LIMIT ?;
                """,
                (session_id, limit),
            ).fetchall()
        # Return oldest->newest for deterministic timeline rendering.
        ordered = list(reversed(rows))
        return [
            CollaborationHandoff(
                handoff_id=f"handoff-{int(row['id'])}",
                session_id=str(row["session_id"]),
                from_agent_id=str(row["from_agent_id"]) if row["from_agent_id"] is not None else None,
                from_role=str(row["from_role"]) if row["from_role"] is not None else None,
                to_agent_id=str(row["to_agent_id"]),
                to_role=str(row["to_role"]),
                objective=str(row["objective"]) if row["objective"] is not None else None,
                reason=str(row["reason"]) if row["reason"] is not None else None,
                created_at=int(row["created_at"]),
                created_by=str(row["created_by"]) if row["created_by"] is not None else None,
            )
            for row in ordered
        ]

    def handoff_collaboration(
        self,
        *,
        session_id: str,
        to_agent_id: str,
        to_role: str,
        objective: str | None = None,
        reason: str | None = None,
        created_by: str | None = None,
    ) -> tuple[CollaborationState, CollaborationHandoff]:
        safe_agent_id = to_agent_id.strip()
        safe_role = to_role.strip()
        if not safe_agent_id:
            raise ValueError("to_agent_id cannot be blank.")
        if not safe_role:
            raise ValueError("to_role cannot be blank.")
        safe_objective = objective.strip() if objective and objective.strip() else None
        safe_reason = reason.strip() if reason and reason.strip() else None
        safe_created_by = created_by.strip() if created_by and created_by.strip() else None

        now = _now_ms()
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO chats(session_id, title, created_at, updated_at, status, deprecated_at)
                VALUES (?, ?, ?, ?, 'active', NULL)
                ON CONFLICT(session_id) DO NOTHING;
                """,
                (session_id, DEFAULT_CHAT_TITLE, now, now),
            )
            current_row = conn.execute(
                """
                SELECT active_agent_id, active_role
                FROM chat_collaboration_state
                WHERE session_id = ?;
                """,
                (session_id,),
            ).fetchone()
            from_agent_id = (
                str(current_row["active_agent_id"]) if current_row is not None else None
            )
            from_role = str(current_row["active_role"]) if current_row is not None else None
            conn.execute(
                """
                INSERT INTO chat_collaboration_state(
                  session_id,
                  active_agent_id,
                  active_role,
                  objective,
                  updated_at,
                  updated_by
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                  active_agent_id = excluded.active_agent_id,
                  active_role = excluded.active_role,
                  objective = excluded.objective,
                  updated_at = excluded.updated_at,
                  updated_by = excluded.updated_by;
                """,
                (session_id, safe_agent_id, safe_role, safe_objective, now, safe_created_by),
            )
            inserted = conn.execute(
                """
                INSERT INTO chat_handoffs(
                  session_id,
                  from_agent_id,
                  from_role,
                  to_agent_id,
                  to_role,
                  objective,
                  reason,
                  created_at,
                  created_by
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    session_id,
                    from_agent_id,
                    from_role,
                    safe_agent_id,
                    safe_role,
                    safe_objective,
                    safe_reason,
                    now,
                    safe_created_by,
                ),
            )
            conn.execute(
                "UPDATE chats SET updated_at = ? WHERE session_id = ?;",
                (now, session_id),
            )

        handoff_row_id = int(inserted.lastrowid) if inserted.lastrowid is not None else 0
        state = CollaborationState(
            session_id=session_id,
            active_agent_id=safe_agent_id,
            active_role=safe_role,
            objective=safe_objective,
            updated_at=now,
            updated_by=safe_created_by,
        )
        handoff = CollaborationHandoff(
            handoff_id=f"handoff-{handoff_row_id}",
            session_id=session_id,
            from_agent_id=from_agent_id,
            from_role=from_role,
            to_agent_id=safe_agent_id,
            to_role=safe_role,
            objective=safe_objective,
            reason=safe_reason,
            created_at=now,
            created_by=safe_created_by,
        )
        return state, handoff

    def get_personalization(self, session_id: str) -> PersonalizationSettings | None:
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT session_id, memory_scope, updated_at, updated_by
                FROM chat_personalization
                WHERE session_id = ?;
                """,
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return PersonalizationSettings(
            session_id=str(row["session_id"]),
            memory_scope=str(row["memory_scope"]),
            updated_at=int(row["updated_at"]),
            updated_by=str(row["updated_by"]) if row["updated_by"] is not None else None,
        )

    def set_personalization(
        self,
        *,
        session_id: str,
        memory_scope: str,
        updated_by: str | None = None,
    ) -> PersonalizationSettings:
        safe_scope = memory_scope.strip().lower()
        if safe_scope not in {"session", "global"}:
            raise ValueError("memory_scope must be 'session' or 'global'.")
        now = _now_ms()
        safe_updated_by = updated_by.strip() if updated_by and updated_by.strip() else None
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO chats(session_id, title, created_at, updated_at, status, deprecated_at)
                VALUES (?, ?, ?, ?, 'active', NULL)
                ON CONFLICT(session_id) DO NOTHING;
                """,
                (session_id, DEFAULT_CHAT_TITLE, now, now),
            )
            conn.execute(
                """
                INSERT INTO chat_personalization(session_id, memory_scope, updated_at, updated_by)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                  memory_scope = excluded.memory_scope,
                  updated_at = excluded.updated_at,
                  updated_by = excluded.updated_by;
                """,
                (session_id, safe_scope, now, safe_updated_by),
            )
            conn.execute(
                "UPDATE chats SET updated_at = ? WHERE session_id = ?;",
                (now, session_id),
            )
        return PersonalizationSettings(
            session_id=session_id,
            memory_scope=safe_scope,
            updated_at=now,
            updated_by=safe_updated_by,
        )

    def clear_messages(self, session_id: str) -> None:
        now = _now_ms()
        with self._connection() as conn:
            conn.execute("DELETE FROM chat_messages WHERE session_id = ?;", (session_id,))
            conn.execute("UPDATE chats SET updated_at = ? WHERE session_id = ?;", (now, session_id))


def _message_feedback_from_row(row: sqlite3.Row) -> MessageFeedback:
    normalized_outcome = _normalize_feedback_outcome(str(row["outcome"]))
    parsed_positive_tags: list[str] = []
    parsed_negative_tags: list[str] = []
    parsed_tags: list[str] = []
    raw_tags = row["tags_json"]
    if raw_tags is not None:
        try:
            decoded = json.loads(str(raw_tags))
        except (TypeError, ValueError):
            decoded = []
        if isinstance(decoded, dict):
            raw_positive = decoded.get("positive")
            if isinstance(raw_positive, list):
                parsed_positive_tags = [str(item).strip() for item in raw_positive if str(item).strip()]
            raw_negative = decoded.get("negative")
            if isinstance(raw_negative, list):
                parsed_negative_tags = [str(item).strip() for item in raw_negative if str(item).strip()]
            raw_all = decoded.get("all")
            if isinstance(raw_all, list):
                parsed_tags = [str(item).strip() for item in raw_all if str(item).strip()]
    parsed_positive_tags = list(dict.fromkeys(parsed_positive_tags))
    parsed_negative_tags = list(dict.fromkeys(parsed_negative_tags))
    if not parsed_tags:
        parsed_tags = list(dict.fromkeys(parsed_positive_tags + parsed_negative_tags))
    return MessageFeedback(
        session_id=str(row["session_id"]),
        message_id=str(row["message_id"]),
        outcome=normalized_outcome,
        positive_tags=parsed_positive_tags,
        negative_tags=parsed_negative_tags,
        tags=parsed_tags,
        note=str(row["note"]) if row["note"] is not None else None,
        recommended_action=(
            str(row["recommended_action"]) if row["recommended_action"] is not None else None
        ),
        action_taken=str(row["action_taken"]) if row["action_taken"] is not None else None,
        status=str(row["status"]),
        created_at=int(row["created_at"]),
        updated_at=int(row["updated_at"]),
    )
