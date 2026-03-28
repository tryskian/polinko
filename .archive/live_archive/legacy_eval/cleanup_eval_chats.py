from __future__ import annotations

import argparse
import os
from typing import Any

import requests
from dotenv import load_dotenv


DEFAULT_PREFIXES = [
    "retrieval-eval-",
    "file-search-eval-",
    "ocr-eval-",
    "style-eval-",
    "hallucination-eval-",
    "clip-ab-eval-",
]


def _headers(api_key: str | None) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key
    return headers


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
    payload: dict[str, Any] | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    response = requests.request(
        method=method,
        url=f"{base_url}{path}",
        headers=headers,
        json=payload,
        timeout=timeout,
    )
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


def _parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> int:
    load_dotenv(dotenv_path=".env")
    parser = argparse.ArgumentParser(description="Delete eval-generated chats by session prefix.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Polinko API base URL.")
    parser.add_argument(
        "--prefixes",
        default=",".join(DEFAULT_PREFIXES),
        help="Comma-separated session_id prefixes to delete.",
    )
    parser.add_argument("--timeout", type=int, default=60, help="HTTP timeout in seconds.")
    parser.add_argument("--dry-run", action="store_true", help="List matches without deleting.")
    args = parser.parse_args()

    headers = _headers(os.getenv("POLINKO_SERVER_API_KEY"))
    prefixes = tuple(_parse_csv(args.prefixes))
    if not prefixes:
        raise SystemExit("No prefixes provided.")

    payload = _request_json(
        method="GET",
        base_url=args.base_url,
        path="/chats",
        headers=headers,
        timeout=args.timeout,
    )
    chats = payload.get("chats", [])
    if not isinstance(chats, list):
        raise SystemExit("Unexpected /chats payload.")

    matches = [
        chat
        for chat in chats
        if isinstance(chat, dict)
        and isinstance(chat.get("session_id"), str)
        and chat["session_id"].startswith(prefixes)
    ]

    if not matches:
        print("No eval chats found.")
        return 0

    print(f"Found {len(matches)} eval chat(s).")
    for chat in matches:
        print(f"- {chat.get('session_id')} | {chat.get('title')}")

    if args.dry_run:
        print("Dry run only. No deletions performed.")
        return 0

    deleted = 0
    for chat in matches:
        session_id = str(chat["session_id"])
        try:
            _request_json(
                method="DELETE",
                base_url=args.base_url,
                path=f"/chats/{session_id}",
                headers=headers,
                timeout=args.timeout,
            )
            deleted += 1
        except Exception as exc:
            print(f"WARN delete failed for {session_id}: {exc}")

    print(f"Deleted {deleted}/{len(matches)} eval chat(s).")
    return 0 if deleted == len(matches) else 1


if __name__ == "__main__":
    raise SystemExit(main())
