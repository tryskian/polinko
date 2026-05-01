import argparse
import time

from dotenv import load_dotenv

from tools.eval_chat_common import chat_message
from tools.eval_chat_common import create_chat
from tools.eval_chat_common import default_headers
from tools.eval_chat_common import delete_chat
from tools.eval_chat_common import request_json


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
    headers = default_headers()

    print(f"Running API smoke on {args.base_url}")

    health = request_json(
        method="GET",
        base_url=args.base_url,
        path="/health",
        headers=headers,
        timeout=args.timeout,
    )
    if str(health.get("status", "")).lower() != "ok":
        raise RuntimeError(f"GET /health returned unexpected payload: {health}")
    print("  PASS /health")

    request_json(
        method="GET",
        base_url=args.base_url,
        path="/chats",
        headers=headers,
        timeout=args.timeout,
    )
    print("  PASS /chats list")

    create_chat(args.base_url, headers, session_id, args.timeout)
    print("  PASS /chats create")

    try:
        request_json(
            method="POST",
            base_url=args.base_url,
            path=f"/chats/{session_id}/personalization",
            headers=headers,
            payload={"memory_scope": "session"},
            timeout=args.timeout,
        )
        print("  PASS /personalization")

        request_json(
            method="POST",
            base_url=args.base_url,
            path="/skills/ocr",
            headers=headers,
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

        search_payload = request_json(
            method="POST",
            base_url=args.base_url,
            path="/skills/file_search",
            headers=headers,
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

        chat_payload = chat_message(
            base_url=args.base_url,
            headers=headers,
            session_id=session_id,
            message="hello",
            timeout=args.timeout,
        )
        output = str(chat_payload.get("output", "")).strip()
        assistant_message_id = str(chat_payload.get("assistant_message_id", "")).strip()
        if not output or not assistant_message_id:
            raise RuntimeError("POST /chat returned missing output or assistant_message_id.")
        print("  PASS /chat")
    finally:
        delete_chat(args.base_url, headers, session_id, args.timeout)
        print("  PASS /chats delete")

    print("API smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
