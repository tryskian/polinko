"""Build a reusable fail cohort from OCR growth-lane stability outputs."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _load_case_map(path: Path) -> dict[str, dict[str, Any]]:
    payload = _load_json_object(path)
    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list):
        raise RuntimeError(f"Expected 'cases' list in: {path}")

    out: dict[str, dict[str, Any]] = {}
    for row in raw_cases:
        if not isinstance(row, dict):
            continue
        case_id = str(row.get("id", "")).strip()
        if not case_id:
            continue
        out[case_id] = row
    return out


def _resolve_run_report_path(*, report_path: str, stability_report_path: Path) -> Path:
    candidate = Path(report_path).expanduser()
    if candidate.is_absolute():
        return candidate
    cwd_candidate = (Path.cwd() / candidate).resolve()
    if cwd_candidate.is_file():
        return cwd_candidate
    return (stability_report_path.parent / candidate).resolve()


def _load_run_case_map(
    *, stability_payload: dict[str, Any], stability_report_path: Path
) -> dict[str, dict[str, Any]]:
    runs = stability_payload.get("runs")
    if not isinstance(runs, list):
        return {}
    for run in runs:
        if not isinstance(run, dict):
            continue
        report_rel = str(run.get("report_json", "")).strip()
        if not report_rel:
            continue
        report_path = _resolve_run_report_path(
            report_path=report_rel,
            stability_report_path=stability_report_path,
        )
        if not report_path.is_file():
            continue
        try:
            payload = _load_json_object(report_path)
        except Exception:
            continue
        raw_cases = payload.get("cases")
        if not isinstance(raw_cases, list) or not raw_cases:
            continue
        out: dict[str, dict[str, Any]] = {}
        for row in raw_cases:
            if not isinstance(row, dict):
                continue
            case_id = str(row.get("id", "")).strip()
            if not case_id:
                continue
            out[case_id] = row
        if out:
            return out
    return {}


def _load_review_index(path: Path) -> dict[str, list[dict[str, Any]]]:
    if not path.is_file():
        return {}
    payload = _load_json_object(path)
    raw_episodes = payload.get("episodes")
    if not isinstance(raw_episodes, list):
        return {}

    out: dict[str, list[dict[str, Any]]] = {}
    for row in raw_episodes:
        if not isinstance(row, dict):
            continue
        image_path = str(row.get("image_path", "")).strip()
        if not image_path:
            continue
        out.setdefault(image_path, []).append(row)
    return out


def _normalise_reason(raw: str) -> str:
    cleaned = " ".join(str(raw).split()).strip()
    if not cleaned:
        return ""
    if len(cleaned) <= 140:
        return cleaned
    return f"{cleaned[:137]}..."


def _reason_pattern(reason: str) -> str:
    lowered = reason.lower()
    if "missing ordered phrase" in lowered:
        return "ordered_phrase_missing"
    if "missing one-of required phrase" in lowered:
        return "anchor_any_missing"
    if "missing one-of required phrases" in lowered:
        return "anchor_any_missing"
    if "missing required phrase" in lowered:
        return "required_phrase_missing"
    if "error" in lowered:
        return "runtime_error"
    return "other"


def _fallback_failure_pattern(
    *,
    growth_case: dict[str, Any],
    fail_runs: int,
    pass_runs: int,
    error_runs: int,
    first_status: str,
    latest_status: str,
) -> str:
    must_order = growth_case.get("must_appear_in_order")
    if isinstance(must_order, list) and must_order:
        return "ordered_phrase_missing_proxy"

    must_any = growth_case.get("must_contain_any")
    if isinstance(must_any, list) and must_any:
        return "anchor_any_missing_proxy"

    if error_runs > 0 and fail_runs <= 0 and pass_runs <= 0:
        return "runtime_error_only"
    if error_runs > 0 and fail_runs > 0 and pass_runs <= 0:
        return "fail_with_errors"
    if fail_runs > 0 and pass_runs <= 0:
        return "persistent_fail"
    if fail_runs > 0 and pass_runs > 0:
        if latest_status == "PASS":
            return "recovered_after_fail"
        if latest_status == "FAIL":
            return "regressed_after_pass"
        if first_status == "FAIL":
            return "flaky_fail_first"
        return "flaky_mixed"
    return "other"


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        token = str(item).strip()
        if token:
            out.append(token)
    return out


def _effective_gate_terms(
    *,
    growth_case: dict[str, Any],
    run_case: dict[str, Any],
) -> tuple[list[str], list[str]]:
    run_any = _string_list(run_case.get("must_contain_any"))
    growth_any = _string_list(growth_case.get("must_contain_any"))
    run_order = _string_list(run_case.get("must_appear_in_order"))
    growth_order = _string_list(growth_case.get("must_appear_in_order"))
    return (run_any or growth_any, run_order or growth_order)


def _preview_terms(values: list[str], *, limit: int = 3) -> str:
    if not values:
        return "-"
    head = values[:limit]
    preview = ", ".join(head)
    if len(values) > limit:
        preview = f"{preview} (+{len(values) - limit})"
    return preview


def _format_gate_probe(must_any: list[str], must_order: list[str]) -> str:
    return f"any[{_preview_terms(must_any)}] order[{_preview_terms(must_order)}]"


def _merge_case_rows(
    *,
    stability_cases: list[dict[str, Any]],
    metrics_map: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], int]:
    merged: dict[str, dict[str, Any]] = {}
    for row in stability_cases:
        case_id = str(row.get("id", "")).strip()
        if not case_id:
            continue
        merged[case_id] = row

    added_from_metrics = 0
    for case_id, metrics in metrics_map.items():
        if case_id in merged:
            continue
        observed_runs = int(metrics.get("observed_runs", 0) or 0)
        if observed_runs <= 0:
            continue
        pass_runs = int(metrics.get("pass_runs", 0) or 0)
        fail_runs = int(metrics.get("fail_runs", 0) or 0)
        error_runs = int(metrics.get("error_runs", 0) or 0)
        statuses: list[str] = []
        if observed_runs > 0 and pass_runs <= 0 and fail_runs <= 0 and error_runs > 0:
            statuses = ["ERROR"]

        merged[case_id] = {
            "id": case_id,
            "observed_runs": observed_runs,
            "pass_runs": pass_runs,
            "fail_runs": fail_runs,
            "error_runs": error_runs,
            "pass_rate": float(metrics.get("pass_rate", 0.0) or 0.0),
            "decision_stable": bool(metrics.get("decision_stable", False)),
            "always_fail": bool(metrics.get("always_fail", False)),
            "statuses": statuses,
            "sample_reasons": [],
            "text_variant_count": int(metrics.get("text_variant_count", 0) or 0),
            "char_count_span": int(metrics.get("char_count_span", 0) or 0),
        }
        added_from_metrics += 1

    return list(merged.values()), added_from_metrics


def build_fail_cohort(
    *,
    stability_payload: dict[str, Any],
    growth_case_map: dict[str, dict[str, Any]],
    run_case_map: dict[str, dict[str, Any]],
    metrics_map: dict[str, dict[str, Any]],
    review_index: dict[str, list[dict[str, Any]]],
    min_runs: int,
    include_unstable: bool,
    require_ocr_framing: bool,
) -> dict[str, Any]:
    raw_cases = stability_payload.get("cases")
    if not isinstance(raw_cases, list):
        raise RuntimeError("Expected 'cases' list in stability payload")
    stability_cases_total = len(raw_cases)
    raw_cases, metrics_rows_added = _merge_case_rows(
        stability_cases=raw_cases,
        metrics_map=metrics_map,
    )

    selected: list[dict[str, Any]] = []
    fail_history_cases: list[dict[str, Any]] = []
    rate_limited_cases: list[dict[str, Any]] = []
    lane_counts: Counter[str] = Counter()
    fail_history_lane_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    reason_pattern_counts: Counter[str] = Counter()
    skipped_non_framed = 0
    skipped_case_map_mismatch = 0
    rate_limit_abort_runs = 0
    fail_to_pass_cases = 0

    raw_runs = stability_payload.get("runs")
    if isinstance(raw_runs, list):
        rate_limit_abort_runs = sum(
            1
            for run in raw_runs
            if isinstance(run, dict)
            and isinstance(run.get("summary"), dict)
            and bool(run["summary"].get("aborted_due_to_rate_limit", False))
        )

    for row in raw_cases:
        if not isinstance(row, dict):
            continue
        case_id = str(row.get("id", "")).strip()
        if not case_id:
            continue

        observed_runs = int(row.get("observed_runs", 0) or 0)
        pass_runs = int(row.get("pass_runs", 0) or 0)
        fail_runs = int(row.get("fail_runs", 0) or 0)
        decision_stable = bool(row.get("decision_stable", False))
        always_fail = bool(row.get("always_fail", False))

        if observed_runs < min_runs:
            continue
        if fail_runs <= 0:
            continue

        growth_case = growth_case_map.get(case_id, {})
        run_case = run_case_map.get(case_id, {})
        lane = str(growth_case.get("lane", "unknown")).strip() or "unknown"
        source_name = (
            str(run_case.get("source_name", "")).strip()
            or str(growth_case.get("source_name", "")).strip()
            or case_id
        )
        image_path = (
            str(run_case.get("image_path", "")).strip()
            or str(growth_case.get("image_path", "")).strip()
        )
        growth_image_path = str(growth_case.get("image_path", "")).strip()
        if run_case_map and growth_image_path and image_path and growth_image_path != image_path:
            skipped_case_map_mismatch += 1
            continue
        linked_review_rows = review_index.get(image_path, [])
        if lane == "unknown" and linked_review_rows:
            review_lane_counts: Counter[str] = Counter(
                str(review_row.get("lane", "")).strip() or "unknown"
                for review_row in linked_review_rows
                if isinstance(review_row, dict)
            )
            if review_lane_counts:
                lane = review_lane_counts.most_common(1)[0][0]
        framing_episode_count = sum(
            1 for review_row in linked_review_rows if bool(review_row.get("ocr_framing_signal", False))
        )
        if require_ocr_framing and framing_episode_count <= 0:
            skipped_non_framed += 1
            continue

        metrics = metrics_map.get(case_id, {})
        unresolved_fail_age_hours = metrics.get("unresolved_fail_age_hours")
        age_hours = float(unresolved_fail_age_hours or 0.0)
        fail_to_pass_converted = bool(metrics.get("fail_to_pass_converted", False))
        first_status = str(metrics.get("first_status", "")).strip().upper() or "ERROR"
        latest_status = str(metrics.get("latest_status", "")).strip().upper() or "ERROR"

        sample_reasons_raw = row.get("sample_reasons")
        sample_reasons = (
            [str(item).strip() for item in sample_reasons_raw if str(item).strip()]
            if isinstance(sample_reasons_raw, list)
            else []
        )
        effective_must_any, effective_must_order = _effective_gate_terms(
            growth_case=growth_case,
            run_case=run_case,
        )
        gate_probe_summary = _format_gate_probe(effective_must_any, effective_must_order)
        case_reason_patterns: Counter[str] = Counter()

        for reason in sample_reasons:
            reason_key = _normalise_reason(reason)
            if reason_key:
                reason_counts[reason_key] += 1
            pattern = _reason_pattern(reason)
            case_reason_patterns[pattern] += 1
            reason_pattern_counts[pattern] += 1

        primary_failure_pattern = "unknown"
        if case_reason_patterns:
            primary_failure_pattern = case_reason_patterns.most_common(1)[0][0]
        else:
            primary_failure_pattern = _fallback_failure_pattern(
                growth_case=growth_case,
                fail_runs=fail_runs,
                pass_runs=pass_runs,
                error_runs=int(row.get("error_runs", 0) or 0),
                first_status=first_status,
                latest_status=latest_status,
            )
            reason_pattern_counts[primary_failure_pattern] += 1

        if fail_runs > 0 and pass_runs > 0:
            fail_history_cases.append(
                {
                    "id": case_id,
                    "lane": lane,
                    "source_name": source_name,
                    "image_path": image_path,
                    "observed_runs": observed_runs,
                    "pass_runs": pass_runs,
                    "fail_runs": fail_runs,
                    "error_runs": int(row.get("error_runs", 0) or 0),
                    "pass_rate": float(row.get("pass_rate", 0.0) or 0.0),
                    "fail_to_pass_converted": fail_to_pass_converted,
                    "first_status": first_status,
                    "latest_status": latest_status,
                    "sample_reasons": sample_reasons,
                    "failure_patterns": sorted(case_reason_patterns.keys()),
                    "primary_failure_pattern": primary_failure_pattern,
                    "gate_probe_summary": gate_probe_summary,
                    "effective_must_contain_any": effective_must_any,
                    "effective_must_appear_in_order": effective_must_order,
                    "framing_episode_count": framing_episode_count,
                    "review_episode_count": len(linked_review_rows),
                }
            )
            fail_history_lane_counts[lane] += 1
            if fail_to_pass_converted:
                fail_to_pass_cases += 1

        persistent_fail_selected = False
        if pass_runs == 0:
            if include_unstable:
                persistent_fail_selected = True
            else:
                persistent_fail_selected = bool(decision_stable and always_fail)

        if not persistent_fail_selected:
            continue

        selected_row = {
            "id": case_id,
            "lane": lane,
            "source_name": source_name,
            "image_path": image_path,
            "observed_runs": observed_runs,
            "pass_runs": pass_runs,
            "fail_runs": fail_runs,
            "error_runs": int(row.get("error_runs", 0) or 0),
            "pass_rate": float(row.get("pass_rate", 0.0) or 0.0),
            "decision_stable": decision_stable,
            "always_fail": always_fail,
            "statuses": row.get("statuses") if isinstance(row.get("statuses"), list) else [],
            "sample_reasons": sample_reasons,
            "failure_patterns": sorted(case_reason_patterns.keys()),
            "primary_failure_pattern": primary_failure_pattern,
            "text_variant_count": int(row.get("text_variant_count", 0) or 0),
            "char_count_span": int(row.get("char_count_span", 0) or 0),
            "must_contain_any": growth_case.get("must_contain_any", []),
            "must_appear_in_order": growth_case.get("must_appear_in_order", []),
            "run_must_contain_any": run_case.get("must_contain_any", []),
            "run_must_appear_in_order": run_case.get("must_appear_in_order", []),
            "effective_must_contain_any": effective_must_any,
            "effective_must_appear_in_order": effective_must_order,
            "gate_probe_summary": gate_probe_summary,
            "unresolved_fail_age_hours": round(age_hours, 3),
            "review_episode_count": len(linked_review_rows),
            "framing_episode_count": framing_episode_count,
        }
        selected.append(selected_row)
        lane_counts[lane] += 1

    for row in raw_cases:
        if not isinstance(row, dict):
            continue
        case_id = str(row.get("id", "")).strip()
        if not case_id:
            continue
        observed_runs = int(row.get("observed_runs", 0) or 0)
        pass_runs = int(row.get("pass_runs", 0) or 0)
        fail_runs = int(row.get("fail_runs", 0) or 0)
        error_runs = int(row.get("error_runs", 0) or 0)
        raw_statuses = row.get("statuses")
        statuses = raw_statuses if isinstance(raw_statuses, list) else []
        has_only_error_statuses = bool(statuses) and all(str(item).upper() == "ERROR" for item in statuses)
        if observed_runs <= 0:
            continue
        if pass_runs > 0 or fail_runs > 0 or error_runs <= 0:
            continue
        if not has_only_error_statuses:
            continue

        growth_case = growth_case_map.get(case_id, {})
        run_case = run_case_map.get(case_id, {})
        lane = str(growth_case.get("lane", "unknown")).strip() or "unknown"
        source_name = (
            str(run_case.get("source_name", "")).strip()
            or str(growth_case.get("source_name", "")).strip()
            or case_id
        )
        image_path = (
            str(run_case.get("image_path", "")).strip()
            or str(growth_case.get("image_path", "")).strip()
        )
        growth_image_path = str(growth_case.get("image_path", "")).strip()
        if run_case_map and growth_image_path and image_path and growth_image_path != image_path:
            continue
        linked_review_rows = review_index.get(image_path, [])
        framing_episode_count = sum(
            1 for review_row in linked_review_rows if bool(review_row.get("ocr_framing_signal", False))
        )

        rate_limited_cases.append(
            {
                "id": case_id,
                "lane": lane,
                "source_name": source_name,
                "image_path": image_path,
                "observed_runs": observed_runs,
                "error_runs": error_runs,
                "statuses": statuses,
                "framing_episode_count": framing_episode_count,
                "effective_must_contain_any": _string_list(
                    run_case.get("must_contain_any")
                )
                or _string_list(growth_case.get("must_contain_any")),
                "effective_must_appear_in_order": _string_list(
                    run_case.get("must_appear_in_order")
                )
                or _string_list(growth_case.get("must_appear_in_order")),
            }
        )

    selected.sort(
        key=lambda item: (
            item["lane"],
            -float(item.get("unresolved_fail_age_hours", 0.0) or 0.0),
            item["id"],
        )
    )
    fail_history_cases.sort(
        key=lambda item: (
            item["lane"],
            -int(item.get("fail_runs", 0) or 0),
            item["id"],
        )
    )
    rate_limited_cases.sort(key=lambda item: (item["lane"], item["id"]))

    summary = {
        "cases_total": len(raw_cases),
        "stability_cases_total": stability_cases_total,
        "metrics_rows_added": metrics_rows_added,
        "selected_fail_cases": len(selected),
        "fail_history_cases": len(fail_history_cases),
        "fail_to_pass_cases": fail_to_pass_cases,
        "rate_limited_cases": len(rate_limited_cases),
        "rate_limit_abort_runs": rate_limit_abort_runs,
        "min_runs": min_runs,
        "include_unstable": include_unstable,
        "require_ocr_framing": require_ocr_framing,
        "skipped_non_framed": skipped_non_framed,
        "skipped_case_map_mismatch": skipped_case_map_mismatch,
        "lane_counts": dict(sorted(lane_counts.items())),
        "fail_history_lane_counts": dict(sorted(fail_history_lane_counts.items())),
        "top_reasons": [
            {"reason": reason, "count": count}
            for reason, count in reason_counts.most_common(10)
        ],
        "failure_pattern_counts": dict(sorted(reason_pattern_counts.items())),
    }

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": summary,
        "cases": selected,
        "fail_history_cases": fail_history_cases,
        "rate_limited_cases": rate_limited_cases,
    }


def _render_markdown(*, report: dict[str, Any], stability_report: Path, growth_cases: Path) -> str:
    summary = report["summary"]
    selected = report["cases"]
    fail_history_cases = (
        report.get("fail_history_cases")
        if isinstance(report.get("fail_history_cases"), list)
        else []
    )
    rate_limited_cases = (
        report.get("rate_limited_cases") if isinstance(report.get("rate_limited_cases"), list) else []
    )
    top_reasons = summary.get("top_reasons") if isinstance(summary.get("top_reasons"), list) else []

    lines: list[str] = []
    lines.append("# OCR Growth Fail Cohort")
    lines.append("")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append(f"Stability report: `{stability_report}`")
    lines.append(f"Growth cases: `{growth_cases}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---:|")
    lines.append(f"| cases_total | {summary['cases_total']} |")
    lines.append(f"| stability_cases_total | {summary['stability_cases_total']} |")
    lines.append(f"| metrics_rows_added | {summary['metrics_rows_added']} |")
    lines.append(f"| selected_fail_cases | {summary['selected_fail_cases']} |")
    lines.append(f"| fail_history_cases | {summary['fail_history_cases']} |")
    lines.append(f"| fail_to_pass_cases | {summary['fail_to_pass_cases']} |")
    lines.append(f"| rate_limited_cases | {summary['rate_limited_cases']} |")
    lines.append(f"| rate_limit_abort_runs | {summary['rate_limit_abort_runs']} |")
    lines.append(f"| min_runs | {summary['min_runs']} |")
    lines.append(f"| include_unstable | {summary['include_unstable']} |")
    lines.append(f"| require_ocr_framing | {summary['require_ocr_framing']} |")
    lines.append(f"| skipped_non_framed | {summary['skipped_non_framed']} |")
    lines.append(f"| skipped_case_map_mismatch | {summary['skipped_case_map_mismatch']} |")
    lines.append("")

    lane_counts = summary.get("lane_counts")
    if isinstance(lane_counts, dict) and lane_counts:
        lines.append("## Lane Counts")
        lines.append("")
        lines.append("| lane | selected_fail_cases |")
        lines.append("|---|---:|")
        for lane, count in lane_counts.items():
            lines.append(f"| {lane} | {count} |")
        lines.append("")

    fail_history_lane_counts = summary.get("fail_history_lane_counts")
    if isinstance(fail_history_lane_counts, dict) and fail_history_lane_counts:
        lines.append("## Fail-History Lane Counts")
        lines.append("")
        lines.append("| lane | fail_history_cases |")
        lines.append("|---|---:|")
        for lane, count in fail_history_lane_counts.items():
            lines.append(f"| {lane} | {count} |")
        lines.append("")

    if top_reasons:
        lines.append("## Top Failure Reasons")
        lines.append("")
        lines.append("| reason | count |")
        lines.append("|---|---:|")
        for row in top_reasons:
            reason = str(row.get("reason", "")).replace("|", "\\|")
            count = int(row.get("count", 0) or 0)
            lines.append(f"| {reason} | {count} |")
        lines.append("")

    failure_pattern_counts = summary.get("failure_pattern_counts")
    if isinstance(failure_pattern_counts, dict) and failure_pattern_counts:
        lines.append("## Failure Pattern Counts")
        lines.append("")
        lines.append("| pattern | count |")
        lines.append("|---|---:|")
        for pattern, count in failure_pattern_counts.items():
            lines.append(f"| {pattern} | {int(count)} |")
        lines.append("")

    if selected:
        lines.append("## Selected Cases")
        lines.append("")

    if fail_history_cases:
        lines.append("## Fail-History Cases (At Least One PASS and One FAIL)")
        lines.append("")
        lines.append(
            "| case_id | lane | pattern | gate_probe | fail_runs | pass_runs | observed_runs | fail_to_pass | source_name | image_path |"
        )
        lines.append("|---|---|---|---|---:|---:|---:|---|---|---|")
        for row in fail_history_cases:
            case_id = str(row.get("id", ""))
            lane = str(row.get("lane", ""))
            pattern = str(row.get("primary_failure_pattern", ""))
            gate_probe = str(row.get("gate_probe_summary", "-")).replace("|", "\\|")
            fail_runs = int(row.get("fail_runs", 0) or 0)
            pass_runs = int(row.get("pass_runs", 0) or 0)
            observed = int(row.get("observed_runs", 0) or 0)
            fail_to_pass = bool(row.get("fail_to_pass_converted", False))
            source_name = str(row.get("source_name", "")).replace("|", "\\|")
            image_path = str(row.get("image_path", "")).replace("|", "\\|")
            lines.append(
                f"| {case_id} | {lane} | {pattern} | {gate_probe} | {fail_runs} | {pass_runs} | {observed} | {fail_to_pass} | "
                f"{source_name} | {image_path} |"
            )
        lines.append("")
        lines.append(
            "| case_id | lane | pattern | gate_probe | fail_runs | observed_runs | framing_eps | age_hours | source_name | image_path |"
        )
        lines.append("|---|---|---|---|---:|---:|---:|---:|---|---|")
        for row in selected:
            case_id = str(row.get("id", ""))
            lane = str(row.get("lane", ""))
            pattern = str(row.get("primary_failure_pattern", ""))
            gate_probe = str(row.get("gate_probe_summary", "-")).replace("|", "\\|")
            fail_runs = int(row.get("fail_runs", 0) or 0)
            observed = int(row.get("observed_runs", 0) or 0)
            framing_eps = int(row.get("framing_episode_count", 0) or 0)
            age_hours = float(row.get("unresolved_fail_age_hours", 0.0) or 0.0)
            source_name = str(row.get("source_name", "")).replace("|", "\\|")
            image_path = str(row.get("image_path", "")).replace("|", "\\|")
            lines.append(
                f"| {case_id} | {lane} | {pattern} | {gate_probe} | {fail_runs} | {observed} | {framing_eps} | {age_hours:.3f} | "
                f"{source_name} | {image_path} |"
            )
        lines.append("")

    if rate_limited_cases:
        lines.append("## Rate-Limited Cases (No PASS/FAIL Decision Yet)")
        lines.append("")
        lines.append(
            "| case_id | lane | gate_probe | error_runs | observed_runs | framing_eps | source_name | image_path |"
        )
        lines.append("|---|---|---|---:|---:|---:|---|---|")
        for row in rate_limited_cases:
            case_id = str(row.get("id", ""))
            lane = str(row.get("lane", ""))
            gate_probe = _format_gate_probe(
                _string_list(row.get("effective_must_contain_any")),
                _string_list(row.get("effective_must_appear_in_order")),
            ).replace("|", "\\|")
            error_runs = int(row.get("error_runs", 0) or 0)
            observed = int(row.get("observed_runs", 0) or 0)
            framing_eps = int(row.get("framing_episode_count", 0) or 0)
            source_name = str(row.get("source_name", "")).replace("|", "\\|")
            image_path = str(row.get("image_path", "")).replace("|", "\\|")
            lines.append(
                f"| {case_id} | {lane} | {gate_probe} | {error_runs} | {observed} | {framing_eps} | {source_name} | {image_path} |"
            )
        lines.append("")

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a fail cohort from OCR growth-lane stability outputs."
    )
    parser.add_argument(
        "--stability-report",
        default=".local/eval_reports/ocr_growth_stability.json",
        help="Path to OCR growth stability summary JSON.",
    )
    parser.add_argument(
        "--cases",
        default=".local/eval_cases/ocr_transcript_cases_growth.json",
        help="Path to OCR growth cases JSON.",
    )
    parser.add_argument(
        "--metrics",
        default=".local/eval_reports/ocr_growth_metrics.json",
        help="Optional path to OCR growth metrics JSON (for fail-age enrichment).",
    )
    parser.add_argument(
        "--review",
        default=".local/eval_cases/ocr_transcript_cases_review.json",
        help="Optional path to OCR transcript review JSON (for OCR-framing filter).",
    )
    parser.add_argument(
        "--output-json",
        default=".local/eval_cases/ocr_growth_fail_cohort.json",
        help="Output path for fail cohort JSON.",
    )
    parser.add_argument(
        "--output-markdown",
        default=".local/eval_reports/ocr_growth_fail_cohort.md",
        help="Output path for fail cohort markdown report.",
    )
    parser.add_argument(
        "--min-runs",
        type=int,
        default=3,
        help="Minimum observed runs required before selecting a fail case.",
    )
    parser.add_argument(
        "--include-unstable",
        action="store_true",
        help="Include persistent fail cases even when decision_stable is false.",
    )
    parser.add_argument(
        "--require-ocr-framing",
        action="store_true",
        help="Require selected fail cases to map to at least one review episode with ocr_framing_signal=true.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.min_runs < 1:
        print("min-runs must be >= 1")
        return 2

    stability_path = Path(args.stability_report).expanduser()
    cases_path = Path(args.cases).expanduser()
    metrics_path = Path(args.metrics).expanduser()
    review_path = Path(args.review).expanduser()
    output_json = Path(args.output_json).expanduser()
    output_markdown = Path(args.output_markdown).expanduser()

    if not stability_path.is_file():
        print(f"stability report not found: {stability_path}")
        return 2
    if not cases_path.is_file():
        print(f"growth cases not found: {cases_path}")
        return 2

    stability_payload = _load_json_object(stability_path)
    growth_case_map = _load_case_map(cases_path)

    metrics_map: dict[str, dict[str, Any]] = {}
    if metrics_path.is_file():
        metrics_payload = _load_json_object(metrics_path)
        raw_metrics_cases = metrics_payload.get("cases")
        if isinstance(raw_metrics_cases, list):
            for row in raw_metrics_cases:
                if not isinstance(row, dict):
                    continue
                case_id = str(row.get("id", "")).strip()
                if case_id:
                    metrics_map[case_id] = row
    review_index = _load_review_index(review_path)
    run_case_map = _load_run_case_map(
        stability_payload=stability_payload,
        stability_report_path=stability_path,
    )

    report = build_fail_cohort(
        stability_payload=stability_payload,
        growth_case_map=growth_case_map,
        run_case_map=run_case_map,
        metrics_map=metrics_map,
        review_index=review_index,
        min_runs=int(args.min_runs),
        include_unstable=bool(args.include_unstable),
        require_ocr_framing=bool(args.require_ocr_framing),
    )
    report["stability_report"] = str(stability_path)
    report["cases_path"] = str(cases_path)
    report["metrics_path"] = str(metrics_path)
    report["review_path"] = str(review_path)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    markdown = _render_markdown(
        report=report,
        stability_report=stability_path,
        growth_cases=cases_path,
    )
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.write_text(markdown, encoding="utf-8")

    summary = report["summary"]
    print("OCR growth fail cohort")
    print(f"  stability_cases_total: {summary['stability_cases_total']}")
    print(f"  metrics_rows_added: {summary['metrics_rows_added']}")
    print(f"  selected_fail_cases: {summary['selected_fail_cases']}")
    print(f"  fail_history_cases: {summary['fail_history_cases']}")
    print(f"  fail_to_pass_cases: {summary['fail_to_pass_cases']}")
    print(f"  rate_limited_cases: {summary['rate_limited_cases']}")
    print(f"  rate_limit_abort_runs: {summary['rate_limit_abort_runs']}")
    print(f"  cases_total: {summary['cases_total']}")
    print(f"  min_runs: {summary['min_runs']}")
    print(f"  include_unstable: {summary['include_unstable']}")
    print(f"  require_ocr_framing: {summary['require_ocr_framing']}")
    print(f"  skipped_non_framed: {summary['skipped_non_framed']}")
    print(f"  skipped_case_map_mismatch: {summary['skipped_case_map_mismatch']}")
    print(f"  json: {output_json}")
    print(f"  markdown: {output_markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
