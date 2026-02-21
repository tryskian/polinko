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

    return AppConfig(
        openai_api_key=openai_api_key,
        session_db_path=session_db_path,
        history_db_path=history_db_path,
        default_session_id=default_session_id,
        log_level=log_level,
        server_api_key=server_api_key,
        server_api_key_principals=server_api_key_principals,
        rate_limit_per_minute=rate_limit_per_minute,
    )
