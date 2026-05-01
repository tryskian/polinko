import argparse
import json
import time
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from tools.eval_gate import gate_counts_from_case_results
from tools.eval_gate import resolve_fail_closed_status
from tools.eval_retrieval_common import chat_message as _chat
from tools.eval_retrieval_common import create_chat as _create_chat
from tools.eval_retrieval_common import default_headers
from tools.eval_retrieval_common import delete_chat as _delete_chat
from tools.eval_retrieval_common import find_expected_citation as _find_expected_citation
from tools.eval_retrieval_common import has_cross_session_leak as _has_cross_session_leak
from tools.eval_retrieval_common import load_cases as _load_cases
from tools.eval_retrieval_common import preflight as _preflight
from tools.eval_retrieval_common import seed_ocr_memory as _seed_ocr_memory
from tools.eval_retrieval_common import set_memory_scope as _set_memory_scope
from tools.eval_trace_artifacts import DEFAULT_TRACE_JSONL
from tools.eval_trace_artifacts import append_eval_trace
from tools.eval_trace_artifacts import build_eval_trace

RETRYABLE_HTTP_STATUS_CODES = {429, 500, 502, 503, 504}


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
    payload: dict[str, Any] | None = None,
    timeout: int = 60,
    retries: int = 0,
    retry_delay_ms: int = 0,
) -> dict[str, Any]:
    attempts = max(0, retries) + 1
    delay_seconds = max(0, retry_delay_ms) / 1000.0
    last_error: RuntimeError | None = None

    for attempt in range(attempts):
        try:
            response = requests.request(
                method=method,
                url=f"{base_url}{path}",
                headers=headers,
                json=payload,
                timeout=timeout,
            )
        except requests.RequestException as exc:
            last_error = RuntimeError(
                f"{method} {path} failed: connection error - {exc}"
            )
            if attempt < attempts - 1 and delay_seconds > 0:
                time.sleep(delay_seconds)
            if attempt < attempts - 1:
                continue
            raise last_error from exc

        if response.ok:
            try:
                body = response.json()
            except ValueError:
                return {}
            return body if isinstance(body, dict) else {}

        detail = response.text
        try:
            body = response.json()
            if isinstance(body, dict) and "detail" in body:
                detail = str(body["detail"])
        except ValueError:
            pass
        last_error = RuntimeError(
            f"{method} {path} failed: HTTP {response.status_code} - {detail}"
        )
        is_retryable = response.status_code in RETRYABLE_HTTP_STATUS_CODES
        if is_retryable and attempt < attempts - 1:
            if delay_seconds > 0:
                time.sleep(delay_seconds)
            continue
        raise last_error

    if last_error is not None:
        raise last_error
    raise RuntimeError(f"{method} {path} failed: unknown request error")


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
        default="docs/eval/beta_2_0/retrieval_eval_cases.json",
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
        "--request-retries",
        type=int,
        default=2,
        help="Retry count for transient HTTP failures (429/5xx) and connection errors.",
    )
    parser.add_argument(
        "--request-retry-delay-ms",
        type=int,
        default=750,
        help="Delay between transient HTTP retries, in milliseconds.",
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
    if args.request_retries < 0:
        raise SystemExit("--request-retries must be >= 0")
    if args.request_retry_delay_ms < 0:
        raise SystemExit("--request-retry-delay-ms must be >= 0")
    run_id = args.run_id.strip() or str(int(time.time()))
    headers = default_headers()

    print(f"Running retrieval eval on {args.base_url}")
    print(
        f"Cases: {len(cases)} | run_id={run_id} | request_retries={args.request_retries} | "
        f"retry_delay_ms={args.request_retry_delay_ms}"
    )
    try:
        _preflight(
            request_json=_request_json,
            base_url=args.base_url,
            headers=headers,
            timeout=args.timeout,
            retries=args.request_retries,
            retry_delay_ms=args.request_retry_delay_ms,
        )
    except Exception as exc:
        print(f"Preflight failed: {exc}")
        print("Checks:")
        print("  - Is `make server` running on the expected base URL?")
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
            _create_chat(
                request_json=_request_json,
                base_url=args.base_url,
                headers=headers,
                session_id=seed_session,
                timeout=args.timeout,
                retries=args.request_retries,
                retry_delay_ms=args.request_retry_delay_ms,
            )
            _create_chat(
                request_json=_request_json,
                base_url=args.base_url,
                headers=headers,
                session_id=target_session,
                timeout=args.timeout,
                retries=args.request_retries,
                retry_delay_ms=args.request_retry_delay_ms,
            )
            _seed_ocr_memory(
                request_json=_request_json,
                base_url=args.base_url,
                headers=headers,
                session_id=seed_session,
                source_name=source_name,
                text=case["seed_text"],
                timeout=args.timeout,
                retries=args.request_retries,
                retry_delay_ms=args.request_retry_delay_ms,
            )

            _set_memory_scope(
                request_json=_request_json,
                base_url=args.base_url,
                headers=headers,
                session_id=target_session,
                scope="global",
                timeout=args.timeout,
                retries=args.request_retries,
                retry_delay_ms=args.request_retry_delay_ms,
            )
            global_chat = _chat(
                request_json=_request_json,
                base_url=args.base_url,
                headers=headers,
                session_id=target_session,
                message=case["query"],
                timeout=args.timeout,
                retries=args.request_retries,
                retry_delay_ms=args.request_retry_delay_ms,
            )
            global_memory = global_chat.get("memory_used")
            if not isinstance(global_memory, list):
                raise RuntimeError("Missing or invalid memory_used in /chat response.")
            global_memory_count = len(
                [item for item in global_memory if isinstance(item, dict)]
            )
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
                request_json=_request_json,
                base_url=args.base_url,
                headers=headers,
                session_id=target_session,
                scope="session",
                timeout=args.timeout,
                retries=args.request_retries,
                retry_delay_ms=args.request_retry_delay_ms,
            )
            session_chat = _chat(
                request_json=_request_json,
                base_url=args.base_url,
                headers=headers,
                session_id=target_session,
                message=case["query"],
                timeout=args.timeout,
                retries=args.request_retries,
                retry_delay_ms=args.request_retry_delay_ms,
            )
            session_memory = session_chat.get("memory_used")
            if not isinstance(session_memory, list):
                raise RuntimeError(
                    "Missing or invalid memory_used in session-scope response."
                )
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
                            request_json=_request_json,
                            base_url=args.base_url,
                            headers=headers,
                            session_id=session_id,
                            timeout=args.timeout,
                            retries=args.request_retries,
                            retry_delay_ms=args.request_retry_delay_ms,
                        )
                    except Exception as exc:
                        print(f"  WARN cleanup failed for {session_id}: {exc}")

    print("\nSummary")
    print(f"  Passed: {passes}/{len(cases)}")
    print(f"  Failed: {len(failures)}")
    print(
        f"  Breakdown: global_miss={global_miss_count} leak={leak_count} errors={error_count}"
    )
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
                    "request_retries": args.request_retries,
                    "request_retry_delay_ms": args.request_retry_delay_ms,
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
