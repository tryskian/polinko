"""Build a local multi-lane behaviour backlog from ChatGPT export search text."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SEARCH_INDEX_PREFIX = "window.CONVO_SEARCH_INDEX="


@dataclass(frozen=True)
class SignalPattern:
    label: str
    pattern: str

    @property
    def regex(self) -> re.Pattern[str]:
        return re.compile(self.pattern, re.IGNORECASE)


@dataclass(frozen=True)
class LaneDefinition:
    slug: str
    title: str
    description: str
    required_groups: tuple[tuple[SignalPattern, ...], ...]
    optional_patterns: tuple[SignalPattern, ...] = ()
    preferred_tags: tuple[str, ...] = ()
    min_score: int = 4


def _search_index_rows(search_index_js: Path) -> list[dict[str, Any]]:
    text = search_index_js.read_text(encoding="utf-8")
    start = text.find(SEARCH_INDEX_PREFIX)
    if start < 0:
        raise RuntimeError(f"Missing '{SEARCH_INDEX_PREFIX}' in {search_index_js}")
    payload = text[start + len(SEARCH_INDEX_PREFIX) :].strip()
    if payload.endswith(";"):
        payload = payload[:-1]
    rows = json.loads(payload)
    if not isinstance(rows, list):
        raise RuntimeError(f"Expected list payload in {search_index_js}")
    return rows


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def _normalize_family_title(title: str) -> str:
    value = _normalize_whitespace(title)
    return re.sub(r"^Branch\s+·\s+", "", value, flags=re.IGNORECASE).strip() or value


def _conversation_lookup(conversation_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for row in conversation_rows:
        conversation_id = str(row.get("conversation_id", "")).strip()
        if not conversation_id:
            continue
        lookup[conversation_id] = row
    return lookup


LANE_DEFINITIONS: tuple[LaneDefinition, ...] = (
    LaneDefinition(
        slug="co_reasoning",
        title="Co-Reasoning Reliability",
        description=(
            "Collaborative reasoning quality under fast constraint, tone, and abstraction shifts."
        ),
        required_groups=(
            (
                SignalPattern("co_reasoning", r"\bco-?reason(?:ing)?\b"),
                SignalPattern("working_style", r"\bworking style\b"),
                SignalPattern("collaboration_protocol", r"\bcollaboration protocol\b"),
                SignalPattern("constraint_retention", r"\bconstraint retention\b"),
                SignalPattern("meta_level_shift", r"\bmeta-?level shift\b"),
                SignalPattern("style_adaptation", r"\bstyle adaptation\b"),
                SignalPattern("playful_abstraction", r"\bplayful abstraction\b"),
                SignalPattern("grounding_drift", r"\bgrounding drift\b"),
                SignalPattern("mimicry", r"\bmimicry\b"),
            ),
        ),
        optional_patterns=(
            SignalPattern("constraint", r"\bconstraint(?:s)?\b"),
            SignalPattern("voice", r"\bvoice\b"),
            SignalPattern("cadence", r"\bcadence\b"),
            SignalPattern("persona", r"\bpersona\b"),
            SignalPattern("style", r"\bstyle\b"),
            SignalPattern("grounding", r"\bgrounding\b"),
            SignalPattern("shift", r"\bshift\b"),
        ),
        preferred_tags=("behaviour", "eval"),
    ),
    LaneDefinition(
        slug="operator_burden",
        title="Operator Burden Shift",
        description=(
            "Cases where direct execution collapses into commentary, hedging, or fuzzy advisory output."
        ),
        required_groups=(
            (
                SignalPattern("operator_burden", r"\boperator burden\b"),
                SignalPattern("minimal_control", r"\bminimal[- ]control\b"),
                SignalPattern("reference_binding", r"\breference binding\b"),
                SignalPattern("operation_fidelity", r"\boperation fidelity\b"),
                SignalPattern("decision_clarity", r"\bdecision clarity\b"),
                SignalPattern("advisory_commentary", r"\badvisory commentary\b"),
                SignalPattern("commentary_heavy", r"\bcommentary-heavy\b"),
                SignalPattern("configuration_heavy", r"\bconfiguration-heavy\b"),
                SignalPattern("direct_mapping", r"\bdirect mapping\b"),
                SignalPattern("match_a_to_b", r"\bmatch a to b\b"),
            ),
        ),
        optional_patterns=(
            SignalPattern("qualitative_judgement", r"\bqualitative judgement\b"),
            SignalPattern("fuzzy_percentages", r"\bfuzzy percentages?\b"),
            SignalPattern("hedging", r"\bhedg(?:e|ing)\b"),
            SignalPattern("direct_execution", r"\bdirect execution\b"),
            SignalPattern("commentary", r"\bcommentary\b"),
            SignalPattern("advisory", r"\badvis(?:e|ory)\b"),
        ),
        preferred_tags=("behaviour", "eval"),
    ),
    LaneDefinition(
        slug="hallucination_boundary",
        title="Hallucination Boundary",
        description=(
            "Evidence-boundary cases where certainty, invention, or unsupported claims need explicit gating."
        ),
        required_groups=(
            (
                SignalPattern("hallucination", r"\bhallucination(?: risk)?\b"),
                SignalPattern("unsupported_claim", r"\bunsupported claims?\b"),
                SignalPattern("grounding_gap", r"\bgrounding gap\b"),
                SignalPattern("explicit_uncertainty", r"\bexplicit uncertainty\b"),
                SignalPattern("fabricated", r"\bfabricat(?:ed|ion)\b"),
                SignalPattern("invented", r"\binvent(?:ed|ion)\b"),
                SignalPattern("certainty_outruns_evidence", r"\bcertainty outruns evidence\b"),
                SignalPattern("evidence_boundary", r"\bevidence boundar(?:y|ies)\b"),
                SignalPattern("low_signal_inference", r"\blow signal inference\b"),
            ),
        ),
        optional_patterns=(
            SignalPattern("inference", r"\binference\b"),
            SignalPattern("uncertainty", r"\buncertainty\b"),
            SignalPattern("verify", r"\bverif(?:y|ication)\b"),
            SignalPattern("evidence_missing", r"\bevidence missing\b"),
            SignalPattern("source_evidence", r"\bsource evidence\b"),
        ),
        preferred_tags=("behaviour", "eval", "policy"),
    ),
    LaneDefinition(
        slug="retrieval_grounding",
        title="Retrieval Grounding",
        description=(
            "Retrieval and file-search cases where grounding should stay tied to cited or source-backed evidence."
        ),
        required_groups=(
            (
                SignalPattern("retrieval", r"\bretrieval\b"),
                SignalPattern("file_search", r"\bfile search\b"),
                SignalPattern("file_search_snake", r"\bfile_search\b"),
                SignalPattern("citation", r"\bcitation(?:s)?\b"),
                SignalPattern("cite", r"\bcit(?:e|ed|ing)\b"),
                SignalPattern("memory_retrieval", r"\bmemory retrieval\b"),
                SignalPattern("grounded_in_source", r"\bgrounded in source\b"),
                SignalPattern("source_evidence", r"\bsource evidence\b"),
            ),
        ),
        optional_patterns=(
            SignalPattern("search_results", r"\bsearch results?\b"),
            SignalPattern("source", r"\bsource\b"),
            SignalPattern("recall", r"\brecall\b"),
            SignalPattern("evidence", r"\bevidence\b"),
        ),
        preferred_tags=("behaviour", "eval"),
    ),
    LaneDefinition(
        slug="ocr_confidence_boundary",
        title="OCR Confidence Boundary",
        description=(
            "OCR-adjacent cases where reliable transcription should help suppress low-signal inference or hallucination."
        ),
        required_groups=(
            (
                SignalPattern("ocr", r"\bocr(?:[- ]able)?\b"),
                SignalPattern("transcription", r"\btranscrib\w*\b"),
                SignalPattern("handwriting", r"\bhandwriting\b"),
                SignalPattern("cursive", r"\bcursive\b"),
            ),
            (
                SignalPattern("hallucination", r"\bhallucination(?: risk)?\b"),
                SignalPattern("unsupported_claim", r"\bunsupported claims?\b"),
                SignalPattern("grounding_gap", r"\bgrounding gap\b"),
                SignalPattern("explicit_uncertainty", r"\bexplicit uncertainty\b"),
                SignalPattern("certainty_outruns_evidence", r"\bcertainty outruns evidence\b"),
                SignalPattern("low_signal_inference", r"\blow signal inference\b"),
                SignalPattern("inference", r"\binference\b"),
                SignalPattern("source_evidence", r"\bsource evidence\b"),
            ),
        ),
        optional_patterns=(
            SignalPattern("evidence", r"\bevidence\b"),
            SignalPattern("confidence", r"\bconfidence\b"),
            SignalPattern("accuracy", r"\baccur(?:acy|ate)\b"),
            SignalPattern("verify", r"\bverif(?:y|ication)\b"),
        ),
        preferred_tags=("behaviour", "ocr", "policy"),
        min_score=7,
    ),
)


def _match_patterns(text: str, patterns: tuple[SignalPattern, ...]) -> list[SignalPattern]:
    return [pattern for pattern in patterns if pattern.regex.search(text)]


def _extract_snippet(text: str, patterns: list[SignalPattern], *, radius: int = 120) -> str:
    compact = _normalize_whitespace(text)
    if not compact:
        return ""
    for pattern in patterns:
        match = pattern.regex.search(compact)
        if match is None:
            continue
        start = max(0, match.start() - radius)
        end = min(len(compact), match.end() + radius)
        snippet = compact[start:end].strip()
        if start > 0:
            snippet = "..." + snippet
        if end < len(compact):
            snippet = snippet + "..."
        return snippet
    return compact[: 2 * radius].strip() + ("..." if len(compact) > 2 * radius else "")


def _score_lane(
    lane: LaneDefinition,
    *,
    title: str,
    text: str,
    tags: list[str],
) -> dict[str, Any] | None:
    haystack = _normalize_whitespace(f"{title}\n{text}")
    if not haystack:
        return None

    required_matches: list[SignalPattern] = []
    for group in lane.required_groups:
        group_matches = _match_patterns(haystack, group)
        if not group_matches:
            return None
        required_matches.append(group_matches[0])

    optional_matches = _match_patterns(haystack, lane.optional_patterns)
    score = 3 * len(required_matches) + len(optional_matches)
    preferred_tag_hits = [tag for tag in lane.preferred_tags if tag in tags]
    score += len(preferred_tag_hits)
    if score < lane.min_score:
        return None

    matched_patterns = required_matches + optional_matches
    snippet = _extract_snippet(haystack, matched_patterns)
    return {
        "score": score,
        "matched_terms": [pattern.label for pattern in matched_patterns],
        "preferred_tag_hits": preferred_tag_hits,
        "snippet": snippet,
    }


def build_backlog(
    *,
    search_rows: list[dict[str, Any]],
    conversation_rows: list[dict[str, Any]],
    limit_per_lane: int = 25,
) -> dict[str, Any]:
    conversation_lookup = _conversation_lookup(conversation_rows)
    lanes_payload: list[dict[str, Any]] = []

    for lane in LANE_DEFINITIONS:
        candidates: list[dict[str, Any]] = []
        for row in search_rows:
            conversation_id = str(row.get("id", "")).strip()
            if not conversation_id:
                continue
            title = str(row.get("title", "")).strip()
            text = str(row.get("text", "")).strip()
            conversation_meta = conversation_lookup.get(conversation_id, {})
            tags = list(conversation_meta.get("tags", []))
            lane_score = _score_lane(lane, title=title, text=text, tags=tags)
            if lane_score is None:
                continue

            candidates.append(
                {
                    "conversation_id": conversation_id,
                    "title": title,
                    "family_title": _normalize_family_title(title),
                    "score": lane_score["score"],
                    "matched_terms": lane_score["matched_terms"],
                    "preferred_tag_hits": lane_score["preferred_tag_hits"],
                    "snippet": lane_score["snippet"],
                    "tags": tags,
                    "attachment_count": int(conversation_meta.get("attachment_count", 0)),
                    "has_attachment": bool(conversation_meta.get("has_attachment", False)),
                    "already_tagged": bool(conversation_meta),
                }
            )

        candidates.sort(
            key=lambda row: (
                -int(row["score"]),
                0 if row["already_tagged"] else 1,
                -int(row["attachment_count"]),
                str(row["title"]).lower(),
                str(row["conversation_id"]),
            )
        )
        family_payload: list[dict[str, Any]] = []
        family_map: dict[str, dict[str, Any]] = {}
        for candidate in candidates:
            family_key = str(candidate["family_title"]).lower()
            family_entry = family_map.get(family_key)
            if family_entry is None:
                family_entry = {
                    "family_title": candidate["family_title"],
                    "score": candidate["score"],
                    "matched_terms": list(candidate["matched_terms"]),
                    "preferred_tag_hits": list(candidate["preferred_tag_hits"]),
                    "snippet": candidate["snippet"],
                    "tags": list(candidate["tags"]),
                    "attachment_count": candidate["attachment_count"],
                    "has_attachment": candidate["has_attachment"],
                    "already_tagged": candidate["already_tagged"],
                    "variant_count": 0,
                    "conversation_ids": [],
                    "titles": [],
                }
                family_map[family_key] = family_entry
                family_payload.append(family_entry)
            family_entry["variant_count"] += 1
            family_entry["conversation_ids"].append(candidate["conversation_id"])
            if candidate["title"] not in family_entry["titles"]:
                family_entry["titles"].append(candidate["title"])
            family_entry["score"] = max(int(family_entry["score"]), int(candidate["score"]))
            family_entry["attachment_count"] = max(
                int(family_entry["attachment_count"]),
                int(candidate["attachment_count"]),
            )
            family_entry["has_attachment"] = family_entry["has_attachment"] or candidate["has_attachment"]
            family_entry["already_tagged"] = family_entry["already_tagged"] or candidate["already_tagged"]
            for tag in candidate["tags"]:
                if tag not in family_entry["tags"]:
                    family_entry["tags"].append(tag)
            for term in candidate["matched_terms"]:
                if term not in family_entry["matched_terms"]:
                    family_entry["matched_terms"].append(term)
            for tag in candidate["preferred_tag_hits"]:
                if tag not in family_entry["preferred_tag_hits"]:
                    family_entry["preferred_tag_hits"].append(tag)

        family_payload.sort(
            key=lambda row: (
                -int(row["score"]),
                0 if row["already_tagged"] else 1,
                -int(row["variant_count"]),
                -int(row["attachment_count"]),
                str(row["family_title"]).lower(),
            )
        )
        lanes_payload.append(
            {
                "lane": lane.slug,
                "title": lane.title,
                "description": lane.description,
                "candidate_count": len(candidates),
                "family_count": len(family_payload),
                "candidates": family_payload[:limit_per_lane],
            }
        )

    return {
        "summary": {
            "search_conversations": len(search_rows),
            "indexed_behaviour_conversations": len(conversation_rows),
            "lanes": [
                {
                    "lane": lane_payload["lane"],
                    "candidate_count": lane_payload["candidate_count"],
                }
                for lane_payload in lanes_payload
            ],
        },
        "lanes": lanes_payload,
    }


def _markdown_report(backlog: dict[str, Any]) -> str:
    lines = [
        "# Behaviour Export Backlog",
        "",
        "Local-only candidate backlog mined from ChatGPT export search text.",
        "",
    ]
    summary = backlog.get("summary", {})
    lines.append(f"- search conversations: `{summary.get('search_conversations', 0)}`")
    lines.append(
        f"- indexed behaviour conversations: `{summary.get('indexed_behaviour_conversations', 0)}`"
    )
    lines.append("")

    for lane in backlog.get("lanes", []):
        lines.append(f"## {lane['title']}")
        lines.append("")
        lines.append(lane["description"])
        lines.append("")
        lines.append(f"- candidate_count: `{lane['candidate_count']}`")
        lines.append(f"- family_count: `{lane['family_count']}`")
        lines.append("")
        for candidate in lane.get("candidates", []):
            tags = ", ".join(candidate.get("tags", [])) or "untagged"
            matched = ", ".join(candidate.get("matched_terms", []))
            lines.append(
                f"- `{candidate['family_title']}` | score=`{candidate['score']}` | variants=`{candidate['variant_count']}` | attachments=`{candidate['attachment_count']}` | tags=`{tags}`"
            )
            lines.append(f"  - conversation_ids: `{', '.join(candidate['conversation_ids'][:5])}`")
            if candidate.get("titles"):
                lines.append(f"  - titles: `{', '.join(candidate['titles'][:3])}`")
            lines.append(f"  - matched: `{matched}`")
            if candidate.get("snippet"):
                lines.append(f"  - snippet: {candidate['snippet']}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a local multi-lane behaviour backlog from ChatGPT export search text."
    )
    parser.add_argument(
        "--export-root",
        required=True,
        help="Path to the ChatGPT export root (must contain conversations/html/search_index.js).",
    )
    parser.add_argument(
        "--conversation-index",
        default=".local/eval_cases/cgpt_export_behaviour_eval_conversations.json",
        help="Path to the indexed behaviour conversation metadata JSON.",
    )
    parser.add_argument(
        "--output-json",
        default=".local/eval_cases/behaviour_export_backlog.json",
        help="Output JSON path for the mined backlog.",
    )
    parser.add_argument(
        "--output-md",
        default=".local/eval_cases/behaviour_export_backlog.md",
        help="Output Markdown path for the mined backlog.",
    )
    parser.add_argument(
        "--limit-per-lane",
        type=int,
        default=25,
        help="Maximum number of candidates to keep per lane (default: 25).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    export_root = Path(args.export_root).expanduser().resolve()
    conversation_index_path = Path(args.conversation_index).expanduser().resolve()
    output_json = Path(args.output_json).expanduser().resolve()
    output_md = Path(args.output_md).expanduser().resolve()

    search_rows = _search_index_rows(export_root / "conversations" / "html" / "search_index.js")
    conversation_rows = _load_json(conversation_index_path)
    backlog = build_backlog(
        search_rows=search_rows,
        conversation_rows=conversation_rows,
        limit_per_lane=args.limit_per_lane,
    )

    _write_json(output_json, backlog)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(_markdown_report(backlog), encoding="utf-8")

    print(f"export_root={export_root}")
    print(f"conversation_index={conversation_index_path}")
    print(f"output_json={output_json}")
    print(f"output_md={output_md}")
    for lane in backlog["summary"]["lanes"]:
        print(f"{lane['lane']}={lane['candidate_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
