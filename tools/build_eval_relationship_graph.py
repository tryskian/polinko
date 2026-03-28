from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class ChatRow:
    session_id: str
    title: str
    status: str
    created_at: int
    updated_at: int


@dataclass(frozen=True)
class MessageRow:
    session_id: str
    message_id: str
    parent_message_id: str | None
    role: str
    created_at: int


@dataclass(frozen=True)
class FeedbackRow:
    session_id: str
    message_id: str
    outcome: str
    positive_tags: list[str]
    negative_tags: list[str]
    all_tags: list[str]
    status: str
    updated_at: int


@dataclass(frozen=True)
class CheckpointRow:
    session_id: str
    checkpoint_id: str
    total_count: int
    pass_count: int
    fail_count: int
    non_binary_count: int
    created_at: int


@dataclass(frozen=True)
class EvalReportSnapshot:
    suite: str
    run_id: str
    total: int
    passed: int
    failed: int
    mode: str | None
    high_risk: int | None
    file_path: Path
    generated_utc: str


_REPORT_NAME_PATTERN = re.compile(r"^(?P<suite>.+)-(?P<run_id>\d{8}-\d{6})\.json$")


def _escape_mermaid(value: str) -> str:
    return value.replace('"', '\\"')


def _escape_md_cell(value: str) -> str:
    return value.replace("|", "\\|")


def _anchor_for_session(session_id: str) -> str:
    chars: list[str] = []
    for ch in session_id.lower():
        if ch.isalnum() or ch in {"-", "_"}:
            chars.append(ch)
        else:
            chars.append("-")
    anchor = "".join(chars).strip("-")
    return anchor or "session"


def _short(value: str, size: int = 12) -> str:
    if len(value) <= size:
        return value
    return value[:size]


