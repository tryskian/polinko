import hmac
import json
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any, cast

from agents import Agent, Runner, RunConfig
from agents.memory import Session
from fastapi import FastAPI, HTTPException, Request
from openai import APIConnectionError, APIStatusError, AuthenticationError, RateLimitError
from pydantic import BaseModel, Field

from config import AppConfig
from core.prompts import ACTIVE_PROMPT_VERSION
from core.rate_limit import SlidingWindowRateLimiter
from core.retrieval import build_augmented_user_message
from core.runtime import create_agent, create_run_config, create_session


logger = logging.getLogger("polinko.api")


@dataclass
class RuntimeDeps:
    session_db_path: str
    default_session_id: str
    server_api_key: str | None
    server_api_key_principals: dict[str, str]
    rate_limit_per_minute: int
    rate_limiter: SlidingWindowRateLimiter
    run_config: RunConfig
    agent: Agent[Any]


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message.")
    session_id: str | None = Field(default=None, min_length=1, description="Conversation session ID.")


class ChatResponse(BaseModel):
    output: str
    session_id: str
    prompt_version: str


class ResetRequest(BaseModel):
    session_id: str | None = Field(default=None, min_length=1)


def _log_event(event: str, **fields: object) -> None:
    payload = {"event": event, **fields}
    logger.info(json.dumps(payload, default=str))


def _runtime_deps(app: FastAPI) -> RuntimeDeps:
    return cast(RuntimeDeps, app.state.runtime_deps)


def _client_identifier(request: Request, session_id: str, principal: str | None) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    client_ip = forwarded_for or (request.client.host if request.client else "unknown")
    subject = principal or "anonymous"
    return f"{subject}:{client_ip}:{session_id}"


def _enforce_api_key(request: Request) -> str | None:
    deps = _runtime_deps(request.app)
    configured_api_keys = deps.server_api_key_principals
    if not configured_api_keys:
        return None

    presented = request.headers.get("x-api-key")
    if not presented:
        raise HTTPException(status_code=401, detail="Invalid API key.")
    for expected_key, principal in configured_api_keys.items():
        if hmac.compare_digest(presented, expected_key):
            return principal
    raise HTTPException(status_code=401, detail="Invalid API key.")


def _enforce_rate_limit(request: Request, identifier: str) -> None:
    deps = _runtime_deps(request.app)
    retry_after = deps.rate_limiter.consume(identifier, limit_per_minute=deps.rate_limit_per_minute)
    if retry_after is not None:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Rate limit exceeded ({deps.rate_limit_per_minute}/min). "
                f"Retry in ~{retry_after}s."
            ),
            headers={"Retry-After": str(retry_after)},
        )


def _session_for_request(request: Request, session_id: str) -> Session:
    deps = _runtime_deps(request.app)
    return create_session(session_id=session_id, db_path=deps.session_db_path, limit=80)


def create_app(config: AppConfig) -> FastAPI:
    logging.basicConfig(level=getattr(logging, config.log_level, logging.INFO), format="%(message)s")

    app = FastAPI(title="Polinko Agent API", version="0.1.0")
    app.state.runtime_deps = RuntimeDeps(
        session_db_path=config.session_db_path,
        default_session_id=config.default_session_id,
        server_api_key=config.server_api_key,
        server_api_key_principals=config.server_api_key_principals,
        rate_limit_per_minute=config.rate_limit_per_minute,
        rate_limiter=SlidingWindowRateLimiter(),
        run_config=create_run_config(store=True),
        agent=create_agent(),
    )

    @app.middleware("http")
    async def request_logging(request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.request_id = request_id
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            _log_event(
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
        _log_event(
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
        principal = _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        session_id = req.session_id or deps.default_session_id
        limiter_id = _client_identifier(request, session_id, principal)
        try:
            _enforce_rate_limit(request, limiter_id)
        except HTTPException:
            _log_event(
                "chat_rate_limited",
                request_id=getattr(request.state, "request_id", None),
                session_id=session_id,
                limiter_id=limiter_id,
                principal=principal,
                limit_per_minute=deps.rate_limit_per_minute,
            )
            raise

        session = _session_for_request(request, session_id)
        start = time.perf_counter()
        request_id = getattr(request.state, "request_id", None)
        try:
            augmented_message = build_augmented_user_message(req.message)
            result = await Runner.run(
                deps.agent,
                augmented_message,
                run_config=deps.run_config,
                session=session,
            )
        except AuthenticationError as exc:
            _log_event(
                "chat_error",
                request_id=request_id,
                session_id=session_id,
                error_type="AuthenticationError",
            )
            raise HTTPException(status_code=401, detail="Authentication failed. Check OPENAI_API_KEY.") from exc
        except RateLimitError as exc:
            _log_event(
                "chat_error",
                request_id=request_id,
                session_id=session_id,
                error_type="RateLimitError",
            )
            raise HTTPException(status_code=429, detail="Rate limit reached. Try again shortly.") from exc
        except APIConnectionError as exc:
            _log_event(
                "chat_error",
                request_id=request_id,
                session_id=session_id,
                error_type="APIConnectionError",
            )
            raise HTTPException(status_code=503, detail="Connection error reaching OpenAI API.") from exc
        except APIStatusError as exc:
            _log_event(
                "chat_error",
                request_id=request_id,
                session_id=session_id,
                error_type="APIStatusError",
                status_code=exc.status_code,
            )
            raise HTTPException(status_code=502, detail=f"OpenAI API error ({exc.status_code}).") from exc

        response = ChatResponse(
            output=str(result.final_output),
            session_id=session_id,
            prompt_version=ACTIVE_PROMPT_VERSION,
        )
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        _log_event(
            "chat_success",
            request_id=request_id,
            session_id=session_id,
            principal=principal,
            prompt_version=ACTIVE_PROMPT_VERSION,
            input_chars=len(req.message),
            output_chars=len(response.output),
            duration_ms=duration_ms,
        )
        return response

    @app.post("/session/reset")
    async def reset_session(req: ResetRequest, request: Request) -> dict[str, str]:
        principal = _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        session_id = req.session_id or deps.default_session_id
        session = _session_for_request(request, session_id)
        await session.clear_session()
        _log_event(
            "session_reset",
            request_id=getattr(request.state, "request_id", None),
            session_id=session_id,
            principal=principal,
        )
        return {"status": "ok", "session_id": session_id}

    return app
