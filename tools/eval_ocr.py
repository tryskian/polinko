import argparse
import base64
import json
import mimetypes
import os
import re
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


def _load_cases(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Cases file must be a JSON object.")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise RuntimeError("Cases file must include a non-empty 'cases' list.")
    normalized: list[dict[str, Any]] = []
    for idx, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            raise RuntimeError(f"Case #{idx} must be an object.")
        case_id = str(case.get("id", f"ocr-{idx}")).strip()
        image_path = str(case.get("image_path", "")).strip()
        text_hint = str(case.get("text_hint", "")).strip()
        visual_context_hint = str(case.get("visual_context_hint", "")).strip()
        mime_type = str(case.get("mime_type", "")).strip().lower()
        if not case_id:
            raise RuntimeError(f"Case #{idx} must include non-empty 'id'.")
        if not image_path and not text_hint:
            raise RuntimeError(f"Case '{case_id}' must include either 'image_path' or 'text_hint'.")
        if mime_type and "/" not in mime_type:
            raise RuntimeError(f"Case '{case_id}' mime_type must look like type/subtype.")

        must_contain = [str(x).strip() for x in case.get("must_contain", []) if str(x).strip()]
        must_contain_any = [str(x).strip() for x in case.get("must_contain_any", []) if str(x).strip()]
        must_not_contain = [str(x).strip() for x in case.get("must_not_contain", []) if str(x).strip()]
        must_not_contain_words = [str(x).strip() for x in case.get("must_not_contain_words", []) if str(x).strip()]
        must_appear_in_order = [str(x).strip() for x in case.get("must_appear_in_order", []) if str(x).strip()]
        must_match_regex = [str(x).strip() for x in case.get("must_match_regex", []) if str(x).strip()]
        must_not_match_regex = [str(x).strip() for x in case.get("must_not_match_regex", []) if str(x).strip()]
        transcription_mode = str(case.get("transcription_mode", "verbatim")).strip() or "verbatim"
        if transcription_mode not in {"verbatim", "normalized"}:
            raise RuntimeError(f"Case '{case_id}' transcription_mode must be verbatim|normalized.")
        min_chars = case.get("min_chars")
        max_chars = case.get("max_chars")
        if min_chars is not None:
            min_chars = int(min_chars)
            if min_chars < 0:
                raise RuntimeError(f"Case '{case_id}' min_chars must be >= 0.")
        if max_chars is not None:
            max_chars = int(max_chars)
            if max_chars < 1:
                raise RuntimeError(f"Case '{case_id}' max_chars must be >= 1.")

        normalized.append(
            {
                "id": case_id,
                "image_path": image_path,
                "source_name": str(case.get("source_name", Path(image_path).name if image_path else case_id)).strip()
                or None,
                "mime_type": mime_type or None,
                "text_hint": text_hint or None,
                "visual_context_hint": visual_context_hint or None,
                "transcription_mode": transcription_mode,
                "must_contain": must_contain,
                "must_contain_any": must_contain_any,
                "must_not_contain": must_not_contain,
                "must_not_contain_words": must_not_contain_words,
                "must_appear_in_order": must_appear_in_order,
                "must_match_regex": must_match_regex,
                "must_not_match_regex": must_not_match_regex,
                "min_chars": min_chars,
                "max_chars": max_chars,
                "case_sensitive": bool(case.get("case_sensitive", False)),
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


def _ocr(
    *,
    base_url: str,
    headers: dict[str, str],
    session_id: str,
    source_name: str | None,
    mime_type: str,
    data_base64: str,
    text_hint: str | None,
    visual_context_hint: str | None,
    transcription_mode: str,
    timeout: int,
) -> dict[str, Any]:
    payload = {
        "session_id": session_id,
        "source_name": source_name,
        "mime_type": mime_type,
        "data_base64": data_base64,
        "text_hint": text_hint,
        "visual_context_hint": visual_context_hint,
        "transcription_mode": transcription_mode,
        "attach_to_chat": False,
    }
    return _request_json(
        method="POST",
        base_url=base_url,
        path="/skills/ocr",
        headers=headers,
        payload=payload,
        timeout=timeout,
    )


def _check_case(case: dict[str, Any], extracted_text: str) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    case_sensitive = bool(case["case_sensitive"])
    haystack = extracted_text if case_sensitive else extracted_text.lower()

    def contains(needle: str) -> bool:
        probe = needle if case_sensitive else needle.lower()
        return probe in haystack

    def contains_word(word: str) -> bool:
        probe = word if case_sensitive else word.lower()
        pattern = re.compile(rf"(?<!\w){re.escape(probe)}(?!\w)")
        return bool(pattern.search(haystack))

    for phrase in case["must_contain"]:
        if not contains(phrase):
            reasons.append(f"missing required phrase: {phrase!r}")

    if case["must_contain_any"]:
        if not any(contains(phrase) for phrase in case["must_contain_any"]):
            reasons.append(f"missing one-of required phrases: {case['must_contain_any']}")

    for phrase in case["must_not_contain"]:
        if contains(phrase):
            reasons.append(f"contains forbidden phrase: {phrase!r}")

    for word in case["must_not_contain_words"]:
        if contains_word(word):
            reasons.append(f"contains forbidden whole word: {word!r}")

    if case["must_appear_in_order"]:
        cursor = 0
        for phrase in case["must_appear_in_order"]:
            probe = phrase if case_sensitive else phrase.lower()
            index = haystack.find(probe, cursor)
            if index < 0:
                reasons.append(
                    f"missing ordered phrase: {phrase!r} after offset {cursor}"
                )
                break
            cursor = index + len(probe)

    regex_flags = 0 if case_sensitive else re.IGNORECASE
    for pattern in case["must_match_regex"]:
        try:
            if re.search(pattern, extracted_text, flags=regex_flags) is None:
                reasons.append(f"regex did not match: /{pattern}/")
        except re.error as exc:
            reasons.append(f"invalid must_match_regex pattern /{pattern}/: {exc}")

    for pattern in case["must_not_match_regex"]:
        try:
            if re.search(pattern, extracted_text, flags=regex_flags) is not None:
                reasons.append(f"forbidden regex matched: /{pattern}/")
        except re.error as exc:
            reasons.append(f"invalid must_not_match_regex pattern /{pattern}/: {exc}")

    length = len(extracted_text)
    min_chars = case["min_chars"]
    max_chars = case["max_chars"]
    if isinstance(min_chars, int) and length < min_chars:
        reasons.append(f"text too short: {length} < min_chars={min_chars}")
    if isinstance(max_chars, int) and length > max_chars:
        reasons.append(f"text too long: {length} > max_chars={max_chars}")

    return (len(reasons) == 0), reasons


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run OCR eval cases against /skills/ocr.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Polinko API base URL.")
    parser.add_argument(
        "--cases",
        default="docs/ocr_eval_cases.json",
        help="Path to OCR eval cases JSON file.",
    )
    parser.add_argument("--session-prefix", default="ocr-eval", help="Session id prefix for generated eval chats.")
    parser.add_argument("--run-id", default="", help="Optional run id suffix. Defaults to current epoch seconds.")
    parser.add_argument("--timeout", type=int, default=90, help="HTTP timeout in seconds.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any case fails.")
    parser.add_argument("--keep-chats", action="store_true", help="Keep generated eval chats.")
    parser.add_argument("--show-text", action="store_true", help="Print extracted text for each case.")
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

    print(f"Running OCR eval on {args.base_url}")
    print(f"Cases: {len(cases)} | run_id={run_id}")

    try:
        _preflight(args.base_url, headers, args.timeout)
    except Exception as exc:
        print(f"Preflight failed: {exc}")
        return 2

    failures = 0
    errors = 0
    session_ids: list[str] = []
    case_results: list[dict[str, Any]] = []

    for index, case in enumerate(cases, start=1):
        case_id = case["id"]
        session_id = f"{args.session_prefix}-{run_id}-{index:02d}"
        session_ids.append(session_id)
        image_path_value = str(case["image_path"]).strip()
        image_path = Path(image_path_value).expanduser() if image_path_value else None
        extracted_text = ""
        reasons: list[str] = []
        status = "PASS"
        error_text = ""
        mime_type = ""
        try:
            _create_chat(args.base_url, headers, session_id, args.timeout)
            if image_path is not None:
                if not image_path.is_file():
                    raise RuntimeError(f"image_path does not exist: {image_path}")
                raw_bytes = image_path.read_bytes()
            else:
                # Placeholder payload for text-hint-only deterministic cases.
                raw_bytes = b"0"
            data_base64 = base64.b64encode(raw_bytes).decode("ascii")
            inferred_mime = case["mime_type"] or (
                mimetypes.guess_type(str(image_path))[0] if image_path is not None else "application/octet-stream"
            )
            mime_type = str(inferred_mime or "application/octet-stream")
            payload = _ocr(
                base_url=args.base_url,
                headers=headers,
                session_id=session_id,
                source_name=case["source_name"],
                mime_type=mime_type,
                data_base64=data_base64,
                text_hint=case["text_hint"],
                visual_context_hint=case["visual_context_hint"],
                transcription_mode=case["transcription_mode"],
                timeout=args.timeout,
            )
            extracted_text = str(payload.get("run", {}).get("extracted_text", "")).strip()
            passed, reasons = _check_case(case, extracted_text)
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] {case_id} chars={len(extracted_text)} mode={case['transcription_mode']}")
            if args.show_text:
                print(f"  text: {extracted_text!r}")
            if reasons:
                for reason in reasons:
                    print(f"  - {reason}")
            if not passed:
                failures += 1
        except Exception as exc:
            status = "ERROR"
            error_text = str(exc)
            errors += 1
            failures += 1
            print(f"[ERROR] {case_id}: {exc}")
        finally:
            case_results.append(
                {
                    "id": case_id,
                    "session_id": session_id,
                    "status": status,
                    "error": error_text,
                    "image_path": str(image_path) if image_path is not None else None,
                    "source_name": case["source_name"],
                    "mime_type": mime_type or case["mime_type"],
                    "transcription_mode": case["transcription_mode"],
                    "text_hint_present": bool(case["text_hint"]),
                    "visual_context_hint_present": bool(case["visual_context_hint"]),
                    "must_contain": list(case["must_contain"]),
                    "must_contain_any": list(case["must_contain_any"]),
                    "must_not_contain": list(case["must_not_contain"]),
                    "must_not_contain_words": list(case["must_not_contain_words"]),
                    "must_appear_in_order": list(case["must_appear_in_order"]),
                    "must_match_regex": list(case["must_match_regex"]),
                    "must_not_match_regex": list(case["must_not_match_regex"]),
                    "min_chars": case["min_chars"],
                    "max_chars": case["max_chars"],
                    "char_count": len(extracted_text),
                    "reasons": reasons,
                    "extracted_text": extracted_text,
                }
            )

    if not args.keep_chats:
        for session_id in session_ids:
            try:
                _delete_chat(args.base_url, headers, session_id, args.timeout)
            except Exception as exc:
                print(f"  WARN cleanup failed for {session_id}: {exc}")

    passed_count = len(cases) - failures
    print("\nSummary")
    print(f"  Passed: {passed_count}/{len(cases)}")
    print(f"  Failed: {failures}")
    print(f"  Errors: {errors}")
    report_json = str(args.report_json or "").strip()
    if report_json:
        output_path = Path(report_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report_payload = {
            "run_id": run_id,
            "base_url": args.base_url,
            "cases_path": str(cases_path),
            "strict": bool(args.strict),
            "summary": {
                "total": len(cases),
                "passed": passed_count,
                "failed": failures,
                "errors": errors,
            },
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
                tool_name="tools/eval_ocr.py",
                source_artifacts={
                    "report_json": str(output_path),
                    "cases_path": str(cases_path),
                },
                gate_outcomes=[
                    {
                        "name": "ocr_eval",
                        "passed": failures == 0,
                        "detail": (
                            f"passed={passed_count}/{len(cases)}, "
                            f"failed={failures}, errors={errors}"
                        ),
                    }
                ],
                summary=report_payload["summary"],
                metadata={
                    "base_url": args.base_url,
                    "strict": bool(args.strict),
                },
            )
            trace_path = append_eval_trace(
                trace_payload=trace_payload,
                trace_jsonl_path=Path(trace_jsonl),
            )
            print(f"  Trace: {trace_path}")

    if failures > 0 and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
