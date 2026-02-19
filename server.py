import os
from typing import cast

from agents import Agent, ModelSettings, RunConfig, Runner
from agents.memory import Session, SessionSettings, SQLiteSession
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import APIConnectionError, APIStatusError, AuthenticationError, RateLimitError

from prompts import ACTIVE_PROMPT, ACTIVE_PROMPT_VERSION


load_dotenv(dotenv_path=".env")
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set. Add it to .env or export it before starting server.py.")

SESSION_DB_PATH = os.getenv("POLINKO_MEMORY_DB_PATH", ".polinko_memory.db")
DEFAULT_SESSION_ID = "default"

app = FastAPI(title="Polinko Agent API", version="0.1.0")

agent = Agent(
    name="Polinko Repositining System",
    instructions=ACTIVE_PROMPT,
    model="gpt-5-chat-latest",
)
run_config = RunConfig(
    model_settings=ModelSettings(
        temperature=1.0,
        top_p=1.0,
        store=True,
    )
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message.")
    session_id: str = Field(default=DEFAULT_SESSION_ID, min_length=1, description="Conversation session ID.")


class ChatResponse(BaseModel):
    output: str
    session_id: str
    prompt_version: str


class ResetRequest(BaseModel):
    session_id: str = Field(default=DEFAULT_SESSION_ID, min_length=1)


def get_session(session_id: str) -> Session:
    return cast(
        Session,
        SQLiteSession(
            session_id=session_id,
            db_path=SESSION_DB_PATH,
            session_settings=SessionSettings(limit=80),
        ),
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "prompt_version": ACTIVE_PROMPT_VERSION,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    session = get_session(req.session_id)
    try:
        result = await Runner.run(
            agent,
            req.message,
            run_config=run_config,
            session=session,
        )
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail="Authentication failed. Check OPENAI_API_KEY.") from exc
    except RateLimitError as exc:
        raise HTTPException(status_code=429, detail="Rate limit reached. Try again shortly.") from exc
    except APIConnectionError as exc:
        raise HTTPException(status_code=503, detail="Connection error reaching OpenAI API.") from exc
    except APIStatusError as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI API error ({exc.status_code}).") from exc

    return ChatResponse(
        output=str(result.final_output),
        session_id=req.session_id,
        prompt_version=ACTIVE_PROMPT_VERSION,
    )


@app.post("/session/reset")
async def reset_session(req: ResetRequest) -> dict[str, str]:
    session = get_session(req.session_id)
    await session.clear_session()
    return {"status": "ok", "session_id": req.session_id}
