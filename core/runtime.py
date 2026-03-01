import sqlite3
import threading
from typing import cast

from agents import Agent, ModelSettings, RunConfig
from agents.memory import Session, SessionSettings, SQLiteSession

from core.prompts import ACTIVE_PROMPT


AGENT_NAME = "Polinko Repositining System"
MODEL_NAME = "gpt-5-chat-latest"


class ManagedSQLiteSession(SQLiteSession):
    """SQLiteSession wrapper that closes all thread-local connections on close()."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._tracked_connections: set[sqlite3.Connection] = set()
        self._tracked_connections_lock = threading.Lock()

    def _get_connection(self) -> sqlite3.Connection:
        conn = super()._get_connection()
        with self._tracked_connections_lock:
            self._tracked_connections.add(conn)
        return conn

    def close(self) -> None:
        with self._tracked_connections_lock:
            tracked = list(self._tracked_connections)
            self._tracked_connections.clear()

        for conn in tracked:
            try:
                conn.close()
            except Exception:
                # Best-effort close; ignore already-closed handles.
                pass

        try:
            super().close()
        except Exception:
            # Upstream close() only targets current-thread locals; ignore failures here.
            pass


def create_agent() -> Agent:
    return Agent(
        name=AGENT_NAME,
        instructions=ACTIVE_PROMPT,
        model=MODEL_NAME,
    )


def create_run_config(*, store: bool) -> RunConfig:
    return RunConfig(
        model_settings=ModelSettings(
            temperature=1.0,
            top_p=1.0,
            store=store,
        )
    )


def create_session(*, session_id: str, db_path: str, limit: int = 80) -> Session:
    return cast(
        Session,
        ManagedSQLiteSession(
            session_id=session_id,
            db_path=db_path,
            session_settings=SessionSettings(limit=limit),
        ),
    )
