import argparse
import json
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from tools.eval_file_search_common import create_chat as _create_chat
from tools.eval_file_search_common import default_headers as _headers
from tools.eval_file_search_common import delete_chat as _delete_chat
from tools.eval_file_search_common import file_search as _file_search
from tools.eval_file_search_common import find_matching_result as _find_matching_result
from tools.eval_file_search_common import load_cases as _load_cases
from tools.eval_file_search_common import preflight as _preflight
from tools.eval_file_search_common import seed_image_context_memory as _seed_image_context_memory
from tools.eval_file_search_common import seed_ocr_memory as _seed_ocr_memory
from tools.eval_file_search_common import seed_pdf_memory as _seed_pdf_memory
from tools.eval_gate import gate_counts_from_case_results
from tools.eval_gate import resolve_fail_closed_status
from tools.eval_trace_artifacts import DEFAULT_TRACE_JSONL
from tools.eval_trace_artifacts import append_eval_trace
from tools.eval_trace_artifacts import build_eval_trace


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run file_search reliability checks for scoped and global lookup behavior.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Polinko API base URL.")
    parser.add_argument(
        "--cases",
        default="docs/eval/cases/file_search_eval_cases.json",
        help="Path to file-search eval cases JSON file.",
    )
    parser.add_argument(
        "--session-prefix",
        default="file-search-eval",
        help="Session id prefix for generated eval chats.",
    )
    parser.add_argument(
        "--run-id",
        default="",
        help="Optional run id suffix. Defaults to current epoch seconds.",
    )
    parser.add_argument("--timeout", type=int, default=90, help="HTTP timeout in seconds.")
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
    headers = _headers()

    print(f"Running file_search eval on {args.base_url}")
    print(f"Cases: {len(cases)} | run_id={run_id}")
    try:
        _preflight(args.base_url, headers, args.timeout)
    except Exception as exc:
        print(f"Preflight failed: {exc}")
        print("Checks:")
        print("  - Is `make server` running on the expected base URL?")
        print("  - Is vector memory enabled on the running server (`POLINKO_VECTOR_ENABLED=true`)?")
        return 1

    passes = 0
    failures: list[str] = []
    scoped_failures = 0
    global_failures = 0
    leak_failures = 0
    error_failures = 0
    case_results: list[dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        case_id = case["id"]
        seed_session = f"{args.session_prefix}-{run_id}-seed-{case_id}"
        distractor_session = f"{args.session_prefix}-{run_id}-distractor-{case_id}"
        seed_method = case["seed_method"]
        source_type = case["source_type"]
        must_include = case["must_include"]
        source_name = case["source_name"]

        print(f"\n[{index}/{len(cases)}] {case_id}")
        case_status = "PASS"
        detail = "scoped+global pass"
        case_error = ""
        scoped_hit_found = False
        global_hit_found = False
        scoped_leak_detected = False
        try:
            _create_chat(args.base_url, headers, seed_session, args.timeout)
            _create_chat(args.base_url, headers, distractor_session, args.timeout)

            if seed_method == "ocr":
                _seed_ocr_memory(
                    base_url=args.base_url,
                    headers=headers,
                    session_id=seed_session,
                    source_name=source_name,
                    text=case["seed_text"],
                    timeout=args.timeout,
                )
            elif seed_method == "pdf":
                _seed_pdf_memory(
                    base_url=args.base_url,
                    headers=headers,
                    session_id=seed_session,
                    source_name=source_name,
                    text=case["seed_text"],
                    timeout=args.timeout,
                )
            elif seed_method == "image_context":
                _seed_image_context_memory(
                    base_url=args.base_url,
                    headers=headers,
                    session_id=seed_session,
                    source_name=source_name,
                    text_hint=case["seed_text"],
                    visual_context_hint=case["seed_text"],
                    timeout=args.timeout,
                )
            else:
                raise RuntimeError(f"Unsupported seed method '{seed_method}'.")

            _seed_ocr_memory(
                base_url=args.base_url,
                headers=headers,
                session_id=distractor_session,
                source_name=f"{case_id}-noise.txt",
                text=f"noise content unrelated to query: {case_id}",
                timeout=args.timeout,
            )

            scoped = _file_search(
                base_url=args.base_url,
                headers=headers,
                query=case["query"],
                session_id=seed_session,
                source_types=[source_type],
                limit=5,
                timeout=args.timeout,
            )
            scoped_hit = _find_matching_result(
                matches=[item for item in scoped if isinstance(item, dict)],
                expected_session=seed_session,
                expected_source_type=source_type,
                terms=must_include,
            )
            if scoped_hit is None:
                case_status = "FAIL"
                detail = "scoped search miss"
                scoped_failures += 1
                failures.append(f"{case_id}: scoped search miss")
                print("  FAIL scoped: expected seeded snippet not found.")
            else:
                scoped_hit_found = True
                print(
                    "  PASS scoped:"
                    f" score={scoped_hit.get('score')} source_ref={scoped_hit.get('source_ref')}"
                )

            leaked = any(
                isinstance(item, dict) and str(item.get("session_id", "")) != seed_session
                for item in scoped
            )
            if leaked:
                scoped_leak_detected = True
                case_status = "FAIL"
                detail = "scoped search leak"
                leak_failures += 1
                failures.append(f"{case_id}: scoped search leak")
                print("  FAIL scoped: returned results from outside session filter.")

            global_matches = _file_search(
                base_url=args.base_url,
                headers=headers,
                query=case["query"],
                source_types=[source_type],
                limit=5,
                timeout=args.timeout,
            )
            global_hit = _find_matching_result(
                matches=[item for item in global_matches if isinstance(item, dict)],
                expected_session=seed_session,
                expected_source_type=source_type,
                terms=must_include,
            )
            if global_hit is None:
                case_status = "FAIL"
                detail = "global search miss"
                global_failures += 1
                failures.append(f"{case_id}: global search miss")
                print("  FAIL global: expected seeded snippet not found.")
            else:
                global_hit_found = True
                print(
                    "  PASS global:"
                    f" score={global_hit.get('score')} source_ref={global_hit.get('source_ref')}"
                )

            if scoped_hit is not None and not leaked and global_hit is not None:
                passes += 1
                case_status = "PASS"
                detail = "scoped+global pass"
        except Exception as exc:
            case_status = "ERROR"
            case_error = str(exc)
            detail = case_error
            error_failures += 1
            failures.append(f"{case_id}: error - {exc}")
            print(f"  ERROR: {exc}")
        finally:
            gate_decision = resolve_fail_closed_status(
                status=case_status,
                detail=detail,
            )
            case_results.append(
                {
                    "id": case_id,
                    "seed_session": seed_session,
                    "distractor_session": distractor_session,
                    "seed_method": seed_method,
                    "source_type": source_type,
                    "query": case["query"],
                    "must_include": must_include,
                    "status": case_status,
                    "detail": detail,
                    "error": case_error,
                    "gate_outcome": gate_decision.outcome,
                    "gate_reasons": list(gate_decision.reasons),
                    "scoped_hit_found": scoped_hit_found,
                    "global_hit_found": global_hit_found,
                    "scoped_leak_detected": scoped_leak_detected,
                }
            )
            if not args.keep_chats:
                for session_id in (seed_session, distractor_session):
                    try:
                        _delete_chat(args.base_url, headers, session_id, args.timeout)
                    except Exception as exc:
                        print(f"  WARN cleanup failed for {session_id}: {exc}")

    print("\nSummary")
    print(f"  Passed: {passes}/{len(cases)}")
    print(f"  Failed: {len(failures)}")
    print(
        "  Breakdown:"
        f" scoped_miss={scoped_failures}"
        f" global_miss={global_failures}"
        f" scoped_leak={leak_failures}"
        f" errors={error_failures}"
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
                "scoped_miss": scoped_failures,
                "global_miss": global_failures,
                "scoped_leak": leak_failures,
                "errors": error_failures,
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
                tool_name="tools/eval_file_search.py",
                source_artifacts={
                    "report_json": str(output_path),
                    "cases_path": str(cases_path),
                },
                gate_outcomes=[
                    {
                        "name": "file_search_report",
                        "passed": gate_failed == 0,
                        "detail": (
                            f"passed={passes}/{len(cases)}, failed={len(failures)}, "
                            f"errors={error_failures}, "
                            f"gate_failed={gate_failed}"
                        ),
                    }
                ],
                summary=report_payload["summary"],
                metadata={
                    "base_url": args.base_url,
                    "strict": False,
                },
            )
            trace_path = append_eval_trace(
                trace_payload=trace_payload,
                trace_jsonl_path=Path(trace_jsonl),
            )
            print(f"  Trace: {trace_path}")
    for entry in failures:
        print(f"  - {entry}")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