def _to_utc(ms: int) -> str:
    if ms <= 0:
        return "-"
    return datetime.fromtimestamp(ms / 1000, tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_utc_seconds(seconds: float) -> str:
    if seconds <= 0:
        return "-"
    return datetime.fromtimestamp(seconds, tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _coerce_int(value: object) -> int | None:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if text.isdigit():
            return int(text)
    return None


def _extract_eval_counts(payload: dict[str, object]) -> tuple[int | None, int | None, int | None]:
    total: int | None = None
    passed: int | None = None
    failed: int | None = None

    summary = payload.get("summary")
    if isinstance(summary, dict):
        summary_total = _coerce_int(summary.get("total"))
        summary_passed = _coerce_int(summary.get("passed"))
        summary_failed = _coerce_int(summary.get("failed"))
        if summary_total is not None:
            total = summary_total
        if summary_passed is not None:
            passed = summary_passed
        if summary_failed is not None:
            failed = summary_failed

    if total is None:
        total = _coerce_int(payload.get("total_cases"))
    if passed is None:
        passed = _coerce_int(payload.get("passed"))
    if failed is None:
        failed = _coerce_int(payload.get("failed"))

    if passed is None or failed is None:
        cases = payload.get("cases")
        if isinstance(cases, list):
            case_passed = 0
            case_failed = 0
            for case in cases:
                if not isinstance(case, dict):
                    continue
                pass_field = case.get("pass")
                if isinstance(pass_field, bool):
                    if pass_field:
                        case_passed += 1
                    else:
                        case_failed += 1
                    continue
                status_field = case.get("status")
                if isinstance(status_field, str):
                    normalized = status_field.strip().lower()
                    if normalized == "pass":
                        case_passed += 1
                    elif normalized == "fail":
                        case_failed += 1
            if passed is None:
                passed = case_passed
            if failed is None:
                failed = case_failed
            if total is None:
                total = case_passed + case_failed

    if total is None and passed is not None and failed is not None:
        total = passed + failed
    return total, passed, failed


def _extract_eval_mode(payload: dict[str, object]) -> str | None:
    for key in ("effective_evaluation_mode", "requested_evaluation_mode", "evaluation_mode"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _suite_label_from_slug(slug: str) -> str:
    words = [word for word in slug.replace("_", "-").split("-") if word]
    return " ".join(word.capitalize() for word in words) if words else slug


def _load_latest_eval_snapshots(report_dir: Path | None) -> list[EvalReportSnapshot]:
    if report_dir is None or not report_dir.exists():
        return []

    latest_by_suite: dict[str, Path] = {}
    for report_path in sorted(report_dir.glob("*.json")):
        match = _REPORT_NAME_PATTERN.match(report_path.name)
        if match is None:
            continue
        suite_slug = match.group("suite")
        run_id = match.group("run_id")
        previous = latest_by_suite.get(suite_slug)
        if previous is None:
            latest_by_suite[suite_slug] = report_path
            continue
        previous_match = _REPORT_NAME_PATTERN.match(previous.name)
        if previous_match is None:
            latest_by_suite[suite_slug] = report_path
            continue
        previous_run_id = previous_match.group("run_id")
        if run_id > previous_run_id:
            latest_by_suite[suite_slug] = report_path

    snapshots: list[EvalReportSnapshot] = []
    for suite_slug, report_path in sorted(latest_by_suite.items()):
        try:
            raw_payload = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(raw_payload, dict):
            continue

        total, passed, failed = _extract_eval_counts(raw_payload)
        if total is None or passed is None or failed is None:
            continue

        risk_counts = raw_payload.get("risk_counts")
        high_risk: int | None = None
        if isinstance(risk_counts, dict):
            high_risk = _coerce_int(risk_counts.get("high"))

        run_match = _REPORT_NAME_PATTERN.match(report_path.name)
        run_id = run_match.group("run_id") if run_match is not None else "-"
        snapshots.append(
            EvalReportSnapshot(
                suite=_suite_label_from_slug(suite_slug),
                run_id=run_id,
                total=total,
                passed=passed,
                failed=failed,
                mode=_extract_eval_mode(raw_payload),
                high_risk=high_risk,
                file_path=report_path,
                generated_utc=_to_utc_seconds(report_path.stat().st_mtime),
            )
        )
    return snapshots


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name = ?;
        """,
        (table_name,),
    ).fetchone()
    return row is not None


def _load_chats(conn: sqlite3.Connection) -> list[ChatRow]:
    if not _table_exists(conn, "chats"):
        return []
    rows = conn.execute(
        """
        SELECT session_id, title, status, created_at, updated_at
        FROM chats
        ORDER BY updated_at DESC, session_id ASC;
        """
    ).fetchall()
    return [
        ChatRow(
            session_id=str(row["session_id"]),
            title=str(row["title"]),
            status=str(row["status"]),
            created_at=int(row["created_at"]),
            updated_at=int(row["updated_at"]),
        )
        for row in rows
    ]


def _load_messages(conn: sqlite3.Connection, session_ids: set[str]) -> list[MessageRow]:
    if not _table_exists(conn, "chat_messages") or not session_ids:
        return []
    placeholders = ",".join("?" for _ in session_ids)
    rows = conn.execute(
        f"""
        SELECT session_id, message_id, parent_message_id, role, created_at, id
        FROM chat_messages
        WHERE session_id IN ({placeholders})
          AND role IN ('user', 'assistant')
          AND message_id IS NOT NULL
        ORDER BY created_at ASC, id ASC;
        """,
        tuple(sorted(session_ids)),
    ).fetchall()
    return [
        MessageRow(
            session_id=str(row["session_id"]),
            message_id=str(row["message_id"]),
            parent_message_id=str(row["parent_message_id"]) if row["parent_message_id"] is not None else None,
            role=str(row["role"]),
            created_at=int(row["created_at"]),
        )
        for row in rows
    ]


def _parse_tags(raw: str | None) -> tuple[list[str], list[str], list[str]]:
    if not raw:
        return [], [], []
    try:
        payload = json.loads(raw)
    except (TypeError, ValueError):
        return [], [], []
    if not isinstance(payload, dict):
        return [], [], []

    positive = payload.get("positive", [])
    negative = payload.get("negative", [])
    combined = payload.get("all", [])
    if not isinstance(positive, list):
        positive = []
    if not isinstance(negative, list):
        negative = []
    if not isinstance(combined, list):
        combined = []

    def _clean(items: Sequence[object]) -> list[str]:
        seen: dict[str, None] = {}
        for item in items:
            text = str(item).strip()
            if text:
                seen[text] = None
        return list(seen.keys())

    cleaned_positive = _clean(positive)
    cleaned_negative = _clean(negative)
    cleaned_combined = _clean(combined)
    if not cleaned_combined:
        cleaned_combined = _clean(cleaned_positive + cleaned_negative)
    return cleaned_positive, cleaned_negative, cleaned_combined


def _load_feedback(conn: sqlite3.Connection, session_ids: set[str]) -> list[FeedbackRow]:
    if not _table_exists(conn, "message_feedback") or not session_ids:
        return []
    placeholders = ",".join("?" for _ in session_ids)
    rows = conn.execute(
        f"""
        SELECT session_id, message_id, outcome, tags_json, status, updated_at, id
        FROM message_feedback
        WHERE session_id IN ({placeholders})
        ORDER BY updated_at DESC, id DESC;
        """,
        tuple(sorted(session_ids)),
    ).fetchall()

    feedback: list[FeedbackRow] = []
    for row in rows:
        positive, negative, combined = _parse_tags(
            str(row["tags_json"]) if row["tags_json"] is not None else None
        )
        feedback.append(
            FeedbackRow(
                session_id=str(row["session_id"]),
                message_id=str(row["message_id"]),
                outcome=str(row["outcome"]).lower(),
                positive_tags=positive,
                negative_tags=negative,
                all_tags=combined,
                status=str(row["status"]).lower(),
                updated_at=int(row["updated_at"]),
            )
        )
    return feedback


def _load_checkpoints(conn: sqlite3.Connection, session_ids: set[str]) -> list[CheckpointRow]:
    if not _table_exists(conn, "eval_checkpoints") or not session_ids:
        return []
    placeholders = ",".join("?" for _ in session_ids)
    rows = conn.execute(
        f"""
        SELECT session_id, checkpoint_id, total_count, pass_count, fail_count, other_count, created_at, id
        FROM eval_checkpoints
        WHERE session_id IN ({placeholders})
        ORDER BY created_at ASC, id ASC;
        """,
        tuple(sorted(session_ids)),
    ).fetchall()
    return [
        CheckpointRow(
            session_id=str(row["session_id"]),
            checkpoint_id=str(row["checkpoint_id"]),
            total_count=int(row["total_count"]),
            pass_count=int(row["pass_count"]),
            fail_count=int(row["fail_count"]),
            non_binary_count=int(row["other_count"]),
            created_at=int(row["created_at"]),
        )
        for row in rows
    ]


def _gate_outcome(checkpoints: list[CheckpointRow]) -> str:
    if not checkpoints:
        return "none"
    latest = checkpoints[-1]
    if latest.total_count > 0 and latest.fail_count == 0 and latest.non_binary_count == 0:
        return "pass"
    return "fail"


def _render_schema_er() -> list[str]:
    return [
        "```mermaid",
        "erDiagram",
        "  chats ||--o{ chat_messages : has",
        "  chats ||--o{ message_feedback : evaluates",
        "  chats ||--o{ eval_checkpoints : aggregates",
        "  chat_messages ||--o| message_feedback : rated_by_message_id",
        "```",
    ]


def _render_session_topology(
    chats: list[ChatRow],
    messages_by_session: dict[str, list[MessageRow]],
    feedback_by_session: dict[str, list[FeedbackRow]],
    checkpoints_by_session: dict[str, list[CheckpointRow]],
) -> list[str]:
    lines: list[str] = ["```mermaid", "graph LR"]
    for index, chat in enumerate(chats):
        session_node = f"s{index}"
        messages = messages_by_session.get(chat.session_id, [])
        feedback = feedback_by_session.get(chat.session_id, [])
        checkpoints = checkpoints_by_session.get(chat.session_id, [])
        pass_count = sum(1 for row in feedback if row.outcome == "pass")
        fail_count = sum(1 for row in feedback if row.outcome != "pass")
        gate = _gate_outcome(checkpoints)

        lines.append(
            f'  {session_node}["{_escape_mermaid(chat.session_id)}\\nstatus:{_escape_mermaid(chat.status)}"]'
        )
        lines.append(f'  {session_node}_m["messages:{len(messages)}"]')
        lines.append(f'  {session_node}_f["feedback P:{pass_count} F:{fail_count}"]')
        lines.append(f'  {session_node}_c["checkpoints:{len(checkpoints)}\\nlatest:{gate}"]')
        lines.append(f"  {session_node} --> {session_node}_m")
        lines.append(f"  {session_node} --> {session_node}_f")
        lines.append(f"  {session_node} --> {session_node}_c")
        if index < len(chats) - 1:
            lines.append(f"  {session_node} --- s{index + 1}")

    lines.append("  classDef session fill:#1f3b6d,stroke:#5ea2ff,color:#ffffff")
    lines.append("  classDef summary fill:#132a4a,stroke:#3f6ea8,color:#ffffff")
    session_nodes = [f"s{i}" for i in range(len(chats))]
    summary_nodes: list[str] = []
    for node in session_nodes:
        summary_nodes.extend([f"{node}_m", f"{node}_f", f"{node}_c"])
    if session_nodes:
        lines.append(f"  class {','.join(session_nodes)} session")
    if summary_nodes:
        lines.append(f"  class {','.join(summary_nodes)} summary")
    lines.append("```")
    return lines


def _render_session_graph(
    session_id: str,
    messages: list[MessageRow],
    feedback: list[FeedbackRow],
    checkpoints: list[CheckpointRow],
) -> list[str]:
    lines: list[str] = ["```mermaid", "flowchart LR"]
    lines.append(f'  sess["session:{_escape_mermaid(session_id)}"]')

    message_nodes: dict[str, str] = {}
    user_nodes: list[str] = []
    assistant_nodes: list[str] = []
    for index, message in enumerate(messages):
        node_id = f"m{index}"
        message_nodes[message.message_id] = node_id
        label = _escape_mermaid(f"{message.role}:{_short(message.message_id, 14)}")
        lines.append(f'  {node_id}["{label}"]')
        lines.append(f"  sess --> {node_id}")
        if message.role == "user":
            user_nodes.append(node_id)
        else:
            assistant_nodes.append(node_id)

    for message in messages:
        if message.parent_message_id and message.parent_message_id in message_nodes:
            parent = message_nodes[message.parent_message_id]
            child = message_nodes[message.message_id]
            lines.append(f"  {parent} --> {child}")

    pass_feedback_nodes: list[str] = []
    fail_feedback_nodes: list[str] = []
    tag_nodes: dict[str, str] = {}
    for index, feedback_row in enumerate(feedback):
        feedback_node = f"f{index}"
        label = _escape_mermaid(f"{feedback_row.outcome}:{_short(feedback_row.message_id, 12)}")
        lines.append(f'  {feedback_node}["{label}"]')
        if feedback_row.outcome == "pass":
            pass_feedback_nodes.append(feedback_node)
        else:
            fail_feedback_nodes.append(feedback_node)

        if feedback_row.message_id in message_nodes:
            lines.append(f"  {message_nodes[feedback_row.message_id]} --> {feedback_node}")
        else:
            lines.append(f"  sess --> {feedback_node}")

        for tag in feedback_row.all_tags:
            if tag not in tag_nodes:
                tag_nodes[tag] = f"t{len(tag_nodes)}"
                lines.append(f'  {tag_nodes[tag]}["tag:{_escape_mermaid(tag)}"]')
            lines.append(f"  {feedback_node} --> {tag_nodes[tag]}")

    checkpoint_nodes: list[str] = []
    for index, checkpoint_row in enumerate(checkpoints):
        node_id = f"c{index}"
        checkpoint_nodes.append(node_id)
        gate = (
            "pass"
            if checkpoint_row.total_count > 0
            and checkpoint_row.fail_count == 0
            and checkpoint_row.non_binary_count == 0
            else "fail"
        )
        label = _escape_mermaid(
            f"cp:{_short(checkpoint_row.checkpoint_id, 12)} {gate}\\nP:{checkpoint_row.pass_count} F:{checkpoint_row.fail_count} N:{checkpoint_row.non_binary_count}"
        )
        lines.append(f'  {node_id}["{label}"]')
        lines.append(f"  sess --> {node_id}")

    lines.append("  classDef session fill:#1f3b6d,stroke:#5ea2ff,color:#ffffff")
    lines.append("  classDef user fill:#113322,stroke:#39b26b,color:#ffffff")
    lines.append("  classDef assistant fill:#332211,stroke:#f3a347,color:#ffffff")
    lines.append("  classDef feedbackPass fill:#143d2a,stroke:#6ad39a,color:#ffffff")
    lines.append("  classDef feedbackFail fill:#4a1e1e,stroke:#ff8a8a,color:#ffffff")
    lines.append("  classDef tag fill:#2a2352,stroke:#9f8cff,color:#ffffff")
    lines.append("  classDef checkpoint fill:#2e2e2e,stroke:#999999,color:#ffffff")

    lines.append("  class sess session")
    if user_nodes:
        lines.append(f"  class {','.join(user_nodes)} user")
    if assistant_nodes:
        lines.append(f"  class {','.join(assistant_nodes)} assistant")
    if pass_feedback_nodes:
        lines.append(f"  class {','.join(pass_feedback_nodes)} feedbackPass")
    if fail_feedback_nodes:
        lines.append(f"  class {','.join(fail_feedback_nodes)} feedbackFail")
    if tag_nodes:
        lines.append(f"  class {','.join(tag_nodes.values())} tag")
    if checkpoint_nodes:
        lines.append(f"  class {','.join(checkpoint_nodes)} checkpoint")

    lines.append("```")
    return lines


def build_eval_relationship_markdown(
    *,
    db_path: Path,
    report_dir: Path | None = None,
    session_filter: set[str] | None = None,
) -> str:
    if not db_path.exists():
        raise FileNotFoundError(f"History DB not found: {db_path}")

    with _connect(db_path) as conn:
        chats = _load_chats(conn)
        if session_filter:
            chats = [chat for chat in chats if chat.session_id in session_filter]
        session_ids = {chat.session_id for chat in chats}
        messages = _load_messages(conn, session_ids)
        feedback = _load_feedback(conn, session_ids)
        checkpoints = _load_checkpoints(conn, session_ids)

    messages_by_session: dict[str, list[MessageRow]] = {}
    for message_row in messages:
        messages_by_session.setdefault(message_row.session_id, []).append(message_row)

    feedback_by_session: dict[str, list[FeedbackRow]] = {}
    for feedback_row in feedback:
        feedback_by_session.setdefault(feedback_row.session_id, []).append(feedback_row)

    checkpoints_by_session: dict[str, list[CheckpointRow]] = {}
    for checkpoint_row in checkpoints:
        checkpoints_by_session.setdefault(checkpoint_row.session_id, []).append(checkpoint_row)

    total_pass = sum(1 for feedback_row in feedback if feedback_row.outcome == "pass")
    total_fail = sum(1 for feedback_row in feedback if feedback_row.outcome != "pass")
    eval_snapshots = _load_latest_eval_snapshots(report_dir)

    tag_counts: dict[str, int] = {}
    for feedback_row in feedback:
        for tag in feedback_row.all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    lines: list[str] = []
    lines.append("# Eval Relationship Graph")
    lines.append("")
    lines.append("Navigation-first visual report for runtime eval data in `history.db`.")
    lines.append("")
    lines.append("## Quick Navigation")
    lines.append("")
    lines.append("- [Overview](#overview)")
    lines.append("- [Eval Report Snapshot](#eval-report-snapshot)")
    lines.append("- [Schema ER](#schema-er)")
    lines.append("- [Session Topology](#session-topology)")
    lines.append("- [Session Directory](#session-directory)")
    lines.append("- [Session Details](#session-details)")
    lines.append("- [Tag Frequency](#tag-frequency)")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| generated_utc | `{datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}` |")
    lines.append(f"| db_path | `{db_path}` |")
    lines.append(f"| sessions | {len(chats)} |")
    lines.append(f"| messages | {len(messages)} |")
    lines.append(f"| feedback | {len(feedback)} (pass={total_pass}, fail={total_fail}) |")
    lines.append(f"| checkpoints | {len(checkpoints)} |")
    lines.append(f"| latest_eval_reports | {len(eval_snapshots)} suite snapshots |")
    lines.append("")
    lines.append("## Eval Report Snapshot")
    lines.append("")
    lines.append("Latest report artifact per suite from `eval_reports/`.")
    lines.append("")
    lines.append("| suite | run_id | total | pass | fail | pass_rate | mode | high_risk | generated_utc | report_file |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- | --- |")
    if eval_snapshots:
        for snapshot in eval_snapshots:
            pass_rate = (snapshot.passed / snapshot.total * 100.0) if snapshot.total > 0 else 0.0
            mode = snapshot.mode or "-"
            high_risk = str(snapshot.high_risk) if snapshot.high_risk is not None else "-"
            lines.append(
                "| "
                f"{_escape_md_cell(snapshot.suite)} | "
                f"`{snapshot.run_id}` | "
                f"{snapshot.total} | "
                f"{snapshot.passed} | "
                f"{snapshot.failed} | "
                f"{pass_rate:.1f}% | "
                f"{_escape_md_cell(mode)} | "
                f"{high_risk} | "
                f"{snapshot.generated_utc} | "
                f"`{_escape_md_cell(str(snapshot.file_path))}` |"
            )
    else:
        lines.append("| _none_ | - | 0 | 0 | 0 | 0.0% | - | - | - | - |")
    lines.append("")
    lines.append("## Schema ER")
    lines.append("")
    lines.extend(_render_schema_er())
    lines.append("")
    lines.append("## Session Topology")
    lines.append("")
    if chats:
        lines.extend(
            _render_session_topology(
                chats,
                messages_by_session,
                feedback_by_session,
                checkpoints_by_session,
            )
        )
    else:
        lines.append("_No sessions found for the selected scope._")
        lines.append("")
        lines.append("Populate data with:")
        lines.append("")
        lines.append("1. Run chat + feedback in API/CLI.")
        lines.append("2. Submit checkpoint(s) for the session.")
        lines.append("3. Re-run `make eval-viz`.")
    lines.append("")
    lines.append("## Session Directory")
    lines.append("")
    lines.append("| Session | Title | Status | Messages | Feedback (pass/fail) | Checkpoints | Latest Gate | Updated UTC |")
    lines.append("| --- | --- | --- | ---: | --- | ---: | --- | --- |")
    for chat in chats:
        sess_messages = messages_by_session.get(chat.session_id, [])
        sess_feedback = feedback_by_session.get(chat.session_id, [])
        sess_checkpoints = checkpoints_by_session.get(chat.session_id, [])
        sess_pass = sum(1 for row in sess_feedback if row.outcome == "pass")
        sess_fail = sum(1 for row in sess_feedback if row.outcome != "pass")
        gate = _gate_outcome(sess_checkpoints)
        anchor = _anchor_for_session(chat.session_id)
        lines.append(
            "| "
            f"[{_escape_md_cell(chat.session_id)}](#session-{anchor}) | "
            f"{_escape_md_cell(chat.title)} | "
            f"{_escape_md_cell(chat.status)} | "
            f"{len(sess_messages)} | "
            f"{sess_pass}/{sess_fail} | "
            f"{len(sess_checkpoints)} | "
            f"{gate} | "
            f"{_to_utc(chat.updated_at)} |"
        )
    if not chats:
        lines.append("| _none_ | _none_ | _none_ | 0 | 0/0 | 0 | none | _none_ |")
    lines.append("")
    lines.append("## Session Details")
    lines.append("")
    if not chats:
        lines.append("_No sessions to detail yet._")
        lines.append("")
    for chat in chats:
        anchor = _anchor_for_session(chat.session_id)
        sess_messages = messages_by_session.get(chat.session_id, [])
        sess_feedback = feedback_by_session.get(chat.session_id, [])
        sess_checkpoints = checkpoints_by_session.get(chat.session_id, [])

        lines.append(f"### Session {anchor}")
        lines.append("")
        lines.append(f"- session_id: `{chat.session_id}`")
        lines.append(f"- title: `{chat.title}`")
        lines.append(f"- status: `{chat.status}`")
        lines.append(f"- updated_utc: `{_to_utc(chat.updated_at)}`")
        lines.append("")
        lines.append("Relationship Map:")
        lines.append("")
        lines.extend(_render_session_graph(chat.session_id, sess_messages, sess_feedback, sess_checkpoints))
        lines.append("")
        lines.append("Messages:")
        lines.append("")
        lines.append("| message_id | role | parent_message_id | created_utc |")
        lines.append("| --- | --- | --- | --- |")
        if sess_messages:
            for message_row in sess_messages:
                lines.append(
                    "| "
                    f"`{_escape_md_cell(message_row.message_id)}` | "
                    f"{_escape_md_cell(message_row.role)} | "
                    f"`{_escape_md_cell(message_row.parent_message_id or '-')}` | "
                    f"{_to_utc(message_row.created_at)} |"
                )
        else:
            lines.append("| _none_ | _none_ | _none_ | _none_ |")
        lines.append("")
        lines.append("Feedback:")
        lines.append("")
        lines.append("| message_id | outcome | positive_tags | negative_tags | status | updated_utc |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        if sess_feedback:
            for feedback_row in sess_feedback:
                lines.append(
                    "| "
                    f"`{_escape_md_cell(feedback_row.message_id)}` | "
                    f"{_escape_md_cell(feedback_row.outcome)} | "
                    f"{_escape_md_cell(', '.join(feedback_row.positive_tags) or '-')} | "
                    f"{_escape_md_cell(', '.join(feedback_row.negative_tags) or '-')} | "
                    f"{_escape_md_cell(feedback_row.status)} | "
                    f"{_to_utc(feedback_row.updated_at)} |"
                )
        else:
            lines.append("| _none_ | _none_ | _none_ | _none_ | _none_ | _none_ |")
        lines.append("")
        lines.append("Checkpoints:")
        lines.append("")
        lines.append("| checkpoint_id | total | pass | fail | non_binary | gate_outcome | created_utc |")
        lines.append("| --- | ---: | ---: | ---: | ---: | --- | --- |")
        if sess_checkpoints:
            for checkpoint_row in sess_checkpoints:
                gate = (
                    "pass"
                    if checkpoint_row.total_count > 0
                    and checkpoint_row.fail_count == 0
                    and checkpoint_row.non_binary_count == 0
                    else "fail"
                )
                lines.append(
                    "| "
                    f"`{_escape_md_cell(checkpoint_row.checkpoint_id)}` | "
                    f"{checkpoint_row.total_count} | "
                    f"{checkpoint_row.pass_count} | "
                    f"{checkpoint_row.fail_count} | "
                    f"{checkpoint_row.non_binary_count} | "
                    f"{gate} | "
                    f"{_to_utc(checkpoint_row.created_at)} |"
                )
        else:
            lines.append("| _none_ | 0 | 0 | 0 | 0 | none | _none_ |")
        lines.append("")
        lines.append("[Back to top](#quick-navigation)")
        lines.append("")
    lines.append("## Tag Frequency")
    lines.append("")
    lines.append("| tag | count |")
    lines.append("| --- | ---: |")
    if tag_counts:
        for tag, count in sorted(tag_counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"| `{_escape_md_cell(tag)}` | {count} |")
    else:
        lines.append("| _none_ | 0 |")
    lines.append("")
    lines.append("## Legend")
    lines.append("")
    lines.append("- `session` nodes: chat scope")
    lines.append("- `user` and `assistant` nodes: message lineage")
    lines.append("- `feedbackPass` / `feedbackFail`: binary eval outcomes")
    lines.append("- `tag` nodes: diagnostic tag attachments")
    lines.append("- `checkpoint` nodes: fail-closed gate snapshots")
    return "\n".join(lines) + "\n"


def build_eval_relationship_graph(
    *,
    db_path: Path,
    output: Path,
    report_dir: Path | None = None,
    session_filter: set[str] | None = None,
) -> None:
    markdown = build_eval_relationship_markdown(
        db_path=db_path,
        report_dir=report_dir,
        session_filter=session_filter,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a markdown eval relationship graph from the runtime history DB."
    )
    parser.add_argument(
        "--db-path",
        default=".local/runtime_dbs/active/history.db",
        help="Path to runtime history sqlite DB.",
    )
    parser.add_argument(
        "--output",
        default=".local/visuals/eval_relationship_graph.md",
        help="Output markdown path (local-only by default).",
    )
    parser.add_argument(
        "--report-dir",
        default="eval_reports",
        help="Directory containing eval report JSON artifacts to snapshot.",
    )
    parser.add_argument(
        "--session-id",
        action="append",
        default=[],
        help="Optional session id filter. Repeat for multiple sessions.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    db_path = Path(args.db_path).expanduser().resolve()
    output = Path(args.output).expanduser()
    if not output.is_absolute():
        output = (Path.cwd() / output).resolve()
    report_dir = Path(args.report_dir).expanduser()
    if not report_dir.is_absolute():
        report_dir = (Path.cwd() / report_dir).resolve()
    session_filter = {item.strip() for item in args.session_id if item.strip()}
    build_eval_relationship_graph(
        db_path=db_path,
        output=output,
        report_dir=report_dir,
        session_filter=session_filter if session_filter else None,
    )
    print(f"Eval relationship graph written: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
