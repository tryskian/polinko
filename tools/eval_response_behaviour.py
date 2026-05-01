import argparse
import json
import re
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from tools.eval_chat_common import chat_message as _chat
from tools.eval_chat_common import create_chat as _create_chat
from tools.eval_chat_common import default_headers as _headers
from tools.eval_chat_common import delete_chat as _delete_chat
from tools.eval_chat_common import preflight as _preflight
from tools.eval_chat_common import request_json as _request_json
from tools.eval_gate import resolve_binary_gate
from tools.eval_trace_artifacts import DEFAULT_TRACE_JSONL
from tools.eval_trace_artifacts import append_eval_trace
from tools.eval_trace_artifacts import build_eval_trace


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _normalize_text_for_match(text: str) -> str:
    normalized = (
        text.lower()
        .replace("’", "'")
        .replace("‘", "'")
        .replace("`", "'")
        .replace("“", '"')
        .replace("”", '"')
        .replace("‑", "-")
        .replace("–", "-")
        .replace("—", "-")
    )
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _normalize_phrase_list(raw: Any, *, field_name: str, case_id: str) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise RuntimeError(f"Case '{case_id}' field '{field_name}' must be a list of strings.")
    normalized: list[str] = []
    for value in raw:
        phrase = _normalize_text_for_match(str(value))
        if phrase:
            normalized.append(phrase)
    return normalized


def _normalize_phrase_groups(raw: Any, *, field_name: str, case_id: str) -> list[list[str]]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise RuntimeError(f"Case '{case_id}' field '{field_name}' must be a list of string lists.")
    groups: list[list[str]] = []
    for group in raw:
        if not isinstance(group, list):
            raise RuntimeError(f"Case '{case_id}' field '{field_name}' must only contain lists.")
        normalized_group: list[str] = []
        for value in group:
            phrase = _normalize_text_for_match(str(value))
            if phrase:
                normalized_group.append(phrase)
        if normalized_group:
            groups.append(normalized_group)
    return groups


def _load_cases(path: Path, *, default_case_prefix: str = "response-behaviour") -> list[dict[str, Any]]:
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
        case_id = str(case.get("id", f"{default_case_prefix}-{index}")).strip()
        query = str(case.get("query", "")).strip()
        if not case_id or not query:
            raise RuntimeError(f"Case #{index} must include non-empty 'id' and 'query'.")

        max_words_raw = case.get("max_words")
        max_words: int | None = None
        if max_words_raw is not None:
            try:
                parsed = int(max_words_raw)
            except (TypeError, ValueError) as exc:
                raise RuntimeError(f"Case '{case_id}' has invalid max_words.") from exc
            if parsed <= 0:
                raise RuntimeError(f"Case '{case_id}' max_words must be > 0.")
            max_words = parsed

        normalized.append(
            {
                "id": case_id,
                "query": query,
                "required_all": _normalize_phrase_list(
                    case.get("required_all"),
                    field_name="required_all",
                    case_id=case_id,
                ),
                "required_any_groups": _normalize_phrase_groups(
                    case.get("required_any_groups"),
                    field_name="required_any_groups",
                    case_id=case_id,
                ),
                "must_not_contain": _normalize_phrase_list(
                    case.get("must_not_contain"),
                    field_name="must_not_contain",
                    case_id=case_id,
                ),
                "max_words": max_words,
            }
        )
    return normalized


def _contains_forbidden_phrases(answer: str, forbidden_phrases: list[str]) -> list[str]:
    lowered = _normalize_text_for_match(answer)
    hits: list[str] = []
    for phrase in forbidden_phrases:
        if phrase and phrase in lowered:
            hits.append(phrase)
    return hits


def _missing_required_all(answer: str, required_all: list[str]) -> list[str]:
    lowered = _normalize_text_for_match(answer)
    return [phrase for phrase in required_all if phrase and phrase not in lowered]


