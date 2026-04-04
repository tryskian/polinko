"""Build a reusable fail cohort from OCR growth-lane stability outputs."""

from __future__ import annotations

import argparse
import json
import re
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


NON_ACTIONABLE_REASON_RX = re.compile(
    r"(?ix)"
    r"(?:"
    r"\bno\s+(?:readable\s+)?text\b"
    r"|"
    r"\btext\s+not\s+detected\b"
    r"|"
    r"\bunable\s+to\s+(?:read|detect|recognis[ez]e|transcrib(?:e|ing))\b"
    r"|"
    r"\bcould\s+not\s+(?:read|detect|recognis[ez]e|transcrib(?:e|ing))\b"
    r"|"
    r"\billegible\b"
    r"|"
    r"\bblank\s+(?:image|output)\b"
    r"|"
    r"\bempty\s+(?:image|output)\b"
    r")"
)


def _is_symbol_only_tiny_variants(row: dict[str, Any], *, sample_reasons: list[str]) -> bool:
    reasons_text = " | ".join(sample_reasons).lower()
    if "text too short" not in reasons_text:
        return False

    max_chars = int(row.get("char_count_max", 0) or 0)
    if max_chars > 2:
        return False

    raw_variants = row.get("text_variants")
    if not isinstance(raw_variants, list):
        return False
    variants = [str(item).strip() for item in raw_variants if str(item).strip()]
    if not variants:
        return False

    # Keep this strict: classify as non-actionable only when every variant is
    # tiny and has no ASCII alphanumeric anchor we could gate against.
    for text in variants:
        if len(text) > 2:
            return False
        if any(char.isascii() and char.isalnum() for char in text):
            return False
    return True


def _non_actionable_skip_reason(*, row: dict[str, Any], sample_reasons: list[str]) -> str:
    for reason in sample_reasons:
        if NON_ACTIONABLE_REASON_RX.search(reason):
            return "no_text_detected_or_illegible"
    if _is_symbol_only_tiny_variants(row, sample_reasons=sample_reasons):
        return "symbol_only_tiny_output"
    return ""


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


def _tokenise_phrase(phrase: str) -> list[str]:
    return [token for token in re.findall(r"[A-Za-z0-9]+", phrase.lower()) if token]


EXPLORATORY_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "into",
    "that",
    "this",
    "were",
    "was",
    "are",
    "but",
    "not",
    "you",
    "your",
    "our",
    "their",
    "thing",
    "things",
    "note",
    "notes",
    "text",
    "line",
    "lines",
}

# Keep exploratory order probes compact to avoid brittle tail-token failures
# that are less diagnostic than head/mid sequence breaks.
EXPLORATORY_ORDER_MAX_TERMS = 2
EXPLORATORY_MIN_TOKEN_LEN = 5
EXPLORATORY_LANE_ORDER = ("handwriting", "typed", "illustration", "unknown")


def _canonical_probe_token(token: str) -> str:
    lowered = token.lower()
    if len(lowered) > 5 and lowered.endswith("ies"):
        return f"{lowered[:-3]}y"
    if len(lowered) > 4 and lowered.endswith("s") and not lowered.endswith("ss"):
        return lowered[:-1]
    return lowered


def _drop_prefix_stem_terms(
    terms: list[str],
    *,
    min_len: int = 6,
    max_extra_chars: int = 2,
) -> list[str]:
    lowered = [item.lower() for item in terms]
    dropped: set[int] = set()
    for idx, token in enumerate(lowered):
        if len(token) < min_len:
            continue
        for other_idx, other in enumerate(lowered):
            if idx == other_idx:
                continue
            if len(other) <= len(token):
                continue
            if len(other) - len(token) > max_extra_chars:
                continue
            if other.startswith(token):
                dropped.add(idx)
                break
    return [term for idx, term in enumerate(terms) if idx not in dropped]


