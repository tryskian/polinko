import base64
import binascii
import hashlib
import hmac
import json
import logging
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, cast

from agents import Agent, Runner, RunConfig
from agents.memory import Session
from fastapi import FastAPI, HTTPException, Request
from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)
from pydantic import BaseModel, Field

from config import AppConfig
from core.history_store import (
    ChatHistoryStore,
    ChatSummary,
    OcrRun,
    CollaborationHandoff,
    CollaborationState,
    PersonalizationSettings,
    DEFAULT_CHAT_TITLE,
)
from core.prompts import ACTIVE_PROMPT, ACTIVE_PROMPT_VERSION
from core.rate_limit import SlidingWindowRateLimiter
from core.runtime import create_agent, create_run_config, create_session
from core.vector_store import VectorMatch, VectorStore


logger = logging.getLogger("polinko.api")


_LATENCY_BUCKET_EDGES_MS = (10.0, 25.0, 50.0, 100.0, 250.0, 500.0, 1000.0, 2000.0)
_OCR_VECTOR_CHUNK_CHARS = 700
_OCR_VECTOR_CHUNK_OVERLAP = 120
_OCR_MAX_BYTES = 5 * 1024 * 1024
_PDF_MAX_BYTES = 10 * 1024 * 1024
_OCR_RETRY_AFTER_RATE_LIMIT_SECONDS = 10
_OCR_RETRY_AFTER_TRANSIENT_SECONDS = 3
_FILE_SEARCH_DEFAULT_SOURCE_TYPES = ("ocr",)
_FILE_SEARCH_ALLOWED_SOURCE_TYPES = {"chat", "ocr", "pdf"}
_FILE_SEARCH_TOKEN_RE = re.compile(r"[a-z0-9]+")
_FILE_SEARCH_CANDIDATE_MULTIPLIER = 8
_FILE_SEARCH_MAX_CANDIDATES = 200
_FILE_SEARCH_MIN_SIMILARITY_FLOOR = 0.15
_RESPONSES_HISTORY_MAX_MESSAGE_CHARS = 550
_STRUCTURED_PREVIEW_MAX_CHARS = 240
_FACTUAL_QUERY_HINTS = (
    "latest",
    "today",
    "current",
    "according to",
    "official",
    "source",
    "evidence",
    "statistics",
    "study",
    "what is",
    "who is",
    "how many",
    "market cap",
    "gdp",
    "law",
    "policy",
)


def _default_latency_buckets() -> dict[str, int]:
    buckets = {f"le_{int(edge)}ms": 0 for edge in _LATENCY_BUCKET_EDGES_MS}
    buckets["gt_2000ms"] = 0
    return buckets


def _latency_bucket_label(duration_ms: float) -> str:
    for edge in _LATENCY_BUCKET_EDGES_MS:
        if duration_ms <= edge:
            return f"le_{int(edge)}ms"
    return "gt_2000ms"


@dataclass
class RuntimeMetrics:
    started_at_ms: int
    started_monotonic: float
    requests_total: int = 0
    status_counts: dict[str, int] = field(default_factory=dict)
    rate_limited_total: int = 0
    cumulative_duration_ms: float = 0.0
    latency_buckets: dict[str, int] = field(default_factory=_default_latency_buckets)


def create_runtime_metrics() -> RuntimeMetrics:
    return RuntimeMetrics(
        started_at_ms=int(time.time() * 1000),
        started_monotonic=time.perf_counter(),
    )


def _record_metrics(metrics: RuntimeMetrics, status_code: int, duration_ms: float) -> None:
    status_key = str(status_code)
    metrics.requests_total += 1
    metrics.status_counts[status_key] = metrics.status_counts.get(status_key, 0) + 1
    metrics.cumulative_duration_ms += duration_ms
    if status_code == 429:
        metrics.rate_limited_total += 1
    bucket = _latency_bucket_label(duration_ms)
    metrics.latency_buckets[bucket] = metrics.latency_buckets.get(bucket, 0) + 1


@dataclass
class RuntimeDeps:
    openai_api_key: str
    session_db_path: str
    history_store: ChatHistoryStore
    default_session_id: str
    server_api_key: str | None
    server_api_key_principals: dict[str, str]
    rate_limit_per_minute: int
    rate_limiter: SlidingWindowRateLimiter
    deprecate_on_reset: bool
    ocr_provider: str
    ocr_model: str
    ocr_prompt: str
    ocr_client: OpenAI | None
    vector_enabled: bool
    vector_top_k: int
    vector_min_similarity: float
    vector_max_chars: int
    vector_exclude_current_session: bool
    vector_embedding_model: str
    vector_store: VectorStore | None
    embedding_client: OpenAI | None
    responses_orchestration_enabled: bool
    responses_orchestration_model: str
    responses_vector_store_id: str | None
    responses_include_web_search: bool
    responses_history_turn_limit: int
    responses_client: OpenAI | None
    governance_enabled: bool
    governance_allow_web_search: bool
    governance_log_only: bool
    hallucination_guardrails_enabled: bool
    personalization_default_memory_scope: str
    metrics: RuntimeMetrics
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
    deprecate: bool = False


class ChatSummaryResponse(BaseModel):
    session_id: str
    title: str
    created_at: int
    updated_at: int
    message_count: int
    status: str
    deprecated_at: int | None


class ChatsResponse(BaseModel):
    chats: list[ChatSummaryResponse]


class CreateChatRequest(BaseModel):
    session_id: str | None = Field(default=None, min_length=1)
    title: str | None = None


class RenameChatRequest(BaseModel):
    title: str = Field(..., min_length=1)


class ChatMessageResponse(BaseModel):
    message_id: str
    parent_message_id: str | None
    role: str
    content: str
    content_sha256: str
    created_at: int


class ChatMessagesResponse(BaseModel):
    session_id: str
    messages: list[ChatMessageResponse]


class ChatExportResponse(BaseModel):
    session_id: str
    title: str
    status: str
    prompt_version: str
    exported_at: int
    message_count: int
    transcript_sha256: str
    messages: list[ChatMessageResponse]
    ocr_runs: list["OcrRunResponse"] = Field(default_factory=list)
    markdown: str | None = None


class CollaborationStateResponse(BaseModel):
    session_id: str
    active_agent_id: str
    active_role: str
    objective: str | None
    updated_at: int
    updated_by: str | None


class CollaborationHandoffResponse(BaseModel):
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


class CollaborationResponse(BaseModel):
    session_id: str
    active: CollaborationStateResponse | None
    handoffs: list[CollaborationHandoffResponse]


class CollaborationHandoffRequest(BaseModel):
    to_agent_id: str = Field(..., min_length=1, max_length=80)
    to_role: str = Field(..., min_length=1, max_length=120)
    objective: str | None = Field(default=None, max_length=500)
    reason: str | None = Field(default=None, max_length=500)


class NoteRequest(BaseModel):
    note: str = Field(..., min_length=1, max_length=500)


class PersonalizationRequest(BaseModel):
    memory_scope: str = Field(..., min_length=1, max_length=20)


class OcrRequest(BaseModel):
    session_id: str | None = Field(default=None, min_length=1)
    source_name: str | None = Field(default=None, max_length=255)
    mime_type: str | None = Field(default=None, max_length=120)
    data_base64: str | None = None
    text_hint: str | None = None
    source_message_id: str | None = None
    attach_to_chat: bool = True


class OcrRunResponse(BaseModel):
    run_id: str
    session_id: str
    source_name: str | None
    mime_type: str | None
    source_message_id: str | None
    result_message_id: str | None
    status: str
    extracted_text: str
    structured: "ExtractionStructuredResponse"
    created_at: int


