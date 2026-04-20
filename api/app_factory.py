import base64
import binascii
import hashlib
import json
import logging
import re
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, cast

from agents import Agent, Runner, RunConfig
from agents.memory import Session
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)
from pydantic import BaseModel, Field

from api.eval_viz import build_pass_fail_viz_payload, render_pass_fail_viz_html
from api.manual_evals_surface import build_manual_evals_surface_payload
from api.portfolio_sankey import build_portfolio_sankey_payload
from config import AppConfig
from core.history_store import (
    ChatHistoryStore,
    ChatSummary,
    OcrRun,
    EvalCheckpoint,
    CollaborationHandoff,
    CollaborationState,
    PersonalizationSettings,
    MessageFeedback,
    DEFAULT_CHAT_TITLE,
)
from core.prompts import ACTIVE_PROMPT, ACTIVE_PROMPT_VERSION
from core.rate_limit import SlidingWindowRateLimiter
from core.runtime import create_agent, create_run_config, create_session
from core.vector_store import VectorMatch, VectorStore


logger = logging.getLogger("polinko.api")


_PORTFOLIO_FALLBACK_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect width='16' height='16' rx='8' fill='%23262626'/%3E%3C/svg%3E">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700;800&display=swap">
  <title>Krystian Fernando</title>
  <style>
    :root {
      --paper: #fdfdfd;
      --ink: #262626;
      --muted: #686868;
      --font-main:
        "Instrument Sans",
        "Helvetica Neue",
        Helvetica,
        Arial,
        sans-serif;
      --page-inline: clamp(4.5rem, 8.8vw, 8rem);
      --page-block-start: clamp(3.5rem, 7vh, 5rem);
      background: var(--paper);
      color: var(--ink);
      font-family: var(--font-main);
    }

    *,
    *::before,
    *::after {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100svh;
      background: var(--paper);
      color: var(--ink);
      overflow-x: hidden;
    }

    .portal {
      min-height: 100svh;
      position: relative;
      padding: var(--page-block-start) var(--page-inline) 5.5rem;
    }

    main {
      bottom: 0;
      inline-size: calc(100% - (var(--page-inline) * 2));
      left: var(--page-inline);
      position: absolute;
      top: 0;
    }

    a {
      color: inherit;
    }

    .identity-menu {
      display: grid;
      justify-items: start;
      inline-size: max-content;
      left: var(--page-inline);
      position: absolute;
      top: clamp(4.9rem, 8.5svh, 5.5rem);
      z-index: 2;
    }

    .identity-name {
      color: var(--ink);
      font-family: var(--font-main);
      font-size: 0.9rem;
      font-style: normal;
      font-weight: 550;
      letter-spacing: 0.17em;
      line-height: 1;
      text-transform: uppercase;
      white-space: nowrap;
    }

    .because-link:focus-visible {
      outline: 1px solid currentColor;
      outline-offset: 6px;
    }

    .bio {
      display: flex;
      flex-direction: column;
      gap: 2.1rem;
      align-items: flex-start;
      bottom: var(--page-inline);
      inline-size: 100%;
      left: 0;
      position: absolute;
      top: auto;
    }

    .copy-block {
      display: grid;
      gap: 0.62rem;
      margin: 0;
    }

    .copy-line {
      color: var(--ink);
      font-family: var(--font-main);
      margin: 0;
      max-width: min(70vw, 56rem);
      font-size: 2.1875rem;
      font-style: normal;
      font-weight: 300;
      letter-spacing: 0;
      line-height: normal;
      text-wrap: pretty;
    }

    .compact-line {
      max-width: 18rem;
    }

    .because-link {
      color: var(--ink);
      display: inline-block;
      font-family: var(--font-main);
      margin: 0;
      position: relative;
      font-size: 2.1875rem;
      font-style: normal;
      font-weight: 500;
      letter-spacing: 0;
      line-height: normal;
      text-decoration: none;
      text-wrap: balance;
      transition:
        color 320ms cubic-bezier(0.22, 1, 0.36, 1),
        text-decoration-color 320ms cubic-bezier(0.22, 1, 0.36, 1);
    }

    .cta-stack {
      display: grid;
      gap: 0.65rem;
      inline-size: min(83vw, 64rem);
      margin-left: 0;
      padding-top: 1rem;
    }

    .because-link:hover,
    .because-link:focus-visible {
      color: #4a4a4a;
    }

    .because-text,
    .link-icon {
      text-decoration-line: underline;
      text-decoration-thickness: 1px;
      text-decoration-color: transparent;
      text-underline-offset: 0.16em;
      transition: text-decoration-color 320ms cubic-bezier(0.22, 1, 0.36, 1);
    }

    .because-link:hover .because-text,
    .because-link:hover .link-icon,
    .because-link:focus-visible .because-text,
    .because-link:focus-visible .link-icon {
      text-decoration-color: currentColor;
    }

    .repo-tooltip {
      color: #6b6b6b;
      display: inline-block;
      font-family: var(--font-main);
      font-size: clamp(1.3rem, 2vw, 1.75rem);
      font-weight: 500;
      line-height: 1.1;
      opacity: 0;
      pointer-events: none;
      text-decoration-line: underline;
      text-decoration-thickness: 1px;
      text-decoration-color: transparent;
      text-underline-offset: 0.16em;
      transform: translateY(-0.22rem);
      transition:
        color 320ms cubic-bezier(0.22, 1, 0.36, 1),
        opacity 360ms cubic-bezier(0.22, 1, 0.36, 1),
        text-decoration-color 320ms cubic-bezier(0.22, 1, 0.36, 1),
        transform 360ms cubic-bezier(0.22, 1, 0.36, 1);
    }

    .cta-stack:hover .repo-tooltip,
    .cta-stack:focus-within .repo-tooltip {
      color: #4a4a4a;
      opacity: 1;
      text-decoration-color: currentColor;
      transform: translateY(0);
    }

    @media (prefers-reduced-motion: reduce) {
      .because-link,
      .repo-tooltip {
        transition: none;
      }
    }

    .sr-only {
      block-size: 1px;
      clip: rect(0 0 0 0);
      clip-path: inset(50%);
      inline-size: 1px;
      overflow: hidden;
      position: absolute;
      white-space: nowrap;
    }

    .link-icon {
      display: inline-block;
      font-family:
        "Apple Symbols",
        "Segoe UI Symbol",
        "Noto Sans Symbols 2",
        "Noto Sans Symbols",
        sans-serif;
      font-size: 0.9em;
      font-style: normal;
      font-weight: 400;
      line-height: 1;
      margin-inline-start: 0.22em;
      text-decoration: none;
      text-transform: none;
      vertical-align: -0.08em;
      white-space: nowrap;
    }

    @media (max-width: 1180px) {
      :root {
        --page-inline: clamp(32px, 8vw, 96px);
      }

      .copy-line {
        font-size: clamp(1.75rem, 2.9vw, 2.1875rem);
        max-width: min(74vw, 54rem);
      }

      .because-link {
        font-size: clamp(1.75rem, 2.9vw, 2.1875rem);
      }

      .cta-stack {
        inline-size: min(82vw, 64rem);
        margin-left: 0;
      }
    }

    @media (min-width: 861px) {
      .because-link {
        text-wrap: nowrap;
        white-space: nowrap;
      }
    }

    @media (max-width: 860px) {
      :root {
        --page-inline: clamp(28px, 8vw, 56px);
        --page-block-start: 30px;
      }

      .portal {
        padding-block-start: var(--page-block-start);
        padding-inline: var(--page-inline);
      }

      .identity-menu {
        left: var(--page-inline);
        top: var(--page-block-start);
      }

      .identity-name {
        font-size: 1.16rem;
      }

      main {
        left: var(--page-inline);
        inline-size: calc(100% - (var(--page-inline) * 2));
        position: relative;
        top: auto;
        transform: none;
        padding-top: clamp(7rem, 18svh, 11rem);
      }

      .bio {
        position: static;
      }

      .bio {
        gap: 2rem;
      }

      .copy-line {
        font-size: clamp(1.3rem, 5.35vw, 1.85rem);
        font-weight: 400;
        line-height: normal;
        max-width: 100%;
      }

      .because-link {
        font-size: clamp(1.3rem, 5.35vw, 1.85rem);
        line-height: normal;
      }

      .cta-stack {
        inline-size: 100%;
        margin-left: 0;
      }
    }

    @media (max-height: 760px) and (min-width: 861px) {
      .bio {
        gap: 1.85rem;
      }

      .copy-line {
        font-size: 1.85rem;
      }

      .because-link {
        font-size: 1.85rem;
      }
    }
  </style>
</head>
<body>
  <div class="portal">
    <div class="identity-menu">
      <span class="identity-name">Krystian Fernando</span>
    </div>
    <main>
      <div class="bio">
        <section class="copy-block" aria-label="Origin and research focus">
          <p class="copy-line">
            design director who somehow became an AI&nbsp;research engineer
            after one idea came with its own hypothesis. so now i design evals around the useful signals that models reveal
            when they fail.
          </p>
        </section>
        <section class="copy-block" aria-label="Method">
          <p class="copy-line compact-line">for fun.</p>
        </section>
        <div class="cta-stack">
          <a
            class="because-link"
            href="https://github.com/tryskian/polinko"
            aria-describedby="repo-link-destination"
            aria-label="because every signal reshapes the experiment"
          >
            <span class="because-text">because every signal reshapes the experiment.</span> <span class="link-icon" aria-hidden="true">🡭</span>
          </a>
          <span class="repo-tooltip" aria-hidden="true">github.com/tryskian/polinko</span>
          <span id="repo-link-destination" class="sr-only">Opens the Polinko repository on GitHub.</span>
        </div>
      </div>
    </main>
  </div>