def _derive_order_tokens_from_anchors(anchors: list[str]) -> list[str]:
    ordered_tokens: list[str] = []
    seen: set[str] = set()
    for phrase in anchors:
        for token in _tokenise_phrase(phrase):
            canonical = _canonical_probe_token(token)
            if canonical in seen:
                continue
            if token.isdigit():
                continue
            if not re.search(r"[a-z]", token):
                continue
            if len(token) < EXPLORATORY_MIN_TOKEN_LEN:
                continue
            if token in EXPLORATORY_STOPWORDS:
                continue
            seen.add(canonical)
            ordered_tokens.append(token)
    collapsed = _drop_prefix_stem_terms(ordered_tokens)
    return collapsed[:EXPLORATORY_ORDER_MAX_TERMS]


def _derive_order_tokens_from_text(
    text: str,
    *,
    preferred_tokens: set[str] | None = None,
) -> list[str]:
    if not text.strip():
        return []

    ordered_tokens: list[str] = []
    token_first_index: dict[str, int] = {}
    seen: set[str] = set()
    for token in _tokenise_phrase(text):
        canonical = _canonical_probe_token(token)
        if canonical in seen:
            continue
        if token.isdigit():
            continue
        if not re.search(r"[a-z]", token):
            continue
        if len(token) < EXPLORATORY_MIN_TOKEN_LEN:
            continue
        if token in EXPLORATORY_STOPWORDS:
            continue
        seen.add(canonical)
        token_first_index[token] = len(ordered_tokens)
        ordered_tokens.append(token)

    if preferred_tokens:
        preferred = [tok for tok in ordered_tokens if _canonical_probe_token(tok) in preferred_tokens]
        collapsed_preferred = _drop_prefix_stem_terms(preferred)
        if len(collapsed_preferred) >= 3:
            # Heading tokens at the very start are often less stable across OCR
            # variants; prefer later preferred anchors when available.
            late_preferred = [
                tok for tok in collapsed_preferred if int(token_first_index.get(tok, 999)) >= 2
            ]
            collapsed_late_preferred = _drop_prefix_stem_terms(late_preferred)
            if len(collapsed_late_preferred) >= 2:
                return collapsed_late_preferred[:EXPLORATORY_ORDER_MAX_TERMS]
        if len(collapsed_preferred) >= 2:
            return collapsed_preferred[:EXPLORATORY_ORDER_MAX_TERMS]

    collapsed = _drop_prefix_stem_terms(ordered_tokens)
    return collapsed[:EXPLORATORY_ORDER_MAX_TERMS]


