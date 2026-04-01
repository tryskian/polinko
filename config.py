from dataclasses import dataclass
import os
from typing import Literal

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    openai_api_key: str
    session_db_path: str
    history_db_path: str
    default_session_id: str
    log_level: str
    rate_limit_per_minute: int
    deprecate_on_reset: bool
    ocr_provider: str
    ocr_model: str
    ocr_prompt: str
    ocr_uncertainty_safe: bool
    image_context_enabled: bool
    image_context_model: str
    image_context_prompt: str
    vector_enabled: bool
    vector_db_path: str
    vector_embedding_model: str
    vector_top_k: int
    vector_top_k_global: int
    vector_top_k_session: int
    vector_min_similarity: float
    vector_min_similarity_global: float
    vector_min_similarity_session: float
    vector_max_chars: int
    vector_exclude_current_session: bool
    vector_local_embedding_fallback: bool
    responses_orchestration_enabled: bool
    responses_orchestration_model: str
    responses_vector_store_id: str | None
    responses_include_web_search: bool
    responses_history_turn_limit: int
    responses_pdf_ingest_enabled: bool
    extraction_structured_enabled: bool
    extraction_structured_model: str
    governance_enabled: bool
    governance_allow_web_search: bool
    governance_log_only: bool
    hallucination_guardrails_enabled: bool
    personalization_default_memory_scope: str
    clip_proxy_file_search_enabled: bool
    chat_harness_default_mode: Literal["live", "fixture"]


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


def _normalize_quoted_env_value(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if (
        len(normalized) >= 2
        and normalized[0] == normalized[-1]
        and normalized[0] in {'"', "'"}
    ):
        return normalized[1:-1].strip()
    return normalized


def _read_env(name: str, default: str | None = None) -> str | None:
    raw_value = os.getenv(name)
    if raw_value is None:
        raw_value = default
    return _normalize_quoted_env_value(raw_value)


def _validate_openai_api_key(openai_api_key: str | None) -> str:
    normalized_key = _normalize_quoted_env_value(openai_api_key)
    if not normalized_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to .env or export it before starting. "
            "If CI eval fails, also set the GitHub Actions secret OPENAI_API_KEY."
        )
    if not normalized_key.startswith("sk-"):
        raise RuntimeError("OPENAI_API_KEY appears invalid (expected it to start with 'sk-').")
    if len(normalized_key) < 20:
        raise RuntimeError("OPENAI_API_KEY appears too short; check your .env value.")
    if _looks_like_placeholder(normalized_key):
        raise RuntimeError("OPENAI_API_KEY is a placeholder value; set a real key.")
    return normalized_key


