from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

RAW_EVIDENCE_EXCLUDE_TOP_LEVEL = {"archive", ".DS_Store", ".gitkeep"}


@dataclass(frozen=True)
class ArchiveResult:
    run_id: str
    raw_archive_dir: Path
    eval_reports_archive_dir: Path
    moved_raw_count: int
    moved_report_count: int


def _default_run_id() -> str:
    return datetime.now(UTC).strftime("%Y%m%d-%H%M%S")


def _iter_raw_entries(raw_root: Path) -> list[Path]:
    if not raw_root.exists():
        return []
    entries: list[Path] = []
    for item in sorted(raw_root.iterdir()):
        if item.name in RAW_EVIDENCE_EXCLUDE_TOP_LEVEL:
            continue
        entries.append(item)
    return entries


def _iter_eval_report_files(eval_reports_root: Path) -> list[Path]:
    if not eval_reports_root.exists():
        return []
    entries: list[Path] = []
    for item in sorted(eval_reports_root.iterdir()):
        if item.name in {".DS_Store", ".gitkeep", "archive"}:
            continue
        if item.is_file():
            entries.append(item)
    return entries


def _move_within_root(*, source: Path, source_root: Path, archive_root: Path) -> None:
    rel = source.relative_to(source_root)
    destination = archive_root / rel
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))


def archive_eval_baseline(
    *,
    raw_evidence_root: Path,
    eval_reports_root: Path,
    run_id: str,
) -> ArchiveResult:
    raw_archive_root = raw_evidence_root / "archive"
    raw_archive_dir = raw_archive_root / f"baseline-reset-{run_id}"
    reports_archive_root = eval_reports_root / "archive"
    eval_reports_archive_dir = reports_archive_root / f"baseline-reset-{run_id}"

    raw_entries = _iter_raw_entries(raw_evidence_root)
    report_entries = _iter_eval_report_files(eval_reports_root)

    moved_raw_count = 0
    moved_report_count = 0

    if raw_entries:
        raw_archive_dir.mkdir(parents=True, exist_ok=True)
        for source in raw_entries:
            _move_within_root(source=source, source_root=raw_evidence_root, archive_root=raw_archive_dir)
            moved_raw_count += 1

    if report_entries:
        eval_reports_archive_dir.mkdir(parents=True, exist_ok=True)
        for source in report_entries:
            _move_within_root(source=source, source_root=eval_reports_root, archive_root=eval_reports_archive_dir)
            moved_report_count += 1

    return ArchiveResult(
        run_id=run_id,
        raw_archive_dir=raw_archive_dir,
        eval_reports_archive_dir=eval_reports_archive_dir,
        moved_raw_count=moved_raw_count,
        moved_report_count=moved_report_count,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Archive current eval evidence and report artefacts into timestamped baseline-reset folders.",
    )
    parser.add_argument(
        "--raw-evidence-root",
        default="docs/portfolio/raw_evidence",
        help="Raw evidence root; every top-level entry except archive/* is moved.",
    )
    parser.add_argument(
        "--eval-reports-root",
        default="eval_reports",
        help="Eval reports root with top-level report/log files.",
    )
    parser.add_argument(
        "--run-id",
        default=_default_run_id(),
        help="Archive run id suffix (default: UTC timestamp).",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = archive_eval_baseline(
        raw_evidence_root=Path(args.raw_evidence_root),
        eval_reports_root=Path(args.eval_reports_root),
        run_id=str(args.run_id),
    )
    print(f"run_id={result.run_id}")
    print(f"moved_raw_entries={result.moved_raw_count}")
    print(f"moved_report_entries={result.moved_report_count}")
    if result.moved_raw_count > 0:
        print(f"raw_archive_dir={result.raw_archive_dir}")
    else:
        print("raw_archive_dir=(no moves)")
    if result.moved_report_count > 0:
        print(f"eval_reports_archive_dir={result.eval_reports_archive_dir}")
    else:
        print("eval_reports_archive_dir=(no moves)")


if __name__ == "__main__":
    main()