def _derive_anchor_any_terms(anchors: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for phrase in anchors:
        raw = " ".join(str(phrase).split()).strip()
        if not raw:
            continue
        raw_lower = raw.lower()
        tokens = _tokenise_phrase(raw)
        if not tokens:
            continue
        if len(tokens) == 1:
            token = tokens[0]
            canonical = _canonical_probe_token(token)
            if token.isdigit():
                continue
            if len(token) < EXPLORATORY_MIN_TOKEN_LEN:
                continue
            if canonical in EXPLORATORY_STOPWORDS:
                continue
            if canonical in seen:
                continue
            seen.add(canonical)
            out.append(raw)
            continue

        # Multi-token phrase: keep if it includes meaningful lexical content.
        meaningful_tokens = [
            token
            for token in tokens
            if re.search(r"[a-z]", token)
            and len(token) >= EXPLORATORY_MIN_TOKEN_LEN
            and _canonical_probe_token(token) not in EXPLORATORY_STOPWORDS
        ]
        if len(meaningful_tokens) < 2:
            continue
        phrase_key = f"phrase:{raw_lower}"
        if phrase_key in seen:
            continue
        seen.add(phrase_key)
        out.append(raw)
    single_token_terms: list[str] = []
    multi_token_terms: set[str] = set()
    for term in out:
        tokenised = _tokenise_phrase(term)
        if len(tokenised) == 1:
            single_token_terms.append(term)
        else:
            multi_token_terms.add(term.lower())

    collapsed_single_terms = _drop_prefix_stem_terms(single_token_terms)
    collapsed_single_set = {item.lower() for item in collapsed_single_terms}

    filtered: list[str] = []
    for term in out:
        tokenised = _tokenise_phrase(term)
        if len(tokenised) == 1:
            if term.lower() in collapsed_single_set:
                filtered.append(term)
            continue
        if term.lower() in multi_token_terms:
            filtered.append(term)
    return filtered


def _text_token_pool(text: str) -> set[str]:
    return {
        _canonical_probe_token(token)
        for token in _tokenise_phrase(text)
        if re.search(r"[a-z]", token) and len(token) >= 3
    }


def _term_supported_by_text(
    *,
    term: str,
    text: str,
    text_token_pool: set[str],
) -> bool:
    term_norm = " ".join(str(term).split()).strip().lower()
    if not term_norm:
        return False
    text_norm = " ".join(str(text).split()).strip().lower()
    if term_norm and term_norm in text_norm:
        return True

    canonical_tokens = [
        _canonical_probe_token(token)
        for token in _tokenise_phrase(term_norm)
        if re.search(r"[a-z]", token) and len(token) >= 3
    ]
    if not canonical_tokens:
        return False

    overlap = sum(1 for token in canonical_tokens if token in text_token_pool)
    if len(canonical_tokens) == 1:
        return overlap >= 1
    return overlap >= 2


def _filter_terms_to_text_support(*, terms: list[str], text: str) -> list[str]:
    if not terms:
        return []
    text_tokens = _text_token_pool(text)
    if not text_tokens and not str(text).strip():
        return terms
    supported: list[str] = []
    for term in terms:
        if _term_supported_by_text(term=term, text=text, text_token_pool=text_tokens):
            supported.append(term)
    return supported


def _derive_exploratory_overrides(
    *,
    growth_case: dict[str, Any],
    run_case: dict[str, Any],
) -> dict[str, Any]:
    effective_any, effective_order = _effective_gate_terms(
        growth_case=growth_case,
        run_case=run_case,
    )
    anchor_token_pool = {
        _canonical_probe_token(token)
        for token in _tokenise_phrase(" ".join(effective_any))
        if len(token) >= EXPLORATORY_MIN_TOKEN_LEN
    }
    run_extracted_text = str(run_case.get("extracted_text", "") or "")
    selected_order = _derive_order_tokens_from_text(
        run_extracted_text,
        preferred_tokens=anchor_token_pool or None,
    )
    if len(selected_order) < 2:
        # Prefer known case order before anchor-guess order to avoid
        # introducing new head-token failures when OCR text is terse.
        if run_extracted_text.strip() and len(effective_order) >= 2:
            selected_order = effective_order[:EXPLORATORY_ORDER_MAX_TERMS]
    if len(selected_order) < 2:
        selected_order = _derive_order_tokens_from_anchors(effective_any)
    if len(selected_order) < 2 and len(effective_order) >= 2:
        # Keep source order only as fallback; inherited order chains can be
        # stale and create impossible sequence checks in exploratory replay.
        selected_order = effective_order[:EXPLORATORY_ORDER_MAX_TERMS]
    elif len(selected_order) < 2:
        unique_tokens: list[str] = []
        seen_tokens: set[str] = set()
        for token in sorted(
            {
                token
                for token in _tokenise_phrase(" ".join(effective_order))
                if len(token) >= EXPLORATORY_MIN_TOKEN_LEN
            },
            key=len,
            reverse=True,
        ):
            canonical = _canonical_probe_token(token)
            if canonical in seen_tokens:
                continue
            seen_tokens.add(canonical)
            unique_tokens.append(token)
        selected_order = unique_tokens[:EXPLORATORY_ORDER_MAX_TERMS]
    if len(selected_order) > EXPLORATORY_ORDER_MAX_TERMS:
        selected_order = selected_order[:EXPLORATORY_ORDER_MAX_TERMS]
    if run_extracted_text.strip():
        selected_order = _filter_terms_to_text_support(terms=selected_order, text=run_extracted_text)

    overrides: dict[str, Any] = {}
    if len(selected_order) >= 2:
        overrides["must_appear_in_order"] = selected_order

    if effective_any:
        refined_any = _derive_anchor_any_terms(effective_any)
        if run_extracted_text.strip():
            refined_any = _filter_terms_to_text_support(terms=refined_any, text=run_extracted_text)
        if refined_any:
            overrides["must_contain_any"] = refined_any[:8]

    try:
        base_min_chars = int(run_case.get("min_chars") or growth_case.get("min_chars") or 0)
    except (TypeError, ValueError):
        base_min_chars = 0
    if base_min_chars > 0:
        overrides["min_chars"] = max(base_min_chars, int(round(base_min_chars * 1.15)), 12)
    elif selected_order:
        overrides["min_chars"] = max(10, sum(len(term) for term in selected_order))
    return overrides


def _lane_sort_key(lane: str) -> tuple[int, str]:
    try:
        return (EXPLORATORY_LANE_ORDER.index(lane), lane)
    except ValueError:
        return (len(EXPLORATORY_LANE_ORDER), lane)


def _select_exploratory_rows_balanced(
    *,
    exploratory_candidates: list[tuple[int, dict[str, Any]]],
    max_cases: int,
) -> list[dict[str, Any]]:
    if max_cases <= 0 or not exploratory_candidates:
        return []

    lanes: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    for score, row in exploratory_candidates:
        lane = str(row.get("lane", "unknown")).strip() or "unknown"
        lanes.setdefault(lane, []).append((score, row))

    for queue in lanes.values():
        queue.sort(key=lambda item: (-item[0], str(item[1].get("id", ""))))

    lane_order = sorted(lanes.keys(), key=_lane_sort_key)
    selected: list[dict[str, Any]] = []
    while len(selected) < max_cases:
        progressed = False
        for lane in lane_order:
            queue = lanes.get(lane, [])
            if not queue:
                continue
            _score, row = queue.pop(0)
            selected.append(row)
            progressed = True
            if len(selected) >= max_cases:
                break
        if not progressed:
            break
    return selected


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
    include_exploratory: bool = False,
    exploratory_max_cases: int = 0,
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
    exploratory_cases: list[dict[str, Any]] = []
    rate_limited_cases: list[dict[str, Any]] = []
    lane_counts: Counter[str] = Counter()
    fail_history_lane_counts: Counter[str] = Counter()
    exploratory_lane_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    reason_pattern_counts: Counter[str] = Counter()
    non_actionable_reason_counts: Counter[str] = Counter()
    skipped_non_framed = 0
    skipped_non_actionable = 0
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

        non_actionable_reason = _non_actionable_skip_reason(
            row=row,
            sample_reasons=sample_reasons,
        )
        if non_actionable_reason:
            skipped_non_actionable += 1
            non_actionable_reason_counts[non_actionable_reason] += 1
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

    if include_exploratory and exploratory_max_cases > 0:
        lane_priority = {"handwriting": 3, "illustration": 2, "typed": 1}
        exploratory_candidates: list[tuple[int, dict[str, Any]]] = []
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
            if observed_runs < min_runs:
                continue
            if pass_runs <= 0 or fail_runs > 0 or error_runs > 0:
                continue
            growth_case = growth_case_map.get(case_id, {})
            run_case = run_case_map.get(case_id, {})
            lane = str(growth_case.get("lane", "unknown")).strip() or "unknown"
            if lane == "unknown":
                continue
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
            if require_ocr_framing and framing_episode_count <= 0:
                continue

            overrides = _derive_exploratory_overrides(
                growth_case=growth_case,
                run_case=run_case,
            )
            # Keep exploratory probes actionable: they need at least a 2-token
            # ordered gate so we can intentionally stress OCR sequence quality.
            ordered_terms = _string_list(overrides.get("must_appear_in_order"))
            if len(ordered_terms) < 2:
                continue
            effective_must_any, effective_must_order = _effective_gate_terms(
                growth_case=growth_case,
                run_case=run_case,
            )
            gate_probe_summary = _format_gate_probe(effective_must_any, effective_must_order)
            score = (
                lane_priority.get(lane, 0) * 1_000_000
                + int(row.get("text_variant_count", 0) or 0) * 10_000
                + int(row.get("char_count_span", 0) or 0) * 100
                + len(ordered_terms) * 10
                + min(len(" ".join(ordered_terms)), 9)
            )
            exploratory_candidates.append(
                (
                    score,
                    {
                        "id": case_id,
                        "lane": lane,
                        "source_name": source_name,
                        "image_path": image_path,
                        "observed_runs": observed_runs,
                        "pass_runs": pass_runs,
                        "fail_runs": fail_runs,
                        "error_runs": error_runs,
                        "pass_rate": float(row.get("pass_rate", 0.0) or 0.0),
                        "decision_stable": bool(row.get("decision_stable", False)),
                        "always_fail": bool(row.get("always_fail", False)),
                        "primary_failure_pattern": "exploratory_stress_probe",
                        "failure_patterns": ["exploratory_stress_probe"],
                        "text_variant_count": int(row.get("text_variant_count", 0) or 0),
                        "char_count_span": int(row.get("char_count_span", 0) or 0),
                        "effective_must_contain_any": effective_must_any,
                        "effective_must_appear_in_order": effective_must_order,
                        "gate_probe_summary": gate_probe_summary,
                        "focus_overrides": overrides,
                        "exploratory_reason": "strict_replay_from_stable_pass_only",
                        "review_episode_count": len(linked_review_rows),
                        "framing_episode_count": framing_episode_count,
                    },
                )
            )

        for row in _select_exploratory_rows_balanced(
            exploratory_candidates=exploratory_candidates,
            max_cases=exploratory_max_cases,
        ):
            exploratory_cases.append(row)
            exploratory_lane_counts[str(row.get("lane", "unknown"))] += 1

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
    exploratory_cases.sort(key=lambda item: (str(item.get("lane", "")), str(item.get("id", ""))))
    rate_limited_cases.sort(key=lambda item: (item["lane"], item["id"]))

    summary = {
        "cases_total": len(raw_cases),
        "stability_cases_total": stability_cases_total,
        "metrics_rows_added": metrics_rows_added,
        "selected_fail_cases": len(selected),
        "fail_history_cases": len(fail_history_cases),
        "exploratory_cases": len(exploratory_cases),
        "fail_to_pass_cases": fail_to_pass_cases,
        "rate_limited_cases": len(rate_limited_cases),
        "rate_limit_abort_runs": rate_limit_abort_runs,
        "min_runs": min_runs,
        "include_unstable": include_unstable,
        "require_ocr_framing": require_ocr_framing,
        "include_exploratory": include_exploratory,
        "exploratory_max_cases": exploratory_max_cases,
        "skipped_non_framed": skipped_non_framed,
        "skipped_non_actionable": skipped_non_actionable,
        "skipped_case_map_mismatch": skipped_case_map_mismatch,
        "lane_counts": dict(sorted(lane_counts.items())),
        "fail_history_lane_counts": dict(sorted(fail_history_lane_counts.items())),
        "exploratory_lane_counts": dict(sorted(exploratory_lane_counts.items())),
        "non_actionable_reason_counts": dict(sorted(non_actionable_reason_counts.items())),
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
        "exploratory_cases": exploratory_cases,
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
    exploratory_cases = (
        report.get("exploratory_cases")
        if isinstance(report.get("exploratory_cases"), list)
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
    lines.append(f"| exploratory_cases | {summary['exploratory_cases']} |")
    lines.append(f"| fail_to_pass_cases | {summary['fail_to_pass_cases']} |")
    lines.append(f"| rate_limited_cases | {summary['rate_limited_cases']} |")
    lines.append(f"| rate_limit_abort_runs | {summary['rate_limit_abort_runs']} |")
    lines.append(f"| min_runs | {summary['min_runs']} |")
    lines.append(f"| include_unstable | {summary['include_unstable']} |")
    lines.append(f"| require_ocr_framing | {summary['require_ocr_framing']} |")
    lines.append(f"| include_exploratory | {summary['include_exploratory']} |")
    lines.append(f"| exploratory_max_cases | {summary['exploratory_max_cases']} |")
    lines.append(f"| skipped_non_framed | {summary['skipped_non_framed']} |")
    lines.append(f"| skipped_non_actionable | {summary['skipped_non_actionable']} |")
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

    exploratory_lane_counts = summary.get("exploratory_lane_counts")
    if isinstance(exploratory_lane_counts, dict) and exploratory_lane_counts:
        lines.append("## Exploratory Lane Counts")
        lines.append("")
        lines.append("| lane | exploratory_cases |")
        lines.append("|---|---:|")
        for lane, count in exploratory_lane_counts.items():
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

    non_actionable_reason_counts = summary.get("non_actionable_reason_counts")
    if isinstance(non_actionable_reason_counts, dict) and non_actionable_reason_counts:
        lines.append("## Non-Actionable Skip Reasons")
        lines.append("")
        lines.append("| reason | count |")
        lines.append("|---|---:|")
        for reason, count in non_actionable_reason_counts.items():
            lines.append(f"| {reason} | {int(count)} |")
        lines.append("")

    if selected:
        lines.append("## Selected Cases")
        lines.append("")

    if exploratory_cases:
        lines.append("## Exploratory Cases (Strict Replay of Stable PASS Cases)")
        lines.append("")
        lines.append(
            "| case_id | lane | gate_probe | focus_override_order | focus_override_min_chars | observed_runs | source_name | image_path |"
        )
        lines.append("|---|---|---|---|---:|---:|---|---|")
        for row in exploratory_cases:
            case_id = str(row.get("id", ""))
            lane = str(row.get("lane", ""))
            gate_probe = str(row.get("gate_probe_summary", "-")).replace("|", "\\|")
            focus_overrides = row.get("focus_overrides") if isinstance(row.get("focus_overrides"), dict) else {}
            order_override = _preview_terms(_string_list(focus_overrides.get("must_appear_in_order")), limit=4)
            min_chars_override = int(focus_overrides.get("min_chars", 0) or 0)
            observed = int(row.get("observed_runs", 0) or 0)
            source_name = str(row.get("source_name", "")).replace("|", "\\|")
            image_path = str(row.get("image_path", "")).replace("|", "\\|")
            lines.append(
                f"| {case_id} | {lane} | {gate_probe} | {order_override} | {min_chars_override} | {observed} | {source_name} | {image_path} |"
            )
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
    parser.add_argument(
        "--include-exploratory",
        action="store_true",
        help="Include strict replay exploratory cases when fail history is sparse.",
    )
    parser.add_argument(
        "--exploratory-max-cases",
        type=int,
        default=12,
        help="Maximum exploratory cases to emit when --include-exploratory is set.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.min_runs < 1:
        print("min-runs must be >= 1")
        return 2
    if args.exploratory_max_cases < 0:
        print("exploratory-max-cases must be >= 0")
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
        include_exploratory=bool(args.include_exploratory),
        exploratory_max_cases=int(args.exploratory_max_cases),
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
    print(f"  exploratory_cases: {summary['exploratory_cases']}")
    print(f"  fail_to_pass_cases: {summary['fail_to_pass_cases']}")
    print(f"  rate_limited_cases: {summary['rate_limited_cases']}")
    print(f"  rate_limit_abort_runs: {summary['rate_limit_abort_runs']}")
    print(f"  cases_total: {summary['cases_total']}")
    print(f"  min_runs: {summary['min_runs']}")
    print(f"  include_unstable: {summary['include_unstable']}")
    print(f"  require_ocr_framing: {summary['require_ocr_framing']}")
    print(f"  include_exploratory: {summary['include_exploratory']}")
    print(f"  exploratory_max_cases: {summary['exploratory_max_cases']}")
    print(f"  skipped_non_framed: {summary['skipped_non_framed']}")
    print(f"  skipped_non_actionable: {summary['skipped_non_actionable']}")
    print(f"  skipped_case_map_mismatch: {summary['skipped_case_map_mismatch']}")
    print(f"  json: {output_json}")
    print(f"  markdown: {output_markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
