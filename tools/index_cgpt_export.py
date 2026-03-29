"""Build local indexes from a ChatGPT data export for OCR/eval curation."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

SEARCH_INDEX_PREFIX = "window.CONVO_SEARCH_INDEX="

IMAGE_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".heic",
    ".heif",
    ".tif",
    ".tiff",
    ".bmp",
    ".gif",
}

TAG_PATTERNS: dict[str, re.Pattern[str]] = {
    "eval": re.compile(
        r"\beval\b|evaluation|benchmark|rubric|pass\s*/\s*fail|binary\s+gate|quality\s+gate",
        re.IGNORECASE,
    ),
    "behaviour": re.compile(
        r"behaviou?r|style|cadence|voice|persona|co-?reasoning|reasoning\s+loop",
        re.IGNORECASE,
    ),
    "ocr": re.compile(r"\bocr\b|handwriting|cursive|transcrib", re.IGNORECASE),
    "policy": re.compile(r"policy|guardrail|safety|compliance", re.IGNORECASE),
}

OCR_PRIORITY_HINTS = re.compile(
    r"hand|curs|journal|note|scan|ink|scrib|manifold|theory|img_|screenshot",
    re.IGNORECASE,
)

ASSET_TOKEN_RE = re.compile(r"^(file[_-][^-]+)", re.IGNORECASE)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _search_index_by_id(search_index_js: Path) -> dict[str, dict[str, Any]]:
    text = search_index_js.read_text(encoding="utf-8")
    start = text.find(SEARCH_INDEX_PREFIX)
    if start < 0:
        raise RuntimeError(f"Missing '{SEARCH_INDEX_PREFIX}' in {search_index_js}")
    payload = text[start + len(SEARCH_INDEX_PREFIX) :].strip()
    if payload.endswith(";"):
        payload = payload[:-1]
    records = json.loads(payload)
    by_id: dict[str, dict[str, Any]] = {}
    for row in records:
        conversation_id = str(row.get("id", "")).strip()
        if not conversation_id:
            continue
        by_id[conversation_id] = {
            "title": str(row.get("title", "")),
            "text": str(row.get("text", "")),
            "create_time": row.get("create_time"),
            "update_time": row.get("update_time"),
        }
    return by_id


def _asset_indexes(assets_root: Path) -> tuple[dict[str, Path], dict[str, list[Path]]]:
    by_name: dict[str, Path] = {}
    by_token: dict[str, list[Path]] = defaultdict(list)
    for path in sorted(assets_root.iterdir()):
        if not path.is_file():
            continue
        by_name[path.name.lower()] = path
        match = ASSET_TOKEN_RE.match(path.name)
        if match:
            by_token[match.group(1).lower()].append(path)
    return by_name, by_token


def _asset_id_variants(asset_id: str) -> list[str]:
    value = asset_id.strip().lower()
    if not value:
        return []
    variants = {value}
    if value.startswith("file-"):
        variants.add("file_" + value[5:])
    if value.startswith("file_"):
        variants.add("file-" + value[5:])
    return sorted(variants)


def _resolve_asset_paths(
    asset_name: str,
    asset_id: str,
    by_name: dict[str, Path],
    by_token: dict[str, list[Path]],
) -> list[str]:
    resolved: list[str] = []
    if asset_name:
        found = by_name.get(asset_name.lower())
        if found is not None:
            resolved.append(str(found))
    for variant in _asset_id_variants(asset_id):
        for path in by_token.get(variant, []):
            resolved.append(str(path))
    return _dedupe_preserve_order(resolved)


def _conversation_tags(title: str, text: str) -> list[str]:
    haystack = f"{title}\n{text}"
    return [name for name, rx in TAG_PATTERNS.items() if rx.search(haystack)]


def _ocr_priority_score(
    *,
    title: str,
    asset_name: str,
    tags: list[str],
    width: int | None,
    height: int | None,
) -> int:
    score = 0
    if OCR_PRIORITY_HINTS.search(asset_name):
        score += 2
    if OCR_PRIORITY_HINTS.search(title):
        score += 1
    if "ocr" in tags:
        score += 1
    if width and height and min(width, height) < 500:
        score += 1
    return score


def build_indexes(export_root: Path, output_dir: Path) -> dict[str, int]:
    conversations_dir = export_root / "conversations"
    assets_dir = export_root / "assets"
    search_index_js = export_root / "conversations" / "html" / "search_index.js"

    if not conversations_dir.is_dir():
        raise RuntimeError(f"Missing conversations directory: {conversations_dir}")
    if not assets_dir.is_dir():
        raise RuntimeError(f"Missing assets directory: {assets_dir}")
    if not search_index_js.is_file():
        raise RuntimeError(f"Missing search index file: {search_index_js}")

    search_by_id = _search_index_by_id(search_index_js)
    by_name, by_token = _asset_indexes(assets_dir)

    attachments: list[dict[str, Any]] = []

    conversation_files = sorted(conversations_dir.glob("*.json"))
    for conversation_path in conversation_files:
        convo = _load_json(conversation_path)
        conversation_id = str(convo.get("conversation_id", "")).strip() or conversation_path.stem
        search_meta = search_by_id.get(conversation_id, {})
        title = str(convo.get("title", "")).strip() or str(search_meta.get("title", "")).strip()
        search_text = str(search_meta.get("text", ""))
        tags = _conversation_tags(title, search_text)
        mapping = convo.get("mapping") or {}
        if not isinstance(mapping, dict):
            continue

        for node in mapping.values():
            if not isinstance(node, dict):
                continue
            message = node.get("message")
            if not isinstance(message, dict):
                continue
            metadata = message.get("metadata") or {}
            if not isinstance(metadata, dict):
                continue
            attachment_rows = metadata.get("attachments") or []
            if not isinstance(attachment_rows, list):
                continue

            message_id = message.get("id")
            message_role = ((message.get("author") or {}).get("role") or "")
            message_create_time = message.get("create_time")

            for attachment in attachment_rows:
                if not isinstance(attachment, dict):
                    continue
                asset_id = str(attachment.get("id", "")).strip()
                asset_name = str(attachment.get("name", "")).strip()
                resolved_paths = _resolve_asset_paths(asset_name, asset_id, by_name, by_token)
                attachments.append(
                    {
                        "conversation_id": conversation_id,
                        "conversation_json": str(conversation_path),
                        "title": title,
                        "message_id": message_id,
                        "message_role": message_role,
                        "message_create_time": message_create_time,
                        "search_text_present": bool(search_text),
                        "conversation_tags": tags,
                        "asset_id": asset_id,
                        "asset_name": asset_name,
                        "mime_type": str(attachment.get("mime_type", "")).strip(),
                        "size": attachment.get("size"),
                        "width": attachment.get("width"),
                        "height": attachment.get("height"),
                        "asset_paths": resolved_paths,
                    }
                )

    deduped_attachments: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str, str, str]] = set()
    for row in attachments:
        key = (
            str(row.get("conversation_id", "")),
            str(row.get("message_id", "")),
            str(row.get("asset_id", "")),
            str(row.get("asset_name", "")),
        )
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped_attachments.append(row)

    attachments = deduped_attachments
    missing_attachments = [row for row in attachments if not row.get("asset_paths")]

    conversation_index: dict[str, dict[str, Any]] = {}
    for row in attachments:
        conversation_id = str(row["conversation_id"])
        entry = conversation_index.setdefault(
            conversation_id,
            {
                "conversation_id": conversation_id,
                "title": str(row.get("title", "")),
                "tags": list(row.get("conversation_tags", [])),
                "attachment_count": 0,
                "has_attachment": False,
            },
        )
        entry["attachment_count"] += 1
        entry["has_attachment"] = True
        if not entry["title"] and row.get("title"):
            entry["title"] = str(row["title"])
        if not entry["tags"] and row.get("conversation_tags"):
            entry["tags"] = list(row["conversation_tags"])

    tagged_conversations = [
        entry for entry in conversation_index.values() if entry.get("tags")
    ]
    tagged_conversations.sort(
        key=lambda entry: (
            0 if {"eval", "behaviour"} & set(entry.get("tags", [])) else 1,
            -int(entry.get("attachment_count", 0)),
            str(entry.get("title", "")).lower(),
        )
    )

    tagged_ids = {row["conversation_id"] for row in tagged_conversations}
    tagged_attachments = [row for row in attachments if row["conversation_id"] in tagged_ids]

    ocr_ready: list[dict[str, Any]] = []
    for row in tagged_attachments:
        if str(row.get("message_role", "")) != "user":
            continue
        asset_paths = list(row.get("asset_paths") or [])
        if not asset_paths:
            continue
        image_path = Path(asset_paths[0])
        if image_path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        if not image_path.is_file():
            continue

        tags = list(row.get("conversation_tags") or [])
        title = str(row.get("title", ""))
        asset_name = str(row.get("asset_name", ""))
        width = row.get("width")
        height = row.get("height")
        priority_score = _ocr_priority_score(
            title=title,
            asset_name=asset_name,
            tags=tags,
            width=width if isinstance(width, int) else None,
            height=height if isinstance(height, int) else None,
        )

        ocr_ready.append(
            {
                "conversation_id": row["conversation_id"],
                "title": title,
                "conversation_tags": tags,
                "asset_name": asset_name,
                "asset_id": row.get("asset_id"),
                "image_path": str(image_path),
                "size": row.get("size"),
                "width": width,
                "height": height,
                "priority_score": priority_score,
            }
        )

    ocr_ready.sort(
        key=lambda row: (
            -int(row.get("priority_score", 0)),
            str(row.get("title", "")).lower(),
            str(row.get("asset_name", "")).lower(),
        )
    )

    ocr_ready_dedup: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for row in ocr_ready:
        image_path = str(row.get("image_path", ""))
        if image_path in seen_paths:
            continue
        seen_paths.add(image_path)
        ocr_ready_dedup.append(row)

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "cgpt_export_attachment_index.json", attachments)
    _write_json(output_dir / "cgpt_export_attachment_missing.json", missing_attachments)
    _write_json(
        output_dir / "cgpt_export_behaviour_eval_conversations.json",
        tagged_conversations,
    )
    _write_json(
        output_dir / "cgpt_export_behaviour_eval_attachments.json",
        tagged_attachments,
    )
    _write_json(output_dir / "cgpt_export_behaviour_eval_ocr_ready.json", ocr_ready)
    _write_json(
        output_dir / "cgpt_export_behaviour_eval_ocr_ready_dedup.json",
        ocr_ready_dedup,
    )

    return {
        "conversation_files": len(conversation_files),
        "attachments": len(attachments),
        "missing_attachments": len(missing_attachments),
        "tagged_conversations": len(tagged_conversations),
        "tagged_attachments": len(tagged_attachments),
        "ocr_ready": len(ocr_ready),
        "ocr_ready_dedup": len(ocr_ready_dedup),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build OCR/eval-friendly indexes from a ChatGPT data export."
    )
    parser.add_argument(
        "--export-root",
        required=True,
        help="Path to export root (must contain conversations/, conversations/html/search_index.js, assets/).",
    )
    parser.add_argument(
        "--output-dir",
        default=".local/eval_cases",
        help="Output directory for generated JSON files (default: .local/eval_cases).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    export_root = Path(args.export_root).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    summary = build_indexes(export_root, output_dir)
    print(f"export_root={export_root}")
    print(f"output_dir={output_dir}")
    for key in (
        "conversation_files",
        "attachments",
        "missing_attachments",
        "tagged_conversations",
        "tagged_attachments",
        "ocr_ready",
        "ocr_ready_dedup",
    ):
        print(f"{key}={summary[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
