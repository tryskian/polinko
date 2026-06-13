from __future__ import annotations

from pathlib import Path
from typing import Any


def int_value(value: object) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return 0
        return int(value)
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def display_text(value: object) -> str:
    text = normalize_text(value)
    return text if text else "none"


def truncate_text(value: object, *, max_chars: int = 180) -> str:
    text = normalize_text(value)
    if len(text) <= max_chars:
        return text
    return text[: max(0, max_chars - 1)].rstrip() + "..."


def format_feedback_ids(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "none"
    return ",".join(str(int_value(item)) for item in value)


def format_readiness_flags(readiness: dict[str, Any]) -> str:
    flags = readiness.get("flags")
    if not isinstance(flags, list) or not flags:
        return "none"
    return ",".join(str(item) for item in flags)


def format_input_blocker_state(value: object) -> str:
    if not isinstance(value, dict):
        return "unknown"
    state = str(value.get("state") or "unknown")
    reason_code = str(value.get("reason_code") or "")
    next_action = str(value.get("next_action") or "")
    if not reason_code and not next_action:
        return state
    parts = [state]
    if reason_code:
        parts.append(f"reason={reason_code}")
    if next_action:
        parts.append(f"next={next_action}")
    return " ".join(parts)


def format_plan_thumbnail(value: object) -> str:
    if not isinstance(value, dict) or not value.get("available"):
        return "none"
    return f"{int_value(value.get('width'))}x{int_value(value.get('height'))}"


def format_terminal_source_path(value: object) -> str:
    raw_path = str(value or "").strip()
    if not raw_path:
        return "none"
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path.name or "none"
    return raw_path


def format_plan_source_preview(value: object) -> str:
    if not isinstance(value, dict):
        return "unknown"
    preview = truncate_text(value.get("source_preview"), max_chars=100)
    return (
        f"feedback={int_value(value.get('feedback_id'))} "
        f"message={value.get('message_id') or 'unknown'} "
        f"source_state={value.get('source_state') or 'unknown'} "
        f"role={value.get('source_role') or 'unknown'} "
        f"preview={preview or 'none'}"
    )
