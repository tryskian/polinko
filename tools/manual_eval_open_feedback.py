from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from contextlib import closing
from pathlib import Path
from typing import Any


ACTIONABLES_SCHEMA_VERSION = "polinko.manual_eval_feedback_actionables.v1"
COHORTS_SCHEMA_VERSION = "polinko.manual_eval_feedback_cohorts.v1"

COHORT_DESCRIPTIONS = {
    "ocr_retry_evidence": "Retry OCR/crop and attach fresh image evidence.",
    "ocr_overlay_hypothesis": (
        "Review overlay-assisted OCR hypothesis evidence before rerunning OCR."
    ),
    "grounding_source_verification": (
        "Re-run with grounding constraints and verify against source evidence."
    ),
    "expected_output_regression": (
        "Rerun exact prompt against expected output and record mismatch."
    ),
    "instruction_following_regression": (
        "Rerun exact prompt with instruction-following constraints."
    ),
    "style_regression": "Adjust style notes and add style regression coverage.",
    "other_explicit_action": "Explicit recommended action outside known cohorts.",
    "missing_recommended_action": "Open feedback row has no recommended action.",
}
COHORT_IDS = tuple(COHORT_DESCRIPTIONS)
COHORT_FILTER_CHOICES = ("all", *COHORT_IDS)


def _connect_readonly(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _int_value(value: object) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return 0
        return int(value)
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def _row_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def _fetch_rows(
    conn: sqlite3.Connection,
    sql: str,
    params: Sequence[object] = (),
) -> list[dict[str, Any]]:
    return [_row_dict(row) for row in conn.execute(sql, params).fetchall()]


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def _display_text(value: object) -> str:
    text = normalize_text(value)
    return text if text else "none"


def parse_tags(value: object) -> list[str]:
    if value is None:
        return []
    try:
        parsed = json.loads(str(value))
    except json.JSONDecodeError:
        return []
    if isinstance(parsed, dict):
        all_tags = parsed.get("all")
        if isinstance(all_tags, list):
            return [str(item) for item in all_tags if str(item).strip()]
        tags: list[str] = []
        for key in ("positive", "negative"):
            value = parsed.get(key)
            if isinstance(value, list):
                tags.extend(str(item) for item in value if str(item).strip())
        return list(dict.fromkeys(tags))
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed if str(item).strip()]


def feedback_action_cohort(recommended_action: object) -> str:
    action = normalize_text(recommended_action).lower()
    if not action:
        return "missing_recommended_action"
    if (
        "overlay-assisted" in action
        or "overlay hypothesis" in action
        or "overlay/source image" in action
        or "seed missing" in action
        or "source context" in action
    ):
        return "ocr_overlay_hypothesis"
    if (
        "retry ocr" in action
        or "tighter crop" in action
        or "fresh image evidence" in action
    ):
        return "ocr_retry_evidence"
    if "grounding constraints" in action or "source evidence" in action:
        return "grounding_source_verification"
    if "expected-output" in action or "expected output" in action:
        return "expected_output_regression"
    if "instruction-following" in action or "no interpretation" in action:
        return "instruction_following_regression"
    if (
        "style notes" in action
        or "style eval regression" in action
        or "style regression" in action
    ):
        return "style_regression"
    return "other_explicit_action"


def normalize_cohort_filter(cohort: str | None) -> str | None:
    if cohort is None:
        return None
    cohort_id = cohort.strip().lower()
    if not cohort_id or cohort_id == "all":
        return None
    if cohort_id not in COHORT_DESCRIPTIONS:
        valid = ", ".join(COHORT_IDS)
        raise ValueError(f"unknown feedback cohort '{cohort_id}' (expected: {valid})")
    return cohort_id


def normalize_outcome_filter(outcome: str | None) -> str | None:
    if outcome is None:
        return None
    outcome_filter = outcome.strip().lower()
    if not outcome_filter or outcome_filter == "all":
        return None
    return outcome_filter


def _open_feedback_where_clause(outcome: str | None) -> tuple[str, list[str]]:
    conditions = ["LOWER(f.status) = 'open'"]
    params: list[str] = []
    if outcome:
        conditions.append("LOWER(f.outcome) = ?")
        params.append(outcome.strip().lower())
    return " AND ".join(conditions), params


