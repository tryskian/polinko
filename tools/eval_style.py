import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Literal

import requests
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

from tools.eval_gate import resolve_binary_gate
from tools.eval_trace_artifacts import DEFAULT_TRACE_JSONL
from tools.eval_trace_artifacts import append_eval_trace
from tools.eval_trace_artifacts import build_eval_trace


class StyleJudgeResponse(BaseModel):
    pass_: bool = Field(alias="pass")
    score: int
    fit: Literal["on_style", "mixed", "off_style"]
    notes: str

    model_config = {
        "extra": "forbid",
        "populate_by_name": True,
    }

    @property
    def passed(self) -> bool:
        return self.pass_


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


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _normalize_phrase_list(raw: Any, *, field_name: str, case_id: str | None = None) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        where = f"case '{case_id}'" if case_id else "root payload"
        raise RuntimeError(f"{where} field '{field_name}' must be a list of strings.")
    phrases: list[str] = []
    for value in raw:
        phrase = str(value).strip()
        if not phrase:
            continue
        phrases.append(phrase.lower())
    return phrases


def _load_cases(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Cases file must be a JSON object.")
    global_forbidden_phrases = _normalize_phrase_list(
        payload.get("global_forbidden_phrases"),
        field_name="global_forbidden_phrases",
    )
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise RuntimeError("Cases file must include a non-empty 'cases' list.")

    normalized: list[dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            raise RuntimeError(f"Case #{index} must be an object.")
        case_id = str(case.get("id", f"style-{index}")).strip()
        query = str(case.get("query", "")).strip()
        style_notes = str(case.get("style_notes", "")).strip()
        max_words_raw = case.get("max_words")
        case_forbidden_phrases = _normalize_phrase_list(
            case.get("forbidden_phrases"),
            field_name="forbidden_phrases",
            case_id=case_id,
        )
        max_words: int | None = None
        if max_words_raw is not None:
            try:
                parsed = int(max_words_raw)
            except (TypeError, ValueError) as exc:
                raise RuntimeError(f"Case '{case_id}' has invalid max_words.") from exc
            if parsed <= 0:
                raise RuntimeError(f"Case '{case_id}' max_words must be > 0.")
            max_words = parsed
        if not case_id or not query:
            raise RuntimeError(f"Case #{index} must include non-empty 'id' and 'query'.")
        normalized.append(
            {
                "id": case_id,
                "query": query,
                "style_notes": style_notes,
                "max_words": max_words,
                "forbidden_phrases": sorted(set(global_forbidden_phrases + case_forbidden_phrases)),
            }
        )
    return normalized, global_forbidden_phrases


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


def _judge_case(
    *,
    judge_client: OpenAI,
    model: str,
    case: dict[str, Any],
    answer: str,
    word_count: int,
) -> dict[str, Any]:
    max_words = case["max_words"]
    max_words_text = str(max_words) if isinstance(max_words, int) else "(none)"
    style_notes = case["style_notes"] or "(none)"

    prompt = (
        "Evaluate whether the assistant response matches this style profile.\n"
        "Return strict JSON only via schema.\n\n"
        "Style profile:\n"
        "- direct, concise, concrete, and context-aware\n"
        "- avoid generic assistant sign-offs or performative closings\n"
        "- avoid motivational fluff and unnecessary meta-explanations\n"
        "- maintain tone continuity with user phrasing\n"
        "- be helpful without becoming verbose\n\n"
        f"case_style_notes: {style_notes}\n"
        f"max_words: {max_words_text}\n"
        f"answer_word_count: {word_count}\n"
        f"user_query: {case['query']}\n"
        f"assistant_answer: {answer}"
    )
    response = judge_client.responses.parse(
        model=model,
        input=prompt,
        text_format=StyleJudgeResponse,
    )
    payload = response.output_parsed
    if payload is None:
        raise RuntimeError("Judge payload must be a JSON object.")
    return {
        "pass": payload.passed,
        "score": payload.score,
        "fit": payload.fit,
        "notes": payload.notes,
    }


def _resolve_case_status(*, attempt_statuses: list[str], pass_attempts: int, min_pass_attempts: int) -> str:
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


def _case_confidence_bucket(
    *,
    final_status: str,
    attempt_statuses: list[str],
    pass_attempts: int,
    attempts_used: int,
) -> str:
    if final_status != "PASS":
        return "low"
    if attempts_used <= 0:
        return "low"
    if pass_attempts == attempts_used and all(status == "PASS" for status in attempt_statuses):
        return "high"
    return "medium"


def _build_confidence_counts(case_results: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"high": 0, "medium": 0, "low": 0}
    for case in case_results:
        confidence = str(case.get("confidence", "low")).lower()
        if confidence in counts:
            counts[confidence] += 1
    return counts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run style/tone eval over /chat outputs with an LLM judge.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Polinko API base URL.")
    parser.add_argument(
        "--cases",
        default="docs/eval/cases/style_eval_cases.json",
        help="Path to style eval cases JSON file.",
    )
    parser.add_argument(
        "--session-prefix",
        default="style-eval",
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
        help="OpenAI model for style pass/fail scoring.",
    )
    parser.add_argument(
        "--case-attempts",
        type=int,
        default=1,
        help="Attempts per style case (for retry-majority hardening).",
    )
    parser.add_argument(
        "--min-pass-attempts",
        type=int,
        default=1,
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
    cases_path = Path(args.cases)
    if not cases_path.exists():
        raise SystemExit(f"Cases file not found: {cases_path}")
    cases, global_forbidden_phrases = _load_cases(cases_path)

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise SystemExit("OPENAI_API_KEY is required for style eval.")
    judge_client = OpenAI(api_key=openai_api_key)

    run_id = args.run_id.strip() or str(int(time.time()))
    headers = _headers()

    print(f"Running style eval on {args.base_url}")
    print(f"Cases: {len(cases)} | run_id={run_id}")
    print(
        "Attempts per case: "
        f"{args.case_attempts} | min passes required: {args.min_pass_attempts}"
    )
    if global_forbidden_phrases:
        print(f"Global forbidden phrases: {', '.join(global_forbidden_phrases)}")

    try:
        _preflight(args.base_url, headers, args.timeout)
    except Exception as exc:
        print(f"Preflight failed: {exc}")
        return 2

    failures = 0
    session_ids: list[str] = []
    case_results: list[dict[str, Any]] = []

    for index, case in enumerate(cases, start=1):
        session_base = f"{args.session_prefix}-{run_id}-{index:02d}"
        attempt_results: list[dict[str, Any]] = []
        attempt_statuses: list[str] = []
        pass_attempts = 0

        for attempt in range(1, args.case_attempts + 1):
            session_id = (
                session_base if args.case_attempts == 1 else f"{session_base}-a{attempt:02d}"
            )
            session_ids.append(session_id)
            answer = ""
            wc = 0
            score: Any = None
            fit: Any = None
            judge_pass: bool | None = None
            notes = ""
            forbidden_hits: list[str] = []
            error_text: str | None = None
            status_text = "PASS"
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
                answer_lower = answer.lower()
                wc = _word_count(answer)
                result = _judge_case(
                    judge_client=judge_client,
                    model=args.judge_model,
                    case=case,
                    answer=answer,
                    word_count=wc,
                )
                score = result.get("score")
                fit = result.get("fit")
                case_pass = bool(result.get("pass", False))
                judge_pass = case_pass
                notes = str(result.get("notes", "")).strip()

                max_words = case["max_words"]
                forbidden_hits = [
                    phrase for phrase in case.get("forbidden_phrases", []) if phrase in answer_lower
                ]
                word_count_ok = not (isinstance(max_words, int) and wc > max_words)
                decision = resolve_binary_gate(
                    policy_pass=not forbidden_hits,
                    high_value_alignment_pass=case_pass,
                    evidence_complete=word_count_ok,
                )
                case_failed = not decision.passed

                if isinstance(max_words, int) and wc > max_words:
                    if notes:
                        notes = f"{notes} | Word count {wc} exceeds limit {max_words}."
                    else:
                        notes = f"Word count {wc} exceeds limit {max_words}."
                if forbidden_hits:
                    forbidden_text = ", ".join(forbidden_hits)
                    if notes:
                        notes = f"{notes} | Contains forbidden phrase(s): {forbidden_text}."
                    else:
                        notes = f"Contains forbidden phrase(s): {forbidden_text}."
                if decision.reasons:
                    reasons_text = "; ".join(decision.reasons)
                    if notes:
                        notes = f"{notes} | Gate: {reasons_text}."
                    else:
                        notes = f"Gate: {reasons_text}."

                status_text = "PASS" if not case_failed else "FAIL"
                if status_text == "PASS":
                    pass_attempts += 1
                print(
                    f"[{status_text}] {case['id']} attempt={attempt}/{args.case_attempts} "
                    f"score={score} fit={fit} words={wc}"
                )
                if notes:
                    print(f"  notes: {notes}")
            except Exception as exc:
                status_text = "ERROR"
                error_text = str(exc)
                print(f"[ERROR] {case['id']} attempt={attempt}/{args.case_attempts}: {exc}")
            finally:
                attempt_statuses.append(status_text)
                attempt_results.append(
                    {
                        "session_id": session_id,
                        "status": status_text,
                        "judge_pass": judge_pass,
                        "score": score,
                        "fit": fit,
                        "notes": notes,
                        "error": error_text,
                        "word_count": wc,
                        "forbidden_hits": forbidden_hits,
                        "answer": answer,
                    }
                )

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
        if final_status != "PASS":
            failures += 1
        final_attempt = next(
            (row for row in attempt_results if row["status"] == "PASS"),
            attempt_results[-1],
        )
        attempts_used = len(attempt_results)
        confidence = _case_confidence_bucket(
            final_status=final_status,
            attempt_statuses=attempt_statuses,
            pass_attempts=pass_attempts,
            attempts_used=attempts_used,
        )
        pass_rate = round((pass_attempts / attempts_used) if attempts_used else 0.0, 4)
        max_words = case["max_words"]
        case_results.append(
            {
                "id": case["id"],
                "session_id": str(final_attempt["session_id"]),
                "status": final_status,
                "judge_pass": final_attempt["judge_pass"],
                "score": final_attempt["score"],
                "fit": final_attempt["fit"],
                "notes": final_attempt["notes"],
                "error": final_attempt["error"],
                "word_count": final_attempt["word_count"],
                "max_words": max_words,
                "forbidden_hits": list(final_attempt["forbidden_hits"]),
                "query": case["query"],
                "answer": final_attempt["answer"],
                "attempts_used": attempts_used,
                "attempts_required": args.min_pass_attempts,
                "pass_attempts": pass_attempts,
                "pass_rate": pass_rate,
                "confidence": confidence,
                "attempts": attempt_results,
            }
        )

    if not args.keep_chats:
        for session_id in session_ids:
            try:
                _delete_chat(args.base_url, headers, session_id, args.timeout)
            except Exception as exc:
                print(f"  WARN cleanup failed for {session_id}: {exc}")

    passed = len(cases) - failures
    confidence_counts = _build_confidence_counts(case_results)
    print("\nSummary")
    print(f"  Passed: {passed}/{len(cases)}")
    print(f"  Failed: {failures}")
    print(
        "  Confidence: "
        f"high={confidence_counts['high']} "
        f"medium={confidence_counts['medium']} "
        f"low={confidence_counts['low']}"
    )

    report_json = str(args.report_json or "").strip()
    if report_json:
        report_path = Path(report_json)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_payload = {
            "run_id": run_id,
            "base_url": args.base_url,
            "cases_path": str(cases_path),
            "judge_model": args.judge_model,
            "case_attempts": args.case_attempts,
            "min_pass_attempts": args.min_pass_attempts,
            "strict": bool(args.strict),
            "global_forbidden_phrases": global_forbidden_phrases,
            "summary": {
                "total": len(cases),
                "passed": passed,
                "failed": failures,
                "confidence": confidence_counts,
            },
            "cases": case_results,
            "generated_at": int(time.time()),
        }
        report_path.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  Report: {report_path}")
        trace_jsonl = str(args.trace_jsonl or "").strip()
        if trace_jsonl:
            trace_payload = build_eval_trace(
                run_id=run_id,
                tool_name="tools/eval_style.py",
                source_artifacts={
                    "report_json": str(report_path),
                    "cases_path": str(cases_path),
                },
                gate_outcomes=[
                    {
                        "name": "style_eval",
                        "passed": failures == 0,
                        "detail": f"passed={passed}/{len(cases)}, failed={failures}",
                    }
                ],
                summary=report_payload["summary"],
                model_metadata={"judge_model": args.judge_model},
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
