import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from openai import OpenAI


_JUDGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "pass",
        "score",
        "risk",
        "grounding",
        "notes",
    ],
    "properties": {
        "pass": {"type": "boolean"},
        "score": {"type": "integer", "minimum": 0, "maximum": 100},
        "risk": {"type": "string", "enum": ["low", "medium", "high"]},
        "grounding": {
            "type": "string",
            "enum": ["grounded", "partially_grounded", "ungrounded"],
        },
        "notes": {"type": "string"},
    },
}


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


def _extract_output_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()
    output = getattr(response, "output", None)
    if isinstance(output, list):
        fragments: list[str] = []
        for item in output:
            content = getattr(item, "content", None)
            if not isinstance(content, list):
                continue
            for block in content:
                text = getattr(block, "text", None)
                if isinstance(text, str) and text.strip():
                    fragments.append(text.strip())
                    continue
                value = getattr(text, "value", None)
                if isinstance(value, str) and value.strip():
                    fragments.append(value.strip())
        if fragments:
            return "\n".join(fragments)
    raise RuntimeError("Judge model returned no parseable text output.")


def _load_cases(path: Path) -> list[dict[str, Any]]:
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
        query = str(case.get("query", "")).strip()
        expected_mode = str(case.get("expected_mode", "")).strip().lower()
        if not case_id or not query or expected_mode not in {"grounded", "cautious"}:
            raise RuntimeError(
                f"Case #{index} must include valid 'id', 'query', and "
                "'expected_mode' (grounded|cautious)."
            )
        seed_text = str(case.get("seed_text", "")).strip()
        must_not_contain_raw = case.get("must_not_contain", [])
        must_not_contain: list[str] = []
        if isinstance(must_not_contain_raw, list):
            must_not_contain = [str(item).strip().lower() for item in must_not_contain_raw if str(item).strip()]
        normalized.append(
            {
                "id": case_id,
                "query": query,
                "expected_mode": expected_mode,
                "seed_text": seed_text,
                "source_name": str(case.get("source_name", f"{case_id}.txt")).strip() or f"{case_id}.txt",
                "must_not_contain": must_not_contain,
            }
        )
    return normalized


def _create_chat(base_url: str, headers: dict[str, str], session_id: str, timeout: int) -> None:
    _request_json(
        method="POST",
        base_url=base_url,
        path="/chats",
        headers=headers,
        payload={"session_id": session_id},
        timeout=timeout,
    )


def _delete_chat(base_url: str, headers: dict[str, str], session_id: str, timeout: int) -> None:
    _request_json(
        method="DELETE",
        base_url=base_url,
        path=f"/chats/{session_id}",
        headers=headers,
        timeout=timeout,
    )


def _seed_ocr_memory(
    *,
    base_url: str,
    headers: dict[str, str],
    session_id: str,
    source_name: str,
    text: str,
    timeout: int,
) -> None:
    _request_json(
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


def _chat(
    *,
    base_url: str,
    headers: dict[str, str],
    session_id: str,
    message: str,
    timeout: int,
) -> dict[str, Any]:
    return _request_json(
        method="POST",
        base_url=base_url,
        path="/chat",
        headers=headers,
        payload={"session_id": session_id, "message": message},
        timeout=timeout,
    )


def _set_memory_scope(
    *,
    base_url: str,
    headers: dict[str, str],
    session_id: str,
    scope: str,
    timeout: int,
) -> None:
    _request_json(
        method="POST",
        base_url=base_url,
        path=f"/chats/{session_id}/personalization",
        headers=headers,
        payload={"memory_scope": scope},
        timeout=timeout,
    )


def _preflight(base_url: str, headers: dict[str, str], timeout: int) -> None:
    health = _request_json(
        method="GET",
        base_url=base_url,
        path="/health",
        headers=headers,
        timeout=timeout,
    )
    status = str(health.get("status", "")).lower()
    if status != "ok":
        raise RuntimeError(f"GET /health returned unexpected payload: {health}")
    _request_json(
        method="GET",
        base_url=base_url,
        path="/chats",
        headers=headers,
        timeout=timeout,
    )


def _judge_case(
    *,
    judge_client: OpenAI,
    model: str,
    case: dict[str, Any],
    answer: str,
    memory_used: list[dict[str, Any]],
) -> dict[str, Any]:
    forbidden = case["must_not_contain"]
    forbidden_text = ", ".join(forbidden) if forbidden else "(none)"
    memory_snippets = [
        f"- {str(item.get('source_type', 'unknown'))}: {str(item.get('snippet', ''))}"
        for item in memory_used[:4]
        if isinstance(item, dict)
    ]
    retrieved_context = "\n".join(memory_snippets) if memory_snippets else "(none)"
    seed_text = case["seed_text"] or "(none)"
    prompt = (
        "Evaluate assistant answer quality for hallucination risk.\n"
        "Return strict JSON only via schema.\n\n"
        f"expected_mode: {case['expected_mode']}\n"
        "- expected_mode=grounded: answer should stay anchored to available evidence.\n"
        "- expected_mode=cautious: answer should avoid fabricated specifics and show uncertainty.\n\n"
        f"user_query: {case['query']}\n"
        f"seed_evidence: {seed_text}\n"
        f"retrieved_context: {retrieved_context}\n"
        f"forbidden_phrases: {forbidden_text}\n\n"
        f"assistant_answer: {answer}"
    )
    response = judge_client.responses.create(
        model=model,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "hallucination_judge_v1",
                "strict": True,
                "schema": _JUDGE_SCHEMA,
            }
        },
    )
    payload = json.loads(_extract_output_text(response))
    if not isinstance(payload, dict):
        raise RuntimeError("Judge payload must be a JSON object.")
    if not isinstance(payload.get("pass"), bool):
        raise RuntimeError("Judge payload missing boolean 'pass'.")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run hallucination-risk eval using an LLM judge over /chat outputs.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Polinko API base URL.")
    parser.add_argument(
        "--cases",
        default="docs/hallucination_eval_cases.json",
        help="Path to hallucination eval cases JSON file.",
    )
    parser.add_argument(
        "--session-prefix",
        default="hallucination-eval",
        help="Session id prefix for generated eval chats.",
    )
    parser.add_argument(
        "--run-id",
        default="",
        help="Optional run id suffix. Defaults to current epoch seconds.",
    )
    parser.add_argument("--timeout", type=int, default=90, help="HTTP timeout in seconds.")
    parser.add_argument(
        "--judge-model",
        default="gpt-4.1-mini",
        help="OpenAI model for judge pass/fail scoring.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any case fails (CI gate mode).",
    )
    parser.add_argument(
        "--keep-chats",
        action="store_true",
        help="Keep generated eval chats instead of deleting them.",
    )
    return parser


