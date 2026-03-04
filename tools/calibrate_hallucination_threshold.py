from __future__ import annotations

import argparse
import glob
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CaseRow:
    passed: bool
    score: int
    risk: str


def _parse_case(raw: dict[str, Any]) -> CaseRow | None:
    try:
        passed = bool(raw["pass"])
        score = int(raw["score"])
        risk = str(raw["risk"]).lower()
    except (KeyError, TypeError, ValueError):
        return None
    if score < 0 or score > 100:
        return None
    return CaseRow(passed=passed, score=score, risk=risk)


def _load_cases(report_path: Path) -> list[CaseRow]:
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    cases_raw = payload.get("cases")
    if not isinstance(cases_raw, list):
        return []
    out: list[CaseRow] = []
    for item in cases_raw:
        if not isinstance(item, dict):
            continue
        row = _parse_case(item)
        if row is not None:
            out.append(row)
    return out


def _metrics(cases: list[CaseRow], threshold: int) -> dict[str, float]:
    tp = tn = fp = fn = 0
    for row in cases:
        predicted_pass = row.score >= threshold and row.risk != "high"
        if predicted_pass and row.passed:
            tp += 1
        elif predicted_pass and not row.passed:
            fp += 1
        elif not predicted_pass and row.passed:
            fn += 1
        else:
            tn += 1
    total = max(1, len(cases))
    accuracy = (tp + tn) / total
    precision = tp / max(1, (tp + fp))
    recall = tp / max(1, (tp + fn))
    return {
        "tp": float(tp),
        "tn": float(tn),
        "fp": float(fp),
        "fn": float(fn),
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
    }


def _select_threshold(cases: list[CaseRow]) -> tuple[int, dict[str, float]]:
    best_threshold = 0
    best_metrics = _metrics(cases, 0)
    best_key = (best_metrics["accuracy"], best_metrics["precision"], -best_threshold)
    for threshold in range(1, 101):
        m = _metrics(cases, threshold)
        key = (m["accuracy"], m["precision"], -threshold)
        if key > best_key:
            best_threshold = threshold
            best_metrics = m
            best_key = key
    return best_threshold, best_metrics


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Calibrate a hallucination min-score threshold from report artifacts.",
    )
    parser.add_argument(
        "--report-glob",
        default="eval_reports/hallucination-*.json",
        help="Glob for hallucination report JSON artifacts.",
    )
    parser.add_argument(
        "--out-json",
        default="eval_reports/hallucination-threshold-calibration.json",
        help="Output path for calibration summary JSON.",
    )
    args = parser.parse_args()

    report_paths = sorted(Path(p) for p in glob.glob(args.report_glob))
    if not report_paths:
        print(f"No reports found for glob: {args.report_glob}")
        return 1

    all_cases: list[CaseRow] = []
    for report in report_paths:
        all_cases.extend(_load_cases(report))
    if not all_cases:
        print("No valid case rows found in matching reports.")
        return 1

    threshold, summary = _select_threshold(all_cases)
    output = {
        "report_glob": args.report_glob,
        "report_count": len(report_paths),
        "case_count": len(all_cases),
        "recommended_min_acceptable_score": threshold,
        "metrics": summary,
        "note": (
            "Recommendation maximizes agreement with prior pass/fail labels using "
            "predict_pass = (score >= threshold and risk != 'high')."
        ),
    }

    out_path = Path(args.out_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print(f"Reports analyzed: {len(report_paths)}")
    print(f"Cases analyzed: {len(all_cases)}")
    print(f"Recommended min acceptable score: {threshold}")
    print(
        "Metrics: "
        f"accuracy={summary['accuracy']:.3f} "
        f"precision={summary['precision']:.3f} "
        f"recall={summary['recall']:.3f}"
    )
    print(f"Calibration summary: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
