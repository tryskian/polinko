from __future__ import annotations

import base64
import json
from pathlib import Path
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


def normalize_terms(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    terms: list[str] = []
    for item in value:
        term = str(item).strip().lower()
        if term:
            terms.append(term)
    return terms


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
        seed_method = str(case.get("seed_method", "ocr")).strip().lower() or "ocr"
        source_type = str(case.get("source_type", "ocr")).strip().lower() or "ocr"
        must_include = normalize_terms(case.get("must_include"))
        source_name = str(case.get("source_name", f"{case_id}.txt")).strip() or f"{case_id}.txt"
        if not case_id or not seed_text or not query:
            raise RuntimeError(
                f"Case #{index} is missing required fields ('id', 'seed_text', 'query')."
            )
        if "optional" in case:
            raise RuntimeError(
                f"Case #{index} ({case_id}) uses deprecated field 'optional'. "
                "Active gate suites are strict binary and fail-closed."
            )
        if seed_method not in {"ocr", "pdf", "image_context"}:
            raise RuntimeError(
                f"Case #{index} has unsupported seed_method '{seed_method}'. "
                "Supported: ocr, pdf, image_context."
            )
        normalized.append(
            {
                "id": case_id,
                "seed_text": seed_text,
                "query": query,
                "seed_method": seed_method,
                "source_type": source_type,
                "must_include": must_include,
                "source_name": source_name,
            }
        )
    return normalized


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


def seed_ocr_memory(
    *,
    base_url: str,
    headers: dict[str, str],
    session_id: str,
    source_name: str,
    text: str,
    timeout: int,
) -> None:
    request_json(
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
    )


def _pdf_escape_text(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return escaped.replace("\n", "\\n")


def _build_minimal_pdf_bytes(text: str) -> bytes:
    content_stream = f"BT /F1 12 Tf 50 750 Td ({_pdf_escape_text(text)}) Tj ET\n"
    content_bytes = content_stream.encode("latin-1", errors="replace")

    objects: list[bytes] = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        (
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        ),
        b"4 0 obj\n<< /Length " + str(len(content_bytes)).encode("ascii") + b" >>\nstream\n"
        + content_bytes
        + b"endstream\nendobj\n",
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]

    payload = b"%PDF-1.4\n"
    offsets: list[int] = []
    for obj in objects:
        offsets.append(len(payload))
        payload += obj

    xref_offset = len(payload)
    xref = [b"xref\n", b"0 6\n", b"0000000000 65535 f \n"]
    for offset in offsets:
        xref.append(f"{offset:010d} 00000 n \n".encode("ascii"))

    trailer = (
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n"
        + str(xref_offset).encode("ascii")
        + b"\n%%EOF\n"
    )
    payload += b"".join(xref) + trailer
    return payload


def seed_pdf_memory(
    *,
    base_url: str,
    headers: dict[str, str],
    session_id: str,
    source_name: str,
    text: str,
    timeout: int,
) -> None:
    payload = _build_minimal_pdf_bytes(text)
    payload_b64 = base64.b64encode(payload).decode("ascii")
    request_json(
        method="POST",
        base_url=base_url,
        path="/skills/pdf_ingest",
        headers=headers,
        payload={
            "session_id": session_id,
            "source_name": source_name if source_name.lower().endswith(".pdf") else f"{source_name}.pdf",
            "mime_type": "application/pdf",
            "data_base64": payload_b64,
            "attach_to_chat": False,
        },
        timeout=timeout,
    )


_ONE_BY_ONE_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO8B9wAAAABJRU5ErkJggg=="
)


def seed_image_context_memory(
    *,
    base_url: str,
    headers: dict[str, str],
    session_id: str,
    source_name: str,
    text_hint: str,
    visual_context_hint: str,
    timeout: int,
) -> None:
    request_json(
        method="POST",
        base_url=base_url,
        path="/skills/ocr",
        headers=headers,
        payload={
            "session_id": session_id,
            "source_name": source_name if source_name.lower().endswith(".png") else f"{source_name}.png",
            "mime_type": "image/png",
            "data_base64": _ONE_BY_ONE_PNG_BASE64,
            "text_hint": text_hint,
            "visual_context_hint": visual_context_hint,
            "attach_to_chat": False,
        },
        timeout=timeout,
    )


def file_search(
    *,
    base_url: str,
    headers: dict[str, str],
    query: str,
    timeout: int,
    session_id: str | None = None,
    source_types: list[str] | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    payload: dict[str, Any] = {
        "query": query,
        "limit": limit,
    }
    if session_id is not None:
        payload["session_id"] = session_id
    if source_types is not None:
        payload["source_types"] = source_types

    response = request_json(
        method="POST",
        base_url=base_url,
        path="/skills/file_search",
        headers=headers,
        payload=payload,
        timeout=timeout,
    )
    matches = response.get("matches", [])
    return matches if isinstance(matches, list) else []


def _contains_all_terms(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return all(term in lowered for term in terms)


def find_matching_result(
    *,
    matches: list[dict[str, Any]],
    expected_session: str,
    expected_source_type: str,
    terms: list[str],
) -> dict[str, Any] | None:
    source_type = expected_source_type.lower()
    for item in matches:
        if not isinstance(item, dict):
            continue
        if str(item.get("session_id", "")) != expected_session:
            continue
        if str(item.get("source_type", "")).lower() != source_type:
            continue
        snippet = str(item.get("snippet", ""))
        if _contains_all_terms(snippet, terms):
            return item
    return None


def preflight(base_url: str, headers: dict[str, str], timeout: int) -> None:
    health = request_json(
        method="GET",
        base_url=base_url,
        path="/health",
        headers=headers,
        timeout=timeout,
    )
    if str(health.get("status", "")).lower() != "ok":
        raise RuntimeError(f"GET /health returned unexpected payload: {health}")
    request_json(
        method="GET",
        base_url=base_url,
        path="/chats",
        headers=headers,
        timeout=timeout,
    )
