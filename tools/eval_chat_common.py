from __future__ import annotations

from typing import Any

import requests


def default_headers() -> dict[str, str]:
    return {"Content-Type": "application/json"}


def request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
    payload: dict[str, Any] | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    try:
        response = requests.request(
            method=method,
            url=f"{base_url}{path}",
            headers=headers,
            json=payload,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"{method} {path} failed: connection error - {exc}") from exc
    if not response.ok:
        detail = response.text
        try:
            body = response.json()
            if isinstance(body, dict) and "detail" in body:
                detail = str(body["detail"])
        except ValueError:
            pass
        raise RuntimeError(f"{method} {path} failed: HTTP {response.status_code} - {detail}")
    try:
        body = response.json()
    except ValueError:
        return {}
    return body if isinstance(body, dict) else {}


def create_chat(base_url: str, headers: dict[str, str], session_id: str, timeout: int) -> None:
    request_json(
        method="POST",
        base_url=base_url,
        path="/chats",
        headers=headers,
        payload={"session_id": session_id, "title": session_id},
        timeout=timeout,
    )


def delete_chat(base_url: str, headers: dict[str, str], session_id: str, timeout: int) -> None:
    request_json(
        method="DELETE",
        base_url=base_url,
        path=f"/chats/{session_id}",
        headers=headers,
        timeout=timeout,
    )


def chat_message(
    *,
    base_url: str,
    headers: dict[str, str],
    session_id: str,
    message: str,
    timeout: int,
) -> dict[str, Any]:
    return request_json(
        method="POST",
        base_url=base_url,
        path="/chat",
        headers=headers,
        payload={"session_id": session_id, "message": message},
        timeout=timeout,
    )


def send_chat(
    *,
    base_url: str,
    headers: dict[str, str],
    session_id: str,
    message: str,
    attachments: list[dict[str, Any]] | None,
    timeout: int,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "session_id": session_id,
        "message": message,
    }
    if attachments:
        payload["attachments"] = attachments
    return request_json(
        method="POST",
        base_url=base_url,
        path="/chat",
        headers=headers,
        payload=payload,
        timeout=timeout,
    )


def preflight(
    base_url: str,
    headers: dict[str, str],
    timeout: int,
    *,
    check_chats: bool = True,
) -> None:
    health = request_json(
        method="GET",
        base_url=base_url,
        path="/health",
        headers=headers,
        timeout=timeout,
    )
    if str(health.get("status", "")).lower() != "ok":
        raise RuntimeError(f"GET /health returned unexpected payload: {health}")
    if check_chats:
        request_json(
            method="GET",
            base_url=base_url,
            path="/chats",
            headers=headers,
            timeout=timeout,
        )
