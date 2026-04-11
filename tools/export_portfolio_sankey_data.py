"""Export twin-Sankey portfolio data from local eval_viz raw points.

Source of truth:
- .local/runtime_dbs/active/eval_viz.db (eval_points table)

Output:
- frontend/src/data/twin_sankey_raw.json
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SuiteRollup:
    suite: str
    total: int
    pass_count: int
    fail_count: int


@dataclass(frozen=True)
class LaneRollup:
    lane: str
    total: int
    pass_count: int
    fail_count: int


CONTROL_SUITES = ("hallucination", "style", "retrieval", "file-search")
BRIDGE_SUITE = "ocr"
BETA2_SUITE = "ocr_transcript_stability"
LEGACY_SUITES = (*CONTROL_SUITES, BRIDGE_SUITE)


def _detect_legacy_suite_from_filename(stem: str) -> str | None:
    # Prefer exact known suite prefixes so hyphenated names (e.g., file-search) map correctly.
    # Keep matching strict to timestamped eval reports, e.g. `suite-YYYY...`.
    for suite in sorted(LEGACY_SUITES, key=len, reverse=True):
        if stem == suite:
            return suite
        prefix = f"{suite}-"
        if stem.startswith(prefix):
            remainder = stem[len(prefix) :]
            if remainder and remainder[0].isdigit():
                return suite
    return None


@dataclass(frozen=True)
class LegacyReportRollup:
    suite: str
    total: int
    pass_count: int
    fail_count: int
    case_ids: list[str]
    source_file: str
    source_mtime: float


def _query_suite_rollups(conn: sqlite3.Connection) -> dict[str, SuiteRollup]:
    rows = conn.execute(
        """
        SELECT
          suite,
          COUNT(*) AS total,
          SUM(CASE WHEN outcome = 'pass' THEN 1 ELSE 0 END) AS pass_count,
          SUM(CASE WHEN outcome = 'fail' THEN 1 ELSE 0 END) AS fail_count
        FROM eval_points
        GROUP BY suite
        """
    ).fetchall()
    result: dict[str, SuiteRollup] = {}
    for row in rows:
        result[str(row["suite"])] = SuiteRollup(
            suite=str(row["suite"]),
            total=int(row["total"] or 0),
            pass_count=int(row["pass_count"] or 0),
            fail_count=int(row["fail_count"] or 0),
        )
    return result


def _query_lane_rollups_for_suite(conn: sqlite3.Connection, suite: str) -> list[LaneRollup]:
    rows = conn.execute(
        """
        SELECT
          lane,
          COUNT(*) AS total,
          SUM(CASE WHEN outcome = 'pass' THEN 1 ELSE 0 END) AS pass_count,
          SUM(CASE WHEN outcome = 'fail' THEN 1 ELSE 0 END) AS fail_count
        FROM eval_points
        WHERE suite = ?
        GROUP BY lane
        ORDER BY total DESC, lane ASC
        """,
        (suite,),
    ).fetchall()
    return [
        LaneRollup(
            lane=str(row["lane"]),
            total=int(row["total"] or 0),
            pass_count=int(row["pass_count"] or 0),
            fail_count=int(row["fail_count"] or 0),
        )
        for row in rows
    ]


def _query_suite_cases(conn: sqlite3.Connection, suite: str, limit: int = 3) -> list[str]:
    rows = conn.execute(
        """
        SELECT case_id
        FROM eval_points
        WHERE suite = ?
        ORDER BY ts_unix DESC, case_index DESC
        LIMIT ?
        """,
        (suite, limit),
    ).fetchall()
    return [str(row["case_id"]) for row in rows if str(row["case_id"]).strip()]


def _query_source_meta(conn: sqlite3.Connection) -> dict[str, object]:
    row = conn.execute(
        """
        SELECT
          COUNT(*) AS total_points,
          COUNT(DISTINCT run_id) AS run_count,
          MIN(ts_unix) AS min_ts_unix,
          MAX(ts_unix) AS max_ts_unix
        FROM eval_points
        """
    ).fetchone()
    return {
        "total_points": int(row["total_points"] or 0),
        "run_count": int(row["run_count"] or 0),
        "min_ts_unix": int(row["min_ts_unix"] or 0),
        "max_ts_unix": int(row["max_ts_unix"] or 0),
    }


def _suite_label(suite: str) -> str:
    labels = {
        "hallucination": "Hallucination checks",
        "style": "Style checks",
        "retrieval": "Retrieval checks",
        "file-search": "File-search checks",
        "ocr": "OCR checks",
        "ocr_transcript_stability": "OCR transcript stability",
    }
    return labels.get(suite, suite.replace("-", " ").replace("_", " ").title())


def _coerce_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _extract_legacy_report_rollup(report_path: Path, suite: str) -> LegacyReportRollup | None:
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    total = 0
    pass_count = 0
    fail_count = 0

    summary = payload.get("summary")
    if isinstance(summary, dict):
        total = _coerce_int(summary.get("total"))
        pass_count = _coerce_int(summary.get("passed") or summary.get("pass_count"))
        fail_count = _coerce_int(summary.get("failed") or summary.get("fail_count"))
    elif "total_cases" in payload:
        total = _coerce_int(payload.get("total_cases"))
        pass_count = _coerce_int(payload.get("passed"))
        fail_count = _coerce_int(payload.get("failed"))

    if total <= 0:
        return None

    case_ids: list[str] = []
    raw_cases = payload.get("cases")
    if isinstance(raw_cases, list):
        for case in raw_cases:
            if not isinstance(case, dict):
                continue
            case_id = str(case.get("id") or "").strip()
            if case_id:
                case_ids.append(case_id)
            if len(case_ids) >= 3:
                break

    return LegacyReportRollup(
        suite=suite,
        total=total,
        pass_count=pass_count,
        fail_count=fail_count,
        case_ids=case_ids,
        source_file=str(report_path),
        source_mtime=report_path.stat().st_mtime,
    )


def _load_latest_legacy_rollups(legacy_reports_dir: Path) -> dict[str, LegacyReportRollup]:
    if not legacy_reports_dir.is_dir():
        return {}

    latest_by_suite: dict[str, LegacyReportRollup] = {}
    for report_path in sorted(legacy_reports_dir.glob("*.json")):
        suite = _detect_legacy_suite_from_filename(report_path.stem)
        if suite is None:
            continue
        rollup = _extract_legacy_report_rollup(report_path, suite)
        if rollup is None:
            continue
        current = latest_by_suite.get(suite)
        if current is None or rollup.source_mtime > current.source_mtime:
            latest_by_suite[suite] = rollup
    return latest_by_suite


def build_payload(history_db: Path, legacy_reports_dir: Path | None = None) -> dict[str, object]:
    if not history_db.is_file():
        raise FileNotFoundError(f"eval_viz DB not found: {history_db}")

    conn = sqlite3.connect(f"file:{history_db}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        suite_rollups = _query_suite_rollups(conn)
        legacy_rollups: dict[str, LegacyReportRollup] = {}
        if legacy_reports_dir is not None:
            legacy_rollups = _load_latest_legacy_rollups(legacy_reports_dir)
        if not suite_rollups:
            raise RuntimeError("eval_points has no rows; cannot build raw Sankey payload.")

        lane_rollups = _query_lane_rollups_for_suite(conn, BETA2_SUITE)
        source_meta = _query_source_meta(conn)

        control_present: list[SuiteRollup] = []
        for suite in CONTROL_SUITES:
            if suite in legacy_rollups:
                lr = legacy_rollups[suite]
                control_present.append(
                    SuiteRollup(
                        suite=suite,
                        total=lr.total,
                        pass_count=lr.pass_count,
                        fail_count=lr.fail_count,
                    )
                )
            elif suite in suite_rollups and suite_rollups[suite].total > 0:
                control_present.append(suite_rollups[suite])

        control_total = sum(item.total for item in control_present)

        if BRIDGE_SUITE in legacy_rollups:
            lr = legacy_rollups[BRIDGE_SUITE]
            bridge_suite_rollup = SuiteRollup(
                BRIDGE_SUITE, lr.total, lr.pass_count, lr.fail_count
            )
        else:
            bridge_suite_rollup = suite_rollups.get(BRIDGE_SUITE, SuiteRollup(BRIDGE_SUITE, 0, 0, 0))
        beta2_suite_rollup = suite_rollups.get(BETA2_SUITE, SuiteRollup(BETA2_SUITE, 0, 0, 0))

        sankey_one_nodes: list[dict[str, object]] = []
        sankey_one_links: list[dict[str, object]] = []

        for item in control_present:
            node_id = f"control_{item.suite.replace('-', '_')}"
            legacy_case_ids = legacy_rollups.get(item.suite).case_ids if item.suite in legacy_rollups else []
            sankey_one_nodes.append(
                {
                    "id": node_id,
                    "name": f"{_suite_label(item.suite)} ({item.total})",
                    "stage": "Baseline",
                    "note": (
                        f"Raw suite={item.suite}; total={item.total}; "
                        f"pass={item.pass_count}; fail={item.fail_count}"
                    ),
                    "evidence": legacy_case_ids or _query_suite_cases(conn, item.suite),
                }
            )
            sankey_one_links.append(
                {
                    "id": f"control_to_bridge_{item.suite.replace('-', '_')}",
                    "source": node_id,
                    "target": "bridge_spine_one",
                    "value": item.total,
                    "note": f"{_suite_label(item.suite)} raw contribution into bridge.",
                }
            )

        sankey_one_nodes.append(
            {
                "id": "bridge_spine_one",
                "name": f"Bridge (Polinko Beta 1.0) ({control_total})",
                "stage": "Bridge (Polinko Beta 1.0)",
                "note": (
                    f"Raw baseline suites collapsed into bridge. "
                    f"Bridge suite ({BRIDGE_SUITE}) observed total={bridge_suite_rollup.total}; "
                    f"pass={bridge_suite_rollup.pass_count}; fail={bridge_suite_rollup.fail_count}."
                ),
                "evidence": (
                    legacy_rollups.get(BRIDGE_SUITE).case_ids
                    if BRIDGE_SUITE in legacy_rollups
                    else _query_suite_cases(conn, BRIDGE_SUITE)
                ),
            }
        )

        sankey_two_nodes: list[dict[str, object]] = [
            {
                "id": "bridge_spine_two",
                "name": (
                    f"Bridge (Polinko Beta 1.0) "
                    f"({beta2_suite_rollup.total if beta2_suite_rollup.total > 0 else bridge_suite_rollup.total})"
                ),
                "stage": "Bridge (Polinko Beta 1.0)",
                "note": (
                    f"Input bridge for {BETA2_SUITE}; "
                    f"raw total={beta2_suite_rollup.total}; "
                    f"pass={beta2_suite_rollup.pass_count}; fail={beta2_suite_rollup.fail_count}"
                ),
                "evidence": _query_suite_cases(conn, BETA2_SUITE),
            }
        ]
        sankey_two_links: list[dict[str, object]] = []

        for lane in lane_rollups:
            lane_id = f"beta2_lane_{lane.lane.replace('-', '_')}"
            sankey_two_nodes.append(
                {
                    "id": lane_id,
                    "name": f"{lane.lane.title()} lane ({lane.total})",
                    "stage": "Polinko Beta 2.0",
                    "note": (
                        f"Raw lane={lane.lane}; total={lane.total}; "
                        f"pass={lane.pass_count}; fail={lane.fail_count}"
                    ),
                }
            )
            sankey_two_links.append(
                {
                    "id": f"bridge_to_beta2_{lane.lane.replace('-', '_')}",
                    "source": "bridge_spine_two",
                    "target": lane_id,
                    "value": lane.total,
                    "note": f"Bridge flow into Beta 2.0 {lane.lane} lane.",
                }
            )

        payload = {
            "meta": {
                "generated_at_utc": datetime.now(UTC).isoformat(),
                "source_db": str(history_db.resolve()),
                **source_meta,
                "control_suites": list(CONTROL_SUITES),
                "bridge_suite": BRIDGE_SUITE,
                "beta2_suite": BETA2_SUITE,
                "legacy_reports_dir": (
                    str(legacy_reports_dir.resolve()) if legacy_reports_dir else None
                ),
                "legacy_rollup_suites": sorted(legacy_rollups.keys()),
            },
            "sankeys": [
                {"id": "sankey-one", "data": {"nodes": sankey_one_nodes, "links": sankey_one_links}},
                {"id": "sankey-two", "data": {"nodes": sankey_two_nodes, "links": sankey_two_links}},
            ],
        }
        return payload
    finally:
        conn.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export raw twin-Sankey portfolio data from eval_viz.db."
    )
    parser.add_argument(
        "--source-db",
        default=".local/runtime_dbs/active/eval_viz.db",
        help="Path to source eval_viz sqlite DB.",
    )
    parser.add_argument(
        "--output-json",
        default="frontend/src/data/twin_sankey_raw.json",
        help="Output JSON file for frontend import.",
    )
    parser.add_argument(
        "--legacy-reports-dir",
        default="../old/polinko-incase/eval_reports",
        help="Optional legacy eval report directory (Polinko-1 baseline source).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_db = Path(args.source_db).expanduser()
    output_json = Path(args.output_json).expanduser()
    legacy_reports_dir_raw = str(args.legacy_reports_dir or "").strip()
    legacy_reports_dir = (
        Path(legacy_reports_dir_raw).expanduser() if legacy_reports_dir_raw else None
    )
    output_json.parent.mkdir(parents=True, exist_ok=True)

    payload = build_payload(source_db, legacy_reports_dir=legacy_reports_dir)
    output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"wrote {output_json} from {source_db} "
        f"(points={payload['meta']['total_points']}, runs={payload['meta']['run_count']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