class OcrResponse(BaseModel):
    run: OcrRunResponse


class PdfIngestRequest(BaseModel):
    session_id: str | None = Field(default=None, min_length=1)
    source_name: str | None = Field(default=None, max_length=255)
    mime_type: str | None = Field(default=None, max_length=120)
    data_base64: str = Field(..., min_length=1)
    source_message_id: str | None = None
    attach_to_chat: bool = True


class PdfIngestResponse(BaseModel):
    ingest_id: str
    session_id: str
    source_name: str | None
    mime_type: str | None
    status: str
    extracted_chars: int
    vector_chunks: int
    result_message_id: str | None
    structured: "ExtractionStructuredResponse"


class ExtractionStructuredResponse(BaseModel):
    schema_version: str
    source_type: str
    source_name: str | None
    mime_type: str | None
    text_sha256: str
    char_count: int
    word_count: int
    line_count: int
    preview: str


class FileSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    session_id: str | None = Field(default=None, min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
    source_types: list[str] | None = None


class FileSearchMatchResponse(BaseModel):
    vector_id: str
    session_id: str
    source_type: str
    source_ref: str | None
    similarity: float
    keyword_score: float
    score: float
    snippet: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class FileSearchResponse(BaseModel):
    query: str
    searched_at: int
    matches: list[FileSearchMatchResponse]


class PersonalizationResponse(BaseModel):
    session_id: str
    memory_scope: str
    updated_at: int
    updated_by: str | None


class MetricsResponse(BaseModel):
    started_at_ms: int
    uptime_seconds: float
    requests_total: int
    status_counts: dict[str, int]
    rate_limited_total: int
    avg_latency_ms: float
    latency_buckets: dict[str, int]


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


def _close_session(session: Session) -> None:
    close_fn = getattr(session, "close", None)
    if callable(close_fn):
        close_fn()


def _chat_summary_response(summary: ChatSummary) -> ChatSummaryResponse:
    return ChatSummaryResponse(
        session_id=summary.session_id,
        title=summary.title,
        created_at=summary.created_at,
        updated_at=summary.updated_at,
        message_count=summary.message_count,
        status=summary.status,
        deprecated_at=summary.deprecated_at,
    )


def _chat_message_response(message: Any) -> ChatMessageResponse:
    return ChatMessageResponse(
        message_id=message.message_id,
        parent_message_id=message.parent_message_id,
        role=message.role,
        content=message.content,
        content_sha256=_sha256_text(message.content),
        created_at=message.created_at,
    )


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _transcript_sha256(messages: list[ChatMessageResponse]) -> str:
    parts = [
        (
            f"{message.message_id}\x1f"
            f"{message.parent_message_id or ''}\x1f"
            f"{message.role}\x1f"
            f"{message.created_at}\x1f"
            f"{message.content_sha256}"
        )
        for message in messages
    ]
    return _sha256_text("\x1e".join(parts))


def _ocr_run_response(run: OcrRun) -> OcrRunResponse:
    return OcrRunResponse(
        run_id=run.run_id,
        session_id=run.session_id,
        source_name=run.source_name,
        mime_type=run.mime_type,
        source_message_id=run.source_message_id,
        result_message_id=run.result_message_id,
        status=run.status,
        extracted_text=run.extracted_text,
        structured=_build_structured_extraction(
            source_type="ocr",
            source_name=run.source_name,
            mime_type=run.mime_type,
            text=run.extracted_text,
        ),
        created_at=run.created_at,
    )


def _build_structured_extraction(
    *,
    source_type: str,
    source_name: str | None,
    mime_type: str | None,
    text: str,
) -> ExtractionStructuredResponse:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line for line in (chunk.strip() for chunk in normalized.split("\n")) if line]
    compact_preview = " ".join(normalized.split())
    if len(compact_preview) > _STRUCTURED_PREVIEW_MAX_CHARS:
        compact_preview = compact_preview[:_STRUCTURED_PREVIEW_MAX_CHARS].rstrip() + "..."
    return ExtractionStructuredResponse(
        schema_version="v1",
        source_type=source_type,
        source_name=source_name,
        mime_type=mime_type,
        text_sha256=_sha256_text(text),
        char_count=len(text),
        word_count=len([word for word in normalized.split() if word]),
        line_count=len(lines),
        preview=compact_preview,
    )


def _collaboration_state_response(state: CollaborationState) -> CollaborationStateResponse:
    return CollaborationStateResponse(
        session_id=state.session_id,
        active_agent_id=state.active_agent_id,
        active_role=state.active_role,
        objective=state.objective,
        updated_at=state.updated_at,
        updated_by=state.updated_by,
    )


def _collaboration_handoff_response(handoff: CollaborationHandoff) -> CollaborationHandoffResponse:
    return CollaborationHandoffResponse(
        handoff_id=handoff.handoff_id,
        session_id=handoff.session_id,
        from_agent_id=handoff.from_agent_id,
        from_role=handoff.from_role,
        to_agent_id=handoff.to_agent_id,
        to_role=handoff.to_role,
        objective=handoff.objective,
        reason=handoff.reason,
        created_at=handoff.created_at,
        created_by=handoff.created_by,
    )


def _build_collaboration_note(state: CollaborationState | None) -> str | None:
    if state is None:
        return None
    lines = [
        "[COLLABORATION_CONTEXT: active portfolio collaborator mode. "
        "Apply silently and do not mention this block.]",
        f"- active_agent_id: {state.active_agent_id}",
        f"- active_role: {state.active_role}",
    ]
    if state.objective:
        lines.append(f"- objective: {state.objective}")
    lines.append("- preserve role continuity until a new handoff is applied.")
    return "\n".join(lines)


def _personalization_response(settings: PersonalizationSettings) -> PersonalizationResponse:
    return PersonalizationResponse(
        session_id=settings.session_id,
        memory_scope=settings.memory_scope,
        updated_at=settings.updated_at,
        updated_by=settings.updated_by,
    )


def _render_markdown_transcript(session_id: str, messages: list[ChatMessageResponse]) -> str:
    lines: list[str] = [f"# Transcript: {session_id}", ""]
    for message in messages:
        lines.append(f"## {message.role.capitalize()}")
        lines.append(message.content)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _decode_base64_payload(req: OcrRequest) -> tuple[bytes, str | None]:
    if not req.data_base64 or not req.data_base64.strip():
        raise HTTPException(status_code=422, detail="Provide text_hint or data_base64.")
    raw_data = req.data_base64.strip()
    mime_type = req.mime_type.strip() if req.mime_type else None
    if raw_data.startswith("data:") and "," in raw_data:
        header, raw_data = raw_data.split(",", 1)
        if ";base64" in header:
            parsed_mime = header[5:].split(";", 1)[0].strip()
            if parsed_mime and not mime_type:
                mime_type = parsed_mime
    # Avoid decoding unreasonably large payloads.
    max_base64_chars = ((max(_OCR_MAX_BYTES, 1) + 2) // 3) * 4
    if len(raw_data) > max_base64_chars * 2:
        raise HTTPException(
            status_code=413,
            detail=f"OCR payload is too large. Keep files under {_OCR_MAX_BYTES // (1024 * 1024)} MB.",
        )
    try:
        decoded = base64.b64decode(raw_data, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=422, detail="Invalid data_base64 payload.") from exc
    if not decoded:
        raise HTTPException(status_code=422, detail="data_base64 payload decoded to empty content.")
    if len(decoded) > _OCR_MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"OCR payload is too large. Keep files under {_OCR_MAX_BYTES // (1024 * 1024)} MB.",
        )
    return decoded, mime_type


