from dataclasses import dataclass
import json
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    openai_api_key: str
    session_db_path: str
    history_db_path: str
    default_session_id: str
    log_level: str
    server_api_key: str | None
    server_api_key_principals: dict[str, str]
    rate_limit_per_minute: int
    deprecate_on_reset: bool
    ocr_provider: str
    ocr_model: str
    ocr_prompt: str
    vector_enabled: bool
    vector_db_path: str
    vector_embedding_model: str
    vector_top_k: int
    vector_min_similarity: float
    vector_max_chars: int
    vector_exclude_current_session: bool
    responses_orchestration_enabled: bool
    responses_orchestration_model: str
    responses_vector_store_id: str | None
    responses_include_web_search: bool
    responses_history_turn_limit: int
    governance_enabled: bool
    governance_allow_web_search: bool
    governance_log_only: bool
    hallucination_guardrails_enabled: bool


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


def _validate_openai_api_key(openai_api_key: str | None) -> str:
    if not openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to .env or export it before starting. "
            "If CI eval fails, also set the GitHub Actions secret OPENAI_API_KEY."
        )
    if not openai_api_key.startswith("sk-"):
        raise RuntimeError("OPENAI_API_KEY appears invalid (expected it to start with 'sk-').")
    if len(openai_api_key) < 20:
        raise RuntimeError("OPENAI_API_KEY appears too short; check your .env value.")
    if _looks_like_placeholder(openai_api_key):
        raise RuntimeError("OPENAI_API_KEY is a placeholder value; set a real key.")
    return openai_api_key


def _validate_server_api_key(server_api_key: str | None) -> str | None:
    if not server_api_key:
        return None
    if len(server_api_key) < 12:
        raise RuntimeError("POLINKO_SERVER_API_KEY is too short; use at least 12 characters.")
    if _looks_like_placeholder(server_api_key):
        raise RuntimeError("POLINKO_SERVER_API_KEY is a placeholder value; set a real key.")
    return server_api_key


def _validate_principal(principal: str) -> str:
    value = principal.strip()
    if not value:
        raise RuntimeError("POLINKO_SERVER_API_KEYS_JSON contains an empty principal name.")
    return value


def _load_server_api_key_principals(single_server_api_key: str | None) -> dict[str, str]:
    principals: dict[str, str] = {}
    if single_server_api_key:
        principals[single_server_api_key] = "default"

    raw_json = os.getenv("POLINKO_SERVER_API_KEYS_JSON", "").strip()
    if not raw_json:
        return principals

    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "POLINKO_SERVER_API_KEYS_JSON must be valid JSON object: "
            '{"principal":"api-key","principal2":"api-key-2"}'
        ) from exc

    if not isinstance(parsed, dict):
        raise RuntimeError("POLINKO_SERVER_API_KEYS_JSON must be a JSON object.")

    for raw_principal, raw_key in parsed.items():
        if not isinstance(raw_principal, str) or not isinstance(raw_key, str):
            raise RuntimeError(
                "POLINKO_SERVER_API_KEYS_JSON values must be string pairs: "
                '{"principal":"api-key"}'
            )
        principal = _validate_principal(raw_principal)
        key = _validate_server_api_key(raw_key)
        if not key:
            continue
        existing_principal = principals.get(key)
        if existing_principal and existing_principal != principal:
            raise RuntimeError(
                "Duplicate API key mapped to different principals in "
                "POLINKO_SERVER_API_KEYS_JSON."
            )
        principals[key] = principal

    return principals


def _parse_bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
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
    raw = os.getenv(name)
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
    raw = os.getenv(name)
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


