import argparse
import time
from typing import Any

import requests
from dotenv import load_dotenv


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    payload: dict[str, Any] | None = None,
    timeout: int = 90,
) -> dict[str, Any]:
    response = requests.request(
        method=method,
        url=f"{base_url}{path}",
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=timeout,
    )
    if not response.ok:
        detail = response.text
        try:
            body = response.json()
        except ValueError:
            body = None
        if isinstance(body, dict) and "detail" in body:
            detail = str(body["detail"])
        raise RuntimeError(f"{method} {path} failed: HTTP {response.status_code} - {detail}")
    try:
        body = response.json()
    except ValueError:
        return {}
    return body if isinstance(body, dict) else {}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a small live API smoke against Polinko.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Polinko API base URL.")
    parser.add_argument("--timeout", type=int, default=90, help="HTTP timeout in seconds.")
    parser.add_argument(
        "--session-prefix",
        default="api-smoke",
        help="Session id prefix for generated smoke chat.",
    )
    return parser


def main() -> int:
    load_dotenv(dotenv_path=".env")
    args = build_parser().parse_args()
    session_id = f"{args.session_prefix}-{int(time.time())}"
    source_name = f"{session_id}.txt"
    seeded_text = "api smoke alpha beta gamma"

    print(f"Running API smoke on {args.base_url}")

    health = _request_json(
        method="GET",
        base_url=args.base_url,
        path="/health",
        timeout=args.timeout,
    )
    if str(health.get("status", "")).lower() != "ok":
        raise RuntimeError(f"GET /health returned unexpected payload: {health}")
    print("  PASS /health")

    _request_json(
        method="GET",
        base_url=args.base_url,
        path="/chats",
        timeout=args.timeout,
    )
    print("  PASS /chats list")

    _request_json(
        method="POST",
        base_url=args.base_url,
        path="/chats",
        payload={"session_id": session_id, "title": session_id},
        timeout=args.timeout,
    )
    print("  PASS /chats create")

    try:
        _request_json(
            method="POST",
            base_url=args.base_url,
            path=f"/chats/{session_id}/personalization",
            payload={"memory_scope": "session"},
            timeout=args.timeout,
        )
        print("  PASS /personalization")

        _request_json(
            method="POST",
            base_url=args.base_url,
            path="/skills/ocr",
            payload={
                "session_id": session_id,
                "source_name": source_name,
                "mime_type": "text/plain",
                "text_hint": seeded_text,
                "attach_to_chat": False,
            },
            timeout=args.timeout,
        )
        print("  PASS /skills/ocr")

        search_payload = _request_json(
            method="POST",
            base_url=args.base_url,
            path="/skills/file_search",
            payload={
                "session_id": session_id,
                "query": "alpha beta gamma",
                "source_types": ["ocr"],
                "limit": 3,
            },
            timeout=args.timeout,
        )
        matches = search_payload.get("matches", [])
        if not isinstance(matches, list) or not matches:
            raise RuntimeError("POST /skills/file_search returned no matches.")
        first_match = matches[0] if isinstance(matches[0], dict) else {}
        snippet = str(first_match.get("snippet", "")).lower()
        if "alpha" not in snippet or "beta" not in snippet or "gamma" not in snippet:
            raise RuntimeError("POST /skills/file_search returned unexpected snippet.")
        print("  PASS /skills/file_search")

        chat_payload = _request_json(
            method="POST",
            base_url=args.base_url,
            path="/chat",
            payload={"session_id": session_id, "message": "hello"},
            timeout=args.timeout,
        )
        output = str(chat_payload.get("output", "")).strip()
        assistant_message_id = str(chat_payload.get("assistant_message_id", "")).strip()
        if not output or not assistant_message_id:
            raise RuntimeError("POST /chat returned missing output or assistant_message_id.")
        print("  PASS /chat")
    finally:
        _request_json(
            method="DELETE",
            base_url=args.base_url,
            path=f"/chats/{session_id}",
            timeout=args.timeout,
        )
        print("  PASS /chats delete")

    print("API smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
