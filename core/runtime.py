from typing import cast

from agents import Agent, ModelSettings, RunConfig
from agents.memory import Session, SessionSettings, SQLiteSession

from core.prompts import ACTIVE_PROMPT


AGENT_NAME = "Polinko Repositining System"
MODEL_NAME = "gpt-5-chat-latest"


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
        SQLiteSession(
            session_id=session_id,
            db_path=db_path,
            session_settings=SessionSettings(limit=limit),
        ),
    )