def _missing_required_any_groups(answer: str, required_any_groups: list[list[str]]) -> list[list[str]]:
    lowered = _normalize_text_for_match(answer)
    missing: list[list[str]] = []
    for group in required_any_groups:
        if not any(phrase in lowered for phrase in group):
            missing.append(group)
    return missing


def _apply_deterministic_gate(
    *,
    case: dict[str, Any],
    answer: str,
) -> dict[str, Any]:
    forbidden_hits = _contains_forbidden_phrases(answer, case["must_not_contain"])
    missing_all = _missing_required_all(answer, case["required_all"])
    missing_any_groups = _missing_required_any_groups(answer, case["required_any_groups"])
    word_count = _word_count(answer)
    max_words = case["max_words"]
    word_count_ok = not isinstance(max_words, int) or word_count <= max_words
    answer_non_empty = bool(answer.strip())

    decision = resolve_binary_gate(
        policy_pass=not forbidden_hits,
        high_value_alignment_pass=not missing_all and not missing_any_groups,
        evidence_complete=word_count_ok and answer_non_empty,
    )

    fail_reasons: list[str] = list(decision.reasons)
    if forbidden_hits:
        fail_reasons.append(f"contains forbidden phrases: {forbidden_hits}")
    if missing_all:
        fail_reasons.append(f"missing required_all phrases: {missing_all}")
    if missing_any_groups:
        fail_reasons.append(f"missing required_any_groups: {missing_any_groups}")
    if not answer_non_empty:
        fail_reasons.append("assistant answer was empty")
    if isinstance(max_words, int) and not word_count_ok:
        fail_reasons.append(f"word count {word_count} exceeds max_words={max_words}")

    deduped: list[str] = []
    seen: set[str] = set()
    for reason in fail_reasons:
        if reason in seen:
            continue
        seen.add(reason)
        deduped.append(reason)

    return {
        "pass": decision.passed,
        "gate_outcome": decision.outcome,
        "word_count": word_count,
        "forbidden_hits": forbidden_hits,
        "missing_required_all": missing_all,
        "missing_required_any_groups": missing_any_groups,
        "fail_reasons": deduped,
    }


def _resolve_case_status(
    *,
    attempt_statuses: list[str],
    pass_attempts: int,
    min_pass_attempts: int,
) -> str:
    if pass_attempts >= min_pass_attempts:
        return "PASS"
    if any(status == "FAIL" for status in attempt_statuses):
        return "FAIL"
    return "ERROR"


