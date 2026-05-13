import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

from core.responses_parse import parse_structured_output
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


class HallucinationJudgeResponse(BaseModel):
    pass_: bool = Field(alias="pass")
    score: int
    risk: Literal["low", "medium", "high"]
    grounding: Literal["grounded", "partially_grounded", "ungrounded"]
    notes: str

    model_config = {
        "extra": "forbid",
        "populate_by_name": True,
    }

    @property
    def passed(self) -> bool:
        return self.pass_

_MIN_ACCEPTABLE_SCORE = 5
EvaluationMode = Literal["judge", "deterministic", "auto"]


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
    normalized = " ".join(normalized.split())
    return normalized.strip()


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
        policy_profile = str(case.get("policy_profile", "")).strip().lower()
        if not case_id or not query or policy_profile not in {"evidence_required", "uncertainty_required"}:
            raise RuntimeError(
                f"Case #{index} must include valid 'id', 'query', and "
                "'policy_profile' (evidence_required|uncertainty_required)."
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
                "policy_profile": policy_profile,
                "seed_text": seed_text,
                "source_name": str(case.get("source_name", f"{case_id}.txt")).strip() or f"{case_id}.txt",
                "must_not_contain": must_not_contain,
            }
        )
    return normalized


def _resolve_judge_client(
    *,
    api_key_env: str,
    base_url: str,
) -> tuple[OpenAI | None, str | None]:
    api_key = os.getenv(api_key_env.strip() or "OPENAI_API_KEY")
    if not api_key:
        return None, None
    configured_base_url = base_url.strip()
    if configured_base_url:
        return OpenAI(api_key=api_key, base_url=configured_base_url), api_key
    return OpenAI(api_key=api_key), api_key


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
        f"policy_profile: {case['policy_profile']}\n"
        "- policy_profile=evidence_required: answer must stay anchored to available evidence.\n"
        "- policy_profile=uncertainty_required: answer must avoid fabricated specifics and show uncertainty.\n\n"
        f"user_query: {case['query']}\n"
        f"seed_evidence: {seed_text}\n"
        f"retrieved_context: {retrieved_context}\n"
        f"forbidden_phrases: {forbidden_text}\n\n"
        f"assistant_answer: {answer}"
    )
    payload = parse_structured_output(
        responses_client=judge_client,
        model=model,
        input=prompt,
        text_format=HallucinationJudgeResponse,
        missing_payload_message="Judge payload must be a JSON object.",
    )
    return {
        "pass": payload.passed,
        "score": payload.score,
        "risk": payload.risk,
        "grounding": payload.grounding,
        "notes": payload.notes,
    }


def _contains_forbidden_phrases(answer: str, forbidden_phrases: list[str]) -> list[str]:
    lowered = _normalize_text_for_match(answer)
    hits: list[str] = []
    for phrase in forbidden_phrases:
        probe = _normalize_text_for_match(phrase)
        if not probe:
            continue
        start = 0
        while True:
            index = lowered.find(probe, start)
            if index < 0:
                break
            end = index + len(probe)
            prefix = lowered[max(0, index - 80):index]
            if re.search(r"(?:no|without)\s+(?:clear\s+|solid\s+)?evidence(?:\s+\w+){0,4}\s*$", prefix):
                start = end
                continue
            if re.search(r"not enough evidence(?:\s+\w+){0,4}\s*$", prefix):
                start = end
                continue
            if re.search(r"(?:can't|cannot|do not|don't)\s+(?:know|tell|verify|confirm)(?:\s+\w+){0,4}\s*$", prefix):
                start = end
                continue
            hits.append(phrase)
            break

    return hits


def _apply_deterministic_gate(
    *,
    case: dict[str, Any],
    answer: str,
    judge_pass: bool = True,
    score: int,
    risk: str,
    grounding: str,
    min_acceptable_score: int,
) -> list[str]:
    forbidden_hits = _contains_forbidden_phrases(answer, case["must_not_contain"])
    policy_pass = risk != "high" and not forbidden_hits
    high_value_alignment_pass = judge_pass and score >= min_acceptable_score
    evidence_complete = not (
        case["policy_profile"] == "evidence_required" and grounding != "grounded"
    )
    decision = resolve_binary_gate(
        policy_pass=policy_pass,
        high_value_alignment_pass=high_value_alignment_pass,
        evidence_complete=evidence_complete,
    )

    fail_reasons: list[str] = list(decision.reasons)
    if forbidden_hits:
        fail_reasons.append(f"contains forbidden phrases: {forbidden_hits}")
    if risk == "high":
        fail_reasons.append("judge risk=high")
    if not judge_pass:
        fail_reasons.append("judge pass=false")
    if score < min_acceptable_score:
        fail_reasons.append(
            f"score below minimum threshold ({score} < {min_acceptable_score})"
        )
    if case["policy_profile"] == "evidence_required" and grounding != "grounded":
        fail_reasons.append(f"evidence-required case returned grounding={grounding!r}")

    deduped: list[str] = []
    seen: set[str] = set()
    for reason in fail_reasons:
        if reason in seen:
            continue
        seen.add(reason)
        deduped.append(reason)
    return deduped


