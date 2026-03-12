from __future__ import annotations

import argparse
import glob
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_BASELINE_ARM = "baseline_mixed"
_PROXY_ARM = "clip_proxy_image_only"


@dataclass(frozen=True)
class ClipReadinessEvaluation:
    path: Path
    run_id: str
    timestamp_unix: int
    cases_count: int
    proxy_any_rate: float
    delta: float
    baseline_errors: int
    baseline_skipped: int
    proxy_errors: int
    proxy_skipped: int
    passed: bool
    reasons: tuple[str, ...]


def _int_value(raw: Any, default: int = 0) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def _float_value(raw: Any, default: float = 0.0) -> float:
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def _load_payload(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _evaluate_report(
    *,
    path: Path,
    payload: dict[str, Any] | None,
    min_cases: int,
    min_proxy_any_rate: float,
    min_delta: float,
) -> ClipReadinessEvaluation:
    if payload is None:
        return ClipReadinessEvaluation(
            path=path,
            run_id=path.stem,
            timestamp_unix=0,
            cases_count=0,
            proxy_any_rate=0.0,
            delta=0.0,
            baseline_errors=0,
            baseline_skipped=0,
            proxy_errors=0,
            proxy_skipped=0,
            passed=False,
            reasons=("invalid JSON payload",),
        )

    run_id = str(payload.get("run_id", "")).strip() or path.stem
    timestamp_unix = _int_value(payload.get("timestamp_unix"), 0)
    cases_count = _int_value(payload.get("cases_count"), 0)

    summary = payload.get("summary")
    reasons: list[str] = []
    if not isinstance(summary, dict):
        summary = {}
        reasons.append("missing summary")

    baseline = summary.get(_BASELINE_ARM)
    proxy = summary.get(_PROXY_ARM)
    if not isinstance(baseline, dict):
        baseline = {}
        reasons.append(f"missing {_BASELINE_ARM} summary")
    if not isinstance(proxy, dict):
        proxy = {}
        reasons.append(f"missing {_PROXY_ARM} summary")

    baseline_any_rate = _float_value(baseline.get("any_rate"), 0.0)
    proxy_any_rate = _float_value(proxy.get("any_rate"), 0.0)
    delta = _float_value(
        payload.get("any_rate_delta_proxy_minus_baseline"),
        proxy_any_rate - baseline_any_rate,
    )
    baseline_errors = _int_value(baseline.get("errors"), 0)
    baseline_skipped = _int_value(baseline.get("skipped"), 0)
    proxy_errors = _int_value(proxy.get("errors"), 0)
    proxy_skipped = _int_value(proxy.get("skipped"), 0)

    if cases_count < min_cases:
        reasons.append(f"cases_count {cases_count} < {min_cases}")
    if proxy_any_rate < min_proxy_any_rate:
        reasons.append(f"proxy any_rate {proxy_any_rate:.3f} < {min_proxy_any_rate:.3f}")
    if delta < min_delta:
        reasons.append(f"delta {delta:+.3f} < {min_delta:+.3f}")
    if baseline_errors != 0:
        reasons.append(f"{_BASELINE_ARM} errors {baseline_errors} != 0")
    if baseline_skipped != 0:
        reasons.append(f"{_BASELINE_ARM} skipped {baseline_skipped} != 0")
    if proxy_errors != 0:
        reasons.append(f"{_PROXY_ARM} errors {proxy_errors} != 0")
    if proxy_skipped != 0:
        reasons.append(f"{_PROXY_ARM} skipped {proxy_skipped} != 0")

    return ClipReadinessEvaluation(
        path=path,
        run_id=run_id,
        timestamp_unix=timestamp_unix,
        cases_count=cases_count,
        proxy_any_rate=proxy_any_rate,
        delta=delta,
        baseline_errors=baseline_errors,
        baseline_skipped=baseline_skipped,
        proxy_errors=proxy_errors,
        proxy_skipped=proxy_skipped,
        passed=not reasons,
        reasons=tuple(reasons),
    )


def _load_evaluations(
    *,
    report_glob: str,
    min_cases: int,
    min_proxy_any_rate: float,
    min_delta: float,
) -> list[ClipReadinessEvaluation]:
    evaluations = [
        _evaluate_report(
            path=path,
            payload=_load_payload(path),
            min_cases=min_cases,
            min_proxy_any_rate=min_proxy_any_rate,
            min_delta=min_delta,
        )
        for path in sorted(Path(match) for match in glob.glob(report_glob))
    ]
    return sorted(
        evaluations,
        key=lambda item: (item.timestamp_unix, item.run_id, item.path.name),
    )


def _format_evaluation(item: ClipReadinessEvaluation) -> str:
    status = "PASS" if item.passed else "FAIL"
    return (
        f"{item.path.name}: {status} run_id={item.run_id} "
        f"cases={item.cases_count} proxy_any_rate={item.proxy_any_rate:.3f} "
        f"delta={item.delta:+.3f} "
        f"baseline_errors={item.baseline_errors} baseline_skipped={item.baseline_skipped} "
        f"proxy_errors={item.proxy_errors} proxy_skipped={item.proxy_skipped}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Check CLIP A/B escalation readiness from the latest report artifacts."
        )
    )
    parser.add_argument(
        "--report-glob",
        default="eval_reports/clip-ab-*.json",
        help="Glob for CLIP A/B report artifacts.",
    )
    parser.add_argument(
        "--required-consecutive",
        type=int,
        default=2,
        help="How many latest reports must all satisfy the readiness criteria.",
    )
    parser.add_argument(
        "--min-cases",
        type=int,
        default=4,
        help="Minimum cases_count required per report.",
    )
    parser.add_argument(
        "--min-proxy-any-rate",
        type=float,
        default=0.90,
        help="Minimum proxy any-hit rate required per report.",
    )
    parser.add_argument(
        "--min-delta",
        type=float,
        default=0.50,
        help="Minimum any-hit delta (proxy - baseline) required per report.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    evaluations = _load_evaluations(
        report_glob=args.report_glob,
        min_cases=args.min_cases,
        min_proxy_any_rate=args.min_proxy_any_rate,
        min_delta=args.min_delta,
    )

    if len(evaluations) < args.required_consecutive:
        print("NO-GO")
        print(
            "Need at least "
            f"{args.required_consecutive} reports matching {args.report_glob}; "
            f"found {len(evaluations)}."
        )
        return 1

    latest = evaluations[-args.required_consecutive :]
    ready = all(item.passed for item in latest)

    print("GO" if ready else "NO-GO")
    print(
        f"Latest {args.required_consecutive} reports must each satisfy: "
        f"cases_count>={args.min_cases}, "
        f"proxy any_rate>={args.min_proxy_any_rate:.2f}, "
        f"delta>={args.min_delta:.2f}, "
        "zero errors/skips in both arms."
    )
    for item in latest:
        print(_format_evaluation(item))
        if item.reasons:
            print(f"  reasons: {'; '.join(item.reasons)}")

    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