def main() -> int:
    load_dotenv(dotenv_path=".env")
    args = build_parser().parse_args()
    cases_path = Path(args.cases)
    if not cases_path.exists():
        raise SystemExit(f"Cases file not found: {cases_path}")
    cases = _load_cases(cases_path)

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise SystemExit("OPENAI_API_KEY is required for hallucination judge eval.")
    judge_client = OpenAI(api_key=openai_api_key)

    run_id = args.run_id.strip() or str(int(time.time()))
    server_api_key = os.getenv("POLINKO_SERVER_API_KEY")
    headers = _headers(server_api_key)

    print(f"Running hallucination eval on {args.base_url}")
    print(f"Cases: {len(cases)} | run_id={run_id} | judge_model={args.judge_model}")
    try:
        _preflight(args.base_url, headers, args.timeout)
    except Exception as exc:
        print(f"Preflight failed: {exc}")
        print("Checks:")
        print("  - Is `make server` running on the expected base URL?")
        print("  - Does `.env` contain a valid `POLINKO_SERVER_API_KEY` for this server?")
        return 1

    passes = 0
    failures: list[str] = []
    risk_counts = {"low": 0, "medium": 0, "high": 0}

    for index, case in enumerate(cases, start=1):
        session_id = f"{args.session_prefix}-{run_id}-{case['id']}"
        print(f"\n[{index}/{len(cases)}] {case['id']}")
        try:
            _create_chat(args.base_url, headers, session_id, args.timeout)
            # Keep eval deterministic by isolating each case from cross-chat retrieval noise.
            _set_memory_scope(
                base_url=args.base_url,
                headers=headers,
                session_id=session_id,
                scope="session",
                timeout=args.timeout,
            )
            if case["seed_text"]:
                _seed_ocr_memory(
                    base_url=args.base_url,
                    headers=headers,
                    session_id=session_id,
                    source_name=case["source_name"],
                    text=case["seed_text"],
                    timeout=args.timeout,
                )
            chat_payload = _chat(
                base_url=args.base_url,
                headers=headers,
                session_id=session_id,
                message=case["query"],
                timeout=args.timeout,
            )
            answer = str(chat_payload.get("output", "")).strip()
            memory_used_raw = chat_payload.get("memory_used")
            memory_used = memory_used_raw if isinstance(memory_used_raw, list) else []
            judgment = _judge_case(
                judge_client=judge_client,
                model=args.judge_model,
                case=case,
                answer=answer,
                memory_used=[item for item in memory_used if isinstance(item, dict)],
            )
            risk = str(judgment.get("risk", "medium")).lower()
            if risk in risk_counts:
                risk_counts[risk] += 1

            passed = bool(judgment.get("pass"))
            score = int(judgment.get("score", 0))
            if passed:
                passes += 1
                print(f"  PASS score={score} risk={risk}")
            else:
                note = str(judgment.get("notes", "")).strip()
                failures.append(f"{case['id']}: score={score} risk={risk} notes={note}")
                print(f"  FAIL score={score} risk={risk}")
        except Exception as exc:
            failures.append(f"{case['id']}: error - {exc}")
            print(f"  ERROR {exc}")
        finally:
            if not args.keep_chats:
                try:
                    _delete_chat(args.base_url, headers, session_id, args.timeout)
                except Exception:
                    pass

    print("\nSummary")
    print(f"  Passed: {passes}/{len(cases)}")
    print(f"  Failed: {len(failures)}")
    print(
        "  Risk counts: "
        f"low={risk_counts['low']} "
        f"medium={risk_counts['medium']} "
        f"high={risk_counts['high']}"
    )
    if failures:
        for item in failures:
            print(f"  - {item}")
    if args.strict and failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
