from __future__ import annotations

import argparse
import json
import os
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


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


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _normalize_for_compare(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _last_visible_char(text: str) -> str | None:
    stripped = text.rstrip()
    if not stripped:
        return None
    return stripped[-1]


def _max_consecutive_repeat(values: list[str]) -> int:
    if not values:
        return 0
    max_run = 1
    current = 1
    for idx in range(1, len(values)):
        if values[idx] == values[idx - 1]:
            current += 1
            max_run = max(max_run, current)
        else:
            current = 1
    return max_run


def _dominance_ratio(values: list[str]) -> float:
    if not values:
        return 0.0
    counts = Counter(values)
    return max(counts.values()) / len(values)


def _normalize_str_list(raw: Any, *, field_name: str, case_id: str | None = None) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        where = f"case '{case_id}'" if case_id else "root payload"
        raise RuntimeError(f"{where} field '{field_name}' must be a list of strings.")
    out: list[str] = []
    for value in raw:
        item = str(value).strip()
        if item:
            out.append(item)
    return out


def _require_float(
    raw: Any,
    *,
    field_name: str,
    case_id: str,
    default: float,
    min_value: float,
    max_value: float,
) -> float:
    if raw is None:
        return default
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Case '{case_id}' has invalid {field_name}.") from exc
    if value < min_value or value > max_value:
        raise RuntimeError(
            f"Case '{case_id}' {field_name} must be in [{min_value}, {max_value}]."
        )
    return value


def _require_int(
    raw: Any,
    *,
    field_name: str,
    case_id: str,
    default: int,
    min_value: int,
) -> int:
    if raw is None:
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Case '{case_id}' has invalid {field_name}.") from exc
    if value < min_value:
        raise RuntimeError(f"Case '{case_id}' {field_name} must be >= {min_value}.")
    return value


def _load_cases(path: Path) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Cases file must be a JSON object.")

    global_forbidden = [item.lower() for item in _normalize_str_list(payload.get("global_forbidden_phrases"), field_name="global_forbidden_phrases")]
    global_motif_chars = _normalize_str_list(payload.get("global_motif_chars"), field_name="global_motif_chars")

    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise RuntimeError("Cases file must include a non-empty 'cases' list.")

    normalized_cases: list[dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            raise RuntimeError(f"Case #{index} must be an object.")
        case_id = str(case.get("id", f"pattern-{index}")).strip()
        turns = _normalize_str_list(case.get("turns"), field_name="turns", case_id=case_id)
        if not case_id or not turns:
            raise RuntimeError(f"Case #{index} must include non-empty 'id' and 'turns'.")

        case_forbidden = [
            item.lower()
            for item in _normalize_str_list(
                case.get("forbidden_phrases"),
                field_name="forbidden_phrases",
                case_id=case_id,
            )
        ]
        case_motif_chars = _normalize_str_list(
            case.get("motif_chars"),
            field_name="motif_chars",
            case_id=case_id,
        )

        normalized_cases.append(
            {
                "id": case_id,
                "description": str(case.get("description", "")).strip(),
                "turns": turns,
                "forbidden_phrases": sorted(set(global_forbidden + case_forbidden)),
                "motif_chars": sorted(set(global_motif_chars + case_motif_chars)),
                "max_avg_words": _require_float(
                    case.get("max_avg_words"),
                    field_name="max_avg_words",
                    case_id=case_id,
                    default=12.0,
                    min_value=0.0,
                    max_value=500.0,
                ),
                "max_words_per_turn": _require_int(
                    case.get("max_words_per_turn"),
                    field_name="max_words_per_turn",
                    case_id=case_id,
                    default=120,
                    min_value=1,
                ),
                "min_unique_ratio": _require_float(
                    case.get("min_unique_ratio"),
                    field_name="min_unique_ratio",
                    case_id=case_id,
                    default=0.6,
                    min_value=0.0,
                    max_value=1.0,
                ),
                "max_consecutive_repeat": _require_int(
                    case.get("max_consecutive_repeat"),
                    field_name="max_consecutive_repeat",
                    case_id=case_id,
                    default=2,
                    min_value=1,
                ),
                "max_filler_hits": _require_int(
                    case.get("max_filler_hits"),
                    field_name="max_filler_hits",
                    case_id=case_id,
                    default=0,
                    min_value=0,
                ),
                "max_tail_motif_dominance": _require_float(
                    case.get("max_tail_motif_dominance"),
                    field_name="max_tail_motif_dominance",
                    case_id=case_id,
                    default=1.0,
                    min_value=0.0,
                    max_value=1.0,
                ),
            }
        )
    return normalized_cases, global_forbidden, global_motif_chars


def _count_filler_hits(text: str, forbidden_phrases: list[str]) -> list[str]:
    lowered = text.lower()
    return [phrase for phrase in forbidden_phrases if phrase in lowered]


def _assess_case(
    *,
    case: dict[str, Any],
    responses: list[str],
    word_counts: list[int],
    filler_hits_by_turn: list[list[str]],
    tail_chars: list[str | None],
) -> dict[str, Any]:
    total_turns = len(responses)
    normalized_responses = [_normalize_for_compare(item) for item in responses if item.strip()]
    unique_ratio = (
        len(set(normalized_responses)) / total_turns
        if total_turns > 0
        else 0.0
    )
    avg_words = (sum(word_counts) / len(word_counts)) if word_counts else 0.0
    max_words = max(word_counts) if word_counts else 0
    max_repeat = _max_consecutive_repeat(normalized_responses) if normalized_responses else 0
    total_filler_hits = sum(len(hits) for hits in filler_hits_by_turn)

    observed_tail_chars = [char for char in tail_chars if char is not None]
    motif_chars = set(case.get("motif_chars", []))
    motif_tails = [char for char in observed_tail_chars if char in motif_chars]
    # One motif-ending instance is not lock-in; require at least two occurrences.
    tail_motif_dominance = _dominance_ratio(motif_tails) if len(motif_tails) >= 2 else 0.0
    tail_char_dominance = _dominance_ratio(observed_tail_chars)

    reasons: list[str] = []
    if avg_words > float(case["max_avg_words"]):
        reasons.append(f"avg_words {avg_words:.2f} exceeds {case['max_avg_words']:.2f}")
    if max_words > int(case["max_words_per_turn"]):
        reasons.append(f"max_words_per_turn {max_words} exceeds {case['max_words_per_turn']}")
    if unique_ratio < float(case["min_unique_ratio"]):
        reasons.append(f"unique_ratio {unique_ratio:.2f} below {case['min_unique_ratio']:.2f}")
    if max_repeat > int(case["max_consecutive_repeat"]):
        reasons.append(
            f"max_consecutive_repeat {max_repeat} exceeds {case['max_consecutive_repeat']}"
        )
    if total_filler_hits > int(case["max_filler_hits"]):
        reasons.append(f"filler_hits {total_filler_hits} exceeds {case['max_filler_hits']}")
    if tail_motif_dominance > float(case["max_tail_motif_dominance"]):
        reasons.append(
            "tail_motif_dominance "
            f"{tail_motif_dominance:.2f} exceeds {case['max_tail_motif_dominance']:.2f}"
        )

    return {
        "passed": len(reasons) == 0,
        "reasons": reasons,
        "metrics": {
            "turns": total_turns,
            "avg_words": avg_words,
            "max_words_per_turn": max_words,
            "unique_ratio": unique_ratio,
            "max_consecutive_repeat": max_repeat,
            "filler_hits": total_filler_hits,
            "tail_char_dominance": tail_char_dominance,
            "tail_motif_dominance": tail_motif_dominance,
            "motif_tail_count": len(motif_tails),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run scripted low-context style-pattern eval and measure variation/drop-off."
        ),
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Polinko API base URL.")
    parser.add_argument(
        "--cases",
        default="docs/style_pattern_eval_cases.json",
        help="Path to style-pattern eval cases JSON file.",
    )
    parser.add_argument(
        "--session-prefix",
        default="style-pattern-eval",
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
        "--strict",
        action="store_true",
        help="Exit non-zero if any case fails.",
    )
    parser.add_argument(
        "--report-json",
        default="",
        help="Optional path to write JSON report artifact.",
    )
    return parser


def main() -> int:
    load_dotenv(dotenv_path=".env")
    args = build_parser().parse_args()
    cases_path = Path(args.cases)
    if not cases_path.exists():
        raise SystemExit(f"Cases file not found: {cases_path}")
    cases, global_forbidden, global_motif_chars = _load_cases(cases_path)

    run_id = args.run_id.strip() or str(int(time.time()))
    api_key = os.getenv("POLINKO_SERVER_API_KEY")
    headers = _headers(api_key)

    print(f"Running style-pattern eval on {args.base_url}")
    print(f"Cases: {len(cases)} | run_id={run_id}")
    if global_forbidden:
        print(f"Global forbidden phrases: {', '.join(global_forbidden)}")
    if global_motif_chars:
        print(f"Global motif chars: {', '.join(global_motif_chars)}")

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
        status_text = "PASS"
        error_text: str | None = None
        print(f"\nCase: {case['id']} ({len(case['turns'])} turns)")
        if case["description"]:
            print(f"  {case['description']}")

        prompts: list[str] = []
        responses: list[str] = []
        word_counts: list[int] = []
        filler_hits_by_turn: list[list[str]] = []
        tail_chars: list[str | None] = []
        turn_rows: list[dict[str, Any]] = []
        assessment: dict[str, Any] | None = None

        try:
            _create_chat(args.base_url, headers, session_id, args.timeout)
            for turn_index, prompt in enumerate(case["turns"], start=1):
                prompts.append(prompt)
                chat_payload = _chat(
                    base_url=args.base_url,
                    headers=headers,
                    session_id=session_id,
                    message=prompt,
                    timeout=args.timeout,
                )
                response_text = str(chat_payload.get("output", "")).strip()
                responses.append(response_text)
                wc = _word_count(response_text)
                word_counts.append(wc)
                filler_hits = _count_filler_hits(response_text, case["forbidden_phrases"])
                filler_hits_by_turn.append(filler_hits)
                tail_char = _last_visible_char(response_text)
                tail_chars.append(tail_char)

                turn_rows.append(
                    {
                        "turn_index": turn_index,
                        "prompt": prompt,
                        "response": response_text,
                        "word_count": wc,
                        "filler_hits": filler_hits,
                        "tail_char": tail_char,
                    }
                )
                print(f"  turn {turn_index}: words={wc} tail={tail_char!r}")

            assessment = _assess_case(
                case=case,
                responses=responses,
                word_counts=word_counts,
                filler_hits_by_turn=filler_hits_by_turn,
                tail_chars=tail_chars,
            )
            status_text = "PASS" if assessment["passed"] else "FAIL"
            if status_text == "FAIL":
                failures += 1
            metrics = assessment["metrics"]
            print(
                f"[{status_text}] {case['id']} unique={metrics['unique_ratio']:.2f} "
                f"avg_words={metrics['avg_words']:.2f} "
                f"max_repeat={metrics['max_consecutive_repeat']} "
                f"motif_dom={metrics['tail_motif_dominance']:.2f}"
            )
            for reason in assessment["reasons"]:
                print(f"  reason: {reason}")
        except Exception as exc:
            failures += 1
            status_text = "ERROR"
            error_text = str(exc)
            print(f"[ERROR] {case['id']}: {error_text}")
        finally:
            case_results.append(
                {
                    "id": case["id"],
                    "session_id": session_id,
                    "status": status_text,
                    "error": error_text,
                    "description": case["description"],
                    "thresholds": {
                        "max_avg_words": case["max_avg_words"],
                        "max_words_per_turn": case["max_words_per_turn"],
                        "min_unique_ratio": case["min_unique_ratio"],
                        "max_consecutive_repeat": case["max_consecutive_repeat"],
                        "max_filler_hits": case["max_filler_hits"],
                        "max_tail_motif_dominance": case["max_tail_motif_dominance"],
                        "forbidden_phrases": case["forbidden_phrases"],
                        "motif_chars": case["motif_chars"],
                    },
                    "assessment": assessment,
                    "turns": turn_rows,
                }
            )

    if not args.keep_chats:
        for session_id in session_ids:
            try:
                _delete_chat(args.base_url, headers, session_id, args.timeout)
            except Exception as exc:
                print(f"  WARN cleanup failed for {session_id}: {exc}")

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
            "strict": bool(args.strict),
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
