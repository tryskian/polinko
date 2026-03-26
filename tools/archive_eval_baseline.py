from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

RAW_EVIDENCE_EXCLUDE_TOP_LEVEL = {"archive", ".DS_Store", ".gitkeep"}
ARCHIVE_EXCLUDE_TOP_LEVEL = {"baseline", ".DS_Store", ".gitkeep"}


@dataclass(frozen=True)
class ArchiveResult:
    run_id: str
    raw_archive_dir: Path
    eval_reports_archive_dir: Path
    moved_raw_count: int
    moved_report_count: int
    consolidated_raw_archive_count: int
    consolidated_report_archive_count: int


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


def _next_available_path(path: Path) -> Path:
    if not path.exists():
        return path
    suffix = "".join(path.suffixes)
    stem = path.name[: -len(suffix)] if suffix else path.name
    index = 2
    while True:
        candidate = path.parent / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def _move_within_root(*, source: Path, source_root: Path, archive_root: Path) -> None:
    rel = source.relative_to(source_root)
    destination = archive_root / rel
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))


def _consolidate_archive_root(*, archive_root: Path, baseline_root: Path) -> int:
    if not archive_root.exists():
        return 0
    moved = 0
    history_root = baseline_root / "history"
    for item in sorted(archive_root.iterdir()):
        if item.name in ARCHIVE_EXCLUDE_TOP_LEVEL:
            continue
        history_root.mkdir(parents=True, exist_ok=True)
        destination = _next_available_path(history_root / item.name)
        shutil.move(str(item), str(destination))
        moved += 1
    return moved


def _rotate_latest_into_history(*, latest_dir: Path, baseline_root: Path, run_id: str) -> None:
    if not latest_dir.exists():
        return
    has_content = any(latest_dir.iterdir())
    if not has_content:
        latest_dir.rmdir()
        return
    history_root = baseline_root / "history"
    history_root.mkdir(parents=True, exist_ok=True)
    destination = _next_available_path(history_root / f"latest-before-{run_id}")
    shutil.move(str(latest_dir), str(destination))


def archive_eval_baseline(
    *,
    raw_evidence_root: Path,
    eval_reports_root: Path,
    run_id: str,
) -> ArchiveResult:
    raw_archive_root = raw_evidence_root / "archive"
    raw_baseline_root = raw_archive_root / "baseline"
    raw_archive_dir = raw_baseline_root / "latest"
    reports_archive_root = eval_reports_root / "archive"
    reports_baseline_root = reports_archive_root / "baseline"
    eval_reports_archive_dir = reports_baseline_root / "latest"

    raw_entries = _iter_raw_entries(raw_evidence_root)
    report_entries = _iter_eval_report_files(eval_reports_root)

    moved_raw_count = 0
    moved_report_count = 0
    consolidated_raw_archive_count = _consolidate_archive_root(
        archive_root=raw_archive_root,
        baseline_root=raw_baseline_root,
    )
    consolidated_report_archive_count = _consolidate_archive_root(
        archive_root=reports_archive_root,
        baseline_root=reports_baseline_root,
    )

    if raw_entries:
        _rotate_latest_into_history(
            latest_dir=raw_archive_dir,
            baseline_root=raw_baseline_root,
            run_id=run_id,
        )
        raw_archive_dir.mkdir(parents=True, exist_ok=True)
        for source in raw_entries:
            _move_within_root(source=source, source_root=raw_evidence_root, archive_root=raw_archive_dir)
            moved_raw_count += 1

    if report_entries:
        _rotate_latest_into_history(
            latest_dir=eval_reports_archive_dir,
            baseline_root=reports_baseline_root,
            run_id=run_id,
        )
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
        consolidated_raw_archive_count=consolidated_raw_archive_count,
        consolidated_report_archive_count=consolidated_report_archive_count,
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
    print(f"consolidated_raw_archive_entries={result.consolidated_raw_archive_count}")
    print(f"consolidated_report_archive_entries={result.consolidated_report_archive_count}")
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