def _parse_bool_env(name: str, default: bool) -> bool:
    raw = _read_env(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    truthy = {"1", "true", "yes", "on"}
    falsy = {"0", "false", "no", "off"}
    if normalized in truthy:
        return True
    if normalized in falsy:
        return False
    raise RuntimeError(f"{name} must be a boolean (true/false).")


def _parse_int_env(name: str, default: int, *, minimum: int = 0) -> int:
    raw = _read_env(name)
    if raw is None or not raw.strip():
        value = default
    else:
        try:
            value = int(raw)
        except ValueError as exc:
            raise RuntimeError(f"{name} must be an integer.") from exc
    if value < minimum:
        raise RuntimeError(f"{name} must be >= {minimum}.")
    return value


def _parse_float_env(name: str, default: float, *, minimum: float = 0.0, maximum: float = 1.0) -> float:
    raw = _read_env(name)
    if raw is None or not raw.strip():
        value = default
    else:
        try:
            value = float(raw)
        except ValueError as exc:
            raise RuntimeError(f"{name} must be a float.") from exc
    if value < minimum or value > maximum:
        raise RuntimeError(f"{name} must be between {minimum} and {maximum}.")
    return value


def _validate_ocr_provider(value: str | None) -> str:
    normalized = (value or "scaffold").strip().lower()
    if normalized in {"scaffold", "openai"}:
        return normalized
    raise RuntimeError("POLINKO_OCR_PROVIDER must be one of: scaffold, openai.")


def _validate_personalization_memory_scope(value: str | None) -> str:
    normalized = (value or "global").strip().lower()
    if normalized in {"session", "global"}:
        return normalized
    raise RuntimeError("POLINKO_PERSONALIZATION_DEFAULT_MEMORY_SCOPE must be one of: session, global.")


def _validate_chat_harness_mode(value: str | None) -> Literal["live", "fixture"]:
    normalized = (value or "live").strip().lower()
    if normalized == "live":
        return "live"
    if normalized == "fixture":
        return "fixture"
    raise RuntimeError("POLINKO_CHAT_HARNESS_DEFAULT_MODE must be one of: live, fixture.")


def load_config(dotenv_path: str = ".env") -> AppConfig:
    load_dotenv(dotenv_path=dotenv_path)

    openai_api_key = _validate_openai_api_key(_read_env("OPENAI_API_KEY"))
    log_level = (_read_env("POLINKO_LOG_LEVEL", "INFO") or "INFO").upper()
    default_session_id = _read_env("POLINKO_DEFAULT_SESSION_ID", "default") or "default"
    session_db_path = (
        _read_env("POLINKO_MEMORY_DB_PATH", ".local/runtime_dbs/active/memory.db")
        or ".local/runtime_dbs/active/memory.db"
    )
    history_db_path = (
        _read_env("POLINKO_HISTORY_DB_PATH", ".local/runtime_dbs/active/history.db")
        or ".local/runtime_dbs/active/history.db"
    )

    raw_rate_limit = _read_env("POLINKO_RATE_LIMIT_PER_MINUTE", "30") or "30"
    try:
        rate_limit_per_minute = int(raw_rate_limit)
    except ValueError as exc:
        raise RuntimeError(
            "POLINKO_RATE_LIMIT_PER_MINUTE must be an integer."
        ) from exc
    deprecate_on_reset = _parse_bool_env("POLINKO_DEPRECATE_ON_RESET", True)
    ocr_provider = _validate_ocr_provider(_read_env("POLINKO_OCR_PROVIDER"))
    ocr_model = (_read_env("POLINKO_OCR_MODEL", "gpt-4.1-mini") or "gpt-4.1-mini").strip() or "gpt-4.1-mini"
    ocr_prompt = (
        (
            _read_env(
                "POLINKO_OCR_PROMPT",
                "Extract all readable text from this image. Preserve line breaks and symbols exactly. "
                "Do not invent letters or words; if uncertain, output [?].",
            )
            or "Extract all readable text from this image. Preserve line breaks and symbols exactly. "
            "Do not invent letters or words; if uncertain, output [?]."
        ).strip()
        or "Extract all readable text from this image. Preserve line breaks and symbols exactly. "
        "Do not invent letters or words; if uncertain, output [?]."
    )
    ocr_uncertainty_safe = _parse_bool_env("POLINKO_OCR_UNCERTAINTY_SAFE", True)
    image_context_enabled = _parse_bool_env("POLINKO_IMAGE_CONTEXT_ENABLED", False)
    image_context_model = (
        _read_env("POLINKO_IMAGE_CONTEXT_MODEL", "gpt-4.1-mini") or "gpt-4.1-mini"
    ).strip() or "gpt-4.1-mini"
    image_context_prompt = (
        (
            _read_env(
                "POLINKO_IMAGE_CONTEXT_PROMPT",
                "Summarize the visual scene for retrieval: key entities, visible text cues, layout, and notable attributes. Keep it concise, factual, and grounded in what is visible.",
            )
            or "Summarize the visual scene for retrieval: key entities, visible text cues, layout, and notable attributes. Keep it concise, factual, and grounded in what is visible."
        ).strip()
        or "Summarize the visual scene for retrieval: key entities, visible text cues, layout, and notable attributes. Keep it concise, factual, and grounded in what is visible."
    )
    vector_enabled = _parse_bool_env("POLINKO_VECTOR_ENABLED", False)
    vector_db_path = (
        _read_env("POLINKO_VECTOR_DB_PATH", ".local/runtime_dbs/active/vector.db")
        or ".local/runtime_dbs/active/vector.db"
    )
    vector_embedding_model = (
        (_read_env("POLINKO_VECTOR_EMBEDDING_MODEL", "text-embedding-3-small") or "text-embedding-3-small").strip()
        or "text-embedding-3-small"
    )
    vector_top_k = _parse_int_env("POLINKO_VECTOR_TOP_K", 2, minimum=1)
    vector_top_k_global = _parse_int_env("POLINKO_VECTOR_TOP_K_GLOBAL", vector_top_k, minimum=1)
    vector_top_k_session = _parse_int_env("POLINKO_VECTOR_TOP_K_SESSION", vector_top_k, minimum=1)
    vector_min_similarity = _parse_float_env("POLINKO_VECTOR_MIN_SIMILARITY", 0.40, minimum=0.0, maximum=1.0)
    vector_min_similarity_global = _parse_float_env(
        "POLINKO_VECTOR_MIN_SIMILARITY_GLOBAL",
        vector_min_similarity,
        minimum=0.0,
        maximum=1.0,
    )
    vector_min_similarity_session = _parse_float_env(
        "POLINKO_VECTOR_MIN_SIMILARITY_SESSION",
        vector_min_similarity,
        minimum=0.0,
        maximum=1.0,
    )
    vector_max_chars = _parse_int_env("POLINKO_VECTOR_MAX_CHARS", 220, minimum=80)
    vector_exclude_current_session = _parse_bool_env("POLINKO_VECTOR_EXCLUDE_CURRENT_SESSION", True)
    vector_local_embedding_fallback = _parse_bool_env(
        "POLINKO_VECTOR_LOCAL_EMBEDDING_FALLBACK",
        False,
    )
    responses_orchestration_enabled = _parse_bool_env("POLINKO_RESPONSES_ORCHESTRATION_ENABLED", False)
    responses_orchestration_model = (
        (_read_env("POLINKO_RESPONSES_MODEL", "gpt-5-chat-latest") or "gpt-5-chat-latest").strip()
        or "gpt-5-chat-latest"
    )
    raw_responses_vector_store_id = _read_env("POLINKO_RESPONSES_VECTOR_STORE_ID")
    responses_vector_store_id = (
        raw_responses_vector_store_id.strip()
        if raw_responses_vector_store_id and raw_responses_vector_store_id.strip()
        else None
    )
    responses_include_web_search = _parse_bool_env("POLINKO_RESPONSES_INCLUDE_WEB_SEARCH", False)
    responses_history_turn_limit = _parse_int_env("POLINKO_RESPONSES_HISTORY_TURN_LIMIT", 12, minimum=1)
    responses_pdf_ingest_enabled = _parse_bool_env("POLINKO_RESPONSES_PDF_INGEST_ENABLED", False)
    extraction_structured_enabled = _parse_bool_env("POLINKO_EXTRACTION_STRUCTURED_ENABLED", False)
    extraction_structured_model = (
        (_read_env("POLINKO_EXTRACTION_STRUCTURED_MODEL", "gpt-4.1-mini") or "gpt-4.1-mini").strip()
        or "gpt-4.1-mini"
    )
    governance_enabled = _parse_bool_env("POLINKO_GOVERNANCE_ENABLED", True)
    governance_allow_web_search = _parse_bool_env("POLINKO_GOVERNANCE_ALLOW_WEB_SEARCH", False)
    governance_log_only = _parse_bool_env("POLINKO_GOVERNANCE_LOG_ONLY", False)
    hallucination_guardrails_enabled = _parse_bool_env("POLINKO_HALLUCINATION_GUARDRAILS_ENABLED", True)
    personalization_default_memory_scope = _validate_personalization_memory_scope(
        _read_env("POLINKO_PERSONALIZATION_DEFAULT_MEMORY_SCOPE", "global")
    )
    clip_proxy_file_search_enabled = _parse_bool_env("POLINKO_CLIP_PROXY_FILE_SEARCH_ENABLED", False)
    chat_harness_default_mode = _validate_chat_harness_mode(
        _read_env("POLINKO_CHAT_HARNESS_DEFAULT_MODE", "live")
    )

    if responses_orchestration_enabled and not responses_vector_store_id:
        raise RuntimeError(
            "POLINKO_RESPONSES_VECTOR_STORE_ID is required when "
            "POLINKO_RESPONSES_ORCHESTRATION_ENABLED=true."
        )
    if responses_pdf_ingest_enabled and not responses_vector_store_id:
        raise RuntimeError(
            "POLINKO_RESPONSES_VECTOR_STORE_ID is required when "
            "POLINKO_RESPONSES_PDF_INGEST_ENABLED=true."
        )

    return AppConfig(
        openai_api_key=openai_api_key,
        session_db_path=session_db_path,
        history_db_path=history_db_path,
        default_session_id=default_session_id,
        log_level=log_level,
        rate_limit_per_minute=rate_limit_per_minute,
        deprecate_on_reset=deprecate_on_reset,
        ocr_provider=ocr_provider,
        ocr_model=ocr_model,
        ocr_prompt=ocr_prompt,
        ocr_uncertainty_safe=ocr_uncertainty_safe,
        image_context_enabled=image_context_enabled,
        image_context_model=image_context_model,
        image_context_prompt=image_context_prompt,
        vector_enabled=vector_enabled,
        vector_db_path=vector_db_path,
        vector_embedding_model=vector_embedding_model,
        vector_top_k=vector_top_k,
        vector_top_k_global=vector_top_k_global,
        vector_top_k_session=vector_top_k_session,
        vector_min_similarity=vector_min_similarity,
        vector_min_similarity_global=vector_min_similarity_global,
        vector_min_similarity_session=vector_min_similarity_session,
        vector_max_chars=vector_max_chars,
        vector_exclude_current_session=vector_exclude_current_session,
        vector_local_embedding_fallback=vector_local_embedding_fallback,
        responses_orchestration_enabled=responses_orchestration_enabled,
        responses_orchestration_model=responses_orchestration_model,
        responses_vector_store_id=responses_vector_store_id,
        responses_include_web_search=responses_include_web_search,
        responses_history_turn_limit=responses_history_turn_limit,
        responses_pdf_ingest_enabled=responses_pdf_ingest_enabled,
        extraction_structured_enabled=extraction_structured_enabled,
        extraction_structured_model=extraction_structured_model,
        governance_enabled=governance_enabled,
        governance_allow_web_search=governance_allow_web_search,
        governance_log_only=governance_log_only,
        hallucination_guardrails_enabled=hallucination_guardrails_enabled,
        personalization_default_memory_scope=personalization_default_memory_scope,
        clip_proxy_file_search_enabled=clip_proxy_file_search_enabled,
        chat_harness_default_mode=chat_harness_default_mode,
    )
