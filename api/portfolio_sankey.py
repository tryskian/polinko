from __future__ import annotations

import json
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from api.eval_viz import build_pass_fail_viz_payload

_MANUAL_EVALS_DB_PATH = Path(".local/runtime_dbs/active/manual_evals.db")
_BINARY_GATE_REPORT_ROOT = Path(".local/eval_reports")

_OUTCOME_LABELS = {
    "PASS": "Pass",
    "PARTIAL": "Partial",
    "FAIL": "Fail",
    "ERROR": "Error",
    "OTHER": "Other",
}

_SIGNAL_LABELS = {
    "ocr_signal": "OCR signal",
    "grounding": "Grounding",
    "hallucination_risk": "Hallucination risk",
    "style_voice": "Style and voice",
    "recovery": "Recovery",
    "correctness": "Correctness",
    "general_eval": "General eval",
}

_LANE_LABELS = {
    "text": "Text",
    "typed": "Text",
    "handwriting": "Handwriting",
    "illustration": "Illustration",
    "other": "Other",
}

_BRIDGE_OCR_LANES = ("text", "handwriting", "illustration")


def _empty_graph(graph_id: str, label: str) -> dict[str, Any]:
    return {
        "id": graph_id,
        "label": label,
        "nodes": [],
        "links": [],
    }


def _empty_payload(*, manual_db_path: Path, report_root: Path, reason: str) -> dict[str, Any]:
    return {
        "available": False,
        "mode": "no_data",
        "source_integrity": "real_data_only",
        "updated_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reason": reason,
        "summary": {
            "legacy_feedback_rows": 0,
            "legacy_signal_mentions": 0,
            "current_binary_cases": 0,
            "current_binary_reports": 0,
            "bridge_categories": 0,
        },
        "sources": {
            "legacy": {
                "kind": "manual_evals_db",
                "path": str(manual_db_path),
                "era": "beta_1_0",
                "available": False,
            },
            "current": {
                "kind": "binary_gate_reports",
                "path": str(report_root),
                "era": "current",
                "available": False,
            },
        },
        "graphs": {
            "legacy": _empty_graph("legacy", "Beta 1.0 manual evals"),
            "bridge": _empty_graph("bridge", "Signal bridge"),
            "current": _empty_graph("current", "Current OCR binary gates"),
        },
        "notes": [
            "Twin Sankey refuses decorative fallback data.",
            reason,
        ],
    }


def _safe_count(conn: sqlite3.Connection, table_name: str, *, era: str | None = None) -> int:
    try:
        if era is None:
            row = conn.execute(f"SELECT COUNT(*) AS c FROM {table_name}").fetchone()
        else:
            row = conn.execute(
                f"SELECT COUNT(*) AS c FROM {table_name} WHERE era = ?",
                (era,),
            ).fetchone()
    except sqlite3.Error:
        return 0
    return int(row["c"] or 0) if row is not None else 0


def _normalize_outcome(value: Any) -> str:
    raw = str(value or "").strip().upper()
    if raw in {"PASS", "PASSED", "SUCCESS", "OK"}:
        return "PASS"
    if raw in {"FAIL", "FAILED"}:
        return "FAIL"
    if raw in {"PARTIAL", "MIXED", "WARN", "WARNING"}:
        return "PARTIAL"
    if raw in {"ERROR", "ERR"}:
        return "ERROR"
    return "OTHER"


def _tags_from_json(value: Any) -> list[str]:
    try:
        parsed = json.loads(str(value or ""))
    except json.JSONDecodeError:
        return []

    raw_tags: list[Any] = []
    if isinstance(parsed, dict):
        for key in ("all", "negative", "positive"):
            maybe_tags = parsed.get(key)
            if isinstance(maybe_tags, list):
                raw_tags.extend(maybe_tags)
    elif isinstance(parsed, list):
        raw_tags.extend(parsed)

    tags: list[str] = []
    seen: set[str] = set()
    for raw_tag in raw_tags:
        tag = str(raw_tag or "").strip().lower()
        if not tag or tag in seen:
            continue
        seen.add(tag)
        tags.append(tag)
    return tags


def _signal_category(tag: str) -> str:
    normalized = tag.strip().lower().replace("-", "_")
    if "ocr" in normalized:
        return "ocr_signal"
    if "ground" in normalized or "evidence" in normalized:
        return "grounding"
    if "halluc" in normalized or "confab" in normalized or "fact" in normalized:
        return "hallucination_risk"
    if "style" in normalized or "voice" in normalized or "tone" in normalized or "whims" in normalized:
        return "style_voice"
    if "retry" in normalized or "recover" in normalized:
        return "recovery"
    if "accurate" in normalized or "complete" in normalized or "useful" in normalized:
        return "correctness"
    return "general_eval"