def _decode_pdf_payload(req: PdfIngestRequest) -> tuple[bytes, str | None]:
    raw_data = req.data_base64.strip()
    mime_type = req.mime_type.strip().lower() if req.mime_type else None
    if raw_data.startswith("data:") and "," in raw_data:
        header, raw_data = raw_data.split(",", 1)
        if ";base64" in header:
            parsed_mime = header[5:].split(";", 1)[0].strip().lower()
            if parsed_mime and not mime_type:
                mime_type = parsed_mime

    max_base64_chars = ((max(_PDF_MAX_BYTES, 1) + 2) // 3) * 4
    if len(raw_data) > max_base64_chars * 2:
        raise HTTPException(
            status_code=413,
            detail=f"PDF payload is too large. Keep files under {_PDF_MAX_BYTES // (1024 * 1024)} MB.",
        )
    try:
        decoded = base64.b64decode(raw_data, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=422, detail="Invalid data_base64 payload.") from exc
    if not decoded:
        raise HTTPException(status_code=422, detail="data_base64 payload decoded to empty content.")
    if len(decoded) > _PDF_MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"PDF payload is too large. Keep files under {_PDF_MAX_BYTES // (1024 * 1024)} MB.",
        )
    return decoded, mime_type


def _extract_text_from_pdf_bytes(payload: bytes) -> str:
    try:
        from io import BytesIO
        from pypdf import PdfReader
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="PDF extractor dependency is missing. Install `pypdf`.",
        ) from exc

    try:
        reader = PdfReader(BytesIO(payload))
    except Exception as exc:
        raise HTTPException(status_code=422, detail="Invalid or unreadable PDF payload.") from exc

    parts: list[str] = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        compact = text.strip()
        if compact:
            parts.append(compact)

    merged = "\n\n".join(parts).strip()
    if not merged:
        raise HTTPException(status_code=422, detail="No extractable text found in PDF.")
    return merged


def _retry_after_header_value(exc: Exception, default_seconds: int) -> str:
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None)
    if headers is not None:
        raw = headers.get("Retry-After") or headers.get("retry-after")
        if raw:
            try:
                parsed = int(raw.strip())
                if parsed > 0:
                    return str(parsed)
            except (TypeError, ValueError):
                pass
    return str(default_seconds)


def _scaffold_extract_text(req: OcrRequest) -> tuple[str, str]:
    if req.text_hint and req.text_hint.strip():
        return req.text_hint.strip(), "ok"

    decoded, _mime_type = _decode_base64_payload(req)
    text = decoded.decode("utf-8", errors="ignore").strip()
    if text:
        return text, "ok"
    return "[OCR scaffold] Binary payload received. Connect OCR engine for text extraction.", "stub"


def _extract_text_with_openai(req: OcrRequest, deps: RuntimeDeps) -> tuple[str, str]:
    if req.text_hint and req.text_hint.strip():
        return req.text_hint.strip(), "ok"

    decoded, detected_mime = _decode_base64_payload(req)
    mime_type = (detected_mime or "application/octet-stream").strip().lower()
    if not mime_type.startswith("image/"):
        raise HTTPException(
            status_code=422,
            detail="OpenAI OCR expects image input. Provide image/* data_base64 or use text_hint.",
        )

    if deps.ocr_client is None:
        raise HTTPException(status_code=503, detail="OCR provider client is not configured.")

    data_url = f"data:{mime_type};base64,{base64.b64encode(decoded).decode('ascii')}"
    try:
        response = deps.ocr_client.responses.create(
            model=deps.ocr_model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": deps.ocr_prompt},
                        {"type": "input_image", "image_url": data_url},
                    ],
                }
            ],
        )
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail="Authentication failed. Check OPENAI_API_KEY.") from exc
    except RateLimitError as exc:
        retry_after = _retry_after_header_value(exc, _OCR_RETRY_AFTER_RATE_LIMIT_SECONDS)
        raise HTTPException(
            status_code=429,
            detail="OCR rate limit reached. Try again shortly.",
            headers={"Retry-After": retry_after},
        ) from exc
    except APIConnectionError as exc:
        raise HTTPException(
            status_code=503,
            detail="Connection error reaching OpenAI OCR provider.",
            headers={"Retry-After": str(_OCR_RETRY_AFTER_TRANSIENT_SECONDS)},
        ) from exc
    except APIStatusError as exc:
        if exc.status_code == 429:
            retry_after = _retry_after_header_value(exc, _OCR_RETRY_AFTER_RATE_LIMIT_SECONDS)
            raise HTTPException(
                status_code=429,
                detail="OCR rate limit reached. Try again shortly.",
                headers={"Retry-After": retry_after},
            ) from exc
        if exc.status_code in {400, 413, 415, 422}:
            raise HTTPException(
                status_code=422,
                detail="OpenAI OCR rejected the image payload. Verify format and size.",
            ) from exc
        if exc.status_code in {401, 403}:
            raise HTTPException(status_code=401, detail="Authentication failed. Check OPENAI_API_KEY.") from exc
        if 500 <= exc.status_code <= 599:
            retry_after = _retry_after_header_value(exc, _OCR_RETRY_AFTER_TRANSIENT_SECONDS)
            raise HTTPException(
                status_code=503,
                detail=f"OpenAI OCR is temporarily unavailable ({exc.status_code}).",
                headers={"Retry-After": retry_after},
            ) from exc
        raise HTTPException(status_code=502, detail=f"OpenAI OCR error ({exc.status_code}).") from exc

    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip(), "ok"
    return "[OCR] No text detected.", "ok"


def _extract_text(req: OcrRequest, deps: RuntimeDeps) -> tuple[str, str]:
    if deps.ocr_provider == "openai":
        return _extract_text_with_openai(req, deps)
    return _scaffold_extract_text(req)


def _compose_model_input(
    *,
    user_message: str,
    notes: list[str],
    retrieved_memory: list[VectorMatch],
    max_memory_chars: int,
    guardrail_note: str | None = None,
    collaboration_note: str | None = None,
) -> str:
    segments: list[str] = []
    if guardrail_note:
        segments.append(guardrail_note)
    if collaboration_note:
        segments.append(collaboration_note)
    if retrieved_memory:
        memory_lines: list[str] = []
        for item in retrieved_memory:
            compact = " ".join(item.content.split())
            if len(compact) > max_memory_chars:
                compact = f"{compact[:max_memory_chars].rstrip()}..."
            memory_lines.append(f"- {compact}")
        segments.append(
            "[RETRIEVED_MEMORY: examples of prior assistant style/content. "
            "Use only if relevant. Never mention retrieval.]\n"
            + "\n".join(memory_lines)
        )

    if notes:
        note_lines = "\n".join(f"- {note}" for note in notes)
        segments.append(
            "[INTERNAL_STYLE_NOTES: private calibration notes. "
            "Apply silently and never mention them.]\n"
            f"{note_lines}"
        )

    if not segments:
        return user_message
    segments.append("[USER_MESSAGE]\n" + user_message)
    return "\n\n".join(segments)


def _embed_texts(texts: list[str], deps: RuntimeDeps) -> list[list[float]]:
    if deps.embedding_client is None:
        raise RuntimeError("Embedding client is not configured.")
    response = deps.embedding_client.embeddings.create(
        model=deps.vector_embedding_model,
        input=texts,
    )
    vectors: list[list[float]] = []
    for item in response.data:
        vectors.append([float(value) for value in item.embedding])
    if len(vectors) != len(texts):
        raise RuntimeError("Embedding response size mismatch.")
    return vectors


