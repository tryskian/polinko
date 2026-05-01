from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

RequestJsonFn = Callable[..., dict[str, Any]]


def default_headers() -> dict[str, str]:
    return {"Content-Type": "application/json"}


def normalize_terms(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    terms: list[str] = []
    for item in value:
        term = str(item).strip().lower()
        if term:
            terms.append(term)
    return terms


def find_expected_citation(
    *,
    memory_used: list[dict[str, Any]],
    seed_session: str,
    source_type: str,
    must_include_terms: list[str],
) -> dict[str, Any] | None:
    expected_source = source_type.strip().lower()
    for item in memory_used:
        if str(item.get("session_id", "")) != seed_session:
            continue
        if str(item.get("source_type", "")).strip().lower() != expected_source:
            continue
        snippet = str(item.get("snippet", "")).lower()
        if all(term in snippet for term in must_include_terms):
            return item
    return None


def has_cross_session_leak(
    memory_used: list[dict[str, Any]], seed_session: str
) -> bool:
    return any(str(item.get("session_id", "")) == seed_session for item in memory_used)


def load_cases(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Cases file must be a JSON object.")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise RuntimeError("Cases file must include a non-empty 'cases' list.")
    normalized: list[dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            raise RuntimeError(f"Case #{index} must be an object.")
        case_id = str(case.get("id", f"case-{index}")).strip()
        seed_text = str(case.get("seed_text", "")).strip()
        query = str(case.get("query", "")).strip()
        source_type = str(case.get("source_type", "ocr")).strip().lower() or "ocr"
        required_terms = normalize_terms(case.get("must_include"))
        if not case_id or not seed_text or not query:
            raise RuntimeError(
                f"Case #{index} is missing required fields ('id', 'seed_text', 'query')."
            )
        normalized.append(
            {
                "id": case_id,
                "seed_text": seed_text,
                "query": query,
                "source_type": source_type,
                "must_include": required_terms,
            }
        )
    return normalized


def create_chat(
    *,
    request_json: RequestJsonFn,
    base_url: str,
    headers: dict[str, str],
    session_id: str,
    timeout: int,
    retries: int,
    retry_delay_ms: int,
) -> None:
    request_json(
        method="POST",
        base_url=base_url,
        path="/chats",
        headers=headers,
        payload={"session_id": session_id, "title": session_id},
        timeout=timeout,
        retries=retries,
        retry_delay_ms=retry_delay_ms,
    )


def delete_chat(
    *,
    request_json: RequestJsonFn,
    base_url: str,
    headers: dict[str, str],
    session_id: str,
    timeout: int,
    retries: int,
    retry_delay_ms: int,
) -> None:
    request_json(
        method="DELETE",
        base_url=base_url,
        path=f"/chats/{session_id}",
        headers=headers,
        timeout=timeout,
        retries=retries,
        retry_delay_ms=retry_delay_ms,
    )


def set_memory_scope(
    *,
    request_json: RequestJsonFn,
    base_url: str,
    headers: dict[str, str],
    session_id: str,
    scope: str,
    timeout: int,
    retries: int,
    retry_delay_ms: int,
) -> None:
    request_json(
        method="POST",
        base_url=base_url,
        path=f"/chats/{session_id}/personalization",
        headers=headers,
        payload={"memory_scope": scope},
        timeout=timeout,
        retries=retries,
        retry_delay_ms=retry_delay_ms,
    )


def seed_ocr_memory(
    *,
    request_json: RequestJsonFn,
    base_url: str,
    headers: dict[str, str],
    session_id: str,
    source_name: str,
    text: str,
    timeout: int,
    retries: int,
    retry_delay_ms: int,
) -> dict[str, Any]:
    return request_json(
        method="POST",
        base_url=base_url,
        path="/skills/ocr",
        headers=headers,
        payload={
            "session_id": session_id,
            "source_name": source_name,
            "mime_type": "text/plain",
            "text_hint": text,
            "attach_to_chat": False,
        },
        timeout=timeout,
        retries=retries,
        retry_delay_ms=retry_delay_ms,
    )


def chat_message(
    *,
    request_json: RequestJsonFn,
    base_url: str,
    headers: dict[str, str],
    session_id: str,
    message: str,
    timeout: int,
    retries: int,
    retry_delay_ms: int,
) -> dict[str, Any]:
    return request_json(
        method="POST",
        base_url=base_url,
        path="/chat",
        headers=headers,
        payload={"session_id": session_id, "message": message},
        timeout=timeout,
        retries=retries,
        retry_delay_ms=retry_delay_ms,
    )


def preflight(
    *,
    request_json: RequestJsonFn,
    base_url: str,
    headers: dict[str, str],
    timeout: int,
    retries: int,
    retry_delay_ms: int,
) -> None:
    health = request_json(
        method="GET",
        base_url=base_url,
        path="/health",
        headers=headers,
        timeout=timeout,
        retries=retries,
        retry_delay_ms=retry_delay_ms,
    )
    status = str(health.get("status", "")).lower()
    if status != "ok":
        raise RuntimeError(f"GET /health returned unexpected payload: {health}")

    request_json(
        method="GET",
        base_url=base_url,
        path="/chats",
        headers=headers,
        timeout=timeout,
        retries=retries,
        retry_delay_ms=retry_delay_ms,
    )