def load_config(dotenv_path: str = ".env") -> AppConfig:
    load_dotenv(dotenv_path=dotenv_path)

    openai_api_key = _validate_openai_api_key(os.getenv("OPENAI_API_KEY"))
    server_api_key = _validate_server_api_key(os.getenv("POLINKO_SERVER_API_KEY"))
    server_api_key_principals = _load_server_api_key_principals(server_api_key)
    log_level = os.getenv("POLINKO_LOG_LEVEL", "INFO").upper()
    default_session_id = os.getenv("POLINKO_DEFAULT_SESSION_ID", "default")
    session_db_path = os.getenv("POLINKO_MEMORY_DB_PATH", ".polinko_memory.db")
    history_db_path = os.getenv("POLINKO_HISTORY_DB_PATH", ".polinko_history.db")

    raw_rate_limit = os.getenv("POLINKO_RATE_LIMIT_PER_MINUTE", "30")
    try:
        rate_limit_per_minute = int(raw_rate_limit)
    except ValueError as exc:
        raise RuntimeError(
            "POLINKO_RATE_LIMIT_PER_MINUTE must be an integer."
        ) from exc
    deprecate_on_reset = _parse_bool_env("POLINKO_DEPRECATE_ON_RESET", True)
    ocr_provider = _validate_ocr_provider(os.getenv("POLINKO_OCR_PROVIDER"))
    ocr_model = os.getenv("POLINKO_OCR_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini"
    ocr_prompt = (
        os.getenv(
            "POLINKO_OCR_PROMPT",
            "Extract all readable text from this image. Return only the extracted text and preserve line breaks.",
        ).strip()
        or "Extract all readable text from this image. Return only the extracted text and preserve line breaks."
    )
    vector_enabled = _parse_bool_env("POLINKO_VECTOR_ENABLED", False)
    vector_db_path = os.getenv("POLINKO_VECTOR_DB_PATH", ".polinko_vector.db")
    vector_embedding_model = (
        os.getenv("POLINKO_VECTOR_EMBEDDING_MODEL", "text-embedding-3-small").strip()
        or "text-embedding-3-small"
    )
    vector_top_k = _parse_int_env("POLINKO_VECTOR_TOP_K", 2, minimum=1)
    vector_min_similarity = _parse_float_env("POLINKO_VECTOR_MIN_SIMILARITY", 0.40, minimum=0.0, maximum=1.0)
    vector_max_chars = _parse_int_env("POLINKO_VECTOR_MAX_CHARS", 220, minimum=80)
    vector_exclude_current_session = _parse_bool_env("POLINKO_VECTOR_EXCLUDE_CURRENT_SESSION", True)
    responses_orchestration_enabled = _parse_bool_env("POLINKO_RESPONSES_ORCHESTRATION_ENABLED", False)
    responses_orchestration_model = (
        os.getenv("POLINKO_RESPONSES_MODEL", "gpt-5-chat-latest").strip() or "gpt-5-chat-latest"
    )
    raw_responses_vector_store_id = os.getenv("POLINKO_RESPONSES_VECTOR_STORE_ID")
    responses_vector_store_id = (
        raw_responses_vector_store_id.strip()
        if raw_responses_vector_store_id and raw_responses_vector_store_id.strip()
        else None
    )
    responses_include_web_search = _parse_bool_env("POLINKO_RESPONSES_INCLUDE_WEB_SEARCH", False)
    responses_history_turn_limit = _parse_int_env("POLINKO_RESPONSES_HISTORY_TURN_LIMIT", 12, minimum=1)
    governance_enabled = _parse_bool_env("POLINKO_GOVERNANCE_ENABLED", True)
    governance_allow_web_search = _parse_bool_env("POLINKO_GOVERNANCE_ALLOW_WEB_SEARCH", False)
    governance_log_only = _parse_bool_env("POLINKO_GOVERNANCE_LOG_ONLY", False)
    hallucination_guardrails_enabled = _parse_bool_env("POLINKO_HALLUCINATION_GUARDRAILS_ENABLED", True)

    if responses_orchestration_enabled and not responses_vector_store_id:
        raise RuntimeError(
            "POLINKO_RESPONSES_VECTOR_STORE_ID is required when "
            "POLINKO_RESPONSES_ORCHESTRATION_ENABLED=true."
        )

    return AppConfig(
        openai_api_key=openai_api_key,
        session_db_path=session_db_path,
        history_db_path=history_db_path,
        default_session_id=default_session_id,
        log_level=log_level,
        server_api_key=server_api_key,
        server_api_key_principals=server_api_key_principals,
        rate_limit_per_minute=rate_limit_per_minute,
        deprecate_on_reset=deprecate_on_reset,
        ocr_provider=ocr_provider,
        ocr_model=ocr_model,
        ocr_prompt=ocr_prompt,
        vector_enabled=vector_enabled,
        vector_db_path=vector_db_path,
        vector_embedding_model=vector_embedding_model,
        vector_top_k=vector_top_k,
        vector_min_similarity=vector_min_similarity,
        vector_max_chars=vector_max_chars,
        vector_exclude_current_session=vector_exclude_current_session,
        responses_orchestration_enabled=responses_orchestration_enabled,
        responses_orchestration_model=responses_orchestration_model,
        responses_vector_store_id=responses_vector_store_id,
        responses_include_web_search=responses_include_web_search,
        responses_history_turn_limit=responses_history_turn_limit,
        governance_enabled=governance_enabled,
        governance_allow_web_search=governance_allow_web_search,
        governance_log_only=governance_log_only,
        hallucination_guardrails_enabled=hallucination_guardrails_enabled,
    )
