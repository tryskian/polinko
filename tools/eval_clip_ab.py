from __future__ import annotations

import argparse
import importlib
import json
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

try:
    from tools import eval_file_search as _eval_file_search
except ModuleNotFoundError:
    _eval_file_search = importlib.import_module("eval_file_search")

from tools.eval_trace_artifacts import DEFAULT_TRACE_JSONL
from tools.eval_trace_artifacts import append_eval_trace
from tools.eval_trace_artifacts import build_eval_trace

_create_chat = _eval_file_search._create_chat
_delete_chat = _eval_file_search._delete_chat
_file_search = _eval_file_search._file_search
_find_matching_result = _eval_file_search._find_matching_result
_headers = _eval_file_search._headers
_load_cases = _eval_file_search._load_cases
_preflight = _eval_file_search._preflight
_seed_image_context_memory = _eval_file_search._seed_image_context_memory
_seed_ocr_memory = _eval_file_search._seed_ocr_memory
_seed_pdf_memory = _eval_file_search._seed_pdf_memory


def _parse_csv(value: str) -> list[str]:
    return [item.strip().lower() for item in value.split(",") if item.strip()]


def _seed_case(
    *,
    base_url: str,
    headers: dict[str, str],
    case: dict[str, Any],
    seed_session: str,
    distractor_session: str,
    timeout: int,
) -> None:
    seed_method = case["seed_method"]
    source_name = case["source_name"]
    seed_text = case["seed_text"]

    if seed_method == "ocr":
        _seed_ocr_memory(
            base_url=base_url,
            headers=headers,
            session_id=seed_session,
            source_name=source_name,
            text=seed_text,
            timeout=timeout,
        )
    elif seed_method == "pdf":
        _seed_pdf_memory(
            base_url=base_url,
            headers=headers,
            session_id=seed_session,
            source_name=source_name,
            text=seed_text,
            timeout=timeout,
        )
    elif seed_method == "image_context":
        _seed_image_context_memory(
            base_url=base_url,
            headers=headers,
            session_id=seed_session,
            source_name=source_name,
            text_hint=seed_text,
            visual_context_hint=seed_text,
            timeout=timeout,
        )
    else:
        raise RuntimeError(f"Unsupported seed method '{seed_method}'.")

    # Distractor content increases lexical overlap to stress ranking behavior.
    distractor_text = (
        f"{case['query']} :: distractor context includes terms {', '.join(case['must_include'])} "
        "but should not outrank target source."
    )
    _seed_ocr_memory(
        base_url=base_url,
        headers=headers,
        session_id=distractor_session,
        source_name=f"{case['id']}-distractor.txt",
        text=distractor_text,
        timeout=timeout,
    )


def _is_top1_hit(
    *,
    matches: list[dict[str, Any]],
    expected_session: str,
    expected_source_type: str,
    required_terms: list[str],
) -> bool:
    if not matches:
        return False
    first = matches[0]
    if not isinstance(first, dict):
        return False
    if str(first.get("session_id", "")) != expected_session:
        return False
    if str(first.get("source_type", "")).lower() != expected_source_type.lower():
        return False
    snippet = str(first.get("snippet", "")).lower()
    return all(term in snippet for term in required_terms)


