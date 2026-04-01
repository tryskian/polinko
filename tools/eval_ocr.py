import argparse
import base64
import json
import mimetypes
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from tools.eval_gate import gate_counts_from_case_results
from tools.eval_gate import resolve_fail_closed_status
from tools.eval_trace_artifacts import DEFAULT_TRACE_JSONL
from tools.eval_trace_artifacts import append_eval_trace
from tools.eval_trace_artifacts import build_eval_trace

SPACED_LETTER_WORD_RX = re.compile(r"\b(?:[A-Za-z]\s+){2,}[A-Za-z]\b")
OCR_WORD_TOKEN_RX = re.compile(r"\b[a-z0-9-]+\b")


def _contains_optional_letter_spacing(
    *,
    haystack: str,
    probe: str,
    whole_word: bool,
    allow_punctuation_gaps: bool = False,
) -> bool:
    """Match probes when OCR inserts spaces inside a single word token."""
    if not probe or re.search(r"\s", probe):
        return False
    if not re.fullmatch(r"[\w-]+", probe):
        return False
    pieces = [re.escape(char) for char in probe]
    separator_pattern = r"[\s\W_]*" if allow_punctuation_gaps else r"\s*"
    spaced_pattern = separator_pattern.join(pieces)
    if whole_word:
        spaced_pattern = rf"(?<!\w){spaced_pattern}(?!\w)"
    return re.search(spaced_pattern, haystack) is not None


def _single_token_signature(value: str) -> str:
    compact = re.sub(r"[^a-z0-9-]", "", value.lower())
    compact = re.sub(r"(.)\1+", r"\1", compact)
    compact = re.sub(r"[aeiouy]", "", compact)
    return compact


def _edit_distance_at_most_one(lhs: str, rhs: str) -> bool:
    if lhs == rhs:
        return True
    lhs_len = len(lhs)
    rhs_len = len(rhs)
    if abs(lhs_len - rhs_len) > 1:
        return False
    if lhs_len == rhs_len:
        mismatches = sum(1 for index in range(lhs_len) if lhs[index] != rhs[index])
        return mismatches <= 1
    if lhs_len > rhs_len:
        lhs, rhs = rhs, lhs
        lhs_len, rhs_len = rhs_len, lhs_len
    # rhs is exactly one char longer than lhs.
    lhs_index = 0
    rhs_index = 0
    edits = 0
    while lhs_index < lhs_len and rhs_index < rhs_len:
        if lhs[lhs_index] == rhs[rhs_index]:
            lhs_index += 1
            rhs_index += 1
            continue
        edits += 1
        if edits > 1:
            return False
        rhs_index += 1
    if rhs_index < rhs_len or lhs_index < lhs_len:
        edits += 1
    return edits <= 1


def _contains_near_single_token(*, tokens: list[str], probe: str) -> bool:
    # Allow one-character OCR drift on longer single-token anchors only.
    if not re.fullmatch(r"[a-z0-9-]{6,}", probe):
        return False
    probe_signature = _single_token_signature(probe)
    for token in tokens:
        if token[:1] != probe[:1]:
            continue
        token_signature = _single_token_signature(token)
        if (
            probe_signature
            and len(probe_signature) >= 4
            and token_signature == probe_signature
            and abs(len(token) - len(probe)) <= 3
        ):
            return True
        if (
            probe_signature
            and token_signature
            and len(probe) >= 8
            and abs(len(token) - len(probe)) <= 3
            and abs(len(token_signature) - len(probe_signature)) <= 1
            and _edit_distance_at_most_one(token_signature, probe_signature)
        ):
            return True
        # Keep a strict final-character guard for shorter anchors, but allow
        # terminal OCR drift on longer anchors (for example `stirring` -> `stirriny`).
        if 5 <= len(probe) < 8 and token[-1:] != probe[-1:]:
            continue
        if abs(len(token) - len(probe)) > 1:
            continue
        if _edit_distance_at_most_one(token, probe):
            return True
    return False


def _find_ordered_phrase_index(
    *,
    haystack: str,
    phrase: str,
    cursor: int,
    case_sensitive: bool,
) -> tuple[int, int] | None:
    probe = phrase if case_sensitive else phrase.lower()
    direct_index = haystack.find(probe, cursor)
    if direct_index >= 0:
        return direct_index, len(probe)
    if not re.fullmatch(r"[a-z0-9-]{6,}", probe):
        return None
    for match in OCR_WORD_TOKEN_RX.finditer(haystack[cursor:]):
        token = match.group(0)
        if _contains_near_single_token(tokens=[token], probe=probe):
            start = cursor + match.start()
            return start, len(token)
    return None


