import os
import json
import logging
import time
import uuid
import threading
from collections import defaultdict, deque
from typing import cast

from agents import Agent, ModelSettings, RunConfig, Runner
from agents.memory import Session, SessionSettings, SQLiteSession
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from openai import APIConnectionError, APIStatusError, AuthenticationError, RateLimitError

from prompts import ACTIVE_PROMPT, ACTIVE_PROMPT_VERSION


load_dotenv(dotenv_path=".env")
SESSION_DB_PATH = os.getenv("POLINKO_MEMORY_DB_PATH", ".polinko_memory.db")
DEFAULT_SESSION_ID = "default"
LOG_LEVEL = os.getenv("POLINKO_LOG_LEVEL", "INFO").upper()
SERVER_API_KEY = os.getenv("POLINKO_SERVER_API_KEY")
RATE_LIMIT_PER_MINUTE = int(os.getenv("POLINKO_RATE_LIMIT_PER_MINUTE", "30"))

logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO), format="%(message)s")
logger = logging.getLogger("polinko.api")
rate_lock = threading.Lock()
rate_buckets: dict[str, deque[float]] = defaultdict(deque)

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


def _looks_like_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    placeholders = {
        "your-key",
        "your_api_key",
        "replace-me",
        "changeme",
        "dummy",
        "placeholder",
    }
    return normalized in placeholders


def validate_startup_config() -> None:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Add it to .env or export it before starting server.py.")
    if not openai_api_key.startswith("sk-"):
        raise RuntimeError("OPENAI_API_KEY appears invalid (expected it to start with 'sk-').")
    if len(openai_api_key) < 20:
        raise RuntimeError("OPENAI_API_KEY appears too short; check your .env value.")
    if _looks_like_placeholder(openai_api_key):
        raise RuntimeError("OPENAI_API_KEY is a placeholder value; set a real key.")

    if SERVER_API_KEY:
        if len(SERVER_API_KEY) < 12:
            raise RuntimeError("POLINKO_SERVER_API_KEY is too short; use at least 12 characters.")
        if _looks_like_placeholder(SERVER_API_KEY):
            raise RuntimeError("POLINKO_SERVER_API_KEY is a placeholder value; set a real key.")


def log_event(event: str, **fields: object) -> None:
    payload = {"event": event, **fields}
    logger.info(json.dumps(payload, default=str))


def enforce_api_key(request: Request) -> None:
    if not SERVER_API_KEY:
        return

    presented = request.headers.get("x-api-key")
    if presented != SERVER_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key.")


def _client_identifier(request: Request, session_id: str) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    client_ip = forwarded_for or (request.client.host if request.client else "unknown")
    return f"{client_ip}:{session_id}"


def enforce_rate_limit(identifier: str) -> None:
    if RATE_LIMIT_PER_MINUTE <= 0:
        return

    now = time.time()
    cutoff = now - 60.0
    with rate_lock:
        bucket = rate_buckets[identifier]
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()
        if len(bucket) >= RATE_LIMIT_PER_MINUTE:
            retry_after = max(1, int(60 - (now - bucket[0])))
            raise HTTPException(
                status_code=429,
                detail=(
                    f"Rate limit exceeded ({RATE_LIMIT_PER_MINUTE}/min). "
                    f"Retry in ~{retry_after}s."
                ),
                headers={"Retry-After": str(retry_after)},
            )
        bucket.append(now)


def get_session(session_id: str) -> Session:
    return cast(
        Session,
        SQLiteSession(
            session_id=session_id,
            db_path=SESSION_DB_PATH,
            session_settings=SessionSettings(limit=80),
        ),
    )


validate_startup_config()


@app.middleware("http")
async def request_logging(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    request.state.request_id = request_id
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        log_event(
            "http_error",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            duration_ms=duration_ms,
            error_type=type(exc).__name__,
        )
        raise

    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["x-request-id"] = request_id
    log_event(
        "http_request",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
    )
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "prompt_version": ACTIVE_PROMPT_VERSION,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request) -> ChatResponse:
    enforce_api_key(request)
    limiter_id = _client_identifier(request, req.session_id)
    try:
        enforce_rate_limit(limiter_id)
    except HTTPException:
        log_event(
            "chat_rate_limited",
            request_id=getattr(request.state, "request_id", None),
            session_id=req.session_id,
            limiter_id=limiter_id,
            limit_per_minute=RATE_LIMIT_PER_MINUTE,
        )
        raise

    session = get_session(req.session_id)
    start = time.perf_counter()
    request_id = getattr(request.state, "request_id", None)
    try:
        result = await Runner.run(
            agent,
            req.message,
            run_config=run_config,
            session=session,
        )
    except AuthenticationError as exc:
        log_event(
            "chat_error",
            request_id=request_id,
            session_id=req.session_id,
            error_type="AuthenticationError",
        )
        raise HTTPException(status_code=401, detail="Authentication failed. Check OPENAI_API_KEY.") from exc
    except RateLimitError as exc:
        log_event(
            "chat_error",
            request_id=request_id,
            session_id=req.session_id,
            error_type="RateLimitError",
        )
        raise HTTPException(status_code=429, detail="Rate limit reached. Try again shortly.") from exc
    except APIConnectionError as exc:
        log_event(
            "chat_error",
            request_id=request_id,
            session_id=req.session_id,
            error_type="APIConnectionError",
        )
        raise HTTPException(status_code=503, detail="Connection error reaching OpenAI API.") from exc
    except APIStatusError as exc:
        log_event(
            "chat_error",
            request_id=request_id,
            session_id=req.session_id,
            error_type="APIStatusError",
            status_code=exc.status_code,
        )
        raise HTTPException(status_code=502, detail=f"OpenAI API error ({exc.status_code}).") from exc

    response = ChatResponse(
        output=str(result.final_output),
        session_id=req.session_id,
        prompt_version=ACTIVE_PROMPT_VERSION,
    )
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    log_event(
        "chat_success",
        request_id=request_id,
        session_id=req.session_id,
        prompt_version=ACTIVE_PROMPT_VERSION,
        input_chars=len(req.message),
        output_chars=len(response.output),
        duration_ms=duration_ms,
    )
    return response


@app.post("/session/reset")
async def reset_session(req: ResetRequest, request: Request) -> dict[str, str]:
    enforce_api_key(request)
    session = get_session(req.session_id)
    await session.clear_session()
    log_event(
        "session_reset",
        request_id=getattr(request.state, "request_id", None),
        session_id=req.session_id,
    )
    return {"status": "ok", "session_id": req.session_id}
