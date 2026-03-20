import argparse
import base64
import json
import os
import time
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

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
        seed_method = str(case.get("seed_method", "ocr")).strip().lower() or "ocr"
        source_type = str(case.get("source_type", "ocr")).strip().lower() or "ocr"
        must_include = _normalize_terms(case.get("must_include"))
        optional = bool(case.get("optional", False))
        source_name = str(case.get("source_name", f"{case_id}.txt")).strip() or f"{case_id}.txt"
        if not case_id or not seed_text or not query:
            raise RuntimeError(
                f"Case #{index} is missing required fields ('id', 'seed_text', 'query')."
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
                "optional": optional,
                "source_name": source_name,
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


def _seed_pdf_memory(
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
    _request_json(
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


def _seed_image_context_memory(
    *,
    base_url: str,
    headers: dict[str, str],
    session_id: str,
    source_name: str,
    text_hint: str,
    visual_context_hint: str,
    timeout: int,
) -> None:
    _request_json(
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


def _file_search(
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

    response = _request_json(
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


def _find_matching_result(
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


def _preflight(base_url: str, headers: dict[str, str], timeout: int) -> None:
    health = _request_json(
        method="GET",
        base_url=base_url,
        path="/health",
        headers=headers,
        timeout=timeout,
    )
    if str(health.get("status", "")).lower() != "ok":
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
        description="Run file_search reliability checks for scoped and global lookup behavior.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Polinko API base URL.")
    parser.add_argument(
        "--cases",
        default="docs/file_search_eval_cases.json",
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
    api_key = os.getenv("POLINKO_SERVER_API_KEY")
    headers = _headers(api_key)

    print(f"Running file_search eval on {args.base_url}")
    print(f"Cases: {len(cases)} | run_id={run_id}")
    try:
        _preflight(args.base_url, headers, args.timeout)
    except Exception as exc:
        print(f"Preflight failed: {exc}")
        print("Checks:")
        print("  - Is `make server` running on the expected base URL?")
        print("  - Is vector memory enabled on the running server (`POLINKO_VECTOR_ENABLED=true`)?")
        print("  - Does `.env` contain a valid `POLINKO_SERVER_API_KEY` for this server?")
        return 1

    passes = 0
    failures: list[str] = []
    skipped: list[str] = []
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
        optional = bool(case["optional"])

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
                if optional:
                    case_status = "SKIP"
                    detail = "optional scoped miss"
                    skipped.append(f"{case_id}: optional scoped miss")
                    print("  SKIP optional: scoped hit not found.")
                else:
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
                if optional:
                    case_status = "SKIP"
                    detail = "optional scoped leak"
                    skipped.append(f"{case_id}: optional scoped leak")
                    print("  SKIP optional: scoped results leaked across sessions.")
                else:
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
                if optional:
                    case_status = "SKIP"
                    detail = "optional global miss"
                    skipped.append(f"{case_id}: optional global miss")
                    print("  SKIP optional: global hit not found.")
                else:
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
            if optional:
                case_status = "SKIP"
                detail = f"optional error - {exc}"
                skipped.append(f"{case_id}: optional error - {exc}")
                print(f"  SKIP optional error: {exc}")
            else:
                case_status = "ERROR"
                case_error = str(exc)
                detail = case_error
                error_failures += 1
                failures.append(f"{case_id}: error - {exc}")
                print(f"  ERROR: {exc}")
        finally:
            case_results.append(
                {
                    "id": case_id,
                    "seed_session": seed_session,
                    "distractor_session": distractor_session,
                    "seed_method": seed_method,
                    "source_type": source_type,
                    "optional": optional,
                    "query": case["query"],
                    "must_include": must_include,
                    "status": case_status,
                    "detail": detail,
                    "error": case_error,
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
    print(f"  Skipped: {len(skipped)}")
    print(
        "  Breakdown:"
        f" scoped_miss={scoped_failures}"
        f" global_miss={global_failures}"
        f" scoped_leak={leak_failures}"
        f" errors={error_failures}"
    )
    report_json = str(args.report_json or "").strip()
    if report_json:
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
                "skipped": len(skipped),
                "scoped_miss": scoped_failures,
                "global_miss": global_failures,
                "scoped_leak": leak_failures,
                "errors": error_failures,
            },
            "failures": failures,
            "skipped_entries": skipped,
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
                        "passed": len(failures) == 0 and len(skipped) == 0,
                        "detail": (
                            f"passed={passes}/{len(cases)}, failed={len(failures)}, "
                            f"skipped={len(skipped)}, errors={error_failures}"
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
    for entry in skipped:
        print(f"  - SKIP {entry}")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