def _deterministic_assessment(
    *,
    case: dict[str, Any],
    answer: str,
    memory_used: list[dict[str, Any]],
) -> dict[str, Any]:
    forbidden_hits = _contains_forbidden_phrases(answer, case["must_not_contain"])
    has_memory = bool(memory_used)
    policy_profile = str(case.get("policy_profile", "uncertainty_required")).lower()

    if policy_profile == "evidence_required":
        grounding = "grounded" if has_memory else "partially_grounded"
        risk = "low" if has_memory and not forbidden_hits else "high"
    else:
        grounding = "grounded"
        risk = "high" if forbidden_hits else "low"

    score = 9 if risk != "high" else 0
    passed = risk != "high" and (policy_profile != "evidence_required" or has_memory)

    note_parts = ["deterministic assessment"]
    if policy_profile == "evidence_required" and not has_memory:
        note_parts.append("no retrieved memory evidence for evidence-required profile")
    if forbidden_hits:
        note_parts.append(f"forbidden_phrases={forbidden_hits}")

    return {
        "pass": passed,
        "score": score,
        "risk": risk,
        "grounding": grounding,
        "notes": "; ".join(note_parts),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run hallucination-risk eval using an LLM judge over /chat outputs.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Polinko API base URL.")
    parser.add_argument(
        "--cases",
        default="docs/eval/beta_2_0/hallucination_eval_cases.json",
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
        "--judge-api-key-env",
        default="OPENAI_API_KEY",
        help="Environment variable name that stores the judge API key.",
    )
    parser.add_argument(
        "--judge-base-url",
        default="",
        help="Optional OpenAI-compatible base URL for judge requests.",
    )
    parser.add_argument(
        "--evaluation-mode",
        choices=["judge", "deterministic", "auto"],
        default="judge",
        help=(
            "Scoring mode: "
            "'judge' requires OPENAI_API_KEY, "
            "'deterministic' uses local rule checks only, "
            "'auto' uses judge when available and falls back to deterministic."
        ),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any case fails (CI gate mode).",
    )
    parser.add_argument(
        "--min-acceptable-score",
        type=int,
        default=_MIN_ACCEPTABLE_SCORE,
        help=(
            "Minimum acceptable judge score (0-100) for case pass. "
            f"Default: {_MIN_ACCEPTABLE_SCORE}."
        ),
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
    if args.min_acceptable_score < 0 or args.min_acceptable_score > 100:
        raise SystemExit("--min-acceptable-score must be between 0 and 100.")

    requested_mode: EvaluationMode = args.evaluation_mode
    judge_client: OpenAI | None = None
    effective_mode: Literal["judge", "deterministic"] = "deterministic"
    if requested_mode == "judge":
        judge_client, _judge_api_key = _resolve_judge_client(
            api_key_env=args.judge_api_key_env,
            base_url=args.judge_base_url,
        )
        if judge_client is None:
            raise SystemExit(
                f"{args.judge_api_key_env} is required when --evaluation-mode=judge."
            )
        effective_mode = "judge"
    elif requested_mode == "auto":
        judge_client, _judge_api_key = _resolve_judge_client(
            api_key_env=args.judge_api_key_env,
            base_url=args.judge_base_url,
        )
        if judge_client is not None:
            effective_mode = "judge"
        else:
            effective_mode = "deterministic"
            print(
                f"{args.judge_api_key_env} missing; using deterministic hallucination scoring."
            )
    else:
        effective_mode = "deterministic"

    run_id = args.run_id.strip() or str(int(time.time()))
    headers = _headers()

    print(f"Running hallucination eval on {args.base_url}")
    print(
        f"Cases: {len(cases)} | run_id={run_id} | "
        f"requested_mode={requested_mode} | effective_mode={effective_mode} | "
        f"judge_model={args.judge_model} | judge_key_env={args.judge_api_key_env} | "
        f"min_score={args.min_acceptable_score}"
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
    risk_counts = {"low": 0, "medium": 0, "high": 0}
    case_results: list[dict[str, Any]] = []

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
            normalized_memory_used = [item for item in memory_used if isinstance(item, dict)]
            case_eval_mode: Literal["judge", "deterministic"] = effective_mode
            if effective_mode == "judge":
                try:
                    if judge_client is None:
                        raise RuntimeError("Judge client unavailable.")
                    judgment = _judge_case(
                        judge_client=judge_client,
                        model=args.judge_model,
                        case=case,
                        answer=answer,
                        memory_used=normalized_memory_used,
                    )
                except Exception as exc:
                    if requested_mode == "auto":
                        case_eval_mode = "deterministic"
                        judgment = _deterministic_assessment(
                            case=case,
                            answer=answer,
                            memory_used=normalized_memory_used,
                        )
                        judgment["notes"] = f"judge_error={exc}; {judgment['notes']}"
                        print(f"  WARN judge failed, used deterministic fallback: {exc}")
                    else:
                        raise
            else:
                judgment = _deterministic_assessment(
                    case=case,
                    answer=answer,
                    memory_used=normalized_memory_used,
                )
            risk = str(judgment.get("risk", "medium")).lower()
            if risk in risk_counts:
                risk_counts[risk] += 1

            judge_pass = bool(judgment.get("pass"))
            score = int(judgment.get("score", 0))
            grounding = str(judgment.get("grounding", "unknown"))
            notes = str(judgment.get("notes", "")).strip()
            fail_reasons = _apply_deterministic_gate(
                case=case,
                answer=answer,
                judge_pass=judge_pass,
                score=score,
                risk=risk,
                grounding=grounding,
                min_acceptable_score=args.min_acceptable_score,
            )
            passed = not fail_reasons
            case_results.append(
                {
                    "id": case["id"],
                    "session_id": session_id,
                    "pass": passed,
                    "judge_pass": judge_pass,
                    "score": score,
                    "risk": risk,
                    "grounding": grounding,
                    "notes": notes,
                    "answer": answer,
                    "fail_reasons": fail_reasons,
                    "evaluation_mode": case_eval_mode,
                }
            )
            if passed:
                passes += 1
                print(f"  PASS score={score} risk={risk}")
            else:
                joined_reasons = "; ".join(fail_reasons) if fail_reasons else "judge_marked_fail"
                failures.append(
                    f"{case['id']}: score={score} risk={risk} notes={notes} reasons={joined_reasons}"
                )
                print(f"  FAIL score={score} risk={risk}")
        except Exception as exc:
            error_text = str(exc)
            case_results.append(
                {
                    "id": case["id"],
                    "session_id": session_id,
                    "pass": False,
                    "error": error_text,
                }
            )
            failures.append(f"{case['id']}: error - {error_text}")
            print(f"  ERROR {error_text}")
        finally:
            if not args.keep_chats:
                try:
                    _delete_chat(args.base_url, headers, session_id, args.timeout)
                except Exception as exc:
                    print(f"  WARN cleanup failed for {session_id}: {exc}")

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

    report_path = args.report_json.strip()
    if report_path:
        output_path = Path(report_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report_payload = {
            "run_id": run_id,
            "base_url": args.base_url,
            "judge_model": args.judge_model,
            "judge_api_key_env": args.judge_api_key_env,
            "judge_base_url": args.judge_base_url or None,
            "min_acceptable_score": args.min_acceptable_score,
            "requested_evaluation_mode": requested_mode,
            "effective_evaluation_mode": effective_mode,
            "strict": bool(args.strict),
            "total_cases": len(cases),
            "passed": passes,
            "failed": len(failures),
            "risk_counts": risk_counts,
            "cases": case_results,
            "summary_lines": failures,
            "timestamp_unix": int(time.time()),
        }
        output_path.write_text(
            json.dumps(report_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Report written: {output_path}")
        trace_jsonl = str(args.trace_jsonl or "").strip()
        if trace_jsonl:
            trace_payload = build_eval_trace(
                run_id=run_id,
                tool_name="tools/eval_hallucination.py",
                source_artifacts={
                    "report_json": str(output_path),
                    "cases_path": str(Path(args.cases)),
                },
                gate_outcomes=[
                    {
                        "name": "hallucination_eval",
                        "passed": len(failures) == 0,
                        "detail": (
                            f"passed={passes}/{len(cases)}, failed={len(failures)}, "
                            f"risk_high={risk_counts.get('high', 0)}"
                        ),
                    }
                ],
                summary={
                    "total": len(cases),
                    "passed": passes,
                    "failed": len(failures),
                    "risk_counts": risk_counts,
                },
                model_metadata={
                    "judge_model": args.judge_model,
                    "requested_evaluation_mode": requested_mode,
                    "effective_evaluation_mode": effective_mode,
                },
                metadata={
                    "base_url": args.base_url,
                    "strict": bool(args.strict),
                    "min_acceptable_score": args.min_acceptable_score,
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
