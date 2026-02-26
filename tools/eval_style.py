import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from openai import OpenAI


_JUDGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["pass", "score", "fit", "notes"],
    "properties": {
        "pass": {"type": "boolean"},
        "score": {"type": "integer", "minimum": 0, "maximum": 100},
        "fit": {"type": "string", "enum": ["on_style", "mixed", "off_style"]},
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
    raise RuntimeError("Judge model returned no parseable text output.")


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
    response = judge_client.responses.create(
        model=model,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "style_judge_v1",
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
        description="Run style/tone eval over /chat outputs with an LLM judge.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Polinko API base URL.")
    parser.add_argument(
        "--cases",
        default="docs/style_eval_cases.json",
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
    return parser


def main() -> int:
    load_dotenv(dotenv_path=".env")
    args = build_parser().parse_args()
    cases_path = Path(args.cases)
    if not cases_path.exists():
        raise SystemExit(f"Cases file not found: {cases_path}")
    cases, global_forbidden_phrases = _load_cases(cases_path)

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise SystemExit("OPENAI_API_KEY is required for style eval.")
    judge_client = OpenAI(api_key=openai_api_key)

    run_id = args.run_id.strip() or str(int(time.time()))
    api_key = os.getenv("POLINKO_SERVER_API_KEY")
    headers = _headers(api_key)

    print(f"Running style eval on {args.base_url}")
    print(f"Cases: {len(cases)} | run_id={run_id}")
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
        session_id = f"{args.session_prefix}-{run_id}-{index:02d}"
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
            passed = bool(result.get("pass", False))
            judge_pass = passed
            case_failed = False
            notes = str(result.get("notes", "")).strip()

            max_words = case["max_words"]
            if isinstance(max_words, int) and wc > max_words:
                case_failed = True
                if notes:
                    notes = f"{notes} | Word count {wc} exceeds limit {max_words}."
                else:
                    notes = f"Word count {wc} exceeds limit {max_words}."

            if not passed:
                case_failed = True

            forbidden_hits = [
                phrase for phrase in case.get("forbidden_phrases", []) if phrase in answer_lower
            ]
            if forbidden_hits:
                case_failed = True
                forbidden_text = ", ".join(forbidden_hits)
                if notes:
                    notes = f"{notes} | Contains forbidden phrase(s): {forbidden_text}."
                else:
                    notes = f"Contains forbidden phrase(s): {forbidden_text}."

            status_text = "PASS" if not case_failed else "FAIL"
            print(f"[{status_text}] {case['id']} score={score} fit={fit} words={wc}")
            if notes:
                print(f"  notes: {notes}")

            if case_failed:
                failures += 1
        except Exception as exc:
            failures += 1
            status_text = "ERROR"
            error_text = str(exc)
            print(f"[ERROR] {case['id']}: {exc}")
        finally:
            max_words = case["max_words"]
            case_results.append(
                {
                    "id": case["id"],
                    "session_id": session_id,
                    "status": status_text,
                    "judge_pass": judge_pass,
                    "score": score,
                    "fit": fit,
                    "notes": notes,
                    "error": error_text,
                    "word_count": wc,
                    "max_words": max_words,
                    "forbidden_hits": forbidden_hits,
                    "query": case["query"],
                    "answer": answer,
                }
            )

    if not args.keep_chats:
        for session_id in session_ids:
            try:
                _delete_chat(args.base_url, headers, session_id, args.timeout)
            except Exception:
                pass

    passed = len(cases) - failures
    print("\nSummary")
    print(f"  Passed: {passed}/{len(cases)}")
    print(f"  Failed: {failures}")

    report_json = str(args.report_json or "").strip()
    if report_json:
        report_path = Path(report_json)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_payload = {
            "run_id": run_id,
            "base_url": args.base_url,
            "cases_path": str(cases_path),
            "judge_model": args.judge_model,
            "strict": bool(args.strict),
            "global_forbidden_phrases": global_forbidden_phrases,
            "summary": {
                "total": len(cases),
                "passed": passed,
                "failed": failures,
            },
            "cases": case_results,
            "generated_at": int(time.time()),
        }
        report_path.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  Report: {report_path}")

    if failures > 0 and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