def _open_feedback_actionables_total(
    conn: sqlite3.Connection,
    *,
    outcome: str | None,
) -> int:
    where_clause, params = _open_feedback_where_clause(outcome)
    row = conn.execute(
        f"""
        SELECT COUNT(*)
        FROM feedback f
        WHERE {where_clause}
        """,
        params,
    ).fetchone()
    return _int_value(row[0] if row is not None else 0)


def _build_open_feedback_actionable_rows(
    conn: sqlite3.Connection,
    *,
    outcome: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    where_clause, params = _open_feedback_where_clause(outcome)
    rows = _fetch_rows(
        conn,
        f"""
        SELECT
          f.id,
          f.era,
          f.source_label,
          f.source_history_db,
          f.source_session_id,
          f.session_id,
          f.message_id,
          f.outcome,
          f.tags_json,
          f.note,
          f.recommended_action,
          f.action_taken,
          f.status,
          f.created_at,
          f.updated_at,
          s.title,
          EXISTS (
            SELECT 1
            FROM ocr_runs linked
            WHERE linked.session_id = f.session_id
              AND linked.result_message_id = f.message_id
          ) AS linked_to_ocr_result,
          (
            SELECT COUNT(*)
            FROM ocr_runs same_session
            WHERE same_session.session_id = f.session_id
          ) AS same_session_ocr_runs,
          (
            SELECT latest.run_id
            FROM ocr_runs latest
            WHERE latest.session_id = f.session_id
            ORDER BY latest.created_at DESC, latest.id DESC
            LIMIT 1
          ) AS latest_same_session_ocr_run_id,
          (
            SELECT latest.source_name
            FROM ocr_runs latest
            WHERE latest.session_id = f.session_id
            ORDER BY latest.created_at DESC, latest.id DESC
            LIMIT 1
          ) AS latest_same_session_ocr_source_name,
          (
            SELECT latest.status
            FROM ocr_runs latest
            WHERE latest.session_id = f.session_id
            ORDER BY latest.created_at DESC, latest.id DESC
            LIMIT 1
          ) AS latest_same_session_ocr_status
        FROM feedback f
        JOIN sessions s ON s.session_id = f.session_id
        WHERE {where_clause}
        ORDER BY
          f.era,
          CASE LOWER(f.outcome)
            WHEN 'fail' THEN 0
            WHEN 'partial' THEN 1
            ELSE 2
          END,
          f.updated_at DESC,
          f.id DESC
        LIMIT ?
        """,
        [*params, str(max(1, limit))],
    )
    actionable_rows: list[dict[str, Any]] = []
    for row in rows:
        note = normalize_text(row.get("note"))
        recommended_action = normalize_text(row.get("recommended_action"))
        action_taken = normalize_text(row.get("action_taken"))
        cohort_id = feedback_action_cohort(recommended_action)
        same_session_ocr_runs = _int_value(row.get("same_session_ocr_runs"))
        actionable_rows.append(
            {
                "feedback_id": _int_value(row.get("id")),
                "era": str(row.get("era") or ""),
                "source_label": str(row.get("source_label") or ""),
                "source_history_db": str(row.get("source_history_db") or ""),
                "source_session_id": str(row.get("source_session_id") or ""),
                "session_id": str(row.get("session_id") or ""),
                "message_id": str(row.get("message_id") or ""),
                "title": normalize_text(row.get("title")),
                "outcome": str(row.get("outcome") or "").lower(),
                "status": str(row.get("status") or "").lower(),
                "tags": parse_tags(row.get("tags_json")),
                "note": note,
                "recommended_action": recommended_action,
                "action_taken": action_taken,
                "has_note": bool(note),
                "has_recommended_action": bool(recommended_action),
                "has_action_taken": bool(action_taken),
                "created_at": _int_value(row.get("created_at")),
                "updated_at": _int_value(row.get("updated_at")),
                "action_cohort": {
                    "id": cohort_id,
                    "description": COHORT_DESCRIPTIONS[cohort_id],
                },
                "ocr_context": {
                    "linked_to_ocr_result": bool(
                        _int_value(row.get("linked_to_ocr_result"))
                    ),
                    "same_session_ocr_runs": same_session_ocr_runs,
                    "latest_same_session_ocr": {
                        "run_id": str(row.get("latest_same_session_ocr_run_id") or ""),
                        "source_name": str(
                            row.get("latest_same_session_ocr_source_name") or ""
                        ),
                        "status": str(row.get("latest_same_session_ocr_status") or ""),
                    },
                },
            }
        )
    return actionable_rows


def _filter_actionable_rows_by_cohort(
    rows: Sequence[dict[str, Any]],
    *,
    cohort: str | None,
) -> list[dict[str, Any]]:
    if cohort is None:
        return list(rows)
    filtered_rows: list[dict[str, Any]] = []
    for row in rows:
        action_cohort = row.get("action_cohort")
        if not isinstance(action_cohort, dict):
            action_cohort = {}
        if action_cohort.get("id") == cohort:
            filtered_rows.append(row)
    return filtered_rows


def build_filtered_open_feedback_actionable_rows(
    conn: sqlite3.Connection,
    *,
    outcome: str | None,
    cohort: str | None,
) -> list[dict[str, Any]]:
    total_rows = _open_feedback_actionables_total(conn, outcome=outcome)
    if total_rows <= 0:
        return []
    rows = _build_open_feedback_actionable_rows(
        conn,
        outcome=outcome,
        limit=total_rows,
    )
    return _filter_actionable_rows_by_cohort(rows, cohort=cohort)


def build_open_feedback_actionables_report(
    *,
    db_path: Path,
    outcome: str | None = None,
    cohort: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    outcome_filter = normalize_outcome_filter(outcome)
    cohort_filter = normalize_cohort_filter(cohort)
    if not db_path.is_file():
        return {
            "schema_version": ACTIONABLES_SCHEMA_VERSION,
            "state": "error",
            "manual_evals_db": {"path": str(db_path), "exists": False},
            "filters": {
                "status": "open",
                "outcome": outcome_filter or "",
                "cohort": cohort_filter or "",
                "limit": max(1, limit),
            },
            "rows": [],
            "warnings": ["manual_evals.db is not available"],
        }

    with closing(_connect_readonly(db_path)) as conn:
        integrity = str(conn.execute("PRAGMA integrity_check").fetchone()[0])
        all_rows = build_filtered_open_feedback_actionable_rows(
            conn,
            outcome=outcome_filter,
            cohort=cohort_filter,
        )
        total_rows = len(all_rows)
        rows = all_rows[: max(1, limit)]

    return {
        "schema_version": ACTIONABLES_SCHEMA_VERSION,
        "state": "ok" if integrity == "ok" else "error",
        "manual_evals_db": {
            "path": str(db_path),
            "exists": True,
            "integrity": integrity,
        },
        "filters": {
            "status": "open",
            "outcome": outcome_filter or "",
            "cohort": cohort_filter or "",
            "limit": max(1, limit),
        },
        "counts": {
            "total_rows": total_rows,
            "returned_rows": len(rows),
            "limit_applied": len(rows) < total_rows,
        },
        "rows": rows,
    }


def _new_cohort_summary(cohort_id: str) -> dict[str, Any]:
    return {
        "cohort_id": cohort_id,
        "description": COHORT_DESCRIPTIONS[cohort_id],
        "rows": 0,
        "sessions": 0,
        "outcomes": {},
        "rows_with_note": 0,
        "rows_with_recommended_action": 0,
        "rows_with_action_taken": 0,
        "linked_to_ocr_result": 0,
        "same_session_ocr": 0,
        "sample_feedback_ids": [],
        "_session_ids": set(),
    }


def _finalize_cohort_summary(summary: dict[str, Any]) -> dict[str, Any]:
    session_ids = summary.pop("_session_ids", set())
    if isinstance(session_ids, set):
        summary["sessions"] = len(session_ids)
    outcomes = summary.get("outcomes")
    if isinstance(outcomes, dict):
        summary["outcomes"] = {
            key: outcomes[key]
            for key in sorted(
                outcomes,
                key=lambda item: (
                    {"fail": 0, "partial": 1}.get(str(item), 2),
                    str(item),
                ),
            )
        }
    return summary


def _summarize_open_feedback_cohort_rows(
    actionables: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    for row in actionables:
        action_cohort = row.get("action_cohort")
        if not isinstance(action_cohort, dict):
            action_cohort = {}
        cohort_id = str(action_cohort.get("id") or "")
        if cohort_id not in COHORT_DESCRIPTIONS:
            cohort_id = feedback_action_cohort(row.get("recommended_action"))
        summary = summaries.setdefault(cohort_id, _new_cohort_summary(cohort_id))
        summary["rows"] = _int_value(summary.get("rows")) + 1
        session_ids = summary.get("_session_ids")
        if isinstance(session_ids, set):
            session_ids.add(str(row.get("session_id") or ""))
        outcome_key = str(row.get("outcome") or "unknown")
        outcomes = summary.get("outcomes")
        if isinstance(outcomes, dict):
            outcomes[outcome_key] = _int_value(outcomes.get(outcome_key)) + 1
        if row.get("has_note"):
            summary["rows_with_note"] = _int_value(summary.get("rows_with_note")) + 1
        if row.get("has_recommended_action"):
            summary["rows_with_recommended_action"] = (
                _int_value(summary.get("rows_with_recommended_action")) + 1
            )
        if row.get("has_action_taken"):
            summary["rows_with_action_taken"] = (
                _int_value(summary.get("rows_with_action_taken")) + 1
            )
        ocr_context = row.get("ocr_context")
        if not isinstance(ocr_context, dict):
            ocr_context = {}
        if ocr_context.get("linked_to_ocr_result"):
            summary["linked_to_ocr_result"] = (
                _int_value(summary.get("linked_to_ocr_result")) + 1
            )
        if _int_value(ocr_context.get("same_session_ocr_runs")) > 0:
            summary["same_session_ocr"] = (
                _int_value(summary.get("same_session_ocr")) + 1
            )
        sample_ids = summary.get("sample_feedback_ids")
        if isinstance(sample_ids, list) and len(sample_ids) < 5:
            sample_ids.append(_int_value(row.get("feedback_id")))

    finalized = [_finalize_cohort_summary(summary) for summary in summaries.values()]
    return sorted(
        finalized,
        key=lambda item: (
            -_int_value(item.get("rows")),
            str(item.get("cohort_id") or ""),
        ),
    )


def build_open_feedback_cohorts_report(
    *,
    db_path: Path,
    outcome: str | None = None,
    cohort: str | None = None,
) -> dict[str, Any]:
    outcome_filter = normalize_outcome_filter(outcome)
    cohort_filter = normalize_cohort_filter(cohort)
    if not db_path.is_file():
        return {
            "schema_version": COHORTS_SCHEMA_VERSION,
            "state": "error",
            "manual_evals_db": {"path": str(db_path), "exists": False},
            "filters": {
                "status": "open",
                "outcome": outcome_filter or "",
                "cohort": cohort_filter or "",
                "cohort_basis": "recommended_action",
            },
            "cohorts": [],
            "warnings": ["manual_evals.db is not available"],
        }

    with closing(_connect_readonly(db_path)) as conn:
        integrity = str(conn.execute("PRAGMA integrity_check").fetchone()[0])
        actionables = build_filtered_open_feedback_actionable_rows(
            conn,
            outcome=outcome_filter,
            cohort=cohort_filter,
        )
        total_rows = len(actionables)
        cohorts = _summarize_open_feedback_cohort_rows(actionables)

    return {
        "schema_version": COHORTS_SCHEMA_VERSION,
        "state": "ok" if integrity == "ok" else "error",
        "manual_evals_db": {
            "path": str(db_path),
            "exists": True,
            "integrity": integrity,
        },
        "filters": {
            "status": "open",
            "outcome": outcome_filter or "",
            "cohort": cohort_filter or "",
            "cohort_basis": "recommended_action",
        },
        "counts": {
            "total_rows": total_rows,
            "cohorts": len(cohorts),
        },
        "cohorts": cohorts,
    }


def format_open_feedback_actionables_report(report: dict[str, Any]) -> str:
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    filters = report.get("filters")
    if not isinstance(filters, dict):
        filters = {}

    total_rows = _int_value(counts.get("total_rows"))
    returned_rows = _int_value(counts.get("returned_rows"))
    lines = [
        "manual eval open feedback actionables: "
        f"state={report.get('state', 'unknown')} "
        f"rows={returned_rows}/{total_rows} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"path={manual_db.get('path', 'unknown')}",
    ]
    rows = report.get("rows")
    if not isinstance(rows, list) or not rows:
        lines.append("rows: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in rows:
        if not isinstance(item, dict):
            continue
        action_cohort = item.get("action_cohort")
        if not isinstance(action_cohort, dict):
            action_cohort = {}
        ocr_context = item.get("ocr_context")
        if not isinstance(ocr_context, dict):
            ocr_context = {}
        latest_ocr = ocr_context.get("latest_same_session_ocr")
        if not isinstance(latest_ocr, dict):
            latest_ocr = {}
        tags = item.get("tags")
        tag_text = ", ".join(str(tag) for tag in tags) if isinstance(tags, list) else ""
        lines.extend(
            [
                "- "
                f"feedback={_int_value(item.get('feedback_id'))} "
                f"era={item.get('era', '') or 'unknown'} "
                f"outcome={item.get('outcome', '') or 'unknown'} "
                f"status={item.get('status', '') or 'unknown'} "
                f"cohort={action_cohort.get('id') or 'unknown'} "
                f"session={item.get('session_id', '') or 'unknown'} "
                f"message={item.get('message_id', '') or 'unknown'}",
                f"  title={_display_text(item.get('title'))}",
                f"  tags={tag_text or 'none'}",
                f"  note={_display_text(item.get('note'))}",
                f"  recommended_action={_display_text(item.get('recommended_action'))}",
                f"  action_taken={_display_text(item.get('action_taken'))}",
                "  ocr_context: "
                "linked_to_ocr_result="
                f"{'yes' if ocr_context.get('linked_to_ocr_result') else 'no'} "
                "same_session_ocr_runs="
                f"{_int_value(ocr_context.get('same_session_ocr_runs'))} "
                f"latest_run={latest_ocr.get('run_id') or 'none'} "
                f"latest_source={latest_ocr.get('source_name') or 'none'} "
                f"latest_status={latest_ocr.get('status') or 'none'}",
            ]
        )
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)


def _format_outcomes(value: object) -> str:
    if not isinstance(value, dict) or not value:
        return "none"
    return ",".join(f"{key}={_int_value(count)}" for key, count in value.items())


def format_open_feedback_cohorts_report(report: dict[str, Any]) -> str:
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    filters = report.get("filters")
    if not isinstance(filters, dict):
        filters = {}

    lines = [
        "manual eval open feedback cohorts: "
        f"state={report.get('state', 'unknown')} "
        f"rows={_int_value(counts.get('total_rows'))} "
        f"cohorts={_int_value(counts.get('cohorts'))} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"basis={filters.get('cohort_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    cohorts = report.get("cohorts")
    if not isinstance(cohorts, list) or not cohorts:
        lines.append("cohorts: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in cohorts:
        if not isinstance(item, dict):
            continue
        sample_ids = item.get("sample_feedback_ids")
        if isinstance(sample_ids, list):
            sample_text = ",".join(str(_int_value(item)) for item in sample_ids)
        else:
            sample_text = "none"
        lines.extend(
            [
                "- "
                f"{item.get('cohort_id', 'unknown')}: "
                f"rows={_int_value(item.get('rows'))} "
                f"sessions={_int_value(item.get('sessions'))} "
                f"outcomes={_format_outcomes(item.get('outcomes'))} "
                f"notes={_int_value(item.get('rows_with_note'))} "
                "recommended_actions="
                f"{_int_value(item.get('rows_with_recommended_action'))} "
                f"action_taken={_int_value(item.get('rows_with_action_taken'))} "
                f"linked_to_ocr_result={_int_value(item.get('linked_to_ocr_result'))} "
                f"same_session_ocr={_int_value(item.get('same_session_ocr'))} "
                f"sample_feedback={sample_text or 'none'}",
                f"  action={_display_text(item.get('description'))}",
            ]
        )
    return "\n".join(lines)