def _headers() -> dict[str, str]:
    return {"Content-Type": "application/json"}


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


def _collapse_spaced_letter_words(text: str) -> str:
    """Normalize OCR outputs like 'C H A T T I E S T' -> 'CHATTIEST' for matching."""

    def _join_letters(match: re.Match[str]) -> str:
        return re.sub(r"\s+", "", match.group(0))

    return SPACED_LETTER_WORD_RX.sub(_join_letters, text)


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


def _is_transient_ocr_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return (
        "connection error" in message
        or "timed out" in message
        or "http 5" in message
        or "http 429" in message
    )


def _ocr_with_retries(
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
    ocr_retries: int,
    ocr_retry_delay_ms: int,
) -> dict[str, Any]:
    if ocr_retries < 0:
        raise RuntimeError("ocr_retries must be >= 0.")
    if ocr_retry_delay_ms < 0:
        raise RuntimeError("ocr_retry_delay_ms must be >= 0.")

    max_attempts = ocr_retries + 1
    for attempt in range(1, max_attempts + 1):
        try:
            return _ocr(
                base_url=base_url,
                headers=headers,
                session_id=session_id,
                source_name=source_name,
                mime_type=mime_type,
                data_base64=data_base64,
                text_hint=text_hint,
                visual_context_hint=visual_context_hint,
                transcription_mode=transcription_mode,
                timeout=timeout,
            )
        except Exception as exc:
            if attempt >= max_attempts or not _is_transient_ocr_error(exc):
                raise
            print(
                f"  WARN transient OCR error for {session_id} "
                f"(attempt {attempt}/{max_attempts - 1} retries): {exc}"
            )
            if ocr_retry_delay_ms > 0:
                time.sleep(ocr_retry_delay_ms / 1000)
    raise RuntimeError("OCR call failed after retries.")


def _check_case(case: dict[str, Any], extracted_text: str) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    case_sensitive = bool(case["case_sensitive"])
    haystack = extracted_text if case_sensitive else extracted_text.lower()
    haystack_spaced_normalized = _collapse_spaced_letter_words(haystack)
    haystack_word_tokens = OCR_WORD_TOKEN_RX.findall(haystack_spaced_normalized)

    def contains(needle: str) -> bool:
        probe = needle if case_sensitive else needle.lower()
        return (
            probe in haystack
            or probe in haystack_spaced_normalized
            or _contains_optional_letter_spacing(
                haystack=haystack,
                probe=probe,
                whole_word=False,
                allow_punctuation_gaps=True,
            )
        )

    def contains_required(needle: str) -> bool:
        probe = needle if case_sensitive else needle.lower()
        return contains(needle) or _contains_near_single_token(tokens=haystack_word_tokens, probe=probe)

    def contains_word(word: str) -> bool:
        probe = word if case_sensitive else word.lower()
        pattern = re.compile(rf"(?<!\w){re.escape(probe)}(?!\w)")
        return (
            bool(pattern.search(haystack))
            or bool(pattern.search(haystack_spaced_normalized))
            or _contains_optional_letter_spacing(haystack=haystack, probe=probe, whole_word=True)
        )

    for phrase in case["must_contain"]:
        if not contains_required(phrase):
            reasons.append(f"missing required phrase: {phrase!r}")

    if case["must_contain_any"]:
        if not any(contains_required(phrase) for phrase in case["must_contain_any"]):
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
            match = _find_ordered_phrase_index(
                haystack=haystack_spaced_normalized,
                phrase=phrase,
                cursor=cursor,
                case_sensitive=case_sensitive,
            )
            if match is None:
                reasons.append(
                    f"missing ordered phrase: {phrase!r} after offset {cursor}"
                )
                break
            index, length = match
            cursor = index + length

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


