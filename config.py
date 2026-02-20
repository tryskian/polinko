from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    openai_api_key: str
    session_db_path: str
    default_session_id: str
    log_level: str
    server_api_key: str | None
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


def load_config(dotenv_path: str = ".env") -> AppConfig:
    load_dotenv(dotenv_path=dotenv_path)

    openai_api_key = _validate_openai_api_key(os.getenv("OPENAI_API_KEY"))
    server_api_key = _validate_server_api_key(os.getenv("POLINKO_SERVER_API_KEY"))
    log_level = os.getenv("POLINKO_LOG_LEVEL", "INFO").upper()
    default_session_id = os.getenv("POLINKO_DEFAULT_SESSION_ID", "default")
    session_db_path = os.getenv("POLINKO_MEMORY_DB_PATH", ".polinko_memory.db")

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
        default_session_id=default_session_id,
        log_level=log_level,
        server_api_key=server_api_key,
        rate_limit_per_minute=rate_limit_per_minute,
    )