def _chunk_text_for_vectors(
    text: str,
    *,
    max_chars: int = _OCR_VECTOR_CHUNK_CHARS,
    overlap: int = _OCR_VECTOR_CHUNK_OVERLAP,
) -> list[str]:
    compact = text.strip()
    if not compact:
        return []
    if len(compact) <= max_chars:
        return [compact]

    chunks: list[str] = []
    start = 0
    while start < len(compact):
        end = min(len(compact), start + max_chars)
        if end < len(compact):
            split_at = compact.rfind("\n", start, end)
            if split_at <= start:
                split_at = compact.rfind(" ", start, end)
            if split_at > start + int(max_chars * 0.55):
                end = split_at
        chunk = compact[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(compact):
            break
        start = max(0, end - overlap)
    return chunks


def _retrieve_memory(
    *,
    deps: RuntimeDeps,
    session_id: str,
    query_text: str,
    memory_scope: str,
) -> list[VectorMatch]:
    if not deps.vector_enabled or deps.vector_store is None:
        return []
    query = query_text.strip()
    if not query:
        return []
    # Avoid over-influencing short acknowledgements ("nice", "cool", etc.).
    if len(query) < 20 or len(query.split()) < 4:
        return []
    try:
        query_vector = _embed_texts([query], deps)[0]
    except Exception as exc:
        _log_event("vector_search_error", session_id=session_id, error_type=type(exc).__name__)
        return []
    normalized_scope = memory_scope.strip().lower()
    include_session_id: str | None = None
    exclude_session_id: str | None = None
    if normalized_scope == "session":
        include_session_id = session_id
    else:
        exclude_session_id = session_id if deps.vector_exclude_current_session else None
    return deps.vector_store.search(
        query_embedding=query_vector,
        limit=deps.vector_top_k,
        min_similarity=deps.vector_min_similarity,
        roles=("assistant",),
        include_session_id=include_session_id,
        exclude_session_id=exclude_session_id,
        source_types=("chat",),
    )


def _index_assistant_output(
    *,
    deps: RuntimeDeps,
    session_id: str,
    message_id: str,
    content: str,
    created_at: int,
) -> None:
    if not deps.vector_enabled or deps.vector_store is None:
        return
    text = content.strip()
    if not text:
        return
    try:
        embedding = _embed_texts([text], deps)[0]
        deps.vector_store.upsert_message_vector(
            session_id=session_id,
            role="assistant",
            message_id=message_id,
            content=text,
            embedding=embedding,
            source_type="chat",
            source_ref=message_id,
            metadata={"source": "chat"},
            created_at=created_at,
        )
    except Exception as exc:
        _log_event("vector_index_error", session_id=session_id, error_type=type(exc).__name__)


def _index_ocr_output(
    *,
    deps: RuntimeDeps,
    session_id: str,
    run: OcrRun,
) -> None:
    if not deps.vector_enabled or deps.vector_store is None:
        return
    chunks = _chunk_text_for_vectors(run.extracted_text)
    if not chunks:
        return
    try:
        embeddings = _embed_texts(chunks, deps)
        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_ref = f"{run.run_id}:{index + 1}/{len(chunks)}"
            deps.vector_store.upsert_message_vector(
                session_id=session_id,
                role="assistant",
                message_id=None,
                content=chunk,
                embedding=embedding,
                source_type="ocr",
                source_ref=chunk_ref,
                metadata={
                    "source": "ocr",
                    "ocr_run_id": run.run_id,
                    "source_name": run.source_name,
                    "mime_type": run.mime_type,
                    "source_message_id": run.source_message_id,
                    "result_message_id": run.result_message_id,
                    "chunk_index": index,
                    "chunk_count": len(chunks),
                },
                created_at=run.created_at,
            )
    except Exception as exc:
        _log_event(
            "vector_ocr_index_error",
            session_id=session_id,
            run_id=run.run_id,
            error_type=type(exc).__name__,
        )


def _normalize_file_search_source_types(source_types: list[str] | None) -> tuple[str, ...]:
    if not source_types:
        return _FILE_SEARCH_DEFAULT_SOURCE_TYPES
    normalized: list[str] = []
    for raw in source_types:
        value = raw.strip().lower()
        if value:
            normalized.append(value)
    if not normalized:
        return _FILE_SEARCH_DEFAULT_SOURCE_TYPES
    invalid = sorted({value for value in normalized if value not in _FILE_SEARCH_ALLOWED_SOURCE_TYPES})
    if invalid:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported source_types: {', '.join(invalid)}.",
        )
    deduped: list[str] = []
    seen: set[str] = set()
    for value in normalized:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return tuple(deduped)


def _tokenize_file_search_text(text: str) -> list[str]:
    lowered = text.lower()
    return _FILE_SEARCH_TOKEN_RE.findall(lowered)


def _keyword_overlap_score(query_tokens: list[str], content: str) -> float:
    if not query_tokens:
        return 0.0
    content_tokens = _tokenize_file_search_text(content)
    if not content_tokens:
        return 0.0
    unique_query_tokens = list(dict.fromkeys(query_tokens))
    token_set = set(content_tokens)
    overlap = sum(1 for token in unique_query_tokens if token in token_set)
    score = overlap / len(unique_query_tokens)
    phrase = " ".join(unique_query_tokens)
    normalized_content = " ".join(content_tokens)
    if phrase and phrase in normalized_content:
        score = min(1.0, score + 0.15)
    return score