def _should_stop_attempts(
    *,
    pass_attempts: int,
    attempts_done: int,
    case_attempts: int,
    min_pass_attempts: int,
) -> bool:
    if pass_attempts >= min_pass_attempts:
        return True
    remaining_attempts = case_attempts - attempts_done
    needed_passes = min_pass_attempts - pass_attempts
    return needed_passes > remaining_attempts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run deterministic response-behaviour eval over /chat outputs.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Polinko API base URL.")
    parser.add_argument(
        "--cases",
        default="docs/eval/beta_2_0/response_behaviour_eval_cases.json",
        help="Path to response-behaviour eval cases JSON file.",
    )
    parser.add_argument(
        "--session-prefix",
        default="response-behaviour-eval",
        help="Session id prefix for generated eval chats.",
    )
    parser.add_argument(
        "--suite-id",
        default="response_behaviour",
        help="Logical suite id used in trace metadata (snake_case).",
    )
    parser.add_argument(
        "--run-id",
        default="",
        help="Optional run id suffix. Defaults to current epoch seconds.",
    )
    parser.add_argument("--timeout", type=int, default=90, help="HTTP timeout in seconds.")
    parser.add_argument(
        "--case-attempts",
        type=int,
        default=3,
        help="Attempts per case (for retry-majority hardening).",
    )
    parser.add_argument(
        "--min-pass-attempts",
        type=int,
        default=2,
        help="Minimum passing attempts required per case.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any case fails.",
    )
    parser.add_argument(
        "--keep-chats",
        action="store_true",
        help="Keep generated eval chats instead of deleting them.",
    )
    parser.add_argument(
        "--report-json",
        default="",
        help="Optional path to write a JSON report.",
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
    if args.case_attempts < 1:
        raise SystemExit("--case-attempts must be >= 1.")
    if args.min_pass_attempts < 1:
        raise SystemExit("--min-pass-attempts must be >= 1.")
    if args.min_pass_attempts > args.case_attempts:
        raise SystemExit("--min-pass-attempts cannot exceed --case-attempts.")
    suite_id = str(args.suite_id).strip().lower().replace("-", "_")
    if not suite_id or not re.fullmatch(r"[a-z0-9_]+", suite_id):
        raise SystemExit("--suite-id must match [a-z0-9_]+.")

    cases_path = Path(args.cases)
    if not cases_path.exists():
        raise SystemExit(f"Cases file not found: {cases_path}")
    cases = _load_cases(cases_path, default_case_prefix=suite_id.replace("_", "-"))
    run_id = args.run_id.strip() or str(int(time.time()))
    headers = _headers()

    print(f"Running {suite_id} eval on {args.base_url}")
    print(f"Cases: {len(cases)} | run_id={run_id}")
    print(
        "Attempts per case: "
        f"{args.case_attempts} | min passes required: {args.min_pass_attempts}"
    )
    try:
        _preflight(args.base_url, headers, args.timeout)
    except Exception as exc:
        print(f"Preflight failed: {exc}")
        print("Checks:")
        print("  - Is `make server` running on the expected base URL?")
        return 1

    passes = 0
    failures: list[str] = []
    case_results: list[dict[str, Any]] = []

    for index, case in enumerate(cases, start=1):
        print(f"\n[{index}/{len(cases)}] {case['id']}")
        attempt_results: list[dict[str, Any]] = []
        attempt_statuses: list[str] = []
        pass_attempts = 0

        for attempt in range(1, args.case_attempts + 1):
            session_base = f"{args.session_prefix}-{run_id}-{case['id']}"
            session_id = (
                session_base if args.case_attempts == 1 else f"{session_base}-a{attempt:02d}"
            )
            status_text = "PASS"
            answer = ""
            assessment: dict[str, Any] = {
                "pass": False,
                "gate_outcome": "fail",
                "word_count": 0,
                "forbidden_hits": [],
                "missing_required_all": [],
                "missing_required_any_groups": [],
                "fail_reasons": [],
            }
            error_text: str | None = None
            try:
                _create_chat(args.base_url, headers, session_id, args.timeout)
                chat_payload = _chat(
                    base_url=args.base_url,
                    headers=headers,
                    session_id=session_id,
                    message=case["query"],
                    timeout=args.timeout,
                )
                answer = str(chat_payload.get("output", "")).strip()
                assessment = _apply_deterministic_gate(case=case, answer=answer)
                status_text = "PASS" if bool(assessment["pass"]) else "FAIL"
                if status_text == "PASS":
                    pass_attempts += 1
                    print(
                        f"  PASS attempt={attempt}/{args.case_attempts} "
                        f"words={assessment['word_count']}"
                    )
                else:
                    joined = "; ".join(assessment["fail_reasons"]) or "deterministic gate failed"
                    print(
                        f"  FAIL attempt={attempt}/{args.case_attempts} "
                        f"words={assessment['word_count']} reasons={joined}"
                    )
            except Exception as exc:
                status_text = "ERROR"
                error_text = str(exc)
                print(f"  ERROR attempt={attempt}/{args.case_attempts} {error_text}")
            finally:
                attempt_statuses.append(status_text)
                attempt_results.append(
                    {
                        "session_id": session_id,
                        "status": status_text,
                        "answer": answer,
                        "assessment": assessment,
                        "error": error_text,
                    }
                )
                if not args.keep_chats:
                    try:
                        _delete_chat(args.base_url, headers, session_id, args.timeout)
                    except Exception as exc:
                        print(f"  WARN cleanup failed for {session_id}: {exc}")

            if _should_stop_attempts(
                pass_attempts=pass_attempts,
                attempts_done=attempt,
                case_attempts=args.case_attempts,
                min_pass_attempts=args.min_pass_attempts,
            ):
                break

        final_status = _resolve_case_status(
            attempt_statuses=attempt_statuses,
            pass_attempts=pass_attempts,
            min_pass_attempts=args.min_pass_attempts,
        )
        final_attempt = next(
            (row for row in attempt_results if row["status"] == "PASS"),
            attempt_results[-1],
        )
        final_assessment = (
            final_attempt["assessment"] if isinstance(final_attempt.get("assessment"), dict) else {}
        )
        final_reasons = (
            list(final_assessment.get("fail_reasons", []))
            if isinstance(final_assessment.get("fail_reasons"), list)
            else []
        )
        if final_status == "PASS":
            passes += 1
        elif final_status == "ERROR":
            error_text = str(final_attempt.get("error") or "unknown error")
            failures.append(f"{case['id']}: error - {error_text}")
        else:
            joined = "; ".join(final_reasons) if final_reasons else "deterministic gate failed"
            failures.append(f"{case['id']}: {joined}")

        case_results.append(
            {
                "id": case["id"],
                "session_id": str(final_attempt.get("session_id", "")),
                "query": case["query"],
                "answer": str(final_attempt.get("answer", "")),
                "status": final_status,
                "gate_outcome": str(final_assessment.get("gate_outcome", "fail")),
                "word_count": int(final_assessment.get("word_count", 0)),
                "forbidden_hits": list(final_assessment.get("forbidden_hits", [])),
                "missing_required_all": list(final_assessment.get("missing_required_all", [])),
                "missing_required_any_groups": list(
                    final_assessment.get("missing_required_any_groups", [])
                ),
                "fail_reasons": final_reasons,
                "attempts_used": len(attempt_results),
                "pass_attempts": pass_attempts,
                "attempts": attempt_results,
            }
        )

    print("\nSummary")
    print(f"  Passed: {passes}/{len(cases)}")
    print(f"  Failed: {len(failures)}")
    if failures:
        for item in failures:
            print(f"  - {item}")

    report_json = str(args.report_json or "").strip()
    if report_json:
        report_path = Path(report_json)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_payload = {
            "run_id": run_id,
            "suite_id": suite_id,
            "base_url": args.base_url,
            "cases_path": str(cases_path),
            "strict": bool(args.strict),
            "case_attempts": args.case_attempts,
            "min_pass_attempts": args.min_pass_attempts,
            "summary": {
                "total": len(cases),
                "passed": passes,
                "failed": len(failures),
            },
            "cases": case_results,
            "generated_at": int(time.time()),
        }
        report_path.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Report written: {report_path}")
        trace_jsonl = str(args.trace_jsonl or "").strip()
        if trace_jsonl:
            trace_payload = build_eval_trace(
                run_id=run_id,
                tool_name="tools/eval_response_behaviour.py",
                source_artifacts={
                    "report_json": str(report_path),
                    "cases_path": str(cases_path),
                },
                gate_outcomes=[
                    {
                        "name": f"{suite_id}_eval",
                        "passed": len(failures) == 0,
                        "detail": f"passed={passes}/{len(cases)}, failed={len(failures)}",
                    }
                ],
                summary=report_payload["summary"],
                model_metadata={"evaluation_mode": "deterministic"},
                metadata={
                    "base_url": args.base_url,
                    "strict": bool(args.strict),
                    "suite_id": suite_id,
                },
            )
            trace_path = append_eval_trace(
                trace_payload=trace_payload,
                trace_jsonl_path=Path(trace_jsonl),
            )
            print(f"Trace written: {trace_path}")

    if args.strict and failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