def _aggregate_arm_results(records: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, dict[str, int]] = {}
    for record in records:
        arm = str(record.get("arm", "unknown"))
        arm_stats = summary.setdefault(
            arm, {"cases": 0, "top1_hits": 0, "any_hits": 0, "errors": 0, "skipped": 0}
        )
        arm_stats["cases"] += 1
        if record.get("error"):
            arm_stats["errors"] += 1
            continue
        if record.get("skipped"):
            arm_stats["skipped"] += 1
            continue
        if bool(record.get("top1_hit")):
            arm_stats["top1_hits"] += 1
        if bool(record.get("any_hit")):
            arm_stats["any_hits"] += 1

    out: dict[str, Any] = {}
    for arm, arm_stats in summary.items():
        evaluated = max(1, arm_stats["cases"] - arm_stats["errors"] - arm_stats["skipped"])
        out[arm] = {
            **arm_stats,
            "top1_rate": arm_stats["top1_hits"] / evaluated,
            "any_rate": arm_stats["any_hits"] / evaluated,
        }
    return out


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run CLIP A/B retrieval scaffold: baseline mixed-source search vs "
            "image-prioritized proxy arm."
        ),
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Polinko API base URL.")
    parser.add_argument(
        "--cases",
        default="docs/clip_ab_eval_cases.json",
        help="Path to file-search eval cases JSON file.",
    )
    parser.add_argument(
        "--source-types",
        default="image",
        help="Comma-separated source_type values to include (default: image).",
    )
    parser.add_argument(
        "--session-prefix",
        default="clip-ab-eval",
        help="Session id prefix for generated eval chats.",
    )
    parser.add_argument(
        "--run-id",
        default="",
        help="Optional run id suffix. Defaults to current epoch seconds.",
    )
    parser.add_argument("--timeout", type=int, default=90, help="HTTP timeout in seconds.")
    parser.add_argument("--limit", type=int, default=5, help="file_search result limit per arm.")
    parser.add_argument(
        "--keep-chats",
        action="store_true",
        help="Keep generated eval chats instead of deleting them.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if proxy any_rate underperforms baseline any_rate.",
    )
    parser.add_argument(
        "--report-json",
        default="",
        help="Optional path to write JSON report artifact.",
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

    include_types = set(_parse_csv(args.source_types))
    if not include_types:
        raise SystemExit("--source-types must include at least one source type.")

    all_cases = _load_cases(cases_path)
    cases = [case for case in all_cases if case["source_type"] in include_types]
    if not cases:
        raise SystemExit(
            f"No cases matched source types {sorted(include_types)} in {cases_path}."
        )

    api_key = os.getenv("POLINKO_SERVER_API_KEY")
    headers = _headers(api_key)
    run_id = args.run_id.strip() or str(int(time.time()))

    print(f"Running CLIP A/B scaffold on {args.base_url}")
    print(f"Cases: {len(cases)} | source_types={sorted(include_types)} | run_id={run_id}")
    try:
        _preflight(args.base_url, headers, args.timeout)
    except Exception as exc:
        print(f"Preflight failed: {exc}")
        return 1

    arms: list[tuple[str, list[str] | None]] = [
        ("baseline_mixed", None),
        ("clip_proxy_image_only", ["image"]),
    ]

    records: list[dict[str, Any]] = []
    for case in cases:
        case_id = case["id"]
        seed_session = f"{args.session_prefix}-{run_id}-seed-{case_id}"
        distractor_session = f"{args.session_prefix}-{run_id}-distractor-{case_id}"
        print(f"\nCase: {case_id}")
        try:
            _create_chat(args.base_url, headers, seed_session, args.timeout)
            _create_chat(args.base_url, headers, distractor_session, args.timeout)
            _seed_case(
                base_url=args.base_url,
                headers=headers,
                case=case,
                seed_session=seed_session,
                distractor_session=distractor_session,
                timeout=args.timeout,
            )

            for arm_name, arm_source_types in arms:
                matches = _file_search(
                    base_url=args.base_url,
                    headers=headers,
                    query=case["query"],
                    source_types=arm_source_types,
                    limit=args.limit,
                    timeout=args.timeout,
                )
                normalized_matches = [item for item in matches if isinstance(item, dict)]
                any_hit = _find_matching_result(
                    matches=normalized_matches,
                    expected_session=seed_session,
                    expected_source_type=case["source_type"],
                    terms=case["must_include"],
                )
                top1_hit = _is_top1_hit(
                    matches=normalized_matches,
                    expected_session=seed_session,
                    expected_source_type=case["source_type"],
                    required_terms=case["must_include"],
                )
                records.append(
                    {
                        "case_id": case_id,
                        "arm": arm_name,
                        "source_types": arm_source_types,
                        "top1_hit": top1_hit,
                        "any_hit": any_hit is not None,
                        "top_score": normalized_matches[0].get("score") if normalized_matches else None,
                        "top_source_type": normalized_matches[0].get("source_type") if normalized_matches else None,
                        "top_session_id": normalized_matches[0].get("session_id") if normalized_matches else None,
                    }
                )
                print(
                    f"  {arm_name}: top1_hit={top1_hit} any_hit={any_hit is not None}"
                )
        except Exception as exc:
            error_text = str(exc)
            print(f"  ERROR {error_text}")
            for arm_name, arm_source_types in arms:
                records.append(
                    {
                        "case_id": case_id,
                        "arm": arm_name,
                        "source_types": arm_source_types,
                        "error": error_text,
                    }
                )
        finally:
            if not args.keep_chats:
                for session_id in (seed_session, distractor_session):
                    try:
                        _delete_chat(args.base_url, headers, session_id, args.timeout)
                    except Exception as exc:
                        print(f"  WARN cleanup failed for {session_id}: {exc}")

    summary = _aggregate_arm_results(records)
    baseline = summary.get("baseline_mixed", {})
    proxy = summary.get("clip_proxy_image_only", {})
    baseline_any = float(baseline.get("any_rate", 0.0))
    proxy_any = float(proxy.get("any_rate", 0.0))

    print("\nSummary")
    for arm_name, arm_stats in summary.items():
        print(
            f"  {arm_name}: top1_rate={arm_stats['top1_rate']:.3f} "
            f"any_rate={arm_stats['any_rate']:.3f} "
            f"errors={arm_stats['errors']} skipped={arm_stats['skipped']}"
        )
    print(f"  any_rate_delta(proxy-baseline)={proxy_any - baseline_any:+.3f}")

    report_path = args.report_json.strip()
    if report_path:
        out_path = Path(report_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        report_payload = {
            "run_id": run_id,
            "base_url": args.base_url,
            "source_types": sorted(include_types),
            "cases_count": len(cases),
            "arms": [arm[0] for arm in arms],
            "summary": summary,
            "any_rate_delta_proxy_minus_baseline": proxy_any - baseline_any,
            "cases": records,
            "timestamp_unix": int(time.time()),
        }
        out_path.write_text(
            json.dumps(report_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Report written: {out_path}")
        trace_jsonl = str(args.trace_jsonl or "").strip()
        if trace_jsonl:
            trace_payload = build_eval_trace(
                run_id=run_id,
                tool_name="tools/eval_clip_ab.py",
                source_artifacts={
                    "report_json": str(out_path),
                    "cases_path": str(cases_path),
                },
                gate_outcomes=[
                    {
                        "name": "clip_proxy_readiness",
                        "passed": proxy_any >= baseline_any,
                        "detail": (
                            f"proxy_any_rate={proxy_any:.3f}, baseline_any_rate={baseline_any:.3f}, "
                            f"delta={proxy_any - baseline_any:+.3f}"
                        ),
                    }
                ],
                summary={
                    "cases_count": len(cases),
                    "proxy_any_rate": proxy_any,
                    "baseline_any_rate": baseline_any,
                    "any_rate_delta_proxy_minus_baseline": proxy_any - baseline_any,
                },
                metadata={
                    "base_url": args.base_url,
                    "source_types": sorted(include_types),
                    "strict": bool(args.strict),
                },
            )
            trace_path = append_eval_trace(
                trace_payload=trace_payload,
                trace_jsonl_path=Path(trace_jsonl),
            )
            print(f"Trace written: {trace_path}")

    if args.strict and proxy_any < baseline_any:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