</body>
</html>
"""


_LATENCY_BUCKET_EDGES_MS = (10.0, 25.0, 50.0, 100.0, 250.0, 500.0, 1000.0, 2000.0)
_OCR_VECTOR_CHUNK_CHARS = 700
_OCR_VECTOR_CHUNK_OVERLAP = 120
_OCR_MAX_BYTES = 5 * 1024 * 1024
_PDF_MAX_BYTES = 10 * 1024 * 1024
_OCR_RETRY_AFTER_RATE_LIMIT_SECONDS = 10
_OCR_RETRY_AFTER_TRANSIENT_SECONDS = 3
_OCR_TEMPERATURE = 0.0
_OCR_TRANSCRIPTION_MODE_VERBATIM = "verbatim"
_OCR_TRANSCRIPTION_MODE_NORMALIZED = "normalized"
_OCR_TRANSCRIPTION_MODES = {
    _OCR_TRANSCRIPTION_MODE_VERBATIM,
    _OCR_TRANSCRIPTION_MODE_NORMALIZED,
}
_OCR_UNCERTAINTY_CUE_PHRASES = (
    "likely",
    "possibly",
    "maybe",
    "might be",
    "could be",
    "appears to",
    "seems to",
    "unclear",
    "illegible",
)
_OCR_QUOTED_ALTERNATIVES_RE = re.compile(
    r'[\"“][^\"”]{1,80}[\"”]\s*(?:or|/)\s*[\"“][^\"”]{1,80}[\"”]',
    flags=re.IGNORECASE,
)
_FILE_SEARCH_DEFAULT_SOURCE_TYPES = ("ocr",)
_FILE_SEARCH_ALLOWED_SOURCE_TYPES = {"chat", "ocr", "pdf", "image"}
_FILE_SEARCH_TOKEN_RE = re.compile(r"[a-z0-9]+")
_FILE_SEARCH_CANDIDATE_MULTIPLIER = 8
_FILE_SEARCH_MAX_CANDIDATES = 200
_FILE_SEARCH_MIN_SIMILARITY_FLOOR = 0.15
_RESPONSES_HISTORY_MAX_MESSAGE_CHARS = 550
_STRUCTURED_PREVIEW_MAX_CHARS = 240
_STRUCTURED_SOURCE_MAX_CHARS = 6000
_IMAGE_CONTEXT_MAX_CHARS = 1200
_CHAT_MEMORY_CITATION_MAX_CHARS = 180
_GLOBAL_MEMORY_LANE_SESSION_ID = "__global_memory__"
_DEFAULT_INTERNAL_STYLE_NOTES = (
    "Maintain a consistent voice across text, OCR, and image contexts.",
    "Avoid generic assistant openers or cheer phrases (for example: 'Clean catch', "
    "'Looks straightforward', 'Great question').",
    "For OCR/image evidence, stay literal and grounded; do not infer intent unless explicitly asked.",
)
_ADAPTIVE_STYLE_FEEDBACK_WINDOW = 16
_ADAPTIVE_STYLE_DECAY = 0.86
_ADAPTIVE_STYLE_GROUNDED_WEIGHT_THRESHOLD = 1.5
_ADAPTIVE_STYLE_HIGH_VALUE_WEIGHT_THRESHOLD = 1.5
_ADAPTIVE_STYLE_RISK_WEIGHT_THRESHOLD = 0.65
_ADAPTIVE_STYLE_MAX_ACTIVE_NOTES = 2
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
_FICTIONAL_QUERY_HINTS = (
    "fictional",
    "fictitious",
    "imaginary",
    "made-up",
    "made up",
)
_OCR_REQUEST_HINTS = (
    "ocr",
    "transcrib",
    "what is this word",
    "read this",
    "read that",
    "text says",
    "what does it say",
    "what does this say",
    "spell this",
)
_OCR_FOLLOWUP_HINTS = (
    "try again",
    "again",
    "without using memory",
    "no memory",
    "ocr again",
    "transcribe again",
    "read again",
    "retry ocr",
)
_OCR_CORRECTION_HINTS = (
    "incorrect",
    "wrong",
    "should be",
    "it should be",
    "it is",
    "it's",
    "that should be",
    "this should be",
    "not that",
    "no,",
)
_OCR_STRICT_NO_NEW_IMAGE_REPLY = (
    "No new image evidence in this turn. Attach a new image (or tighter crop) and "
    "I will transcribe only what is visible."
)
_FEEDBACK_TAG_MAX = 8
_FEEDBACK_TAG_LEN_MAX = 36
_FEEDBACK_NOTE_LEN_MAX = 1200
_EVAL_CHECKPOINT_SCHEMA_VERSION = "polinko.eval_checkpoint.v2"
_FEEDBACK_POSITIVE_TAGS = {
    "accurate",
    "high_value",
    "medium_value",
    "low_value",
    "recovered",
    "ocr_accurate",
    "grounded",
    "style",
    "complete",
    "useful",
}
_FEEDBACK_NEGATIVE_TAGS = {
    "ocr_miss",
    "grounding_gap",
    "style_mismatch",
    "default_style",
    "em_dash_style",
    "hallucination_risk",
    "needs_retry",
}
_FEEDBACK_PASS_SOFT_NEGATIVE_TAGS: set[str] = {
    "default_style",
}


def _default_latency_buckets() -> dict[str, int]:
    buckets = {f"le_{int(edge)}ms": 0 for edge in _LATENCY_BUCKET_EDGES_MS}
    buckets["gt_2000ms"] = 0
    return buckets


_EXTRACTION_STRUCTURED_REQUIRED_FIELDS = [
    "schema_version",
    "source_type",
    "source_name",
    "mime_type",
    "text_sha256",
    "char_count",
    "word_count",
    "line_count",
    "preview",
]

_EXTRACTION_STRUCTURED_COMMON_PROPERTIES: dict[str, object] = {
    "schema_version": {"type": "string", "const": "v1"},
    "source_type": {"type": "string"},
    "source_name": {"type": ["string", "null"]},
    "mime_type": {"type": ["string", "null"]},
    "text_sha256": {"type": "string"},
    "char_count": {"type": "integer", "minimum": 0},
    "word_count": {"type": "integer", "minimum": 0},
    "line_count": {"type": "integer", "minimum": 0},
    "preview": {"type": "string"},
}

_EXTRACTION_STRUCTURED_OCR_JSON_SCHEMA: dict[str, object] = {
    "type": "object",
    "additionalProperties": False,
    "required": _EXTRACTION_STRUCTURED_REQUIRED_FIELDS,
    "properties": {
        **_EXTRACTION_STRUCTURED_COMMON_PROPERTIES,
        "source_type": {"type": "string", "const": "ocr"},
    },
}

_EXTRACTION_STRUCTURED_PDF_JSON_SCHEMA: dict[str, object] = {
    "type": "object",
    "additionalProperties": False,
    "required": _EXTRACTION_STRUCTURED_REQUIRED_FIELDS,
    "properties": {
        **_EXTRACTION_STRUCTURED_COMMON_PROPERTIES,
        "source_type": {"type": "string", "const": "pdf"},
        "mime_type": {"type": ["string", "null"], "const": "application/pdf"},
    },
}

_EXTRACTION_STRUCTURED_DEFAULT_JSON_SCHEMA: dict[str, object] = {
    "type": "object",
    "additionalProperties": False,
    "required": _EXTRACTION_STRUCTURED_REQUIRED_FIELDS,
    "properties": _EXTRACTION_STRUCTURED_COMMON_PROPERTIES,
}


def _latency_bucket_label(duration_ms: float) -> str:
    for edge in _LATENCY_BUCKET_EDGES_MS:
        if duration_ms <= edge:
            return f"le_{int(edge)}ms"
    return "gt_2000ms"


def _structured_schema_for_source_type(source_type: str) -> tuple[str, dict[str, object]]:
    normalized = source_type.strip().lower()
    if normalized == "ocr":
        return ("extraction_structured_ocr_v1", _EXTRACTION_STRUCTURED_OCR_JSON_SCHEMA)
    if normalized == "pdf":
        return ("extraction_structured_pdf_v1", _EXTRACTION_STRUCTURED_PDF_JSON_SCHEMA)
    return ("extraction_structured_v1", _EXTRACTION_STRUCTURED_DEFAULT_JSON_SCHEMA)


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
    rate_limit_per_minute: int
    rate_limiter: SlidingWindowRateLimiter
    deprecate_on_reset: bool
    ocr_provider: str
    ocr_model: str
    ocr_prompt: str
    ocr_uncertainty_safe: bool
    image_context_enabled: bool
    image_context_model: str
    image_context_prompt: str
    ocr_client: OpenAI | None
    vector_enabled: bool
    vector_top_k: int
    vector_top_k_global: int
    vector_top_k_session: int
    vector_min_similarity: float
    vector_min_similarity_global: float
    vector_min_similarity_session: float
    vector_max_chars: int
    vector_exclude_current_session: bool
    vector_local_embedding_fallback: bool
    vector_embedding_model: str
    vector_store: VectorStore | None
    embedding_client: OpenAI | None
    responses_orchestration_enabled: bool
    responses_orchestration_model: str
    responses_vector_store_id: str | None
    responses_include_web_search: bool
    responses_history_turn_limit: int
    responses_pdf_ingest_enabled: bool
    responses_client: OpenAI | None
    extraction_structured_enabled: bool
    extraction_structured_model: str
    governance_enabled: bool
    governance_allow_web_search: bool
    governance_log_only: bool
    hallucination_guardrails_enabled: bool
    personalization_default_memory_scope: str
    clip_proxy_file_search_enabled: bool
    chat_harness_default_mode: Literal["live", "fixture"]
    metrics: RuntimeMetrics
    run_config: RunConfig
    agent: Agent[Any]
    adaptive_note_signatures: dict[str, tuple[str, ...]] = field(default_factory=dict)


class ChatAttachment(BaseModel):
    data_base64: str = Field(..., min_length=1, description="Attachment payload as data URL or base64.")
    source_name: str | None = Field(default=None, max_length=255)
    mime_type: str | None = Field(default=None, max_length=120)
    text_hint: str | None = None
    visual_context_hint: str | None = None
    transcription_mode: str = Field(default=_OCR_TRANSCRIPTION_MODE_VERBATIM, pattern="^(verbatim|normalized)$")
    memory_scope: str = Field(default="session", pattern="^(global|session)$")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message.")
    session_id: str | None = Field(default=None, min_length=1, description="Conversation session ID.")
    attachments: list[ChatAttachment] = Field(default_factory=list)
    source_user_message_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        description="Existing user message id to branch assistant variants from (retry flow).",
    )
    harness_mode: Literal["live", "fixture"] | None = Field(
        default=None,
        description="Optional chat harness mode override. fixture returns deterministic local output.",
    )
    fixture_output: str | None = Field(
        default=None,
        max_length=6000,
        description="Optional deterministic output used when harness_mode=fixture.",
    )


class ChatResponse(BaseModel):
    output: str
    session_id: str
    assistant_message_id: str | None = None
    prompt_version: str
    memory_scope: str
    context_scope: str = Field(..., pattern="^(global|local)$")
    memory_used: list["MemoryCitationResponse"] = Field(default_factory=list)


class MemoryCitationResponse(BaseModel):
    vector_id: str
    session_id: str
    source_type: str
    source_ref: str | None
    similarity: float
    snippet: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ResetRequest(BaseModel):
    session_id: str | None = Field(default=None, min_length=1)
    deprecate: bool = False


class ChatSummaryResponse(BaseModel):
    session_id: str
    title: str
    created_at: int
    updated_at: int
    message_count: int
    memory_scope: str
    context_scope: str = Field(..., pattern="^(global|local)$")
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
    memory_scope: str
    context_scope: str = Field(..., pattern="^(global|local)$")
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


class MessageFeedbackRequest(BaseModel):
    message_id: str = Field(..., min_length=1, max_length=120)
    outcome: str = Field(..., min_length=1, max_length=12)
    positive_tags: list[str] = Field(default_factory=list)
    negative_tags: list[str] = Field(default_factory=list)
    note: str | None = Field(default=None, max_length=_FEEDBACK_NOTE_LEN_MAX)
    action_taken: str | None = Field(default=None, max_length=_FEEDBACK_NOTE_LEN_MAX)


class MessageFeedbackResponse(BaseModel):
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


class ChatFeedbackResponse(BaseModel):
    session_id: str
    feedback: list[MessageFeedbackResponse]


class EvalCheckpointResponse(BaseModel):
    checkpoint_id: str
    session_id: str
    total_count: int
    pass_count: int
    fail_count: int
    non_binary_count: int
    gate_outcome: Literal["pass", "fail"]
    schema_version: str
    created_at: int


class ChatEvalCheckpointsResponse(BaseModel):
    session_id: str
    checkpoints: list[EvalCheckpointResponse]


class OcrRequest(BaseModel):
    session_id: str | None = Field(default=None, min_length=1)
    source_name: str | None = Field(default=None, max_length=255)
    mime_type: str | None = Field(default=None, max_length=120)
    data_base64: str | None = None
    text_hint: str | None = None
    visual_context_hint: str | None = None
    source_message_id: str | None = None
    transcription_mode: str = Field(default=_OCR_TRANSCRIPTION_MODE_VERBATIM, pattern="^(verbatim|normalized)$")
    memory_scope: str = Field(default="session", pattern="^(global|session)$")
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
    visual_context: str | None = None
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
    responses_index_status: Literal["disabled", "indexed", "failed"] = "disabled"
    responses_index_reason: str | None = None
    responses_vector_store_file_id: str | None = None
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
    enrichment_status: Literal["baseline", "enriched", "fallback"] = "baseline"
    fallback_reason: str | None = None


class FileSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    session_id: str | None = Field(default=None, min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
    source_types: list[str] | None = None
    retrieval_profile: Literal["default", "clip_proxy_image_only"] = "default"


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
    backend: Literal["responses_vector_store", "local_vector_store"]
    fallback_reason: str | None = None
    candidate_count: int | None = None
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


def _resolve_chat_memory_scope(*, deps: RuntimeDeps, session_id: str) -> str:
    settings = deps.history_store.get_personalization(session_id=session_id)
    if settings is None:
        return _normalize_memory_scope(deps.personalization_default_memory_scope, default="global")
    return _normalize_memory_scope(settings.memory_scope, default="global")


def _context_scope_from_memory_scope(memory_scope: str) -> str:
    normalized_scope = _normalize_memory_scope(memory_scope, default="global")
    return "local" if normalized_scope == "session" else "global"


def _build_fixture_chat_output(*, message: str, fixture_output: str | None) -> str:
    override = (fixture_output or "").strip()
    if override:
        return override
    prompt = message.strip() or "<empty>"
    return f"[fixture] deterministic response for: {prompt}"


def _chat_summary_response(summary: ChatSummary, *, deps: RuntimeDeps) -> ChatSummaryResponse:
    memory_scope = _resolve_chat_memory_scope(deps=deps, session_id=summary.session_id)
    return ChatSummaryResponse(
        session_id=summary.session_id,
        title=summary.title,
        created_at=summary.created_at,
        updated_at=summary.updated_at,
        message_count=summary.message_count,
        memory_scope=memory_scope,
        context_scope=_context_scope_from_memory_scope(memory_scope),
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


def _message_feedback_response(entry: MessageFeedback) -> MessageFeedbackResponse:
    return MessageFeedbackResponse(
        session_id=entry.session_id,
        message_id=entry.message_id,
        outcome=_feedback_outcome_for_response(entry.outcome),
        positive_tags=list(entry.positive_tags),
        negative_tags=list(entry.negative_tags),
        tags=list(entry.tags),
        note=entry.note,
        recommended_action=entry.recommended_action,
        action_taken=entry.action_taken,
        status=entry.status.lower(),
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


def _eval_checkpoint_response(entry: EvalCheckpoint) -> EvalCheckpointResponse:
    return EvalCheckpointResponse(
        checkpoint_id=entry.checkpoint_id,
        session_id=entry.session_id,
        total_count=entry.total_count,
        pass_count=entry.pass_count,
        fail_count=entry.fail_count,
        non_binary_count=entry.non_binary_count,
        gate_outcome=_checkpoint_gate_outcome(
            total_count=entry.total_count,
            fail_count=entry.fail_count,
            non_binary_count=entry.non_binary_count,
        ),
        schema_version=_EVAL_CHECKPOINT_SCHEMA_VERSION,
        created_at=entry.created_at,
    )


def _normalize_feedback_outcome(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in {"pass", "fail"}:
        raise HTTPException(status_code=400, detail="outcome must be 'pass' or 'fail'.")
    return normalized


def _feedback_outcome_for_response(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in {"pass", "fail"}:
        raise ValueError("Stored feedback outcome must be pass or fail.")
    return normalized


def _normalize_feedback_tag_list(tags: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in tags:
        tag = " ".join(raw.strip().lower().split())
        if not tag:
            continue
        tag = re.sub(r"[^a-z0-9 _-]+", "", tag).strip(" _-")
        if not tag:
            continue
        if len(tag) > _FEEDBACK_TAG_LEN_MAX:
            tag = tag[:_FEEDBACK_TAG_LEN_MAX].rstrip()
        if tag not in seen:
            normalized.append(tag)
            seen.add(tag)
        if len(normalized) >= _FEEDBACK_TAG_MAX:
            break
    return normalized


def _normalize_feedback_tags(
    *,
    outcome: str,
    positive_tags: list[str],
    negative_tags: list[str],
) -> tuple[list[str], list[str], list[str]]:
    normalized_positive = _normalize_feedback_tag_list(positive_tags)
    normalized_negative = _normalize_feedback_tag_list(negative_tags)

    invalid_positive = [tag for tag in normalized_positive if tag not in _FEEDBACK_POSITIVE_TAGS]
    if invalid_positive:
        invalid_text = ", ".join(invalid_positive)
        allowed_text = ", ".join(sorted(_FEEDBACK_POSITIVE_TAGS))
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported positive reason tag(s): {invalid_text}. Allowed: {allowed_text}.",
        )
    invalid_negative = [tag for tag in normalized_negative if tag not in _FEEDBACK_NEGATIVE_TAGS]
    if invalid_negative:
        invalid_text = ", ".join(invalid_negative)
        allowed_text = ", ".join(sorted(_FEEDBACK_NEGATIVE_TAGS))
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported negative reason tag(s): {invalid_text}. Allowed: {allowed_text}.",
        )

    if outcome == "pass":
        if not normalized_positive:
            raise HTTPException(status_code=400, detail="Pass requires at least one positive reason tag.")
        disallowed_negative = [
            tag for tag in normalized_negative if tag not in _FEEDBACK_PASS_SOFT_NEGATIVE_TAGS
        ]
        if disallowed_negative:
            disallowed_text = ", ".join(disallowed_negative)
            raise HTTPException(
                status_code=400,
                detail=f"Pass cannot include negative reason tags: {disallowed_text}.",
            )
    elif outcome == "fail":
        if not normalized_negative:
            raise HTTPException(status_code=400, detail="Fail requires at least one negative reason tag.")
    normalized_tags = list(dict.fromkeys(normalized_positive + normalized_negative))
    return normalized_positive, normalized_negative, normalized_tags


def _suggest_feedback_action(
    *,
    outcome: str,
    positive_tags: list[str],
    negative_tags: list[str],
    note: str | None,
) -> str | None:
    del positive_tags
    if outcome == "pass" or not negative_tags:
        return None
    tag_text = " ".join(negative_tags)
    note_text = (note or "").lower()
    probe = f"{tag_text} {note_text}"
    if any(token in probe for token in ("ocr", "transcrib", "handwriting", "image")):
        return "Retry OCR with a tighter crop and attach fresh image evidence for comparison."
    if any(token in probe for token in ("ground", "halluc", "citation", "factual")):
        return "Re-run with explicit grounding constraints and verify response against source evidence."
    if any(token in probe for token in ("retrieval", "search", "memory", "recall")):
        return "Seed missing context and re-run retrieval/file-search checks for this exact prompt."
    if any(token in probe for token in ("style", "tone", "voice")):
        return "Adjust style notes and add this sample to style eval regression cases."
    return "Capture expected vs actual output, then run the closest eval harness and record remediation."


def _feedback_status_for_outcome(outcome: str) -> str:
    return "closed" if outcome == "pass" else "open"


def _summarize_feedback_streams(entries: list[MessageFeedback]) -> tuple[int, int, int, int]:
    total_count = len(entries)
    pass_count = 0
    fail_count = 0
    non_binary_count = 0
    for entry in entries:
        outcome = entry.outcome.strip().lower()
        if outcome == "pass":
            pass_count += 1
        elif outcome == "fail":
            fail_count += 1
        else:
            non_binary_count += 1
    return total_count, pass_count, fail_count, non_binary_count


def _checkpoint_gate_outcome(
    *, total_count: int, fail_count: int, non_binary_count: int
) -> Literal["pass", "fail"]:
    if total_count <= 0:
        return "fail"
    if fail_count > 0 or non_binary_count > 0:
        return "fail"
    return "pass"


def _normalize_note_text(note: str) -> str:
    compact = re.sub(r"[^a-z0-9\s]+", " ", note.lower())
    return " ".join(compact.split())


def _notes_are_near_duplicate(a: str, b: str) -> bool:
    norm_a = _normalize_note_text(a)
    norm_b = _normalize_note_text(b)
    if not norm_a or not norm_b:
        return False
    if norm_a == norm_b:
        return True
    if len(norm_a) >= 24 and (norm_a in norm_b or norm_b in norm_a):
        return True
    tokens_a = set(norm_a.split())
    tokens_b = set(norm_b.split())
    if not tokens_a or not tokens_b:
        return False
    overlap = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)
    if union <= 0:
        return False
    jaccard = overlap / union
    return overlap >= 6 and jaccard >= 0.68


def _append_unique_note(target: list[str], candidate: str) -> bool:
    if not candidate.strip():
        return False
    for existing in target:
        if _notes_are_near_duplicate(existing, candidate):
            return False
    target.append(candidate)
    return True


def _derive_adaptive_style_notes(feedback_entries: list[MessageFeedback]) -> list[str]:
    if not feedback_entries:
        return []
    style_entries = [
        entry
        for entry in feedback_entries[:_ADAPTIVE_STYLE_FEEDBACK_WINDOW]
        if "style" in entry.positive_tags and "style_mismatch" not in entry.negative_tags
    ]
    if not style_entries:
        return []

    grounded_weight = 0.0
    high_value_weight = 0.0
    risk_weight = 0.0
    recovered_weight = 0.0

    for idx, entry in enumerate(style_entries):
        weight = _ADAPTIVE_STYLE_DECAY**idx
        outcome = entry.outcome.strip().lower()
        is_clean_grounded_pass = (
            outcome == "pass"
            and "grounded" in entry.positive_tags
            and "hallucination_risk" not in entry.negative_tags
            and "grounding_gap" not in entry.negative_tags
        )
        if is_clean_grounded_pass:
            grounded_weight += weight
        if (
            outcome == "pass"
            and "high_value" in entry.positive_tags
            and "hallucination_risk" not in entry.negative_tags
        ):
            high_value_weight += weight
        if "hallucination_risk" in entry.negative_tags:
            risk_weight += weight
        if is_clean_grounded_pass and "recovered" in entry.positive_tags:
            recovered_weight += weight

    scored_candidates: list[tuple[float, str]] = []
    if grounded_weight >= _ADAPTIVE_STYLE_GROUNDED_WEIGHT_THRESHOLD:
        scored_candidates.append(
            (
                grounded_weight,
                "Soft style target: mirror the user's language and continue active metaphors before introducing new framing.",
            )
        )
    if high_value_weight >= _ADAPTIVE_STYLE_HIGH_VALUE_WEIGHT_THRESHOLD:
        scored_candidates.append(
            (
                high_value_weight,
                "Soft style target: keep replies concise (usually 1-3 sentences), vivid, and continuity-first.",
            )
        )
    if risk_weight >= _ADAPTIVE_STYLE_RISK_WEIGHT_THRESHOLD and recovered_weight < risk_weight:
        scored_candidates.append(
            (
                risk_weight,
                "Soft style guardrail: if specifics are uncertain, use one brief uncertainty clause, then continue in the user's tone without guessing.",
            )
        )
    if recovered_weight >= _ADAPTIVE_STYLE_RISK_WEIGHT_THRESHOLD:
        scored_candidates.append(
            (
                recovered_weight + 0.05,
                "Soft style recovery: after a brief uncertainty clause, return to natural cadence and metaphor continuity.",
            )
        )

    scored_candidates.sort(key=lambda item: item[0], reverse=True)
    selected: list[str] = []
    for _score, note in scored_candidates:
        if _append_unique_note(selected, note) and len(selected) >= _ADAPTIVE_STYLE_MAX_ACTIVE_NOTES:
            break
    return selected


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _build_ingest_dedup_key(
    *,
    operation: str,
    principal: str | None,
    session_id: str,
    payload: dict[str, Any],
) -> str:
    canonical_payload = {
        "principal": principal or "",
        "session_id": session_id,
        "operation": operation,
        **payload,
    }
    canonical = json.dumps(canonical_payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return f"{operation}:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"


def _build_ocr_dedup_key(
    *,
    req: OcrRequest,
    deps: RuntimeDeps,
    principal: str | None,
    session_id: str,
) -> str:
    payload: dict[str, Any] = {
        "source_name": req.source_name,
        "mime_type": (req.mime_type or "").strip().lower() or None,
        "source_message_id": req.source_message_id,
        "text_hint": req.text_hint,
        "visual_context_hint": req.visual_context_hint,
        "transcription_mode": req.transcription_mode,
        "memory_scope": _normalize_memory_scope(req.memory_scope, default="session"),
        "attach_to_chat": bool(req.attach_to_chat),
        "ocr_provider": deps.ocr_provider,
        "ocr_model": deps.ocr_model,
        "ocr_prompt_sha256": _sha256_text(deps.ocr_prompt),
        "image_context_enabled": bool(deps.image_context_enabled),
        "image_context_model": deps.image_context_model,
        "image_context_prompt_sha256": _sha256_text(deps.image_context_prompt),
    }
    if req.data_base64 and req.data_base64.strip():
        decoded, detected_mime = _decode_base64_payload(req)
        payload["data_sha256"] = _sha256_bytes(decoded)
        payload["detected_mime_type"] = (detected_mime or "").strip().lower() or None
    return _build_ingest_dedup_key(
        operation="ocr",
        principal=principal,
        session_id=session_id,
        payload=payload,
    )


def _build_pdf_ingest_dedup_key(
    *,
    req: PdfIngestRequest,
    deps: RuntimeDeps,
    principal: str | None,
    session_id: str,
    payload_bytes: bytes,
    resolved_mime_type: str | None,
) -> str:
    return _build_ingest_dedup_key(
        operation="pdf_ingest",
        principal=principal,
        session_id=session_id,
        payload={
            "source_name": req.source_name,
            "mime_type": (req.mime_type or "").strip().lower() or None,
            "resolved_mime_type": resolved_mime_type,
            "source_message_id": req.source_message_id,
            "attach_to_chat": bool(req.attach_to_chat),
            "data_sha256": _sha256_bytes(payload_bytes),
            "vector_embedding_model": deps.vector_embedding_model,
            "extraction_structured_enabled": bool(deps.extraction_structured_enabled),
            "extraction_structured_model": deps.extraction_structured_model,
            "responses_pdf_ingest_enabled": bool(deps.responses_pdf_ingest_enabled),
            "responses_vector_store_id": deps.responses_vector_store_id,
        },
    )


def _normalize_preview_text(value: str, *, max_chars: int) -> str:
    compact = " ".join(value.split()).strip()
    if len(compact) <= max_chars:
        return compact
    if max_chars <= 3:
        return compact[:max_chars]
    return compact[: max_chars - 3].rstrip() + "..."


def _compact_for_citation(value: str, *, max_chars: int) -> str:
    compact = " ".join(value.split())
    if len(compact) > max_chars:
        return f"{compact[:max_chars].rstrip()}..."
    return compact


def _normalize_memory_scope(value: str | None, *, default: str = "global") -> str:
    normalized = (value or default).strip().lower()
    if normalized == "session":
        return "session"
    return "global"


def _resolve_memory_lane_session_id(*, session_id: str, memory_scope: str) -> str:
    scope = _normalize_memory_scope(memory_scope, default="global")
    if scope == "session":
        return session_id
    return _GLOBAL_MEMORY_LANE_SESSION_ID


def _display_session_id(*, session_id: str, metadata: dict[str, Any]) -> str:
    if session_id != _GLOBAL_MEMORY_LANE_SESSION_ID:
        return session_id
    origin_session = metadata.get("origin_session_id")
    if isinstance(origin_session, str) and origin_session.strip():
        return origin_session.strip()
    return session_id


def _memory_citation_response(item: VectorMatch, *, max_chars: int) -> MemoryCitationResponse:
    metadata = dict(item.metadata)
    return MemoryCitationResponse(
        vector_id=item.vector_id,
        session_id=_display_session_id(session_id=item.session_id, metadata=metadata),
        source_type=item.source_type,
        source_ref=item.source_ref,
        similarity=round(float(item.similarity), 4),
        snippet=_compact_for_citation(item.content, max_chars=max_chars),
        metadata=metadata,
    )


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
        visual_context=None,
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
    deps: RuntimeDeps | None = None,
    request_id: str | None = None,
    session_id: str | None = None,
    principal: str | None = None,
) -> ExtractionStructuredResponse:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line for line in (chunk.strip() for chunk in normalized.split("\n")) if line]
    compact_preview = _normalize_preview_text(normalized, max_chars=_STRUCTURED_PREVIEW_MAX_CHARS)
    base = ExtractionStructuredResponse(
        schema_version="v1",
        source_type=source_type,
        source_name=source_name,
        mime_type=mime_type,
        text_sha256=_sha256_text(text),
        char_count=len(text),
        word_count=len([word for word in normalized.split() if word]),
        line_count=len(lines),
        preview=compact_preview,
        enrichment_status="baseline",
        fallback_reason=None,
    )
    if (
        deps is None
        or not deps.extraction_structured_enabled
        or deps.responses_client is None
    ):
        return base
    responses_client = deps.responses_client

    source_snippet = text[:_STRUCTURED_SOURCE_MAX_CHARS]
    schema_name, schema_payload = _structured_schema_for_source_type(source_type=source_type)
    prompt = (
        "Return a strict JSON object matching the provided schema. "
        "Preserve metadata values exactly. Improve only preview readability.\n\n"
        f"schema_version: {base.schema_version}\n"
        f"source_type: {base.source_type}\n"
        f"source_name: {base.source_name!r}\n"
        f"mime_type: {base.mime_type!r}\n"
        f"text_sha256: {base.text_sha256}\n"
        f"char_count: {base.char_count}\n"
        f"word_count: {base.word_count}\n"
        f"line_count: {base.line_count}\n"
        f"default_preview: {base.preview}\n\n"
        "[SOURCE_TEXT]\n"
        f"{source_snippet}"
    )
    try:
        response = responses_client.responses.create(
            model=deps.extraction_structured_model,
            input=prompt,
            text=cast(
                Any,
                {
                    "format": {
                        "type": "json_schema",
                        "name": schema_name,
                        "strict": True,
                        "schema": schema_payload,
                    }
                },
            ),
        )
        payload = json.loads(_extract_responses_output_text(response))
        if not isinstance(payload, dict):
            raise ValueError("Structured extraction payload must be a JSON object.")
        model_structured = ExtractionStructuredResponse.model_validate(payload)
        metadata_fields = (
            "schema_version",
            "source_type",
            "source_name",
            "mime_type",
            "text_sha256",
            "char_count",
            "word_count",
            "line_count",
        )
        metadata_mismatch = [
            field_name
            for field_name in metadata_fields
            if getattr(model_structured, field_name) != getattr(base, field_name)
        ]
        if metadata_mismatch:
            _log_event(
                "structured_extraction_fallback",
                request_id=request_id,
                session_id=session_id,
                principal=principal,
                source_type=source_type,
                reason="metadata_mismatch",
                mismatch_fields=",".join(metadata_mismatch),
            )
            return base.model_copy(
                update={
                    "enrichment_status": "fallback",
                    "fallback_reason": "metadata_mismatch",
                }
            )
        preview = _normalize_preview_text(model_structured.preview, max_chars=_STRUCTURED_PREVIEW_MAX_CHARS)
        if not preview:
            preview = base.preview
        _log_event(
            "structured_extraction_enriched",
            request_id=request_id,
            session_id=session_id,
            principal=principal,
            source_type=source_type,
        )
        return base.model_copy(
            update={
                "preview": preview,
                "enrichment_status": "enriched",
                "fallback_reason": None,
            }
        )
    except (json.JSONDecodeError, ValueError, TypeError):
        _log_event(
            "structured_extraction_fallback",
            request_id=request_id,
            session_id=session_id,
            principal=principal,
            source_type=source_type,
            reason="invalid_json",
        )
        return base.model_copy(
            update={
                "enrichment_status": "fallback",
                "fallback_reason": "invalid_json",
            }
        )
    except (AuthenticationError, RateLimitError, APIConnectionError, APIStatusError):
        _log_event(
            "structured_extraction_fallback",
            request_id=request_id,
            session_id=session_id,
            principal=principal,
            source_type=source_type,
            reason="responses_error",
        )
        return base.model_copy(
            update={
                "enrichment_status": "fallback",
                "fallback_reason": "responses_error",
            }
        )
    except Exception:
        _log_event(
            "structured_extraction_fallback",
            request_id=request_id,
            session_id=session_id,
            principal=principal,
            source_type=source_type,
            reason="unexpected_error",
        )
        return base.model_copy(
            update={
                "enrichment_status": "fallback",
                "fallback_reason": "unexpected_error",
            }
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


def _index_pdf_in_responses_vector_store(
    *,
    deps: RuntimeDeps,
    request_id: str | None,
    session_id: str,
    principal: str | None,
    ingest_id: str,
    source_name: str | None,
    payload: bytes,
) -> tuple[Literal["disabled", "indexed", "failed"], str | None, str | None]:
    if not deps.responses_pdf_ingest_enabled:
        return "disabled", "feature_disabled", None
    if deps.responses_client is None or not deps.responses_vector_store_id:
        return "disabled", "not_configured", None

    from io import BytesIO

    file_name = (source_name or "").strip() or f"{ingest_id}.pdf"
    if not file_name.lower().endswith(".pdf"):
        file_name = f"{file_name}.pdf"
    upload_payload = BytesIO(payload)
    setattr(upload_payload, "name", file_name)

    try:
        vector_file = deps.responses_client.vector_stores.files.upload_and_poll(
            vector_store_id=deps.responses_vector_store_id,
            file=upload_payload,
        )
    except AuthenticationError as exc:
        _log_event(
            "pdf_ingest_responses_index_failed",
            request_id=request_id,
            session_id=session_id,
            principal=principal,
            ingest_id=ingest_id,
            reason="authentication_error",
            error_type=type(exc).__name__,
        )
        return "failed", "authentication_error", None
    except RateLimitError as exc:
        _log_event(
            "pdf_ingest_responses_index_failed",
            request_id=request_id,
            session_id=session_id,
            principal=principal,
            ingest_id=ingest_id,
            reason="rate_limited",
            error_type=type(exc).__name__,
        )
        return "failed", "rate_limited", None
    except APIConnectionError as exc:
        _log_event(
            "pdf_ingest_responses_index_failed",
            request_id=request_id,
            session_id=session_id,
            principal=principal,
            ingest_id=ingest_id,
            reason="connection_error",
            error_type=type(exc).__name__,
        )
        return "failed", "connection_error", None
    except APIStatusError as exc:
        _log_event(
            "pdf_ingest_responses_index_failed",
            request_id=request_id,
            session_id=session_id,
            principal=principal,
            ingest_id=ingest_id,
            reason=f"api_status_{exc.status_code}",
            error_type=type(exc).__name__,
        )
        return "failed", f"api_status_{exc.status_code}", None
    except Exception as exc:
        _log_event(
            "pdf_ingest_responses_index_failed",
            request_id=request_id,
            session_id=session_id,
            principal=principal,
            ingest_id=ingest_id,
            reason="unexpected_error",
            error_type=type(exc).__name__,
        )
        return "failed", "unexpected_error", None

    vector_file_id = getattr(vector_file, "id", None)
    if not isinstance(vector_file_id, str) or not vector_file_id:
        _log_event(
            "pdf_ingest_responses_index_failed",
            request_id=request_id,
            session_id=session_id,
            principal=principal,
            ingest_id=ingest_id,
            reason="missing_file_id",
            error_type=type(vector_file).__name__,
        )
        return "failed", "missing_file_id", None
    _log_event(
        "pdf_ingest_responses_indexed",
        request_id=request_id,
        session_id=session_id,
        principal=principal,
        ingest_id=ingest_id,
        vector_store_id=deps.responses_vector_store_id,
        vector_store_file_id=vector_file_id,
    )
    return "indexed", None, vector_file_id


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


def _resolve_ocr_transcription_mode(value: str | None) -> str:
    normalized = (value or _OCR_TRANSCRIPTION_MODE_VERBATIM).strip().lower()
    if normalized in _OCR_TRANSCRIPTION_MODES:
        return normalized
    return _OCR_TRANSCRIPTION_MODE_VERBATIM


def _ocr_prompt_for_mode(base_prompt: str, mode: str) -> str:
    shared_rules = (
        "Transcription rules:\n"
        "- Do not invent letters, words, symbols, or punctuation.\n"
        "- Preserve visible line order and line breaks.\n"
        "- Preserve symbols exactly when identifiable.\n"
        "- If a mark is ambiguous, output `[?]` instead of guessing.\n"
        "- Do not output best-guess alternatives or candidate words.\n"
        "- Return only extracted text, no explanations."
    )
    if mode == _OCR_TRANSCRIPTION_MODE_NORMALIZED:
        return (
            f"{base_prompt}\n\n"
            "Output mode: normalized.\n"
            "Normalize whitespace and wrapping for readability, while preserving original words, "
            "numbers, symbols, and punctuation.\n\n"
            f"{shared_rules}"
        )
    return (
        f"{base_prompt}\n\n"
        "Output mode: verbatim.\n"
        "Preserve visible line breaks, spacing, punctuation, symbols, and casing.\n\n"
        f"{shared_rules}"
    )


def _normalize_ocr_text(text: str) -> str:
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    compact_lines = [line for line in lines if line]
    return "\n".join(compact_lines).strip()


def _apply_ocr_transcription_mode(text: str, mode: str) -> str:
    if mode == _OCR_TRANSCRIPTION_MODE_NORMALIZED:
        return _normalize_ocr_text(text)
    return text.strip()


def _clean_ocr_line(value: str) -> str:
    line = value.strip()
    if not line:
        return ""
    if line.startswith("[OCR]"):
        line = line[len("[OCR]") :].strip()
    line = re.sub(r"^\*\*(.+)\*\*$", r"\1", line)
    line = line.strip("“”\"'")
    return line.strip()


def _coerce_literal_ocr_output(text: str) -> str:
    raw = text.strip()
    if not raw:
        return ""

    lines = [line.strip() for line in raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    kept: list[str] = []
    preface_kept: list[str] = []

    prefix_rewrites = (
        r"^(?:the\s+)?text\s+(?:reads|read|appears(?:\s+to\s+read)?|appears\s+as)\s*[:\-]\s*(.+)$",
        r"^it\s+(?:reads|appears)\s*[:\-]\s*(.+)$",
    )
    commentary_prefixes = (
        "the image shows",
        "looks straightforward",
        "nothing else visible",
        "all lowercase",
        "capitalised at the start",
        "capitalized at the start",
        "the words are",
        "the words appear",
        "the second word likely",
    )

    for line in lines:
        if not line:
            continue
        lowered = line.lower()

        rewritten = None
        for pattern in prefix_rewrites:
            match = re.match(pattern, lowered, flags=re.IGNORECASE)
            if match:
                original_match = re.match(pattern, line, flags=re.IGNORECASE)
                if original_match:
                    rewritten = original_match.group(1).strip()
                break
        if rewritten is not None:
            cleaned = _clean_ocr_line(rewritten)
            if cleaned:
                preface_kept.append(cleaned)
            continue

        if any(lowered.startswith(prefix) for prefix in commentary_prefixes):
            continue

        cleaned = _clean_ocr_line(line)
        if cleaned:
            kept.append(cleaned)

    if preface_kept:
        candidate = "\n".join(preface_kept).strip()
    elif kept:
        candidate = "\n".join(kept).strip()
    else:
        candidate = raw
    return _disambiguate_model_acronyms(candidate)


def _disambiguate_model_acronyms(text: str) -> str:
    """Apply narrow OCR acronym fixes in strong model-language context only."""
    compact = text.strip()
    if not compact:
        return text
    # Only run when context strongly implies model-language discussion.
    lowered = compact.lower()
    has_model_context = any(
        token in lowered
        for token in (
            "language model",
            "model",
            "reasoning",
            "human semiotics",
            "lexeme",
        )
    )
    if not has_model_context:
        return text
    # Common handwriting ambiguity: "LLM" rendered as "UM".
    return re.sub(r"\bUM\b", "LLM", compact)


def _is_uncertain_ocr_line(value: str) -> bool:
    lowered = value.lower()
    if "[?]" in value:
        return False
    if _OCR_QUOTED_ALTERNATIVES_RE.search(value):
        return True
    return any(cue in lowered for cue in _OCR_UNCERTAINTY_CUE_PHRASES)


def _apply_ocr_uncertainty_safety(text: str) -> str:
    raw = text.strip()
    if not raw:
        return raw
    lines = [line.strip() for line in raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    normalized_lines: list[str] = []
    for line in lines:
        if not line:
            continue
        if _is_uncertain_ocr_line(line):
            normalized_lines.append("[?]")
            continue
        normalized_lines.append(line)

    if not normalized_lines:
        return raw

    deduped: list[str] = []
    for line in normalized_lines:
        if line == "[?]" and deduped and deduped[-1] == "[?]":
            continue
        deduped.append(line)
    return "\n".join(deduped).strip()


def _scaffold_extract_text(req: OcrRequest) -> tuple[str, str]:
    mode = _resolve_ocr_transcription_mode(req.transcription_mode)
    if req.text_hint and req.text_hint.strip():
        return _apply_ocr_transcription_mode(req.text_hint, mode), "ok"

    decoded, _mime_type = _decode_base64_payload(req)
    text = decoded.decode("utf-8", errors="ignore").strip()
    if text:
        return _apply_ocr_transcription_mode(text, mode), "ok"
    return "[OCR scaffold] Binary payload received. Connect OCR engine for text extraction.", "stub"


def _extract_text_with_openai(req: OcrRequest, deps: RuntimeDeps) -> tuple[str, str]:
    mode = _resolve_ocr_transcription_mode(req.transcription_mode)
    if req.text_hint and req.text_hint.strip():
        return _apply_ocr_transcription_mode(req.text_hint, mode), "ok"

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
    ocr_input = cast(
        Any,
        [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": _ocr_prompt_for_mode(deps.ocr_prompt, mode)},
                    {"type": "input_image", "image_url": data_url},
                ],
            }
        ],
    )
    try:
        response = deps.ocr_client.responses.create(
            model=deps.ocr_model,
            input=ocr_input,
            temperature=_OCR_TEMPERATURE,
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
        literal_output = _coerce_literal_ocr_output(output_text)
        if deps.ocr_uncertainty_safe:
            literal_output = _apply_ocr_uncertainty_safety(literal_output)
        return _apply_ocr_transcription_mode(literal_output, mode), "ok"
    return "[OCR] No text detected.", "ok"


def _extract_text(req: OcrRequest, deps: RuntimeDeps) -> tuple[str, str]:
    if deps.ocr_provider == "openai":
        return _extract_text_with_openai(req, deps)
    return _scaffold_extract_text(req)


def _extract_image_context(
    *,
    req: OcrRequest,
    deps: RuntimeDeps,
    request_id: str | None,
    session_id: str,
    principal: str | None,
) -> str | None:
    hint = (req.visual_context_hint or "").strip()
    if hint:
        compact_hint = hint[:_IMAGE_CONTEXT_MAX_CHARS].strip()
        if compact_hint:
            _log_event(
                "image_context_hint_used",
                request_id=request_id,
                session_id=session_id,
                principal=principal,
                chars=len(compact_hint),
            )
            return compact_hint

    if not deps.image_context_enabled:
        return None
    if deps.responses_client is None:
        return None
    responses_client = deps.responses_client
    if not req.data_base64 or not req.data_base64.strip():
        return None

    try:
        decoded, detected_mime = _decode_base64_payload(req)
    except HTTPException:
        return None

    mime_type = (detected_mime or "").strip().lower()
    if not mime_type.startswith("image/"):
        return None

    data_url = f"data:{mime_type};base64,{base64.b64encode(decoded).decode('ascii')}"
    image_context_input = cast(
        Any,
        [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": deps.image_context_prompt},
                    {"type": "input_image", "image_url": data_url},
                ],
            }
        ],
    )
    try:
        response = responses_client.responses.create(
            model=deps.image_context_model,
            input=image_context_input,
        )
        context_text = _extract_responses_output_text(response).strip()
        if not context_text:
            return None
        compact = context_text[:_IMAGE_CONTEXT_MAX_CHARS].strip()
        _log_event(
            "image_context_extracted",
            request_id=request_id,
            session_id=session_id,
            principal=principal,
            chars=len(compact),
        )
        return compact
    except AuthenticationError as exc:
        _log_event(
            "image_context_error",
            request_id=request_id,
            session_id=session_id,
            principal=principal,
            reason="authentication_error",
            error_type=type(exc).__name__,
        )
        return None
    except RateLimitError as exc:
        _log_event(
            "image_context_error",
            request_id=request_id,
            session_id=session_id,
            principal=principal,
            reason="rate_limited",
            error_type=type(exc).__name__,
        )
        return None
    except APIConnectionError as exc:
        _log_event(
            "image_context_error",
            request_id=request_id,
            session_id=session_id,
            principal=principal,
            reason="connection_error",
            error_type=type(exc).__name__,
        )
        return None
    except APIStatusError as exc:
        _log_event(
            "image_context_error",
            request_id=request_id,
            session_id=session_id,
            principal=principal,
            reason=f"api_status_{exc.status_code}",
            error_type=type(exc).__name__,
        )
        return None
    except Exception as exc:
        _log_event(
            "image_context_error",
            request_id=request_id,
            session_id=session_id,
            principal=principal,
            reason="unexpected_error",
            error_type=type(exc).__name__,
        )
        return None


def _compose_model_input(
    *,
    user_message: str,
    notes: list[str],
    retrieved_memory: list[VectorMatch],
    max_memory_chars: int,
    attachment_context_blocks: list[str] | None = None,
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
            memory_lines.append(f"- [{item.source_type}] {compact}")
        segments.append(
            "[RETRIEVED_MEMORY: retrieved context snippets. Use only if relevant.]\n"
            "- Treat [ocr], [pdf], and [image] snippets as grounding evidence; do not contradict them.\n"
            "- Treat [chat] snippets as prior conversational context/style, not external facts.\n"
            "- If evidence is limited, stay cautious rather than inventing specifics.\n"
            "- Never mention retrieval.\n"
            + "\n".join(memory_lines)
        )

    merged_notes: list[str] = []
    for candidate in [*list(_DEFAULT_INTERNAL_STYLE_NOTES), *notes]:
        _append_unique_note(merged_notes, candidate)
    if merged_notes:
        note_lines = "\n".join(f"- {note}" for note in merged_notes)
        segments.append(
            "[INTERNAL_STYLE_NOTES: private calibration notes. "
            "Apply silently and never mention them.]\n"
            f"{note_lines}"
        )
    attachment_segment = _compose_attachment_context_segment(attachment_context_blocks)
    if attachment_segment:
        segments.append(attachment_segment)

    if not segments:
        return user_message
    segments.append("[USER_MESSAGE]\n" + user_message)
    return "\n\n".join(segments)


def _compose_attachment_context_segment(attachment_context_blocks: list[str] | None) -> str | None:
    if not attachment_context_blocks:
        return None
    clean = [block.strip() for block in attachment_context_blocks if block and block.strip()]
    if not clean:
        return None
    numbered = [f"[ATTACHMENT_{idx}]\n{block}" for idx, block in enumerate(clean, start=1)]
    return (
        "[ATTACHMENT_CONTEXT: OCR/image context extracted from user attachments for this turn.]\n"
        "- Treat this as grounding evidence when relevant.\n"
        "- If uncertain, stay explicit about uncertainty.\n"
        "- Never mention this block.\n"
        + "\n\n".join(numbered)
    )


def _has_meaningful_ocr_text(value: str) -> bool:
    if _is_low_confidence_ocr_text(value):
        return False
    return True


def _is_low_confidence_ocr_text(value: str) -> bool:
    compact = value.strip()
    if not compact:
        return True
    if compact.lower() == "[ocr] no text detected.":
        return True

    lines = [line.strip() for line in compact.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    non_empty = [line for line in lines if line]
    if not non_empty:
        return True

    uncertain_tokens = {"[?]", "?", "[unknown]", "unknown", "unclear", "illegible"}
    if all(line.lower() in uncertain_tokens for line in non_empty):
        return True
    return False


def _embed_texts(texts: list[str], deps: RuntimeDeps) -> list[list[float]]:
    if deps.embedding_client is None:
        raise RuntimeError("Embedding client is not configured.")
    try:
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
    except APIConnectionError as exc:
        if not deps.vector_local_embedding_fallback:
            raise
        _log_event(
            "vector_embedding_fallback",
            reason="connection_error",
            error_type=type(exc).__name__,
        )
    except APIStatusError as exc:
        if not deps.vector_local_embedding_fallback or not (500 <= exc.status_code <= 599):
            raise
        _log_event(
            "vector_embedding_fallback",
            reason=f"api_status_{exc.status_code}",
            error_type=type(exc).__name__,
        )

    return [_local_fallback_embedding(text) for text in texts]


def _local_fallback_embedding(text: str, *, dims: int = 256) -> list[float]:
    tokens = _FILE_SEARCH_TOKEN_RE.findall(text.lower())
    if not tokens:
        compact = text.strip().lower()
        tokens = [compact] if compact else ["_empty_"]

    vector = [0.0] * dims
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for offset in range(0, 8, 2):
            idx = int.from_bytes(digest[offset : offset + 2], "big") % dims
            sign = 1.0 if (digest[offset + 2] & 1) == 0 else -1.0
            vector[idx] += sign

    norm = sum(value * value for value in vector) ** 0.5
    if norm <= 0.0:
        return vector
    return [value / norm for value in vector]


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
    top_k = deps.vector_top_k_global
    min_similarity = deps.vector_min_similarity_global
    if normalized_scope == "session":
        include_session_id = session_id
        top_k = deps.vector_top_k_session
        min_similarity = deps.vector_min_similarity_session
    else:
        exclude_session_id = session_id if deps.vector_exclude_current_session else None
    return deps.vector_store.search(
        query_embedding=query_vector,
        limit=top_k,
        min_similarity=min_similarity,
        roles=("assistant",),
        include_session_id=include_session_id,
        exclude_session_id=exclude_session_id,
        source_types=("chat", "ocr", "image", "pdf"),
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
    origin_session_id: str | None = None,
    visual_context: str | None = None,
) -> None:
    if not deps.vector_enabled or deps.vector_store is None:
        return
    chunks = _chunk_text_for_vectors(run.extracted_text)
    if chunks:
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
                        "origin_session_id": origin_session_id or run.session_id,
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

    context_text = (visual_context or "").strip()
    if not context_text:
        return
    try:
        context_embedding = _embed_texts([context_text], deps)[0]
        deps.vector_store.upsert_message_vector(
            session_id=session_id,
            role="assistant",
            message_id=None,
            content=context_text,
            embedding=context_embedding,
            source_type="image",
            source_ref=f"{run.run_id}:visual_context",
            metadata={
                "source": "image_context",
                "ocr_run_id": run.run_id,
                "source_name": run.source_name,
                "mime_type": run.mime_type,
                "source_message_id": run.source_message_id,
                "result_message_id": run.result_message_id,
                "origin_session_id": origin_session_id or run.session_id,
            },
            created_at=run.created_at,
        )
    except Exception as exc:
        _log_event(
            "vector_image_context_index_error",
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


def _resolve_file_search_source_types(
    *,
    deps: RuntimeDeps,
    source_types: list[str] | None,
    retrieval_profile: Literal["default", "clip_proxy_image_only"],
) -> tuple[str, ...]:
    if retrieval_profile == "clip_proxy_image_only":
        if not deps.clip_proxy_file_search_enabled:
            raise HTTPException(
                status_code=409,
                detail=(
                    "retrieval_profile=clip_proxy_image_only is disabled. "
                    "Set POLINKO_CLIP_PROXY_FILE_SEARCH_ENABLED=true to enable it."
                ),
            )
        # Minimal integration slice: proxy profile uses image-only retrieval.
        return ("image",)
    return _normalize_file_search_source_types(source_types)


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


def _responses_file_search_enabled(deps: RuntimeDeps, source_types: tuple[str, ...]) -> bool:
    return (
        "pdf" in source_types
        and deps.responses_pdf_ingest_enabled
        and deps.responses_client is not None
        and bool(deps.responses_vector_store_id)
    )


def _responses_search_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for item in content:
        text: object | None = None
        if isinstance(item, dict):
            text = item.get("text")
        else:
            text = getattr(item, "text", None)
        if isinstance(text, str):
            compact = text.strip()
            if compact:
                parts.append(compact)
    return "\n".join(parts).strip()


def _responses_file_search(
    *,
    deps: RuntimeDeps,
    query: str,
    session_filter: str | None,
    source_types: tuple[str, ...],
    limit: int,
    candidate_limit: int,
) -> tuple[list[FileSearchMatchResponse], int]:
    client = deps.responses_client
    vector_store_id = deps.responses_vector_store_id
    if client is None or not vector_store_id:
        return [], 0

    response = client.vector_stores.search(
        vector_store_id=vector_store_id,
        query=query,
        max_num_results=candidate_limit,
    )

    raw_data = getattr(response, "data", None)
    if raw_data is None:
        response_items: list[Any] = []
    else:
        response_items = list(raw_data)

    query_tokens = _tokenize_file_search_text(query)
    ranked: list[tuple[float, float, float, FileSearchMatchResponse]] = []

    for idx, item in enumerate(response_items):
        raw_attributes = getattr(item, "attributes", None)
        attributes = dict(raw_attributes) if isinstance(raw_attributes, dict) else {}

        source_type = str(attributes.get("source") or "pdf").strip().lower() or "pdf"
        if source_type not in source_types:
            continue

        stored_session = attributes.get("session_id")
        stored_session_text = str(stored_session).strip() if stored_session is not None else ""
        if session_filter and stored_session_text != session_filter:
            continue

        content_text = _responses_search_text(getattr(item, "content", None))
        if not content_text:
            continue

        raw_similarity = getattr(item, "score", 0.0)
        try:
            similarity = float(raw_similarity)
        except (TypeError, ValueError):
            similarity = 0.0
        keyword_score = _keyword_overlap_score(query_tokens, content_text)
        score = (similarity * 0.78) + (keyword_score * 0.22)

        file_id = getattr(item, "file_id", None)
        file_id_text = file_id if isinstance(file_id, str) and file_id else None
        filename = getattr(item, "filename", None)
        filename_text = filename if isinstance(filename, str) and filename else None
        source_ref = attributes.get("source_ref")
        source_ref_text = str(source_ref).strip() if source_ref else None

        metadata = dict(attributes)
        if file_id_text and "file_id" not in metadata:
            metadata["file_id"] = file_id_text
        if filename_text and "filename" not in metadata:
            metadata["filename"] = filename_text
        if "source" not in metadata:
            metadata["source"] = source_type

        candidate = FileSearchMatchResponse(
            vector_id=f"resp:{file_id_text or 'unknown'}:{idx}",
            session_id=_display_session_id(
                session_id=stored_session_text or session_filter or "global",
                metadata=metadata,
            ),
            source_type=source_type,
            source_ref=source_ref_text or file_id_text,
            similarity=round(similarity, 4),
            keyword_score=round(keyword_score, 4),
            score=round(score, 4),
            snippet=_file_search_snippet(content_text, query_tokens),
            metadata=metadata,
        )
        ranked.append((score, similarity, keyword_score, candidate))

    ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
    matches = [candidate for _, _, _, candidate in ranked[:limit]]
    return matches, len(response_items)


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
            "- Constrain claims to retrieved/available evidence.\n"
            "- Do not add mechanisms, conditions, or specifics that are not present in evidence.\n"
            "- If certainty is low, use one concise uncertainty clause, then continue with the best grounded framing.\n"
            "- Keep the user's established tone and rhythm while staying factual.\n"
            "- Do not fabricate citations, dates, names, winners, or numeric values."
        )
    return (
        "[HALLUCINATION_GUARDRAIL: low-evidence mode]\n"
        "- Avoid presenting uncertain facts as certain.\n"
        "- If supporting evidence is missing, state that clearly in one short line before any answer.\n"
        "- Keep tone continuity with the user; avoid sterile or repetitive disclaimer phrasing.\n"
        "- Do not invent sources, statistics, dates, names, winners, organizations, or quotations.\n"
        "- For unknown/fictional events, do not fabricate a winner or concrete outcome."
    )


def _factual_run_config(
    *,
    deps: RuntimeDeps,
    query_text: str,
    evidence_count: int,
) -> RunConfig:
    del query_text, evidence_count
    return deps.run_config


def _low_evidence_factual_reply(query_text: str, evidence_count: int) -> str | None:
    if evidence_count > 0:
        return None
    if not _looks_like_factual_query(query_text):
        return None
    lowered = query_text.lower()
    if any(hint in lowered for hint in _FICTIONAL_QUERY_HINTS):
        return (
            "I can’t verify a winner for that because the event is fictional and there is no "
            "grounding evidence in this session."
        )
    return None


def _looks_like_ocr_request(query_text: str) -> bool:
    lowered = query_text.strip().lower()
    if not lowered:
        return False
    token_set = set(_FILE_SEARCH_TOKEN_RE.findall(lowered))
    for hint in _OCR_REQUEST_HINTS:
        hint_lower = hint.lower()
        if " " in hint_lower:
            if hint_lower in lowered:
                return True
            continue
        if hint_lower in token_set:
            return True
    if "ocr" in token_set:
        return True
    # Short follow-up queries around an active image context are often OCR requests.
    token_count = len(lowered.split())
    if token_count <= 7 and any(token in token_set for token in ("word", "text", "say", "read")):
        return True
    return False


def _looks_like_ocr_followup_without_new_image(query_text: str) -> bool:
    lowered = query_text.strip().lower()
    if not lowered:
        return False
    if _looks_like_ocr_request(lowered):
        return True
    has_followup_hint = any(hint in lowered for hint in _OCR_FOLLOWUP_HINTS)
    if not has_followup_hint:
        return False
    # Only explicit OCR retry language should trigger no-new-image blocking.
    explicit_retry_patterns = (
        r"^\s*again[.!?]*\s*$",
        r"\btry again\b",
        r"\bwithout using memory\b",
        r"\bno memory\b",
        r"\bocr again\b",
        r"\btranscrib(?:e|ing) again\b",
        r"\bread again\b",
        r"\bretry ocr\b",
    )
    return any(re.search(pattern, lowered) is not None for pattern in explicit_retry_patterns)


def _looks_like_ocr_correction_without_new_image(query_text: str) -> bool:
    lowered = query_text.strip().lower()
    if not lowered:
        return False
    if any(hint in lowered for hint in _OCR_CORRECTION_HINTS):
        return True
    # Short correction payloads like "1916", "LLM", "not X, Y".
    if re.fullmatch(r"[a-z0-9+\-:/. ]{1,24}", lowered):
        token_count = len(lowered.split())
        has_digit = any(ch.isdigit() for ch in lowered)
        has_letter = any(ch.isalpha() for ch in lowered)
        if token_count <= 4 and (has_digit or has_letter):
            return True
    return False


def _has_recent_ocr_activity(*, deps: RuntimeDeps, session_id: str, max_age_seconds: int = 600) -> bool:
    runs = deps.history_store.list_ocr_runs(session_id=session_id, limit=1)
    if not runs:
        return False
    latest = runs[0]
    age_ms = int(time.time() * 1000) - int(latest.created_at)
    return age_ms <= max_age_seconds * 1000


def _build_attachment_literal_reply(attachment_ocr_texts: list[tuple[str, str]]) -> str:
    meaningful = [
        (label.strip(), text.strip())
        for label, text in attachment_ocr_texts
        if label.strip() and _has_meaningful_ocr_text(text)
    ]
    if not meaningful:
        return (
            "[OCR]\nNo confident text detected. Attach a tighter crop or clearer image and I will "
            "transcribe only visible text."
        )
    if len(meaningful) == 1:
        _label, text = meaningful[0]
        return f"[OCR]\n{text}"
    lines: list[str] = ["[OCR]"]
    for idx, (label, text) in enumerate(meaningful, start=1):
        lines.append(f"\n[{idx}] {label}\n{text}")
    return "\n".join(lines).strip()


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
    attachment_context_blocks: list[str] | None = None,
    guardrail_note: str | None = None,
    collaboration_note: str | None = None,
) -> tuple[str, int]:
    if deps.responses_client is None:
        raise RuntimeError("Responses orchestration is enabled, but no client is configured.")
    responses_client = deps.responses_client
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
    merged_notes = [*list(_DEFAULT_INTERNAL_STYLE_NOTES), *notes]
    if merged_notes:
        note_lines = "\n".join(f"- {note}" for note in merged_notes)
        segments.append(
            "[INTERNAL_STYLE_NOTES: private calibration notes. "
            "Apply silently and never mention them.]\n"
            f"{note_lines}"
        )
    attachment_segment = _compose_attachment_context_segment(attachment_context_blocks)
    if attachment_segment:
        segments.append(attachment_segment)
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

    response = responses_client.responses.create(
        model=deps.responses_orchestration_model,
        instructions=ACTIVE_PROMPT,
        input=input_text,
        tools=cast(Any, tools),
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
        rate_limit_per_minute=config.rate_limit_per_minute,
        rate_limiter=SlidingWindowRateLimiter(),
        deprecate_on_reset=config.deprecate_on_reset,
        ocr_provider=config.ocr_provider,
        ocr_model=config.ocr_model,
        ocr_prompt=config.ocr_prompt,
        ocr_uncertainty_safe=config.ocr_uncertainty_safe,
        image_context_enabled=config.image_context_enabled,
        image_context_model=config.image_context_model,
        image_context_prompt=config.image_context_prompt,
        ocr_client=shared_openai_client if config.ocr_provider == "openai" else None,
        vector_enabled=config.vector_enabled,
        vector_top_k=config.vector_top_k,
        vector_top_k_global=config.vector_top_k_global,
        vector_top_k_session=config.vector_top_k_session,
        vector_min_similarity=config.vector_min_similarity,
        vector_min_similarity_global=config.vector_min_similarity_global,
        vector_min_similarity_session=config.vector_min_similarity_session,
        vector_max_chars=config.vector_max_chars,
        vector_exclude_current_session=config.vector_exclude_current_session,
        vector_local_embedding_fallback=config.vector_local_embedding_fallback,
        vector_embedding_model=config.vector_embedding_model,
        vector_store=VectorStore(config.vector_db_path) if config.vector_enabled else None,
        embedding_client=shared_openai_client if config.vector_enabled else None,
        responses_orchestration_enabled=config.responses_orchestration_enabled,
        responses_orchestration_model=config.responses_orchestration_model,
        responses_vector_store_id=config.responses_vector_store_id,
        responses_include_web_search=config.responses_include_web_search,
        responses_history_turn_limit=config.responses_history_turn_limit,
        responses_pdf_ingest_enabled=config.responses_pdf_ingest_enabled,
        responses_client=shared_openai_client
        if (
            config.responses_orchestration_enabled
            or config.extraction_structured_enabled
            or config.responses_pdf_ingest_enabled
            or config.image_context_enabled
        )
        else None,
        extraction_structured_enabled=config.extraction_structured_enabled,
        extraction_structured_model=config.extraction_structured_model,
        governance_enabled=config.governance_enabled,
        governance_allow_web_search=config.governance_allow_web_search,
        governance_log_only=config.governance_log_only,
        hallucination_guardrails_enabled=config.hallucination_guardrails_enabled,
        personalization_default_memory_scope=config.personalization_default_memory_scope,
        clip_proxy_file_search_enabled=config.clip_proxy_file_search_enabled,
        chat_harness_default_mode=config.chat_harness_default_mode,
        metrics=create_runtime_metrics(),
        run_config=create_run_config(store=True),
        agent=create_agent(),
    )
    ui_dir = Path(__file__).resolve().parents[1] / "ui"
    portfolio_assets_dir = ui_dir / "assets"
    if portfolio_assets_dir.exists():
        app.mount(
            "/assets",
            StaticFiles(directory=str(portfolio_assets_dir)),
            name="portfolio-assets",
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

    @app.get("/")
    def portfolio_root_redirect() -> RedirectResponse:
        return RedirectResponse(url="/portfolio")

    @app.get("/portfolio")
    def portfolio_shell() -> Any:
        shell_path = ui_dir / "index.html"
        if not shell_path.is_file():
            return HTMLResponse(content=_PORTFOLIO_FALLBACK_HTML)
        return FileResponse(path=shell_path)

    @app.get("/portfolio/sankey-data")
    def portfolio_sankey_data(max_reports: int = 120) -> dict[str, Any]:
        return build_portfolio_sankey_payload(
            max_reports=max(1, min(max_reports, 240)),
        )

    @app.get("/viz/pass-fail", response_class=HTMLResponse)
    def pass_fail_viz(refresh_ms: int = 4000, chart_max_points: int = 20) -> str:
        # Live PASS/FAIL surface with latest eval detail interactions.
        return render_pass_fail_viz_html(
            refresh_ms=refresh_ms,
            chart_max_points=max(8, min(chart_max_points, 120)),
        )

    @app.get("/viz/pass-fail/data")
    def pass_fail_viz_data(max_evals: int = 180, run_id: str | None = None) -> dict[str, Any]:
        return build_pass_fail_viz_payload(
            max_evals=max(1, min(max_evals, 500)),
            run_id=(run_id or "").strip() or None,
        )

    @app.get("/viz/pass-fail/image")
    def pass_fail_viz_image(path: str) -> FileResponse:
        resolved = Path(path).expanduser()
        if not resolved.is_absolute():
            resolved = (Path.cwd() / resolved).resolve()
        else:
            resolved = resolved.resolve()

        allowed_suffixes = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".heic", ".heif"}
        suffix = resolved.suffix.lower()
        if suffix not in allowed_suffixes:
            raise HTTPException(status_code=400, detail="Unsupported image type.")
        if not resolved.is_file():
            raise HTTPException(status_code=404, detail="Image file not found.")

        return FileResponse(path=resolved)

    @app.get("/manual-evals/surface")
    def manual_evals_surface(max_runs: int = 180, max_sessions: int = 60) -> dict[str, Any]:
        return build_manual_evals_surface_payload(
            max_runs=max(1, min(max_runs, 800)),
            max_sessions=max(1, min(max_sessions, 300)),
        )

    @app.get("/metrics", response_model=MetricsResponse)
    def metrics(request: Request) -> MetricsResponse:
        deps = _runtime_deps(request.app)
        return _metrics_response(deps.metrics)

    @app.get("/chats", response_model=ChatsResponse)
    def list_chats(request: Request, include_deprecated: bool = False) -> ChatsResponse:
        deps = _runtime_deps(request.app)
        summaries = [
            _chat_summary_response(summary, deps=deps)
            for summary in deps.history_store.list_chats(include_deprecated=include_deprecated)
        ]
        return ChatsResponse(chats=summaries)

    @app.post("/chats", response_model=ChatSummaryResponse)
    def create_chat(req: CreateChatRequest, request: Request) -> ChatSummaryResponse:
        deps = _runtime_deps(request.app)
        session_id = req.session_id or f"chat-{uuid.uuid4()}"
        title = (req.title or DEFAULT_CHAT_TITLE).strip() or DEFAULT_CHAT_TITLE
        summary = deps.history_store.ensure_chat(session_id=session_id, title=title)
        return _chat_summary_response(summary, deps=deps)

    @app.get("/chats/{session_id}/messages", response_model=ChatMessagesResponse)
    def list_chat_messages(session_id: str, request: Request) -> ChatMessagesResponse:
        deps = _runtime_deps(request.app)
        chat = deps.history_store.get_chat(session_id=session_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found.")
        messages = [
            _chat_message_response(message)
            for message in deps.history_store.list_messages(session_id=session_id)
        ]
        return ChatMessagesResponse(session_id=session_id, messages=messages)

    @app.get("/chats/{session_id}/feedback", response_model=ChatFeedbackResponse)
    def list_chat_feedback(session_id: str, request: Request) -> ChatFeedbackResponse:
        deps = _runtime_deps(request.app)
        chat = deps.history_store.get_chat(session_id=session_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found.")
        feedback = [
            _message_feedback_response(item)
            for item in deps.history_store.list_message_feedback(session_id=session_id)
        ]
        return ChatFeedbackResponse(session_id=session_id, feedback=feedback)

    @app.post("/chats/{session_id}/feedback", response_model=MessageFeedbackResponse)
    def submit_chat_feedback(
        session_id: str,
        req: MessageFeedbackRequest,
        request: Request,
    ) -> MessageFeedbackResponse:
        principal = None
        deps = _runtime_deps(request.app)
        chat = deps.history_store.get_chat(session_id=session_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found.")
        if not deps.history_store.message_exists(session_id=session_id, message_id=req.message_id):
            raise HTTPException(status_code=404, detail="message_id not found in this chat.")
        message_role = deps.history_store.get_message_role(session_id=session_id, message_id=req.message_id)
        if message_role != "assistant":
            raise HTTPException(status_code=400, detail="Only assistant messages can be evaluated.")
        outcome = _normalize_feedback_outcome(req.outcome)
        positive_tags, negative_tags, tags = _normalize_feedback_tags(
            outcome=outcome,
            positive_tags=req.positive_tags,
            negative_tags=req.negative_tags,
        )
        note = req.note.strip() if req.note is not None and req.note.strip() else None
        action_taken = req.action_taken.strip() if req.action_taken is not None and req.action_taken.strip() else None
        recommended_action = _suggest_feedback_action(
            outcome=outcome,
            positive_tags=positive_tags,
            negative_tags=negative_tags,
            note=note,
        )
        status = _feedback_status_for_outcome(outcome)
        saved = deps.history_store.upsert_message_feedback(
            session_id=session_id,
            message_id=req.message_id,
            outcome=outcome,
            positive_tags=positive_tags,
            negative_tags=negative_tags,
            note=note,
            recommended_action=recommended_action,
            action_taken=action_taken,
            status=status,
        )
        _log_event(
            "chat_feedback_submitted",
            request_id=getattr(request.state, "request_id", None),
            session_id=session_id,
            principal=principal,
            message_id=req.message_id,
            outcome=outcome,
            tag_count=len(tags),
            positive_tag_count=len(positive_tags),
            negative_tag_count=len(negative_tags),
            status=status,
        )
        return _message_feedback_response(saved)

    @app.get("/chats/{session_id}/feedback/checkpoints", response_model=ChatEvalCheckpointsResponse)
    def list_eval_checkpoints(session_id: str, request: Request) -> ChatEvalCheckpointsResponse:
        deps = _runtime_deps(request.app)
        chat = deps.history_store.get_chat(session_id=session_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found.")
        checkpoints = [
            _eval_checkpoint_response(item)
            for item in deps.history_store.list_eval_checkpoints(session_id=session_id)
        ]
        return ChatEvalCheckpointsResponse(session_id=session_id, checkpoints=checkpoints)

    @app.post("/chats/{session_id}/feedback/checkpoints", response_model=EvalCheckpointResponse)
    def submit_eval_checkpoint(session_id: str, request: Request) -> EvalCheckpointResponse:
        principal = None
        deps = _runtime_deps(request.app)
        chat = deps.history_store.get_chat(session_id=session_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found.")
        entries = deps.history_store.list_message_feedback(session_id=session_id)
        if not entries:
            raise HTTPException(status_code=400, detail="No saved evals in this chat yet.")
        total_count, pass_count, fail_count, non_binary_count = _summarize_feedback_streams(entries)
        if non_binary_count > 0:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Stored feedback contains non-binary outcomes; expected pass/fail only. "
                    "Repair data before checkpointing."
                ),
            )
        checkpoint_id = f"eval-{uuid.uuid4().hex[:12]}"
        saved = deps.history_store.record_eval_checkpoint(
            checkpoint_id=checkpoint_id,
            session_id=session_id,
            total_count=total_count,
            pass_count=pass_count,
            fail_count=fail_count,
            non_binary_count=non_binary_count,
        )
        _log_event(
            "chat_eval_checkpoint_submitted",
            request_id=getattr(request.state, "request_id", None),
            session_id=session_id,
            principal=principal,
            checkpoint_id=saved.checkpoint_id,
            total_count=saved.total_count,
            pass_count=saved.pass_count,
            fail_count=saved.fail_count,
            non_binary_count=saved.non_binary_count,
            schema_version=_EVAL_CHECKPOINT_SCHEMA_VERSION,
        )
        return _eval_checkpoint_response(saved)

    @app.get("/chats/{session_id}/export", response_model=ChatExportResponse)
    def export_chat(session_id: str, request: Request, include_markdown: bool = False) -> ChatExportResponse:
        deps = _runtime_deps(request.app)
        chat = deps.history_store.get_chat(session_id=session_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found.")
        memory_scope = _resolve_chat_memory_scope(deps=deps, session_id=session_id)
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
            memory_scope=memory_scope,
            context_scope=_context_scope_from_memory_scope(memory_scope),
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
        principal = None
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
        dedup_key = _build_ocr_dedup_key(
            req=req,
            deps=deps,
            principal=principal,
            session_id=session_id,
        )

        cached_payload = deps.history_store.get_ingest_dedup_response(
            dedup_key=dedup_key,
            operation="ocr",
        )
        if cached_payload is not None:
            try:
                cached_response = OcrResponse.model_validate(cached_payload)
            except Exception:
                _log_event(
                    "ocr_run_dedup_payload_invalid",
                    request_id=getattr(request.state, "request_id", None),
                    session_id=session_id,
                    principal=principal,
                )
            else:
                cached_run = cached_response.run
                index_session_id = _resolve_memory_lane_session_id(
                    session_id=session_id,
                    memory_scope=req.memory_scope,
                )
                _log_event(
                    "ocr_run",
                    request_id=getattr(request.state, "request_id", None),
                    session_id=session_id,
                    principal=principal,
                    run_id=cached_run.run_id,
                    provider=deps.ocr_provider,
                    status=cached_run.status,
                    chars=len(cached_run.extracted_text),
                    memory_scope=_normalize_memory_scope(req.memory_scope, default="session"),
                    index_session_id=index_session_id,
                    vector_chunks=len(_chunk_text_for_vectors(cached_run.extracted_text)),
                    dedup_hit=True,
                )
                return cached_response

        extracted_text, status = _extract_text(req, deps)
        visual_context = _extract_image_context(
            req=req,
            deps=deps,
            request_id=getattr(request.state, "request_id", None),
            session_id=session_id,
            principal=principal,
        )
        result_message_id: str | None = None
        if req.attach_to_chat:
            appended = deps.history_store.append_message(
                session_id=session_id,
                role="assistant",
                content=f"[OCR]\n{extracted_text}",
            )
            result_message_id = appended.message_id
        effective_source_message_id = req.source_message_id
        if effective_source_message_id is None and result_message_id is not None:
            # Preserve a concrete trace link when OCR output is attached to chat.
            effective_source_message_id = result_message_id

        run_id = f"ocr-{uuid.uuid4().hex[:12]}"
        try:
            run = deps.history_store.record_ocr_run(
                run_id=run_id,
                session_id=session_id,
                source_name=req.source_name,
                mime_type=req.mime_type,
                source_message_id=effective_source_message_id,
                result_message_id=result_message_id,
                status=status,
                extracted_text=extracted_text,
            )
        except sqlite3.IntegrityError:
            deps.history_store.ensure_chat(session_id=session_id)
            try:
                run = deps.history_store.record_ocr_run(
                    run_id=run_id,
                    session_id=session_id,
                    source_name=req.source_name,
                    mime_type=req.mime_type,
                    source_message_id=effective_source_message_id,
                    result_message_id=result_message_id,
                    status=status,
                    extracted_text=extracted_text,
                )
            except sqlite3.IntegrityError as exc:
                _log_event(
                    "ocr_run_write_conflict",
                    request_id=getattr(request.state, "request_id", None),
                    session_id=session_id,
                    principal=principal,
                    recovered=False,
                )
                raise HTTPException(
                    status_code=409,
                    detail="OCR run could not be recorded due to concurrent chat updates. Retry request.",
                ) from exc
            _log_event(
                "ocr_run_write_conflict",
                request_id=getattr(request.state, "request_id", None),
                session_id=session_id,
                principal=principal,
                recovered=True,
            )
        index_session_id = _resolve_memory_lane_session_id(
            session_id=session_id,
            memory_scope=req.memory_scope,
        )
        _index_ocr_output(
            deps=deps,
            session_id=index_session_id,
            run=run,
            origin_session_id=session_id,
            visual_context=visual_context,
        )
        _log_event(
            "ocr_run",
            request_id=getattr(request.state, "request_id", None),
            session_id=session_id,
            principal=principal,
            run_id=run.run_id,
            provider=deps.ocr_provider,
            status=run.status,
            chars=len(run.extracted_text),
            memory_scope=_normalize_memory_scope(req.memory_scope, default="session"),
            index_session_id=index_session_id,
            vector_chunks=len(_chunk_text_for_vectors(run.extracted_text)),
            dedup_hit=False,
        )
        structured = _build_structured_extraction(
            source_type="ocr",
            source_name=run.source_name,
            mime_type=run.mime_type,
            text=run.extracted_text,
            deps=deps,
            request_id=getattr(request.state, "request_id", None),
            session_id=session_id,
            principal=principal,
        )
        response_payload = OcrResponse(
            run=OcrRunResponse(
                run_id=run.run_id,
                session_id=run.session_id,
                source_name=run.source_name,
                mime_type=run.mime_type,
                source_message_id=run.source_message_id,
                result_message_id=run.result_message_id,
                status=run.status,
                extracted_text=run.extracted_text,
                visual_context=visual_context,
                structured=structured,
                created_at=run.created_at,
            )
        )
        deps.history_store.record_ingest_dedup_response(
            dedup_key=dedup_key,
            operation="ocr",
            session_id=session_id,
            response_payload=response_payload.model_dump(),
        )
        return response_payload

    @app.post("/skills/pdf_ingest", response_model=PdfIngestResponse)
    def pdf_ingest(req: PdfIngestRequest, request: Request) -> PdfIngestResponse:
        principal = None
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

        dedup_key = _build_pdf_ingest_dedup_key(
            req=req,
            deps=deps,
            principal=principal,
            session_id=session_id,
            payload_bytes=decoded,
            resolved_mime_type=resolved_mime or None,
        )
        cached_payload = deps.history_store.get_ingest_dedup_response(
            dedup_key=dedup_key,
            operation="pdf_ingest",
        )
        if cached_payload is not None:
            try:
                cached_response = PdfIngestResponse.model_validate(cached_payload)
            except Exception:
                _log_event(
                    "pdf_ingest_dedup_payload_invalid",
                    request_id=getattr(request.state, "request_id", None),
                    session_id=session_id,
                    principal=principal,
                )
            else:
                _log_event(
                    "pdf_ingest",
                    request_id=getattr(request.state, "request_id", None),
                    session_id=session_id,
                    principal=principal,
                    ingest_id=cached_response.ingest_id,
                    chars=cached_response.extracted_chars,
                    vector_chunks=cached_response.vector_chunks,
                    source_name=cached_response.source_name,
                    dedup_hit=True,
                )
                return cached_response

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
            dedup_hit=False,
        )
        responses_index_status, responses_index_reason, responses_vector_store_file_id = _index_pdf_in_responses_vector_store(
            deps=deps,
            request_id=getattr(request.state, "request_id", None),
            session_id=session_id,
            principal=principal,
            ingest_id=ingest_id,
            source_name=req.source_name,
            payload=decoded,
        )
        if responses_index_status == "indexed" and responses_vector_store_file_id:
            _log_event(
                "pdf_ingest_responses_linked",
                request_id=getattr(request.state, "request_id", None),
                session_id=session_id,
                principal=principal,
                ingest_id=ingest_id,
                vector_store_file_id=responses_vector_store_file_id,
            )
        response_payload = PdfIngestResponse(
            ingest_id=ingest_id,
            session_id=session_id,
            source_name=req.source_name,
            mime_type=resolved_mime or req.mime_type,
            status="ok",
            extracted_chars=len(extracted_text),
            vector_chunks=len(chunks),
            result_message_id=result_message_id,
            responses_index_status=responses_index_status,
            responses_index_reason=responses_index_reason,
            responses_vector_store_file_id=responses_vector_store_file_id,
            structured=_build_structured_extraction(
                source_type="pdf",
                source_name=req.source_name,
                mime_type=resolved_mime or req.mime_type,
                text=extracted_text,
                deps=deps,
                request_id=getattr(request.state, "request_id", None),
                session_id=session_id,
                principal=principal,
            ),
        )
        deps.history_store.record_ingest_dedup_response(
            dedup_key=dedup_key,
            operation="pdf_ingest",
            session_id=session_id,
            response_payload=response_payload.model_dump(),
        )
        return response_payload

    @app.post("/skills/file_search", response_model=FileSearchResponse)
    def file_search(req: FileSearchRequest, request: Request) -> FileSearchResponse:
        principal = None
        deps = _runtime_deps(request.app)
        if not deps.vector_enabled or deps.vector_store is None:
            raise HTTPException(status_code=503, detail="Vector memory is not enabled.")

        query = req.query.strip()
        if not query:
            raise HTTPException(status_code=422, detail="query cannot be blank.")
        session_filter = req.session_id.strip() if req.session_id else None
        if req.session_id is not None and not session_filter:
            raise HTTPException(status_code=422, detail="session_id cannot be blank.")
        source_types = _resolve_file_search_source_types(
            deps=deps,
            source_types=req.source_types,
            retrieval_profile=req.retrieval_profile,
        )
        search_min_similarity = max(
            _FILE_SEARCH_MIN_SIMILARITY_FLOOR,
            deps.vector_min_similarity - 0.15,
        )
        candidate_limit = min(
            _FILE_SEARCH_MAX_CANDIDATES,
            max(req.limit * _FILE_SEARCH_CANDIDATE_MULTIPLIER, 40),
        )
        request_id = getattr(request.state, "request_id", None)
        fallback_reason: str | None = None

        if _responses_file_search_enabled(deps, source_types):
            try:
                responses_matches, responses_candidates = _responses_file_search(
                    deps=deps,
                    query=query,
                    session_filter=session_filter,
                    source_types=source_types,
                    limit=req.limit,
                    candidate_limit=candidate_limit,
                )
                if responses_matches:
                    _log_event(
                        "file_search",
                        request_id=request_id,
                        principal=principal,
                        session_id=req.session_id,
                        retrieval_profile=req.retrieval_profile,
                        source_types=list(source_types),
                        query_chars=len(query),
                        candidate_count=responses_candidates,
                        result_count=len(responses_matches),
                        backend="responses_vector_store",
                    )
                    return FileSearchResponse(
                        query=query,
                        searched_at=int(time.time() * 1000),
                        backend="responses_vector_store",
                        candidate_count=responses_candidates,
                        matches=responses_matches,
                    )
                fallback_reason = "responses_no_matches"
            except AuthenticationError as exc:
                fallback_reason = "authentication_error"
                _log_event(
                    "file_search_responses_fallback",
                    request_id=request_id,
                    principal=principal,
                    session_id=req.session_id,
                    retrieval_profile=req.retrieval_profile,
                    reason="authentication_error",
                    error_type=type(exc).__name__,
                )
            except RateLimitError as exc:
                fallback_reason = "rate_limited"
                _log_event(
                    "file_search_responses_fallback",
                    request_id=request_id,
                    principal=principal,
                    session_id=req.session_id,
                    retrieval_profile=req.retrieval_profile,
                    reason="rate_limited",
                    error_type=type(exc).__name__,
                )
            except APIConnectionError as exc:
                fallback_reason = "connection_error"
                _log_event(
                    "file_search_responses_fallback",
                    request_id=request_id,
                    principal=principal,
                    session_id=req.session_id,
                    retrieval_profile=req.retrieval_profile,
                    reason="connection_error",
                    error_type=type(exc).__name__,
                )
            except APIStatusError as exc:
                fallback_reason = f"api_status_{exc.status_code}"
                _log_event(
                    "file_search_responses_fallback",
                    request_id=request_id,
                    principal=principal,
                    session_id=req.session_id,
                    retrieval_profile=req.retrieval_profile,
                    reason=f"api_status_{exc.status_code}",
                    error_type=type(exc).__name__,
                )
            except Exception as exc:
                fallback_reason = "unexpected_error"
                _log_event(
                    "file_search_responses_fallback",
                    request_id=request_id,
                    principal=principal,
                    session_id=req.session_id,
                    retrieval_profile=req.retrieval_profile,
                    reason="unexpected_error",
                    error_type=type(exc).__name__,
                )

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
            include_session_id=session_filter,
            source_types=source_types,
        )
        query_tokens = _tokenize_file_search_text(query)
        ranked: list[tuple[float, float, float, VectorMatch]] = []
        for candidate in candidates:
            keyword_score = _keyword_overlap_score(query_tokens, candidate.content)
            score = (candidate.similarity * 0.78) + (keyword_score * 0.22)
            ranked.append((score, candidate.similarity, keyword_score, candidate))

        ranked.sort(key=lambda item: (item[0], item[1], item[3].created_at), reverse=True)
        top = ranked[: req.limit]

        matches = [
            FileSearchMatchResponse(
                vector_id=candidate.vector_id,
                session_id=_display_session_id(
                    session_id=candidate.session_id,
                    metadata=candidate.metadata,
                ),
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
            retrieval_profile=req.retrieval_profile,
            source_types=list(source_types),
            query_chars=len(query),
            candidate_count=len(candidates),
            result_count=len(matches),
            backend="local_vector_store",
        )
        return FileSearchResponse(
            query=query,
            searched_at=int(time.time() * 1000),
            backend="local_vector_store",
            fallback_reason=fallback_reason,
            candidate_count=len(candidates),
            matches=matches,
        )

    @app.patch("/chats/{session_id}", response_model=ChatSummaryResponse)
    def rename_chat(session_id: str, req: RenameChatRequest, request: Request) -> ChatSummaryResponse:
        deps = _runtime_deps(request.app)
        try:
            summary = deps.history_store.rename_chat(session_id=session_id, title=req.title)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Chat not found.") from exc
        return _chat_summary_response(summary, deps=deps)

    @app.delete("/chats/{session_id}")
    async def delete_chat(session_id: str, request: Request) -> dict[str, str]:
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
        deps = _runtime_deps(request.app)
        try:
            summary = deps.history_store.deprecate_chat(session_id=session_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Chat not found.") from exc
        if deps.vector_store is not None:
            deps.vector_store.deactivate_session(session_id)
        return _chat_summary_response(summary, deps=deps)

    @app.post("/chats/{session_id}/notes")
    def add_note(session_id: str, req: NoteRequest, request: Request) -> dict[str, str]:
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
        principal = None
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
        principal = None
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
        principal = None
        deps = _runtime_deps(request.app)
        session_id = req.session_id or deps.default_session_id
        source_user_message_id = (
            req.source_user_message_id.strip() if req.source_user_message_id else None
        )
        chat = deps.history_store.ensure_chat(session_id=session_id)
        if chat.status == "deprecated":
            raise HTTPException(
                status_code=409,
                detail="Chat is deprecated. Create a new chat before sending messages.",
            )
        if source_user_message_id is not None:
            if not deps.history_store.message_exists(
                session_id=session_id,
                message_id=source_user_message_id,
            ):
                raise HTTPException(status_code=404, detail="source_user_message_id not found in this chat.")
            source_role = deps.history_store.get_message_role(
                session_id=session_id,
                message_id=source_user_message_id,
            )
            if source_role != "user":
                raise HTTPException(status_code=400, detail="source_user_message_id must reference a user message.")
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
            adaptive_style_notes = _derive_adaptive_style_notes(
                deps.history_store.list_message_feedback(session_id=session_id)
            )
            previous_adaptive_signature = deps.adaptive_note_signatures.get(session_id, tuple())
            next_adaptive_signature = tuple(adaptive_style_notes)
            if next_adaptive_signature != previous_adaptive_signature:
                previous_set = set(previous_adaptive_signature)
                next_set = set(next_adaptive_signature)
                _log_event(
                    "adaptive_style_notes_updated",
                    request_id=request_id,
                    session_id=session_id,
                    principal=principal,
                    added_notes=[note for note in adaptive_style_notes if note not in previous_set],
                    removed_notes=[note for note in previous_adaptive_signature if note not in next_set],
                    active_count=len(adaptive_style_notes),
                )
                deps.adaptive_note_signatures[session_id] = next_adaptive_signature
            for note in adaptive_style_notes:
                _append_unique_note(notes, note)
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
            attachment_context_blocks: list[str] = []
            attachment_count = len(req.attachments)
            attachment_evidence_count = 0
            attachment_ocr_texts: list[tuple[str, str]] = []
            guardrail_note: str | None = None
            harness_mode = req.harness_mode or deps.chat_harness_default_mode
            try:
                if harness_mode == "fixture":
                    pipeline = "fixture"
                    output_text = _build_fixture_chat_output(
                        message=req.message,
                        fixture_output=req.fixture_output,
                    )
                elif req.attachments:
                    for idx, attachment in enumerate(req.attachments, start=1):
                        ocr_req = OcrRequest(
                            session_id=session_id,
                            source_name=attachment.source_name,
                            mime_type=attachment.mime_type,
                            data_base64=attachment.data_base64,
                            text_hint=attachment.text_hint,
                            visual_context_hint=attachment.visual_context_hint,
                            transcription_mode=attachment.transcription_mode,
                            memory_scope=attachment.memory_scope,
                            attach_to_chat=False,
                        )
                        index_session_id = _resolve_memory_lane_session_id(
                            session_id=session_id,
                            memory_scope=ocr_req.memory_scope,
                        )
                        dedup_key = _build_ocr_dedup_key(
                            req=ocr_req,
                            deps=deps,
                            principal=principal,
                            session_id=session_id,
                        )
                        dedup_hit = False
                        cached_payload = deps.history_store.get_ingest_dedup_response(
                            dedup_key=dedup_key,
                            operation="ocr",
                        )
                        if cached_payload is not None:
                            try:
                                cached_response = OcrResponse.model_validate(cached_payload)
                            except Exception:
                                _log_event(
                                    "chat_attachment_ocr_dedup_payload_invalid",
                                    request_id=request_id,
                                    session_id=session_id,
                                    principal=principal,
                                )
                            else:
                                dedup_hit = True
                                cached_run = cached_response.run
                                extracted_text = cached_run.extracted_text
                                visual_context = (cached_run.visual_context or "").strip() or None
                                run_id = cached_run.run_id
                                run_status = cached_run.status
                                run_source_name = cached_run.source_name

                        if not dedup_hit:
                            extracted_text, status = _extract_text(ocr_req, deps)
                            visual_context = _extract_image_context(
                                req=ocr_req,
                                deps=deps,
                                request_id=request_id,
                                session_id=session_id,
                                principal=principal,
                            )
                            run = deps.history_store.record_ocr_run(
                                run_id=f"ocr-{uuid.uuid4().hex[:12]}",
                                session_id=session_id,
                                source_name=ocr_req.source_name,
                                mime_type=ocr_req.mime_type,
                                source_message_id=None,
                                result_message_id=None,
                                status=status,
                                extracted_text=extracted_text,
                            )
                            _index_ocr_output(
                                deps=deps,
                                session_id=index_session_id,
                                run=run,
                                origin_session_id=session_id,
                                visual_context=visual_context,
                            )
                            dedup_payload = OcrResponse(
                                run=OcrRunResponse(
                                    run_id=run.run_id,
                                    session_id=run.session_id,
                                    source_name=run.source_name,
                                    mime_type=run.mime_type,
                                    source_message_id=run.source_message_id,
                                    result_message_id=run.result_message_id,
                                    status=run.status,
                                    extracted_text=run.extracted_text,
                                    visual_context=visual_context,
                                    structured=_build_structured_extraction(
                                        source_type="ocr",
                                        source_name=run.source_name,
                                        mime_type=run.mime_type,
                                        text=run.extracted_text,
                                    ),
                                    created_at=run.created_at,
                                )
                            )
                            deps.history_store.record_ingest_dedup_response(
                                dedup_key=dedup_key,
                                operation="ocr",
                                session_id=session_id,
                                response_payload=dedup_payload.model_dump(),
                            )
                            run_id = run.run_id
                            run_status = run.status
                            run_source_name = run.source_name

                        source_label = (ocr_req.source_name or f"attachment_{idx}").strip()
                        attachment_ocr_texts.append((source_label, extracted_text))
                        context_parts: list[str] = []
                        text_for_context = extracted_text.strip()
                        if _has_meaningful_ocr_text(text_for_context):
                            context_parts.append(f"[OCR_TEXT • {source_label}]\n{text_for_context}")
                        visual_for_context = (visual_context or "").strip()
                        if visual_for_context:
                            context_parts.append(f"[IMAGE_CONTEXT • {source_label}]\n{visual_for_context}")
                        if context_parts:
                            attachment_context_blocks.append("\n\n".join(context_parts))
                            attachment_evidence_count += 1

                        _log_event(
                            "chat_attachment_ocr_run",
                            request_id=request_id,
                            session_id=session_id,
                            principal=principal,
                            run_id=run_id,
                            source_name=run_source_name,
                            status=run_status,
                            chars=len(extracted_text),
                            memory_scope=_normalize_memory_scope(ocr_req.memory_scope, default="session"),
                            index_session_id=index_session_id,
                            dedup_hit=dedup_hit,
                        )

                if harness_mode != "fixture":
                    has_recent_ocr = _has_recent_ocr_activity(deps=deps, session_id=session_id)
                    if req.attachments and _looks_like_ocr_request(req.message):
                        output_text = _build_attachment_literal_reply(attachment_ocr_texts)
                    elif not req.attachments and _looks_like_ocr_followup_without_new_image(req.message):
                        output_text = _OCR_STRICT_NO_NEW_IMAGE_REPLY
                    elif (
                        not req.attachments
                        and has_recent_ocr
                        and _looks_like_ocr_correction_without_new_image(req.message)
                    ):
                        output_text = _OCR_STRICT_NO_NEW_IMAGE_REPLY
                    elif deps.responses_orchestration_enabled:
                        pipeline = "responses"
                        guardrail_note = _build_hallucination_guardrail_note(
                            deps=deps,
                            query_text=req.message,
                            evidence_count=attachment_evidence_count,
                        )
                        output_text, orchestration_tools = _chat_with_responses_orchestration(
                            deps=deps,
                            request_id=request_id,
                            principal=principal,
                            session_id=session_id,
                            user_message=req.message,
                            notes=notes,
                            attachment_context_blocks=attachment_context_blocks,
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
                            evidence_count=len(retrieved_memory) + attachment_evidence_count,
                        )
                        model_input = _compose_model_input(
                            user_message=req.message,
                            notes=notes,
                            retrieved_memory=retrieved_memory,
                            max_memory_chars=deps.vector_max_chars,
                            attachment_context_blocks=attachment_context_blocks,
                            guardrail_note=guardrail_note,
                            collaboration_note=collaboration_note,
                        )
                        low_evidence_reply = _low_evidence_factual_reply(
                            req.message, len(retrieved_memory) + attachment_evidence_count
                        )
                        if low_evidence_reply is not None:
                            output_text = low_evidence_reply
                        else:
                            result = await Runner.run(
                                deps.agent,
                                model_input,
                                run_config=_factual_run_config(
                                    deps=deps,
                                    query_text=req.message,
                                    evidence_count=len(retrieved_memory),
                                ),
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

            if source_user_message_id is None:
                deps.history_store.append_message(session_id=session_id, role="user", content=req.message)
            assistant_message = deps.history_store.append_message(
                session_id=session_id,
                role="assistant",
                content=output_text,
                parent_message_id_override=source_user_message_id,
            )
            _index_assistant_output(
                deps=deps,
                session_id=session_id,
                message_id=assistant_message.message_id,
                content=assistant_message.content,
                created_at=assistant_message.created_at,
            )
            if source_user_message_id is None:
                deps.history_store.maybe_set_title_from_first_user_message(
                    session_id=session_id,
                    user_message=req.message,
                )
            response = ChatResponse(
                output=output_text,
                session_id=session_id,
                assistant_message_id=assistant_message.message_id,
                prompt_version=ACTIVE_PROMPT_VERSION,
                memory_scope=_normalize_memory_scope(memory_scope, default="global"),
                context_scope=_context_scope_from_memory_scope(memory_scope),
                memory_used=[
                    _memory_citation_response(
                        item,
                        max_chars=min(deps.vector_max_chars, _CHAT_MEMORY_CITATION_MAX_CHARS),
                    )
                    for item in retrieved_memory
                ],
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
                attachment_count=attachment_count,
                attachment_evidence_count=attachment_evidence_count,
                memory_scope=memory_scope,
                variant_retry=source_user_message_id is not None,
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
        principal = None
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
