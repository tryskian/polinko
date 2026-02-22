from __future__ import annotations

import json
import math
import sqlite3
import time
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any


def _now_ms() -> int:
    return int(time.time() * 1000)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for lhs, rhs in zip(a, b):
        dot += lhs * rhs
        norm_a += lhs * lhs
        norm_b += rhs * rhs
    if norm_a <= 0.0 or norm_b <= 0.0:
        return 0.0
    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))


@dataclass(frozen=True)
class VectorMatch:
    vector_id: str
    session_id: str
    role: str
    message_id: str | None
    source_type: str
    source_ref: str | None
    metadata: dict[str, Any]
    content: str
    created_at: int
    similarity: float


class VectorStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
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
                CREATE TABLE IF NOT EXISTS message_vectors (
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
            self._ensure_columns(conn)
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_message_vectors_active_created
                ON message_vectors(active, created_at DESC);
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_message_vectors_session
                ON message_vectors(session_id);
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_message_vectors_source_type
                ON message_vectors(source_type);
                """
            )
            conn.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_message_vectors_message_id_unique
                ON message_vectors(message_id)
                WHERE message_id IS NOT NULL;
                """
            )

    def _ensure_columns(self, conn: sqlite3.Connection) -> None:
        columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(message_vectors);").fetchall()
        }
        if "source_type" not in columns:
            conn.execute(
                "ALTER TABLE message_vectors ADD COLUMN source_type TEXT NOT NULL DEFAULT 'chat';"
            )
        if "source_ref" not in columns:
            conn.execute("ALTER TABLE message_vectors ADD COLUMN source_ref TEXT;")
        if "metadata_json" not in columns:
            conn.execute("ALTER TABLE message_vectors ADD COLUMN metadata_json TEXT;")

    def upsert_message_vector(
        self,
        *,
        session_id: str,
        role: str,
        content: str,
        embedding: list[float],
        message_id: str | None = None,
        source_type: str = "chat",
        source_ref: str | None = None,
        metadata: dict[str, Any] | None = None,
        created_at: int | None = None,
    ) -> str:
        if role not in {"user", "assistant"}:
            raise ValueError(f"Unsupported role for vector storage: {role}")
        ts = created_at if created_at is not None else _now_ms()
        vector_id = f"vec-{uuid.uuid4().hex[:12]}"
        payload = json.dumps(embedding, separators=(",", ":"))
        metadata_payload = json.dumps(metadata or {}, separators=(",", ":"))
        with self._connection() as conn:
            if message_id:
                existing = conn.execute(
                    """
                    SELECT vector_id FROM message_vectors WHERE message_id = ? LIMIT 1;
                    """,
                    (message_id,),
                ).fetchone()
                if existing is not None:
                    existing_id = str(existing["vector_id"])
                    conn.execute(
                        """
                        UPDATE message_vectors
                        SET
                          session_id = ?,
                          role = ?,
                          source_type = ?,
                          source_ref = ?,
                          metadata_json = ?,
                          content = ?,
                          embedding_json = ?,
                          created_at = ?,
                          active = 1
                        WHERE vector_id = ?;
                        """,
                        (
                            session_id,
                            role,
                            source_type,
                            source_ref,
                            metadata_payload,
                            content,
                            payload,
                            ts,
                            existing_id,
                        ),
                    )
                    return existing_id
            conn.execute(
                """
                INSERT INTO message_vectors(
                  vector_id,
                  session_id,
                  role,
                  message_id,
                  source_type,
                  source_ref,
                  metadata_json,
                  content,
                  embedding_json,
                  created_at,
                  active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1);
                """,
                (
                    vector_id,
                    session_id,
                    role,
                    message_id,
                    source_type,
                    source_ref,
                    metadata_payload,
                    content,
                    payload,
                    ts,
                ),
            )
        return vector_id

    def search(
        self,
        *,
        query_embedding: list[float],
        limit: int,
        min_similarity: float,
        roles: tuple[str, ...] = ("assistant",),
        exclude_session_id: str | None = None,
        source_types: tuple[str, ...] | None = None,
    ) -> list[VectorMatch]:
        if limit <= 0:
            return []
        placeholders = ",".join("?" for _ in roles)
        params: list[object] = [*roles]
        clause = "AND session_id != ?" if exclude_session_id else ""
        if exclude_session_id:
            params.append(exclude_session_id)
        source_clause = ""
        if source_types:
            source_placeholders = ",".join("?" for _ in source_types)
            source_clause = f"AND source_type IN ({source_placeholders})"
            params.extend(source_types)

        with self._connection() as conn:
            rows = conn.execute(
                f"""
                SELECT
                  vector_id,
                  session_id,
                  role,
                  message_id,
                  source_type,
                  source_ref,
                  metadata_json,
                  content,
                  embedding_json,
                  created_at
                FROM message_vectors
                WHERE active = 1
                  AND role IN ({placeholders})
                  {clause}
                  {source_clause}
                ORDER BY created_at DESC
                LIMIT 500;
                """,
                tuple(params),
            ).fetchall()

        scored: list[VectorMatch] = []
        for row in rows:
            try:
                embedding = json.loads(str(row["embedding_json"]))
            except json.JSONDecodeError:
                continue
            if not isinstance(embedding, list):
                continue
            vector = [float(x) for x in embedding]
            similarity = _cosine_similarity(query_embedding, vector)
            if similarity < min_similarity:
                continue
            metadata: dict[str, Any] = {}
            raw_metadata = row["metadata_json"]
            if raw_metadata:
                try:
                    loaded = json.loads(str(raw_metadata))
                    if isinstance(loaded, dict):
                        metadata = loaded
                except json.JSONDecodeError:
                    metadata = {}
            scored.append(
                VectorMatch(
                    vector_id=str(row["vector_id"]),
                    session_id=str(row["session_id"]),
                    role=str(row["role"]),
                    message_id=str(row["message_id"]) if row["message_id"] is not None else None,
                    source_type=str(row["source_type"]) if row["source_type"] is not None else "chat",
                    source_ref=str(row["source_ref"]) if row["source_ref"] is not None else None,
                    metadata=metadata,
                    content=str(row["content"]),
                    created_at=int(row["created_at"]),
                    similarity=similarity,
                )
            )

        scored.sort(key=lambda item: item.similarity, reverse=True)
        return scored[:limit]

    def deactivate_session(self, session_id: str) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                UPDATE message_vectors
                SET active = 0
                WHERE session_id = ?;
                """,
                (session_id,),
            )

    def delete_session(self, session_id: str) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                DELETE FROM message_vectors
                WHERE session_id = ?;
                """,
                (session_id,),
            )

    def active_count(self) -> int:
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT COUNT(*) AS c
                FROM message_vectors
                WHERE active = 1;
                """
            ).fetchone()
        return int(row["c"]) if row is not None else 0