def _file_search_snippet(content: str, query_tokens: list[str], *, max_chars: int = 240) -> str:
    compact = " ".join(content.split())
    if len(compact) <= max_chars:
        return compact
    lowered = compact.lower()
    anchor = -1
    for token in query_tokens:
        idx = lowered.find(token)
        if idx < 0:
            continue
        if anchor == -1 or idx < anchor:
            anchor = idx
    if anchor < 0:
        anchor = 0
    start = max(0, anchor - max_chars // 3)
    end = min(len(compact), start + max_chars)
    if end - start < max_chars and start > 0:
        start = max(0, end - max_chars)
    snippet = compact[start:end].strip()
    if start > 0:
        snippet = f"...{snippet}"
    if end < len(compact):
        snippet = f"{snippet}..."
    return snippet


def _recent_chat_context_for_responses(messages: list[Any], turn_limit: int) -> str:
    visible = [msg for msg in messages if getattr(msg, "role", "") in {"user", "assistant"}]
    if not visible:
        return ""
    max_messages = max(1, turn_limit * 2)
    recent = visible[-max_messages:]
    lines: list[str] = []
    for msg in recent:
        role = str(getattr(msg, "role", "assistant")).upper()
        content = " ".join(str(getattr(msg, "content", "")).split())
        if len(content) > _RESPONSES_HISTORY_MAX_MESSAGE_CHARS:
            content = f"{content[:_RESPONSES_HISTORY_MAX_MESSAGE_CHARS].rstrip()}..."
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def _extract_responses_output_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    pieces: list[str] = []
    output = getattr(response, "output", None)
    if isinstance(output, list):
        for item in output:
            content_blocks = getattr(item, "content", None)
            if not isinstance(content_blocks, list):
                continue
            for block in content_blocks:
                text_value = getattr(block, "text", None)
                if isinstance(text_value, str) and text_value.strip():
                    pieces.append(text_value.strip())
                    continue
                nested_value = getattr(text_value, "value", None)
                if isinstance(nested_value, str) and nested_value.strip():
                    pieces.append(nested_value.strip())
    if pieces:
        return "\n\n".join(pieces)
    return "[No text output returned.]"


def _looks_like_factual_query(query: str) -> bool:
    lowered = query.strip().lower()
    if not lowered:
        return False
    if any(hint in lowered for hint in _FACTUAL_QUERY_HINTS):
        return True
    if re.search(r"\b(19|20)\d{2}\b", lowered):
        return True
    if re.search(r"\b[A-Z]{2,}\b", query):
        return True
    # Questions with concrete entities are frequently factual/risky.
    if "?" in query and re.search(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b", query):
        return True
    return False


def _build_hallucination_guardrail_note(
    *,
    deps: RuntimeDeps,
    query_text: str,
    evidence_count: int,
) -> str | None:
    if not deps.governance_enabled or not deps.hallucination_guardrails_enabled:
        return None
    if not _looks_like_factual_query(query_text):
        return None
    if evidence_count > 0:
        return (
            "[HALLUCINATION_GUARDRAIL: grounded mode]\n"
            "- Prefer claims that are supported by available context.\n"
            "- If certainty is low, signal uncertainty briefly instead of guessing.\n"
            "- Do not fabricate citations, dates, names, or numeric values."
        )
    return (
        "[HALLUCINATION_GUARDRAIL: low-evidence mode]\n"
        "- Avoid presenting uncertain facts as certain.\n"
        "- If supporting evidence is missing, say that clearly and keep claims cautious.\n"
        "- Do not invent sources, statistics, dates, names, or quotations."
    )


def _resolve_responses_tools(
    *,
    deps: RuntimeDeps,
    request_id: str | None,
    session_id: str,
    principal: str | None,
) -> list[dict[str, Any]]:
    if not deps.responses_vector_store_id:
        raise RuntimeError("Responses orchestration requires POLINKO_RESPONSES_VECTOR_STORE_ID.")
    tools: list[dict[str, Any]] = [
        {
            "type": "file_search",
            "vector_store_ids": [deps.responses_vector_store_id],
        }
    ]
    if not deps.responses_include_web_search:
        return tools
    if not deps.governance_enabled or deps.governance_allow_web_search or deps.governance_log_only:
        if deps.governance_enabled and deps.governance_log_only and not deps.governance_allow_web_search:
            _log_event(
                "governance_tool_violation_logged",
                request_id=request_id,
                session_id=session_id,
                principal=principal,
                tool="web_search_preview",
                action="allow_log_only",
            )
        tools.append({"type": "web_search_preview"})
        return tools
    _log_event(
        "governance_tool_blocked",
        request_id=request_id,
        session_id=session_id,
        principal=principal,
        tool="web_search_preview",
    )
    return tools


def _chat_with_responses_orchestration(
    *,
    deps: RuntimeDeps,
    request_id: str | None,
    principal: str | None,
    session_id: str,
    user_message: str,
    notes: list[str],
    guardrail_note: str | None = None,
    collaboration_note: str | None = None,
) -> tuple[str, int]:
    if deps.responses_client is None:
        raise RuntimeError("Responses orchestration is enabled, but no client is configured.")
    history_messages = deps.history_store.list_messages(session_id=session_id)
    history_context = _recent_chat_context_for_responses(
        history_messages,
        turn_limit=deps.responses_history_turn_limit,
    )
    segments: list[str] = []
    if guardrail_note:
        segments.append(guardrail_note)
    if collaboration_note:
        segments.append(collaboration_note)
    if notes:
        note_lines = "\n".join(f"- {note}" for note in notes)
        segments.append(
            "[INTERNAL_STYLE_NOTES: private calibration notes. "
            "Apply silently and never mention them.]\n"
            f"{note_lines}"
        )
    if history_context:
        segments.append(
            "[RECENT_CHAT_CONTEXT: prior dialogue turns. Keep continuity without re-summarizing.]\n"
            f"{history_context}"
        )
    segments.append("[USER_MESSAGE]\n" + user_message.strip())
    input_text = "\n\n".join(segments)

    tools = _resolve_responses_tools(
        deps=deps,
        request_id=request_id,
        session_id=session_id,
        principal=principal,
    )

    response = deps.responses_client.responses.create(
        model=deps.responses_orchestration_model,
        instructions=ACTIVE_PROMPT,
        input=input_text,
        tools=tools,
    )
    output = _extract_responses_output_text(response)
    return output, len(tools)


def _metrics_response(metrics: RuntimeMetrics) -> MetricsResponse:
    avg_latency_ms = 0.0
    if metrics.requests_total > 0:
        avg_latency_ms = round(metrics.cumulative_duration_ms / metrics.requests_total, 2)
    uptime_seconds = round(max(0.0, time.perf_counter() - metrics.started_monotonic), 2)
    return MetricsResponse(
        started_at_ms=metrics.started_at_ms,
        uptime_seconds=uptime_seconds,
        requests_total=metrics.requests_total,
        status_counts=dict(metrics.status_counts),
        rate_limited_total=metrics.rate_limited_total,
        avg_latency_ms=avg_latency_ms,
        latency_buckets=dict(metrics.latency_buckets),
    )


def create_app(config: AppConfig) -> FastAPI:
    logging.basicConfig(level=getattr(logging, config.log_level, logging.INFO), format="%(message)s")

    shared_openai_client = OpenAI(api_key=config.openai_api_key)
    app = FastAPI(title="Polinko Agent API", version="0.1.0")
    app.state.runtime_deps = RuntimeDeps(
        openai_api_key=config.openai_api_key,
        session_db_path=config.session_db_path,
        history_store=ChatHistoryStore(config.history_db_path),
        default_session_id=config.default_session_id,
        server_api_key=config.server_api_key,
        server_api_key_principals=config.server_api_key_principals,
        rate_limit_per_minute=config.rate_limit_per_minute,
        rate_limiter=SlidingWindowRateLimiter(),
        deprecate_on_reset=config.deprecate_on_reset,
        ocr_provider=config.ocr_provider,
        ocr_model=config.ocr_model,
        ocr_prompt=config.ocr_prompt,
        ocr_client=shared_openai_client if config.ocr_provider == "openai" else None,
        vector_enabled=config.vector_enabled,
        vector_top_k=config.vector_top_k,
        vector_min_similarity=config.vector_min_similarity,
        vector_max_chars=config.vector_max_chars,
        vector_exclude_current_session=config.vector_exclude_current_session,
        vector_embedding_model=config.vector_embedding_model,
        vector_store=VectorStore(config.vector_db_path) if config.vector_enabled else None,
        embedding_client=shared_openai_client if config.vector_enabled else None,
        responses_orchestration_enabled=config.responses_orchestration_enabled,
        responses_orchestration_model=config.responses_orchestration_model,
        responses_vector_store_id=config.responses_vector_store_id,
        responses_include_web_search=config.responses_include_web_search,
        responses_history_turn_limit=config.responses_history_turn_limit,
        responses_client=shared_openai_client if config.responses_orchestration_enabled else None,
        governance_enabled=config.governance_enabled,
        governance_allow_web_search=config.governance_allow_web_search,
        governance_log_only=config.governance_log_only,
        hallucination_guardrails_enabled=config.hallucination_guardrails_enabled,
        personalization_default_memory_scope=config.personalization_default_memory_scope,
        metrics=create_runtime_metrics(),
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
            deps = _runtime_deps(request.app)
            _record_metrics(deps.metrics, status_code=500, duration_ms=duration_ms)
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
        deps = _runtime_deps(request.app)
        _record_metrics(deps.metrics, status_code=response.status_code, duration_ms=duration_ms)
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

    @app.get("/metrics", response_model=MetricsResponse)
    def metrics(request: Request) -> MetricsResponse:
        _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        return _metrics_response(deps.metrics)

    @app.get("/chats", response_model=ChatsResponse)
    def list_chats(request: Request, include_deprecated: bool = False) -> ChatsResponse:
        _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        summaries = [
            _chat_summary_response(summary)
            for summary in deps.history_store.list_chats(include_deprecated=include_deprecated)
        ]
        return ChatsResponse(chats=summaries)

    @app.post("/chats", response_model=ChatSummaryResponse)
    def create_chat(req: CreateChatRequest, request: Request) -> ChatSummaryResponse:
        _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        session_id = req.session_id or f"chat-{uuid.uuid4()}"
        title = (req.title or DEFAULT_CHAT_TITLE).strip() or DEFAULT_CHAT_TITLE
        summary = deps.history_store.ensure_chat(session_id=session_id, title=title)
        return _chat_summary_response(summary)

    @app.get("/chats/{session_id}/messages", response_model=ChatMessagesResponse)
    def list_chat_messages(session_id: str, request: Request) -> ChatMessagesResponse:
        _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        chat = deps.history_store.get_chat(session_id=session_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found.")
        messages = [
            _chat_message_response(message)
            for message in deps.history_store.list_messages(session_id=session_id)
        ]
        return ChatMessagesResponse(session_id=session_id, messages=messages)

    @app.get("/chats/{session_id}/export", response_model=ChatExportResponse)
    def export_chat(session_id: str, request: Request, include_markdown: bool = False) -> ChatExportResponse:
        _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        chat = deps.history_store.get_chat(session_id=session_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found.")
        messages = [
            _chat_message_response(message)
            for message in deps.history_store.list_messages(session_id=session_id)
        ]
        ocr_runs = [_ocr_run_response(run) for run in deps.history_store.list_ocr_runs(session_id=session_id)]
        markdown = _render_markdown_transcript(session_id, messages) if include_markdown else None
        return ChatExportResponse(
            session_id=session_id,
            title=chat.title,
            status=chat.status,
            prompt_version=ACTIVE_PROMPT_VERSION,
            exported_at=int(time.time() * 1000),
            message_count=len(messages),
            transcript_sha256=_transcript_sha256(messages),
            messages=messages,
            ocr_runs=ocr_runs,
            markdown=markdown,
        )

    @app.post("/skills/ocr", response_model=OcrResponse)
    def run_ocr(req: OcrRequest, request: Request) -> OcrResponse:
        principal = _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        session_id = req.session_id or deps.default_session_id
        chat = deps.history_store.ensure_chat(session_id=session_id)
        if chat.status == "deprecated":
            raise HTTPException(
                status_code=409,
                detail="Chat is deprecated. Create a new chat before running OCR.",
            )
        if req.source_message_id and not deps.history_store.message_exists(
            session_id=session_id,
            message_id=req.source_message_id,
        ):
            raise HTTPException(status_code=404, detail="source_message_id not found in this chat.")

        extracted_text, status = _extract_text(req, deps)
        result_message_id: str | None = None
        if req.attach_to_chat:
            appended = deps.history_store.append_message(
                session_id=session_id,
                role="assistant",
                content=f"[OCR]\n{extracted_text}",
            )
            result_message_id = appended.message_id

        run = deps.history_store.record_ocr_run(
            run_id=f"ocr-{uuid.uuid4().hex[:12]}",
            session_id=session_id,
            source_name=req.source_name,
            mime_type=req.mime_type,
            source_message_id=req.source_message_id,
            result_message_id=result_message_id,
            status=status,
            extracted_text=extracted_text,
        )
        _index_ocr_output(deps=deps, session_id=session_id, run=run)
        _log_event(
            "ocr_run",
            request_id=getattr(request.state, "request_id", None),
            session_id=session_id,
            principal=principal,
            run_id=run.run_id,
            provider=deps.ocr_provider,
            status=run.status,
            chars=len(run.extracted_text),
            vector_chunks=len(_chunk_text_for_vectors(run.extracted_text)),
        )
        return OcrResponse(run=_ocr_run_response(run))

    @app.post("/skills/pdf_ingest", response_model=PdfIngestResponse)
    def pdf_ingest(req: PdfIngestRequest, request: Request) -> PdfIngestResponse:
        principal = _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        if not deps.vector_enabled or deps.vector_store is None:
            raise HTTPException(status_code=503, detail="Vector memory is not enabled.")

        session_id = req.session_id or deps.default_session_id
        chat = deps.history_store.ensure_chat(session_id=session_id)
        if chat.status == "deprecated":
            raise HTTPException(
                status_code=409,
                detail="Chat is deprecated. Create a new chat before ingesting PDF content.",
            )
        if req.source_message_id and not deps.history_store.message_exists(
            session_id=session_id,
            message_id=req.source_message_id,
        ):
            raise HTTPException(status_code=404, detail="source_message_id not found in this chat.")

        decoded, detected_mime = _decode_pdf_payload(req)
        resolved_mime = (detected_mime or "").strip().lower()
        name_hint = (req.source_name or "").strip().lower()
        if resolved_mime and resolved_mime != "application/pdf":
            raise HTTPException(status_code=422, detail="PDF ingest expects application/pdf payload.")
        if not resolved_mime and not name_hint.endswith(".pdf"):
            raise HTTPException(
                status_code=422,
                detail="PDF ingest requires mime_type=application/pdf or a .pdf source_name.",
            )
        if b"%PDF" not in decoded[:1024]:
            raise HTTPException(status_code=422, detail="Invalid PDF payload header.")

        extracted_text = _extract_text_from_pdf_bytes(decoded)
        result_message_id: str | None = None
        if req.attach_to_chat:
            appended = deps.history_store.append_message(
                session_id=session_id,
                role="assistant",
                content=f"[PDF]\n{extracted_text}",
            )
            result_message_id = appended.message_id

        chunks = _chunk_text_for_vectors(extracted_text)
        if not chunks:
            raise HTTPException(status_code=422, detail="No extractable text found in PDF.")
        try:
            embeddings = _embed_texts(chunks, deps)
        except AuthenticationError as exc:
            raise HTTPException(status_code=401, detail="Authentication failed. Check OPENAI_API_KEY.") from exc
        except RateLimitError as exc:
            raise HTTPException(status_code=429, detail="Rate limit reached. Try PDF ingest again shortly.") from exc
        except APIConnectionError as exc:
            raise HTTPException(status_code=503, detail="Connection error reaching OpenAI embeddings API.") from exc
        except APIStatusError as exc:
            raise HTTPException(status_code=502, detail=f"OpenAI embeddings API error ({exc.status_code}).") from exc

        ingest_id = f"pdf-{uuid.uuid4().hex[:12]}"
        created_at = int(time.time() * 1000)
        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_ref = f"{ingest_id}:{index + 1}/{len(chunks)}"
            deps.vector_store.upsert_message_vector(
                session_id=session_id,
                role="assistant",
                message_id=None,
                content=chunk,
                embedding=embedding,
                source_type="pdf",
                source_ref=chunk_ref,
                metadata={
                    "source": "pdf",
                    "pdf_ingest_id": ingest_id,
                    "source_name": req.source_name,
                    "mime_type": resolved_mime or req.mime_type,
                    "source_message_id": req.source_message_id,
                    "result_message_id": result_message_id,
                    "chunk_index": index,
                    "chunk_count": len(chunks),
                },
                created_at=created_at,
            )

        _log_event(
            "pdf_ingest",
            request_id=getattr(request.state, "request_id", None),
            session_id=session_id,
            principal=principal,
            ingest_id=ingest_id,
            chars=len(extracted_text),
            vector_chunks=len(chunks),
            source_name=req.source_name,
        )
        return PdfIngestResponse(
            ingest_id=ingest_id,
            session_id=session_id,
            source_name=req.source_name,
            mime_type=resolved_mime or req.mime_type,
            status="ok",
            extracted_chars=len(extracted_text),
            vector_chunks=len(chunks),
            result_message_id=result_message_id,
            structured=_build_structured_extraction(
                source_type="pdf",
                source_name=req.source_name,
                mime_type=resolved_mime or req.mime_type,
                text=extracted_text,
            ),
        )

    @app.post("/skills/file_search", response_model=FileSearchResponse)
    def file_search(req: FileSearchRequest, request: Request) -> FileSearchResponse:
        principal = _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        if not deps.vector_enabled or deps.vector_store is None:
            raise HTTPException(status_code=503, detail="Vector memory is not enabled.")

        query = req.query.strip()
        source_types = _normalize_file_search_source_types(req.source_types)
        search_min_similarity = max(
            _FILE_SEARCH_MIN_SIMILARITY_FLOOR,
            deps.vector_min_similarity - 0.15,
        )
        candidate_limit = min(
            _FILE_SEARCH_MAX_CANDIDATES,
            max(req.limit * _FILE_SEARCH_CANDIDATE_MULTIPLIER, 40),
        )
        request_id = getattr(request.state, "request_id", None)

        try:
            query_vector = _embed_texts([query], deps)[0]
        except AuthenticationError as exc:
            raise HTTPException(status_code=401, detail="Authentication failed. Check OPENAI_API_KEY.") from exc
        except RateLimitError as exc:
            raise HTTPException(status_code=429, detail="Rate limit reached. Try file search again shortly.") from exc
        except APIConnectionError as exc:
            raise HTTPException(status_code=503, detail="Connection error reaching OpenAI embeddings API.") from exc
        except APIStatusError as exc:
            raise HTTPException(status_code=502, detail=f"OpenAI embeddings API error ({exc.status_code}).") from exc

        candidates = deps.vector_store.search(
            query_embedding=query_vector,
            limit=candidate_limit,
            min_similarity=search_min_similarity,
            roles=("assistant",),
            source_types=source_types,
        )
        query_tokens = _tokenize_file_search_text(query)
        ranked: list[tuple[float, float, float, VectorMatch]] = []
        for candidate in candidates:
            if req.session_id and candidate.session_id != req.session_id:
                continue
            keyword_score = _keyword_overlap_score(query_tokens, candidate.content)
            score = (candidate.similarity * 0.78) + (keyword_score * 0.22)
            ranked.append((score, candidate.similarity, keyword_score, candidate))

        ranked.sort(key=lambda item: (item[0], item[1], item[3].created_at), reverse=True)
        top = ranked[: req.limit]

        matches = [
            FileSearchMatchResponse(
                vector_id=candidate.vector_id,
                session_id=candidate.session_id,
                source_type=candidate.source_type,
                source_ref=candidate.source_ref,
                similarity=round(similarity, 4),
                keyword_score=round(keyword_score, 4),
                score=round(score, 4),
                snippet=_file_search_snippet(candidate.content, query_tokens),
                metadata=candidate.metadata,
            )
            for score, similarity, keyword_score, candidate in top
        ]

        _log_event(
            "file_search",
            request_id=request_id,
            principal=principal,
            session_id=req.session_id,
            source_types=list(source_types),
            query_chars=len(query),
            candidate_count=len(candidates),
            result_count=len(matches),
        )
        return FileSearchResponse(
            query=query,
            searched_at=int(time.time() * 1000),
            matches=matches,
        )

    @app.patch("/chats/{session_id}", response_model=ChatSummaryResponse)
    def rename_chat(session_id: str, req: RenameChatRequest, request: Request) -> ChatSummaryResponse:
        _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        try:
            summary = deps.history_store.rename_chat(session_id=session_id, title=req.title)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Chat not found.") from exc
        return _chat_summary_response(summary)

    @app.delete("/chats/{session_id}")
    async def delete_chat(session_id: str, request: Request) -> dict[str, str]:
        _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        try:
            deps.history_store.delete_chat(session_id=session_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Chat not found.") from exc
        if deps.vector_store is not None:
            deps.vector_store.delete_session(session_id)
        session = _session_for_request(request, session_id)
        try:
            await session.clear_session()
        finally:
            _close_session(session)
        return {"status": "ok", "session_id": session_id}

    @app.post("/chats/{session_id}/deprecate", response_model=ChatSummaryResponse)
    def deprecate_chat(session_id: str, request: Request) -> ChatSummaryResponse:
        _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        try:
            summary = deps.history_store.deprecate_chat(session_id=session_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Chat not found.") from exc
        if deps.vector_store is not None:
            deps.vector_store.deactivate_session(session_id)
        return _chat_summary_response(summary)

    @app.post("/chats/{session_id}/notes")
    def add_note(session_id: str, req: NoteRequest, request: Request) -> dict[str, str]:
        _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        deps.history_store.ensure_chat(session_id=session_id)
        deps.history_store.append_message(session_id=session_id, role="note", content=req.note.strip())
        return {"status": "ok", "session_id": session_id}

    @app.post("/chats/{session_id}/personalization", response_model=PersonalizationResponse)
    def set_chat_personalization(
        session_id: str,
        req: PersonalizationRequest,
        request: Request,
    ) -> PersonalizationResponse:
        principal = _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        chat = deps.history_store.ensure_chat(session_id=session_id)
        if chat.status == "deprecated":
            raise HTTPException(status_code=409, detail="Chat is deprecated and cannot be personalized.")
        try:
            settings = deps.history_store.set_personalization(
                session_id=session_id,
                memory_scope=req.memory_scope,
                updated_by=principal,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        _log_event(
            "personalization_updated",
            request_id=getattr(request.state, "request_id", None),
            principal=principal,
            session_id=session_id,
            memory_scope=settings.memory_scope,
        )
        return _personalization_response(settings)

    @app.get("/chats/{session_id}/personalization", response_model=PersonalizationResponse)
    def get_chat_personalization(session_id: str, request: Request) -> PersonalizationResponse:
        _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        chat = deps.history_store.get_chat(session_id=session_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found.")
        settings = deps.history_store.get_personalization(session_id=session_id)
        if settings is None:
            # No explicit override yet; reflect effective default scope.
            return PersonalizationResponse(
                session_id=session_id,
                memory_scope=deps.personalization_default_memory_scope,
                updated_at=chat.updated_at,
                updated_by=None,
            )
        return _personalization_response(settings)

    @app.get("/chats/{session_id}/collaboration", response_model=CollaborationResponse)
    def get_chat_collaboration(session_id: str, request: Request, limit: int = 20) -> CollaborationResponse:
        _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        chat = deps.history_store.get_chat(session_id=session_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found.")
        handoff_limit = max(1, min(limit, 100))
        state = deps.history_store.get_collaboration_state(session_id=session_id)
        handoffs = deps.history_store.list_handoffs(session_id=session_id, limit=handoff_limit)
        return CollaborationResponse(
            session_id=session_id,
            active=_collaboration_state_response(state) if state is not None else None,
            handoffs=[_collaboration_handoff_response(item) for item in handoffs],
        )

    @app.post("/chats/{session_id}/collaboration/handoff", response_model=CollaborationResponse)
    def handoff_chat_collaboration(
        session_id: str,
        req: CollaborationHandoffRequest,
        request: Request,
    ) -> CollaborationResponse:
        principal = _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        chat = deps.history_store.ensure_chat(session_id=session_id)
        if chat.status == "deprecated":
            raise HTTPException(status_code=409, detail="Chat is deprecated and cannot receive handoffs.")
        state, handoff = deps.history_store.handoff_collaboration(
            session_id=session_id,
            to_agent_id=req.to_agent_id,
            to_role=req.to_role,
            objective=req.objective,
            reason=req.reason,
            created_by=principal,
        )
        _log_event(
            "collaboration_handoff",
            request_id=getattr(request.state, "request_id", None),
            session_id=session_id,
            principal=principal,
            from_agent_id=handoff.from_agent_id,
            from_role=handoff.from_role,
            to_agent_id=handoff.to_agent_id,
            to_role=handoff.to_role,
        )
        return CollaborationResponse(
            session_id=session_id,
            active=_collaboration_state_response(state),
            handoffs=[_collaboration_handoff_response(handoff)],
        )

    @app.post("/chat", response_model=ChatResponse)
    async def chat(req: ChatRequest, request: Request) -> ChatResponse:
        principal = _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        session_id = req.session_id or deps.default_session_id
        chat = deps.history_store.ensure_chat(session_id=session_id)
        if chat.status == "deprecated":
            raise HTTPException(
                status_code=409,
                detail="Chat is deprecated. Create a new chat before sending messages.",
            )
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
        try:
            start = time.perf_counter()
            request_id = getattr(request.state, "request_id", None)
            notes = deps.history_store.list_notes(session_id=session_id, limit=8)
            personalization = deps.history_store.get_personalization(session_id=session_id)
            memory_scope = (
                personalization.memory_scope
                if personalization is not None
                else deps.personalization_default_memory_scope
            )
            collaboration_state = deps.history_store.get_collaboration_state(session_id=session_id)
            collaboration_note = _build_collaboration_note(collaboration_state)
            pipeline = "runner"
            orchestration_tools = 0
            retrieved_memory: list[VectorMatch] = []
            guardrail_note: str | None = None
            try:
                if deps.responses_orchestration_enabled:
                    pipeline = "responses"
                    guardrail_note = _build_hallucination_guardrail_note(
                        deps=deps,
                        query_text=req.message,
                        evidence_count=0,
                    )
                    output_text, orchestration_tools = _chat_with_responses_orchestration(
                        deps=deps,
                        request_id=request_id,
                        principal=principal,
                        session_id=session_id,
                        user_message=req.message,
                        notes=notes,
                        guardrail_note=guardrail_note,
                        collaboration_note=collaboration_note,
                    )
                else:
                    retrieved_memory = _retrieve_memory(
                        deps=deps,
                        session_id=session_id,
                        query_text=req.message,
                        memory_scope=memory_scope,
                    )
                    guardrail_note = _build_hallucination_guardrail_note(
                        deps=deps,
                        query_text=req.message,
                        evidence_count=len(retrieved_memory),
                    )
                    model_input = _compose_model_input(
                        user_message=req.message,
                        notes=notes,
                        retrieved_memory=retrieved_memory,
                        max_memory_chars=deps.vector_max_chars,
                        guardrail_note=guardrail_note,
                        collaboration_note=collaboration_note,
                    )
                    result = await Runner.run(
                        deps.agent,
                        model_input,
                        run_config=deps.run_config,
                        session=session,
                    )
                    output_text = str(result.final_output)
            except AuthenticationError as exc:
                _log_event(
                    "chat_error",
                    request_id=request_id,
                    session_id=session_id,
                    error_type="AuthenticationError",
                    pipeline=pipeline,
                )
                raise HTTPException(status_code=401, detail="Authentication failed. Check OPENAI_API_KEY.") from exc
            except RateLimitError as exc:
                _log_event(
                    "chat_error",
                    request_id=request_id,
                    session_id=session_id,
                    error_type="RateLimitError",
                    pipeline=pipeline,
                )
                raise HTTPException(status_code=429, detail="Rate limit reached. Try again shortly.") from exc
            except APIConnectionError as exc:
                _log_event(
                    "chat_error",
                    request_id=request_id,
                    session_id=session_id,
                    error_type="APIConnectionError",
                    pipeline=pipeline,
                )
                raise HTTPException(status_code=503, detail="Connection error reaching OpenAI API.") from exc
            except APIStatusError as exc:
                _log_event(
                    "chat_error",
                    request_id=request_id,
                    session_id=session_id,
                    error_type="APIStatusError",
                    status_code=exc.status_code,
                    pipeline=pipeline,
                )
                raise HTTPException(status_code=502, detail=f"OpenAI API error ({exc.status_code}).") from exc
            except RuntimeError as exc:
                _log_event(
                    "chat_error",
                    request_id=request_id,
                    session_id=session_id,
                    error_type="RuntimeError",
                    pipeline=pipeline,
                )
                raise HTTPException(status_code=503, detail=str(exc)) from exc

            response = ChatResponse(
                output=output_text,
                session_id=session_id,
                prompt_version=ACTIVE_PROMPT_VERSION,
            )
            deps.history_store.append_message(session_id=session_id, role="user", content=req.message)
            assistant_message = deps.history_store.append_message(
                session_id=session_id,
                role="assistant",
                content=response.output,
            )
            _index_assistant_output(
                deps=deps,
                session_id=session_id,
                message_id=assistant_message.message_id,
                content=assistant_message.content,
                created_at=assistant_message.created_at,
            )
            deps.history_store.maybe_set_title_from_first_user_message(
                session_id=session_id,
                user_message=req.message,
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
                vector_matches=len(retrieved_memory),
                memory_scope=memory_scope,
                guardrail_applied=guardrail_note is not None,
                collaboration_applied=collaboration_note is not None,
                active_collaborator=(
                    collaboration_state.active_agent_id if collaboration_state is not None else None
                ),
                pipeline=pipeline,
                orchestration_tools=orchestration_tools,
                duration_ms=duration_ms,
            )
            return response
        finally:
            _close_session(session)

    @app.post("/session/reset")
    async def reset_session(req: ResetRequest, request: Request) -> dict[str, str]:
        principal = _enforce_api_key(request)
        deps = _runtime_deps(request.app)
        session_id = req.session_id or deps.default_session_id
        deps.history_store.ensure_chat(session_id=session_id)
        session = _session_for_request(request, session_id)
        try:
            await session.clear_session()
        finally:
            _close_session(session)
        should_deprecate = req.deprecate or deps.deprecate_on_reset
        if should_deprecate:
            deps.history_store.deprecate_chat(session_id=session_id)
            if deps.vector_store is not None:
                deps.vector_store.deactivate_session(session_id)
            _log_event(
                "session_deprecated",
                request_id=getattr(request.state, "request_id", None),
                session_id=session_id,
                principal=principal,
            )
            return {"status": "ok", "session_id": session_id}

        deps.history_store.clear_messages(session_id=session_id)
        if deps.vector_store is not None:
            deps.vector_store.delete_session(session_id)
        _log_event(
            "session_reset",
            request_id=getattr(request.state, "request_id", None),
            session_id=session_id,
            principal=principal,
        )
        return {"status": "ok", "session_id": session_id}

    return app