def _legacy_manual_eval_surface(db_path: Path) -> dict[str, Any]:
    if not db_path.is_file():
        return {
            "available": False,
            "sessions": 0,
            "ocr_runs": 0,
            "feedback_rows": 0,
            "signal_mentions": 0,
            "outcome_counts": {},
            "signal_counts": {},
            "outcome_signal_counts": {},
        }

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.Error:
        return {
            "available": False,
            "sessions": 0,
            "ocr_runs": 0,
            "feedback_rows": 0,
            "signal_mentions": 0,
            "outcome_counts": {},
            "signal_counts": {},
            "outcome_signal_counts": {},
        }

    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT outcome, tags_json, note, recommended_action, action_taken
            FROM feedback
            WHERE era = 'beta_1_0'
            ORDER BY created_at ASC, id ASC
            """
        ).fetchall()
    except sqlite3.Error:
        rows = []

    outcome_counts: Counter[str] = Counter()
    signal_counts: Counter[str] = Counter()
    outcome_signal_counts: Counter[tuple[str, str]] = Counter()

    for row in rows:
        outcome = _normalize_outcome(row["outcome"])
        outcome_counts[outcome] += 1

        categories = sorted({_signal_category(tag) for tag in _tags_from_json(row["tags_json"])})
        if not categories:
            categories = ["general_eval"]

        for category in categories:
            signal_counts[category] += 1
            outcome_signal_counts[(outcome, category)] += 1

    sessions = _safe_count(conn, "sessions", era="beta_1_0")
    ocr_runs = _safe_count(conn, "ocr_runs", era="beta_1_0")
    conn.close()

    return {
        "available": bool(rows),
        "sessions": sessions,
        "ocr_runs": ocr_runs,
        "feedback_rows": len(rows),
        "signal_mentions": sum(signal_counts.values()),
        "outcome_counts": dict(outcome_counts),
        "signal_counts": dict(signal_counts),
        "outcome_signal_counts": {
            f"{outcome}:{signal}": count
            for (outcome, signal), count in outcome_signal_counts.items()
        },
    }


def _current_binary_gate_surface(report_root: Path, *, max_reports: int) -> dict[str, Any]:
    payload = build_pass_fail_viz_payload(
        report_root=report_root,
        max_evals=50_000,
        max_history_runs=max(1, max_reports),
    )
    points = payload.get("points", [])
    rows = payload.get("evals", [])
    if not isinstance(points, list) or not isinstance(rows, list) or not points:
        return {
            "available": False,
            "binary_reports": 0,
            "binary_cases": 0,
            "outcome_counts": {},
            "lane_counts": {},
            "lane_outcome_counts": {},
            "updated_at": payload.get("updated_at", ""),
        }

    outcome_counts: Counter[str] = Counter()
    lane_counts: Counter[str] = Counter()
    lane_outcome_counts: Counter[tuple[str, str]] = Counter()

    for row in rows:
        if not isinstance(row, dict):
            continue
        outcome = _normalize_outcome(row.get("outcome"))
        lane = str(row.get("lane") or row.get("source_name") or "other").strip().lower() or "other"
        if lane == "typed":
            lane = "text"
        if lane not in {"text", "handwriting", "illustration"}:
            lane = "other"
        outcome_counts[outcome] += 1
        lane_counts[lane] += 1
        lane_outcome_counts[(lane, outcome)] += 1

    return {
        "available": bool(lane_outcome_counts),
        "binary_reports": len(points),
        "binary_cases": sum(outcome_counts.values()),
        "outcome_counts": dict(outcome_counts),
        "lane_counts": dict(lane_counts),
        "lane_outcome_counts": {
            f"{lane}:{outcome}": count
            for (lane, outcome), count in lane_outcome_counts.items()
        },
        "updated_at": str(payload.get("updated_at") or ""),
    }


def _node(node_id: str, label: str, group: str) -> dict[str, str]:
    return {
        "id": node_id,
        "label": label,
        "group": group,
    }


def _link(source: str, target: str, value: int, *, kind: str, provenance: str) -> dict[str, Any]:
    return {
        "source": source,
        "target": target,
        "value": int(value),
        "kind": kind,
        "provenance": provenance,
    }


def _allocate_count_by_weights(total: int, weights: dict[str, int]) -> dict[str, int]:
    if total <= 0:
        return {}

    positive_weights = {
        key: int(weight)
        for key, weight in weights.items()
        if int(weight or 0) > 0
    }
    if not positive_weights:
        return {}

    weight_total = sum(positive_weights.values())
    raw_allocations = {
        key: (total * weight) / weight_total
        for key, weight in positive_weights.items()
    }
    allocations = {
        key: int(value)
        for key, value in raw_allocations.items()
    }
    remainder = total - sum(allocations.values())
    if remainder <= 0:
        return {key: value for key, value in allocations.items() if value > 0}

    ranked_remainders = sorted(
        raw_allocations,
        key=lambda key: (raw_allocations[key] - allocations[key], positive_weights[key], key),
        reverse=True,
    )
    for key in ranked_remainders[:remainder]:
        allocations[key] += 1

    return {key: value for key, value in allocations.items() if value > 0}


def _legacy_graph(legacy: dict[str, Any]) -> dict[str, Any]:
    nodes = [_node("legacy_manual_feedback", "Beta 1.0 manual evals", "legacy_source")]
    links: list[dict[str, Any]] = []

    outcome_signal_counts = legacy.get("outcome_signal_counts", {})
    signal_nodes: set[str] = set()
    outcome_totals: Counter[str] = Counter()

    if isinstance(outcome_signal_counts, dict):
        for key, raw_count in outcome_signal_counts.items():
            try:
                outcome, signal = str(key).split(":", 1)
            except ValueError:
                continue
            count = int(raw_count or 0)
            if count <= 0:
                continue
            outcome_totals[outcome] += count
            signal_nodes.add(signal)
            links.append(
                _link(
                    f"legacy_outcome_{outcome.lower()}",
                    f"legacy_signal_{signal}",
                    count,
                    kind="legacy_outcome_to_signal",
                    provenance="manual_evals.feedback.tags_json",
                )
            )

    for outcome, count in sorted(outcome_totals.items()):
        label = _OUTCOME_LABELS.get(outcome, outcome.title())
        nodes.append(_node(f"legacy_outcome_{outcome.lower()}", f"Manual {label}", "legacy_outcome"))
        links.append(
            _link(
                "legacy_manual_feedback",
                f"legacy_outcome_{outcome.lower()}",
                count,
                kind="legacy_feedback_to_outcome",
                provenance="manual_evals.feedback.outcome",
            )
        )

    for signal in sorted(signal_nodes):
        nodes.append(
            _node(
                f"legacy_signal_{signal}",
                _SIGNAL_LABELS.get(signal, signal.replace("_", " ").title()),
                "legacy_signal",
            )
        )

    return {
        "id": "legacy",
        "label": "Beta 1.0 manual evals",
        "nodes": nodes,
        "links": links,
        "metric": "manual feedback tag mentions",
    }


def _current_graph(current: dict[str, Any]) -> dict[str, Any]:
    nodes = [_node("current_binary_reports", "Current OCR binary gates", "current_source")]
    links: list[dict[str, Any]] = []

    lane_outcome_counts = current.get("lane_outcome_counts", {})
    outcome_nodes: set[str] = set()
    lane_totals: Counter[str] = Counter()

    if isinstance(lane_outcome_counts, dict):
        for key, raw_count in lane_outcome_counts.items():
            try:
                lane, outcome = str(key).split(":", 1)
            except ValueError:
                continue
            count = int(raw_count or 0)
            if count <= 0:
                continue
            outcome_nodes.add(outcome)
            lane_totals[lane] += count
            links.append(
                _link(
                    f"current_lane_{lane}",
                    f"current_outcome_{outcome.lower()}",
                    count,
                    kind="current_lane_to_outcome",
                    provenance="eval_reports.cases.outcome",
                )
            )

    for lane, count in sorted(lane_totals.items()):
        nodes.append(
            _node(
                f"current_lane_{lane}",
                _LANE_LABELS.get(lane, lane.replace("_", " ").title()),
                "current_lane",
            )
        )
        links.append(
            _link(
                "current_binary_reports",
                f"current_lane_{lane}",
                count,
                kind="current_report_to_lane",
                provenance="eval_reports.cases.lane",
            )
        )

    for outcome in sorted(outcome_nodes):
        label = _OUTCOME_LABELS.get(outcome, outcome.title())
        nodes.append(_node(f"current_outcome_{outcome.lower()}", f"Gate {label}", "current_outcome"))

    return {
        "id": "current",
        "label": "Current OCR binary gates",
        "nodes": nodes,
        "links": links,
        "metric": "binary gate case outcomes",
    }


def _bridge_graph(legacy: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    nodes: list[dict[str, str]] = []
    links: list[dict[str, Any]] = []

    signal_counts = legacy.get("signal_counts", {})
    lane_counts = current.get("lane_counts", {})

    if isinstance(signal_counts, dict):
        for signal, raw_count in sorted(signal_counts.items()):
            count = int(raw_count or 0)
            if count <= 0:
                continue
            node_id = f"bridge_signal_{signal}"
            nodes.append(
                _node(
                    node_id,
                    _SIGNAL_LABELS.get(signal, signal.replace("_", " ").title()),
                    "legacy_signal",
                )
            )

    if isinstance(lane_counts, dict):
        for lane, raw_count in sorted(lane_counts.items()):
            count = int(raw_count or 0)
            if count <= 0:
                continue
            node_id = f"bridge_lane_{lane}"
            nodes.append(
                _node(
                    node_id,
                    _LANE_LABELS.get(lane, lane.replace("_", " ").title()),
                    "current_lane",
                )
            )

    if isinstance(signal_counts, dict) and isinstance(lane_counts, dict):
        for signal, raw_signal_count in sorted(signal_counts.items()):
            signal_count = int(raw_signal_count or 0)
            if signal_count <= 0:
                continue
            lane_weights = {
                lane: int(lane_counts.get(lane, 0) or 0)
                for lane in _BRIDGE_OCR_LANES
            }
            for lane, count in sorted(_allocate_count_by_weights(signal_count, lane_weights).items()):
                links.append(
                    _link(
                        f"bridge_signal_{signal}",
                        f"bridge_lane_{lane}",
                        count,
                        kind="bridge_signal_to_lane",
                        provenance="manual_evals.feedback.tags_json weighted by eval_reports.cases.lane",
                    )
                )

    return {
        "id": "bridge",
        "label": "Signal bridge",
        "nodes": nodes,
        "links": links,
        "metric": "legacy signal counts proportionally allocated by current OCR lane counts; no row-level join implied",
    }


def build_portfolio_sankey_payload(
    *,
    manual_db_path: Path | None = None,
    report_root: Path | None = None,
    max_reports: int = 120,
) -> dict[str, Any]:
    target_manual_db = manual_db_path if manual_db_path is not None else _MANUAL_EVALS_DB_PATH
    target_report_root = report_root if report_root is not None else _BINARY_GATE_REPORT_ROOT

    legacy = _legacy_manual_eval_surface(target_manual_db)
    current = _current_binary_gate_surface(target_report_root, max_reports=max_reports)

    if not legacy["available"] or not current["available"]:
        missing = []
        if not legacy["available"]:
            missing.append("Beta 1.0 manual feedback")
        if not current["available"]:
            missing.append("current OCR binary gate reports")
        return _empty_payload(
            manual_db_path=target_manual_db,
            report_root=target_report_root,
            reason="Missing required real data: " + ", ".join(missing),
        )

    updated_at = current.get("updated_at") or datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "available": True,
        "mode": "real_data",
        "source_integrity": "real_data_only",
        "updated_at": updated_at,
        "reason": "",
        "summary": {
            "legacy_feedback_rows": int(legacy["feedback_rows"]),
            "legacy_signal_mentions": int(legacy["signal_mentions"]),
            "legacy_sessions": int(legacy["sessions"]),
            "legacy_ocr_runs": int(legacy["ocr_runs"]),
            "current_binary_cases": int(current["binary_cases"]),
            "current_binary_reports": int(current["binary_reports"]),
            "bridge_categories": len(legacy["signal_counts"]),
        },
        "sources": {
            "legacy": {
                "kind": "manual_evals_db",
                "path": str(target_manual_db),
                "era": "beta_1_0",
                "available": True,
                "feedback_rows": int(legacy["feedback_rows"]),
                "ocr_runs": int(legacy["ocr_runs"]),
                "outcome_counts": legacy["outcome_counts"],
                "signal_counts": legacy["signal_counts"],
            },
            "current": {
                "kind": "binary_gate_reports",
                "path": str(target_report_root),
                "era": "current",
                "available": True,
                "binary_reports": int(current["binary_reports"]),
                "binary_cases": int(current["binary_cases"]),
                "outcome_counts": current["outcome_counts"],
                "lane_counts": current["lane_counts"],
            },
        },
        "graphs": {
            "legacy": _legacy_graph(legacy),
            "bridge": _bridge_graph(legacy, current),
            "current": _current_graph(current),
        },
        "notes": [
            "All graph values are derived from local manual eval rows or local OCR binary gate reports.",
            "The bridge carries legacy signal-family counts forward by current OCR lane proportions; it is not a row-level join.",
        ],
    }
