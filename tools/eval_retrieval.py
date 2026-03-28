import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from tools.eval_gate import gate_counts_from_case_results
from tools.eval_gate import resolve_fail_closed_status
from tools.eval_trace_artifacts import DEFAULT_TRACE_JSONL
from tools.eval_trace_artifacts import append_eval_trace
from tools.eval_trace_artifacts import build_eval_trace


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


def _normalize_terms(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    terms: list[str] = []
    for item in value:
        term = str(item).strip().lower()
        if term:
            terms.append(term)
    return terms


def _find_expected_citation(
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


def _has_cross_session_leak(memory_used: list[dict[str, Any]], seed_session: str) -> bool:
    return any(str(item.get("session_id", "")) == seed_session for item in memory_used)


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
        seed_text = str(case.get("seed_text", "")).strip()
        query = str(case.get("query", "")).strip()
        source_type = str(case.get("source_type", "ocr")).strip().lower() or "ocr"
        required_terms = _normalize_terms(case.get("must_include"))
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


def _create_chat(base_url: str, headers: dict[str, str], session_id: str, timeout: int) -> None:
    _request_json(
        method="POST",
        base_url=base_url,
        path="/chats",
        headers=headers,
        payload={"session_id": session_id, "title": session_id},
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


def _seed_ocr_memory(
    *,
    base_url: str,
    headers: dict[str, str],
    session_id: str,
    source_name: str,
    text: str,
    timeout: int,
) -> dict[str, Any]:
    return _request_json(
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run retrieval quality checks for global recall and session isolation.",
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Polinko API base URL.",
    )
    parser.add_argument(
        "--cases",
        default="docs/eval/cases/retrieval_eval_cases.json",
        help="Path to retrieval eval cases JSON file.",
    )
    parser.add_argument(
        "--session-prefix",
        default="retrieval-eval",
        help="Session id prefix for generated eval chats.",
    )
    parser.add_argument(
        "--run-id",
        default="",
        help="Optional run id suffix. Defaults to current epoch seconds.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=90,
        help="HTTP timeout in seconds.",
    )
    parser.add_argument(
        "--keep-chats",
        action="store_true",
        help="Keep generated eval chats instead of deleting them.",
    )
    parser.add_argument(
        "--report-json",
        default="",
        help="Optional path to write a JSON run report artifact.",
    )
    parser.add_argument(
        "--trace-jsonl",
        default=str(DEFAULT_TRACE_JSONL),
        help="Append-only JSONL trace artifact path (set empty string to disable).",
    )
    return parser


def main() -> int:
    load_dotenv(dotenv_path=".env")
    args = build_parser().parse_args()
    cases_path = Path(args.cases)
    if not cases_path.exists():
        raise SystemExit(f"Cases file not found: {cases_path}")

    cases = _load_cases(cases_path)
    run_id = args.run_id.strip() or str(int(time.time()))
    api_key = os.getenv("POLINKO_SERVER_API_KEY")
    headers = _headers(api_key)

    print(f"Running retrieval eval on {args.base_url}")
    print(f"Cases: {len(cases)} | run_id={run_id}")
    try:
        _preflight(args.base_url, headers, args.timeout)
    except Exception as exc:
        print(f"Preflight failed: {exc}")
        print("Checks:")
        print("  - Is `make server` running on the expected base URL?")
        print("  - Does `.env` contain a valid `POLINKO_SERVER_API_KEY` for this server?")
        print("  - Is `POLINKO_VECTOR_ENABLED=true` on the running server?")
        return 1

    failures: list[str] = []
    passes = 0
    global_miss_count = 0
    leak_count = 0
    error_count = 0
    case_results: list[dict[str, Any]] = []

    for index, case in enumerate(cases, start=1):
        case_id = case["id"]
        seed_session = f"{args.session_prefix}-{run_id}-seed-{case_id}"
        target_session = f"{args.session_prefix}-{run_id}-target-{case_id}"
        source_name = f"{case_id}.txt"
        must_include = case["must_include"]
        source_type = case["source_type"]

        print(f"\n[{index}/{len(cases)}] {case_id}")
        case_status = "PASS"
        case_error = ""
        detail = ""
        global_memory_count = 0
        global_found = False
        session_leak = False
        try:
            _create_chat(args.base_url, headers, seed_session, args.timeout)
            _create_chat(args.base_url, headers, target_session, args.timeout)
            _seed_ocr_memory(
                base_url=args.base_url,
                headers=headers,
                session_id=seed_session,
                source_name=source_name,
                text=case["seed_text"],
                timeout=args.timeout,
            )

            _set_memory_scope(
                base_url=args.base_url,
                headers=headers,
                session_id=target_session,
                scope="global",
                timeout=args.timeout,
            )
            global_chat = _chat(
                base_url=args.base_url,
                headers=headers,
                session_id=target_session,
                message=case["query"],
                timeout=args.timeout,
            )
            global_memory = global_chat.get("memory_used")
            if not isinstance(global_memory, list):
                raise RuntimeError("Missing or invalid memory_used in /chat response.")
            global_memory_count = len([item for item in global_memory if isinstance(item, dict)])
            global_citation = _find_expected_citation(
                memory_used=[item for item in global_memory if isinstance(item, dict)],
                seed_session=seed_session,
                source_type=source_type,
                must_include_terms=must_include,
            )
            if global_citation is None:
                case_status = "FAIL"
                global_miss_count += 1
                detail = f"global retrieval miss (memory_used={global_memory_count})"
                failures.append(
                    f"{case_id}: global retrieval miss (expected seed citation from {seed_session})."
                )
                print(f"  FAIL {detail}")
                continue
            global_found = True

            _set_memory_scope(
                base_url=args.base_url,
                headers=headers,
                session_id=target_session,
                scope="session",
                timeout=args.timeout,
            )
            session_chat = _chat(
                base_url=args.base_url,
                headers=headers,
                session_id=target_session,
                message=case["query"],
                timeout=args.timeout,
            )
            session_memory = session_chat.get("memory_used")
            if not isinstance(session_memory, list):
                raise RuntimeError("Missing or invalid memory_used in session-scope response.")
            session_items = [item for item in session_memory if isinstance(item, dict)]
            if _has_cross_session_leak(session_items, seed_session):
                case_status = "FAIL"
                session_leak = True
                leak_count += 1
                detail = "session-scope leak"
                failures.append(
                    f"{case_id}: session-scope leak (found citation from {seed_session})."
                )
                print("  FAIL session-scope leak")
                continue

            passes += 1
            detail = "global recall + session isolation"
            print("  PASS global recall + session isolation")
        except Exception as exc:  # pragma: no cover - CLI operational guard
            case_status = "ERROR"
            case_error = str(exc)
            detail = case_error
            error_count += 1
            failures.append(f"{case_id}: error - {exc}")
            print(f"  ERROR {exc}")
        finally:
            gate_decision = resolve_fail_closed_status(
                status=case_status,
                detail=detail,
            )
            case_results.append(
                {
                    "id": case_id,
                    "seed_session": seed_session,
                    "target_session": target_session,
                    "source_type": source_type,
                    "must_include": must_include,
                    "query": case["query"],
                    "status": case_status,
                    "detail": detail,
                    "error": case_error,
                    "gate_outcome": gate_decision.outcome,
                    "gate_reasons": list(gate_decision.reasons),
                    "global_citation_found": global_found,
                    "session_scope_leak": session_leak,
                    "global_memory_count": global_memory_count,
                }
            )
            if not args.keep_chats:
                for session_id in (seed_session, target_session):
                    try:
                        _delete_chat(
                            args.base_url,
                            headers,
                            session_id,
                            timeout=args.timeout,
                        )
                    except Exception as exc:
                        print(f"  WARN cleanup failed for {session_id}: {exc}")

    print("\nSummary")
    print(f"  Passed: {passes}/{len(cases)}")
    print(f"  Failed: {len(failures)}")
    print(f"  Breakdown: global_miss={global_miss_count} leak={leak_count} errors={error_count}")
    report_json = str(args.report_json or "").strip()
    if report_json:
        gate_passed, gate_failed = gate_counts_from_case_results(case_results)
        output_path = Path(report_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report_payload = {
            "run_id": run_id,
            "base_url": args.base_url,
            "cases_path": str(cases_path),
            "summary": {
                "total": len(cases),
                "passed": passes,
                "failed": len(failures),
                "global_miss": global_miss_count,
                "leak": leak_count,
                "errors": error_count,
                "gate_passed": gate_passed,
                "gate_failed": gate_failed,
            },
            "failures": failures,
            "cases": case_results,
            "generated_at": int(time.time()),
        }
        output_path.write_text(
            json.dumps(report_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"  Report: {output_path}")
        trace_jsonl = str(args.trace_jsonl or "").strip()
        if trace_jsonl:
            trace_payload = build_eval_trace(
                run_id=run_id,
                tool_name="tools/eval_retrieval.py",
                source_artifacts={
                    "report_json": str(output_path),
                    "cases_path": str(cases_path),
                },
                gate_outcomes=[
                    {
                        "name": "retrieval_eval",
                        "passed": gate_failed == 0,
                        "detail": (
                            f"passed={passes}/{len(cases)}, failed={len(failures)}, "
                            f"global_miss={global_miss_count}, leak={leak_count}, "
                            f"errors={error_count}, gate_failed={gate_failed}"
                        ),
                    }
                ],
                summary=report_payload["summary"],
                metadata={
                    "base_url": args.base_url,
                },
            )
            trace_path = append_eval_trace(
                trace_payload=trace_payload,
                trace_jsonl_path=Path(trace_jsonl),
            )
            print(f"  Trace: {trace_path}")
    if failures:
        for failure in failures:
            print(f"  - {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