def _select_cases(
    cases: list[dict[str, Any]],
    *,
    offset: int = 0,
    max_cases: int = 0,
) -> list[dict[str, Any]]:
    if offset < 0:
        raise RuntimeError("--offset must be >= 0.")
    if max_cases < 0:
        raise RuntimeError("--max-cases must be >= 0.")
    selected = cases[offset:]
    if max_cases > 0:
        selected = selected[:max_cases]
    return selected


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run OCR eval cases against /skills/ocr.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Polinko API base URL.")
    parser.add_argument(
        "--cases",
        default="docs/eval/cases/ocr_eval_cases.json",
        help="Path to OCR eval cases JSON file.",
    )
    parser.add_argument("--session-prefix", default="ocr-eval", help="Session id prefix for generated eval chats.")
    parser.add_argument("--run-id", default="", help="Optional run id suffix. Defaults to current epoch seconds.")
    parser.add_argument("--timeout", type=int, default=90, help="HTTP timeout in seconds.")
    parser.add_argument(
        "--ocr-retries",
        type=int,
        default=0,
        help="Transient OCR retry count for timeout/connection/5xx/429 failures.",
    )
    parser.add_argument(
        "--ocr-retry-delay-ms",
        type=int,
        default=750,
        help="Delay between OCR retries in milliseconds.",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any case fails.")
    parser.add_argument("--keep-chats", action="store_true", help="Keep generated eval chats.")
    parser.add_argument("--show-text", action="store_true", help="Print extracted text for each case.")
    parser.add_argument("--offset", type=int, default=0, help="Skip first N cases before evaluation.")
    parser.add_argument(
        "--max-cases",
        type=int,
        default=0,
        help="Evaluate at most N cases after offset (0 = all remaining).",
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
    try:
        selected_cases = _select_cases(cases, offset=args.offset, max_cases=args.max_cases)
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
    if not selected_cases:
        raise SystemExit(
            f"No OCR eval cases selected from {cases_path} (total={len(cases)} offset={args.offset} max_cases={args.max_cases})."
        )
    if int(args.ocr_retries) < 0:
        raise SystemExit("--ocr-retries must be >= 0.")
    if int(args.ocr_retry_delay_ms) < 0:
        raise SystemExit("--ocr-retry-delay-ms must be >= 0.")
    run_id = args.run_id.strip() or f"{int(time.time() * 1000)}-{os.getpid()}-{uuid.uuid4().hex[:6]}"
    headers = _headers()

    print(f"Running OCR eval on {args.base_url}")
    print(
        f"Cases: {len(selected_cases)}/{len(cases)} "
        f"(offset={args.offset} max_cases={args.max_cases}) | run_id={run_id}"
    )

    try:
        _preflight(args.base_url, headers, args.timeout)
    except Exception as exc:
        print(f"Preflight failed: {exc}")
        return 2

    total_selected = len(selected_cases)
    failures = 0
    errors = 0
    session_ids: list[str] = []
    case_results: list[dict[str, Any]] = []

    for index, case in enumerate(selected_cases, start=1):
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
            payload = _ocr_with_retries(
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
                ocr_retries=args.ocr_retries,
                ocr_retry_delay_ms=args.ocr_retry_delay_ms,
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
            gate_decision = resolve_fail_closed_status(
                status=status,
                detail=error_text or "; ".join(reasons),
            )
            case_results.append(
                {
                    "id": case_id,
                    "session_id": session_id,
                    "status": status,
                    "error": error_text,
                    "gate_outcome": gate_decision.outcome,
                    "gate_reasons": list(gate_decision.reasons),
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

    passed_count = total_selected - failures
    print("\nSummary")
    print(f"  Passed: {passed_count}/{total_selected}")
    print(f"  Failed: {failures}")
    print(f"  Errors: {errors}")
    report_json = str(args.report_json or "").strip()
    if report_json:
        gate_passed, gate_failed = gate_counts_from_case_results(case_results)
        output_path = Path(report_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report_payload = {
            "run_id": run_id,
            "base_url": args.base_url,
            "cases_path": str(cases_path),
            "strict": bool(args.strict),
            "summary": {
                "total": total_selected,
                "passed": passed_count,
                "failed": failures,
                "errors": errors,
                "gate_passed": gate_passed,
                "gate_failed": gate_failed,
                "offset": int(args.offset),
                "max_cases": int(args.max_cases),
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
                        "passed": gate_failed == 0,
                        "detail": (
                            f"passed={passed_count}/{total_selected}, "
                            f"failed={failures}, errors={errors}, gate_failed={gate_failed}"
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
