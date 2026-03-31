"""Build a strict handwriting benchmark case set from mined transcript OCR data."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CONFIDENCE_RANK = {"high": 2, "medium": 1, "low": 0}


@dataclass(frozen=True)
class Candidate:
    image_path: str
    confidence: str
    anchor_terms_count: int
    chosen_phrase_count: int
    conversation_id: str

    @property
    def rank_key(self) -> tuple[int, int, int, str]:
        return (
            CONFIDENCE_RANK.get(self.confidence, 0),
            self.anchor_terms_count,
            self.chosen_phrase_count,
            self.conversation_id,
        )


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected object JSON: {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _iter_candidates(review_payload: dict[str, Any]) -> list[Candidate]:
    episodes = review_payload.get("episodes")
    if not isinstance(episodes, list):
        return []
    candidates: list[Candidate] = []
    for row in episodes:
        if not isinstance(row, dict):
            continue
        if str(row.get("lane", "")).strip() != "handwriting":
            continue
        if str(row.get("emit_status", "")).strip() != "emitted":
            continue
        confidence = str(row.get("confidence", "low")).strip().lower()
        if CONFIDENCE_RANK.get(confidence, 0) <= 0:
            continue
        image_path = str(row.get("image_path", "")).strip()
        if not image_path:
            continue
        candidates.append(
            Candidate(
                image_path=image_path,
                confidence=confidence,
                anchor_terms_count=int(row.get("anchor_terms_count", 0) or 0),
                chosen_phrase_count=len(row.get("chosen_phrases", []) or []),
                conversation_id=str(row.get("conversation_id", "")).strip(),
            )
        )
    dedup: dict[str, Candidate] = {}
    for candidate in sorted(candidates, key=lambda item: item.rank_key, reverse=True):
        dedup.setdefault(candidate.image_path, candidate)
    return list(dedup.values())


def build_handwriting_benchmark_cases(
    *,
    review_path: Path,
    handwriting_cases_path: Path,
    output_cases_path: Path,
    top_k: int,
    min_anchor_terms: int,
) -> dict[str, int]:
    review_payload = _load_json(review_path)
    handwriting_payload = _load_json(handwriting_cases_path)
    source_cases = handwriting_payload.get("cases")
    if not isinstance(source_cases, list):
        raise RuntimeError(f"Expected 'cases' array in {handwriting_cases_path}")

    case_by_image_path: dict[str, dict[str, Any]] = {}
    for case in source_cases:
        if not isinstance(case, dict):
            continue
        image_path = str(case.get("image_path", "")).strip()
        if not image_path:
            continue
        case_by_image_path[image_path] = case

    ranked = sorted(_iter_candidates(review_payload), key=lambda item: item.rank_key, reverse=True)
    selected: list[dict[str, Any]] = []
    for candidate in ranked:
        if top_k > 0 and len(selected) >= top_k:
            break
        base_case = case_by_image_path.get(candidate.image_path)
        if base_case is None:
            continue
        anchor_count = len(base_case.get("must_contain_any", []) or [])
        if anchor_count < min_anchor_terms:
            continue
        selected.append(base_case)

    if not selected and ranked:
        fallback_case = case_by_image_path.get(ranked[0].image_path)
        if fallback_case is not None:
            selected.append(fallback_case)

    output_payload = {
        "cases": selected,
        "metadata": {
            "source_review": str(review_path),
            "source_handwriting_cases": str(handwriting_cases_path),
            "top_k": top_k,
            "min_anchor_terms": min_anchor_terms,
            "candidate_count": len(ranked),
            "selected_count": len(selected),
        },
    }
    _write_json(output_cases_path, output_payload)
    return {
        "candidate_count": len(ranked),
        "selected_count": len(selected),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a strict handwriting benchmark case set from transcript-mined OCR episodes."
    )
    parser.add_argument(
        "--review",
        default=".local/eval_cases/ocr_transcript_cases_review.json",
        help="Path to OCR transcript review episodes JSON.",
    )
    parser.add_argument(
        "--handwriting-cases",
        default=".local/eval_cases/ocr_handwriting_from_transcripts.json",
        help="Path to handwriting OCR cases JSON.",
    )
    parser.add_argument(
        "--output-cases",
        default=".local/eval_cases/ocr_handwriting_benchmark_cases.json",
        help="Path to output handwriting benchmark cases JSON.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=6,
        help="Max number of benchmark cases to keep (0 keeps all).",
    )
    parser.add_argument(
        "--min-anchor-terms",
        type=int,
        default=3,
        help="Minimum must_contain_any term count for strict selection.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_handwriting_benchmark_cases(
        review_path=Path(args.review).expanduser().resolve(),
        handwriting_cases_path=Path(args.handwriting_cases).expanduser().resolve(),
        output_cases_path=Path(args.output_cases).expanduser().resolve(),
        top_k=int(args.top_k),
        min_anchor_terms=int(args.min_anchor_terms),
    )
    print(f"candidate_count={summary['candidate_count']}")
    print(f"selected_count={summary['selected_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
