"""Mine OCR eval cases from ChatGPT export transcripts with correction signals."""

from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

OCR_INTENT_PATTERN = (
    r"what does (this|it) say|what(?:'s| is) written|can you read|read (this|it)|\btranscrib\w*|\bocr\b|\bocr(?:[-\s]?able)?\b|\bbinareyes\b|\bnew\s+drop\b|\b(?:s|sq)cribbles?\s+and\s+bibbles?\b|\bpeanut\s+cursive\b|\bscratched\s+out\b"
)
ASK_RX = re.compile(OCR_INTENT_PATTERN, re.IGNORECASE)
HANDWRITING_HINT_RX = re.compile(
    r"\bhandwrit\w*\b|\bcursive\b|\bscript\b|\bnotebook\b|\bsketchbook\b|\bjournal\b|\bink\b|\bpen\b|\bmanifold\b",
    re.IGNORECASE,
)
TYPED_HINT_RX = re.compile(
    r"\btyped\b|\bprinted\b|\bfont\b|\bui\b|screen ?shot|\bterminal\b|\bcode\b|\bdocument\b|\bpdf\b",
    re.IGNORECASE,
)
ILLUSTRATION_HINT_RX = re.compile(
    r"illustration|diagram|flow ?chart|flowchart|graph|node|edge|arrow|whiteboard|sketch|drawing|doodle|wireframe|figure|geometry|shape|topolog\w*|trapezi\w*|prism",
    re.IGNORECASE,
)
CAMERA_IMAGE_NAME_RX = re.compile(r"(?:^|[-_])(img|dsc)[_-]\d{3,}", re.IGNORECASE)
SCREENSHOT_NAME_RX = re.compile(r"(?:^|[-_])screenshot(?:[-_]|$)", re.IGNORECASE)
UNSTABLE_SOURCE_NAMES = {
    # Quarantined from strict active set: repeatedly flaky in transcript
    # stability runs due highly variable OCR extraction on these crops.
    "file_00000000b01871fdac46c44584b95d6a-sanitized.png",
    "file_0000000047f871f7af65c1ce3955cc2e-sanitized.png",
}
ANCHOR_STOPWORDS = {
    "the",
    "and",
    "from",
    "your",
    "with",
    "that",
    "this",
    "here",
    "just",
    "basically",
    "you",
    "ive",
    "we",
    "is",
    "are",
    "was",
    "were",
    "of",
    "its",
    "it",
    "as",
    "not",
}
ANCHOR_META_WORDS = {
    "transcription",
    "overlay",
    "interpretation",
    "binaric",
    "exposure",
    "peanut",
    "locked",
    "render",
    "preserving",
    "rhythm",
    "logic",
    "here",
    "just",
    "central",
    "glyph",
    "circle",
    "grid",
    "wave",
    "square",
    "frame",
    "clarity",
    "perfect",
    "binareyes",
    "fysics",
    "page",
    "partial",
    "single",
    "line",
    "cropped",
    "continuation",
    "previous",
    "updated",
    "accessible",
    "entry",
    "conversation",
    "found",
    "screenshot",
    "html",
}
ANCHOR_WEAK_WORDS = {
    "there",
    "seems",
    "something",
    "without",
    "inside",
    "note",
    "real",
    "reads",
    "read",
    "more",
    "find",
    "chat",
}
ORDERED_FALLBACK_SKIP_WORDS = {
    "there",
    "seems",
    "without",
    "inside",
    "note",
    "real",
    "reads",
    "read",
    "more",
    "page",
    "partial",
    "single",
    "line",
    "cropped",
    "continuation",
    "previous",
    "updated",
    "accessible",
    "entry",
    "restore",
    "deleted",
    "conversation",
    "found",
    "screenshot",
    "html",
    "find",
    "chat",
}
ANCHOR_FILETYPE_WORDS = {
    "jpeg",
    "jpg",
    "png",
    "webp",
    "gif",
    "tiff",
    "heic",
    "pdf",
}
ANCHOR_GENERIC_WORDS = {
    "high",
    "activity",
    "phase",
    "entire",
    "control",
    "variable",
    "advanced",
    "inherited",
    "existing",
    "allows",
    "allow",
    "clearly",
    "first",
    "image",
    "also",
    "still",
    "connection",
    "margin",
    "draft",
    "rule",
    "form",
}
POSITIVE_RX = re.compile(
    r"exactly right|that'?s exactly right|incredible|good job|perfect|correct",
    re.IGNORECASE,
)
CORRECTION_RX = re.compile(
    r"should be|it says|correction|you read (?:it|this) as|you wrote|wrong|not right|typo|only|first word is|reads? as",
    re.IGNORECASE,
)
OCR_INTENT_RX = re.compile(
    OCR_INTENT_PATTERN,
    re.IGNORECASE,
)
OCR_LITERAL_INTENT_RX = re.compile(
    (
        r"what does (this|it) say|"
        r"what(?:'s| is) written|"
        r"can\s+(?:you|u|ur)\s+(?:read|see|ocr|transcrib\w*)|"
        r"read (this|it)|"
        r"\btranscrib\w*|"
        r"\bocr\b|"
        r"\bocr(?:[-\s]?able)?\b"
    ),
    re.IGNORECASE,
)
OCR_FRAMING_RX = re.compile(
    r"\bit (?:reads?|says)\b|\bhere(?:'s| is)\s+the\s+ocr\b|\btranscri(?:b\w*|pt\w*)\b|\bocr\b",
    re.IGNORECASE,
)
NEGATED_OCR_FRAMING_RX = re.compile(
    r"\bno\s+ocr\b|\bnot\s+ocr\b|\bwithout\s+ocr\b|\bno\s+transcri(?:ption|be\w*)\b",
    re.IGNORECASE,
)

ASSET_TOKEN_RE = re.compile(r"^(file[_-][^-]+)", re.IGNORECASE)
CODE_BLOCK_RX = re.compile(r"```(?:[^\n`]*)\n?(.*?)```", re.DOTALL)
AFTER_COLON_RX = re.compile(
    r"(?:it says|should be|correction|reads?|line)\s*:\s*([^\n]{3,120})",
    re.IGNORECASE,
)
AFTER_MARKER_RX = re.compile(
    r"(?:it says|should be|reads? as|first word is)\s+([^\n]{2,120})",
    re.IGNORECASE,
)
ARROW_RX = re.compile(r"(?:->|→|=>)\s*([^\n]{2,120})")
NOT_CORRECTION_PAIR_RX = re.compile(
    r"\b([a-z0-9][a-z0-9'/-]{1,40})\s*[!,:;]?\s*not\s+([a-z0-9][a-z0-9'/-]{1,40})\b",
    re.IGNORECASE,
)
NOT_CORRECTION_CONTEXT_RX = re.compile(
    r"\b(?:word|read(?:s)?|say(?:s)?|wrote|spell(?:ed|ing)?|ocr|transcrib\w*|binareyes)\b",
    re.IGNORECASE,
)
QUOTED_PHRASE_RX = re.compile(r"[\"“”'`]\s*([^\"“”'`\n]{3,160}?)\s*[\"“”'`]")
EMPHASIS_PHRASE_RX = re.compile(r"\*\*([^*\n]{3,160})\*\*|\*([^*\n]{3,160})\*")
FRAMED_TRANSCRIPTION_RX = re.compile(
    r"\bit (?:reads?|says)\b[,:-]?\s*([^\n]{3,120})",
    re.IGNORECASE,
)
ROOT_PATH_RX = re.compile(
    r"(?:^|[\s(])/(?:mnt|tmp|var|home|users?|data)/[^\s]+",
    re.IGNORECASE,
)
WINDOWS_PATH_RX = re.compile(
    r"(?:^|[\s(])[a-z]:\\(?:[^\\\s]+\\)+[^\\\s]+",
    re.IGNORECASE,
)
ASSET_PATH_FRAGMENT_RX = re.compile(
    r"\b(?:assets?|images?|conversations?|downloads?)/[^\s]+",
    re.IGNORECASE,
)
PATH_FILE_EXT_RX = re.compile(
    r"[\\/][^\s]{1,120}\.(?:png|jpe?g|webp|gif|tiff?|heic|pdf|json|md|txt)\b",
    re.IGNORECASE,
)
REGEX_UI_ERROR_PHRASE_RX = re.compile(
    r"\b(?:conversation|chat)\W*not\W*found\b|\bchat\W*html\b",
    re.IGNORECASE,
)
CONTROL_TOKEN_RX = re.compile(
    r"\b(?:imagegenview|imagegen|sandbox:|mnt/data|tool_call|assistant_response)\b",
    re.IGNORECASE,
)
COMPACT_24H_TIME_RX = re.compile(r"^(?:[01]\d|2[0-3])[0-5]\d$")
COMPACT_YEAR_SUFFIX_DATE_RX = re.compile(r"^\d{4,8}(?:24|25|26)$")
MAX_IMAGE_BYTES = 5 * 1024 * 1024


@dataclass
class Msg:
    create_time: float
    role: str
    text: str
    attachments: list[dict[str, Any]]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _asset_indexes(assets_root: Path) -> tuple[dict[str, Path], dict[str, list[Path]]]:
    by_name: dict[str, Path] = {}
    by_token: dict[str, list[Path]] = {}
    for path in sorted(assets_root.iterdir()):
        if not path.is_file():
            continue
        by_name[path.name.lower()] = path
        match = ASSET_TOKEN_RE.match(path.name)
        if not match:
            continue
        key = match.group(1).lower()
        by_token.setdefault(key, []).append(path)
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
    attachment: dict[str, Any],
    *,
    by_name: dict[str, Path],
    by_token: dict[str, list[Path]],
) -> list[str]:
    asset_name = str(attachment.get("name", "")).strip()
    asset_id = str(attachment.get("id", "")).strip()
    out: list[str] = []
    if asset_name:
        found = by_name.get(asset_name.lower())
        if found is not None:
            out.append(str(found))
    for variant in _asset_id_variants(asset_id):
        for p in by_token.get(variant, []):
            out.append(str(p))
    seen: set[str] = set()
    dedup: list[str] = []
    for item in out:
        if item in seen:
            continue
        seen.add(item)
        dedup.append(item)
    return dedup


def _to_msg(message: dict[str, Any]) -> Msg:
    role = str((message.get("author") or {}).get("role") or "")
    content = message.get("content")
    parts = content.get("parts") if isinstance(content, dict) else []
    if not isinstance(parts, list):
        parts = []
    text = html.unescape(" ".join(part for part in parts if isinstance(part, str)).strip())
    attachments = ((message.get("metadata") or {}).get("attachments") or [])
    if not isinstance(attachments, list):
        attachments = []
    return Msg(
        create_time=float(message.get("create_time") or 0),
        role=role,
        text=text,
        attachments=[a for a in attachments if isinstance(a, dict)],
    )


def _normalize_phrase_candidate(text: str) -> str:
    value = html.unescape(" ".join(text.split())).strip(" -•\t`'\"“”")
    if value.lower().startswith("only "):
        value = value[5:].lstrip(" :;-")
    return value.strip()


def _extract_inline_highlight_phrases(text: str) -> list[str]:
    phrases: list[str] = []
    for raw in QUOTED_PHRASE_RX.findall(text):
        value = _normalize_phrase_candidate(str(raw))
        if 3 <= len(value) <= 180:
            phrases.append(value)
    for match in EMPHASIS_PHRASE_RX.findall(text):
        raw = match[0] or match[1]
        value = _normalize_phrase_candidate(str(raw))
        if 3 <= len(value) <= 180:
            phrases.append(value)
    return phrases


def _extract_candidate_phrases(text: str) -> list[str]:
    phrases: list[str] = []
    not_pair_context = bool(NOT_CORRECTION_CONTEXT_RX.search(text))
    for pattern in (AFTER_COLON_RX, AFTER_MARKER_RX, ARROW_RX):
        for match in pattern.findall(text):
            raw = str(match)
            clipped = re.split(r"[.;!?]\s+", raw, maxsplit=1)[0]
            clipped = clipped.rstrip(".,:;!?")
            value = _normalize_phrase_candidate(clipped)
            if 3 <= len(value) <= 180:
                phrases.append(value)
    if not_pair_context:
        for left, _right in NOT_CORRECTION_PAIR_RX.findall(text):
            value = _normalize_phrase_candidate(str(left))
            if 3 <= len(value) <= 80:
                phrases.append(value)
    phrases.extend(_extract_inline_highlight_phrases(text))
    dedup: list[str] = []
    seen: set[str] = set()
    for p in phrases:
        key = p.lower()
        if key in seen:
            continue
        seen.add(key)
        dedup.append(p)
    return dedup


def _dedupe_phrases(phrases: list[str]) -> list[str]:
    dedup: list[str] = []
    seen: set[str] = set()
    for phrase in phrases:
        key = phrase.lower()
        if key in seen:
            continue
        seen.add(key)
        dedup.append(phrase)
    return dedup


def _phrases_overlap(left: list[str], right: list[str]) -> bool:
    if not left or not right:
        return False
    left_tokens: set[str] = set()
    right_tokens: set[str] = set()
    for phrase in left:
        left_tokens.update(
            token.lower()
            for token in _phrase_tokens(phrase)
            if len(token) >= 4 and token.lower() not in ANCHOR_STOPWORDS
        )
    for phrase in right:
        right_tokens.update(
            token.lower()
            for token in _phrase_tokens(phrase)
            if len(token) >= 4 and token.lower() not in ANCHOR_STOPWORDS
        )
    if not left_tokens or not right_tokens:
        return False
    return bool(left_tokens & right_tokens)


def _has_correction_signal(text: str) -> bool:
    return bool(
        CORRECTION_RX.search(text)
        or (NOT_CORRECTION_CONTEXT_RX.search(text) and NOT_CORRECTION_PAIR_RX.search(text))
    )


def _is_compact_24h_time_token(token: str) -> bool:
    return bool(COMPACT_24H_TIME_RX.fullmatch(token.strip()))


def _is_entry_numeric_token(token: str) -> bool:
    cleaned = token.strip()
    return bool(
        _is_compact_24h_time_token(cleaned) or COMPACT_YEAR_SUFFIX_DATE_RX.fullmatch(cleaned)
    )


def _is_numeric_entry_phrase(text: str) -> bool:
    value = " ".join(text.split()).strip()
    if not value:
        return False
    numeric_tokens = re.findall(r"\d{3,8}", value)
    if not numeric_tokens:
        return False
    if not all(_is_entry_numeric_token(token) for token in numeric_tokens):
        return False
    residue = re.sub(r"\d{3,8}", " ", value)
    residue = re.sub(r"[\s,.;:/|\\\-()\[\]{}]+", "", residue)
    return residue == ""


def _extract_transcribed_lines(assistant_text: str) -> tuple[list[str], bool]:
    candidates: list[str] = []
    candidates.extend(_extract_inline_highlight_phrases(assistant_text))
    for match in FRAMED_TRANSCRIPTION_RX.findall(assistant_text):
        value = _normalize_phrase_candidate(str(match))
        if 2 <= len(value) <= 120 and (
            any(ch.isalpha() for ch in value) or _is_numeric_entry_phrase(value)
        ):
            candidates.append(value)
    blocks = CODE_BLOCK_RX.findall(assistant_text)
    had_code_block = bool(blocks)
    for block in blocks:
        for line in str(block).splitlines():
            value = _normalize_phrase_candidate(line)
            if len(value) >= 2 and (
                any(ch.isalpha() for ch in value) or _is_numeric_entry_phrase(value)
            ):
                candidates.append(value)
    # Also inspect raw assistant lines for OCR-style bullet/label text.
    for raw_line in assistant_text.splitlines():
        value = _normalize_phrase_candidate(raw_line.lstrip("-*•> "))
        if 4 <= len(value) <= 120 and _is_ocr_like_phrase(value):
            candidates.append(value)
    if not candidates:
        # Fallback: split by sentence-like punctuation for short line candidates.
        for chunk in re.split(r"[;\n]+", assistant_text):
            value = _normalize_phrase_candidate(chunk)
            if 6 <= len(value) <= 120 and _is_ocr_like_phrase(value):
                candidates.append(value)
    dedup: list[str] = []
    seen: set[str] = set()
    for p in candidates:
        key = p.lower()
        if key in seen:
            continue
        seen.add(key)
        dedup.append(p)
    return dedup[:8], had_code_block


def _is_ocr_like_phrase(text: str) -> bool:
    value = html.unescape(" ".join(text.split())).strip(" -•\t")
    if len(value) < 2 or len(value) > 80:
        return False
    lowered = value.lower()
    if "![" in value and "](" in value:
        return False
    if ROOT_PATH_RX.search(value):
        return False
    if WINDOWS_PATH_RX.search(value):
        return False
    if ASSET_PATH_FRAGMENT_RX.search(value):
        return False
    if PATH_FILE_EXT_RX.search(value):
        return False
    if CONTROL_TOKEN_RX.search(value):
        return False
    if value.isdigit() and not _is_entry_numeric_token(value):
        return False
    if _is_entry_numeric_token(value):
        return True
    noisy_markers = (
        "confirmed",
        "transcription",
        "binareyes",
        "theory",
        "return theory",
        "json",
        "queries",
        "http://",
        "https://",
        "here's the ocr",
        "from your page",
        "no interpretation",
        "basically found",
        "meta",
    )
    if any(marker in lowered for marker in noisy_markers):
        return False
    if lowered.startswith("only "):
        return False
    if lowered.startswith(("here ", "here's ", "you ", "this ", "that ")):
        return False
    words = [w for w in re.split(r"\s+", value) if w]
    if len(words) > 8:
        return False
    alpha_words = [re.sub(r"[^a-z]", "", w.lower()) for w in words]
    alpha_words = [w for w in alpha_words if w]
    if len(alpha_words) == 1:
        token = alpha_words[0]
        if len(token) < 4 or token in ANCHOR_STOPWORDS or token in ANCHOR_META_WORDS:
            return False
    if len(alpha_words) == 2 and all(token in ANCHOR_STOPWORDS for token in alpha_words):
        return False
    if len(alpha_words) >= 5:
        stopword_ratio = sum(1 for word in alpha_words if word in ANCHOR_STOPWORDS) / len(alpha_words)
        if stopword_ratio > 0.55:
            return False
    alnum = sum(ch.isalnum() for ch in value)
    printable = sum(ch.isprintable() and not ch.isspace() for ch in value)
    if printable == 0:
        return False
    if alnum / printable < 0.45:
        return False
    return True


def _classify_lane(
    *,
    ask_text: str,
    title: str,
    image_path: str,
    followups: list[str],
) -> str:
    haystack = "\n".join([ask_text, title, *followups])
    if ILLUSTRATION_HINT_RX.search(haystack):
        return "illustration"
    if HANDWRITING_HINT_RX.search(haystack):
        return "handwriting"
    if TYPED_HINT_RX.search(haystack):
        return "typed"

    source_name = Path(image_path).name.lower()
    if any(marker in source_name for marker in ("diagram", "sketch", "drawing", "doodle", "flowchart", "graph")):
        return "illustration"
    if CAMERA_IMAGE_NAME_RX.search(source_name):
        return "handwriting"
    if SCREENSHOT_NAME_RX.search(source_name):
        return "typed"
    return "typed"


def _phrase_tokens(phrase: str) -> list[str]:
    return [token for token in re.findall(r"[A-Za-z0-9]+", phrase) if token]


def _merge_short_adjacent_tokens(tokens: list[str]) -> list[str]:
    merged: list[str] = []
    idx = 0
    while idx < len(tokens):
        if (
            idx + 1 < len(tokens)
            and tokens[idx].isalpha()
            and tokens[idx + 1].isalpha()
            and len(tokens[idx]) <= 3
            and len(tokens[idx + 1]) <= 3
        ):
            merged.append(tokens[idx] + tokens[idx + 1])
            idx += 2
            continue
        merged.append(tokens[idx])
        idx += 1
    return merged


def _regex_patterns_for_phrases(phrases: list[str]) -> list[str]:
    patterns: list[str] = []
    seen: set[str] = set()
    for phrase in phrases:
        if REGEX_UI_ERROR_PHRASE_RX.search(phrase):
            continue
        tokens = _phrase_tokens(phrase)
        if len(tokens) < 2:
            continue
        token_patterns = [tokens]
        merged_tokens = _merge_short_adjacent_tokens(tokens)
        if merged_tokens != tokens and len(merged_tokens) >= 2:
            token_patterns.append(merged_tokens)
        for token_list in token_patterns:
            pattern = r"\b" + r"\W*".join(re.escape(token) for token in token_list) + r"\b"
            if pattern in seen:
                continue
            seen.add(pattern)
            patterns.append(pattern)
    return patterns


def _anchor_terms_for_phrases(phrases: list[str]) -> list[str]:
    anchors: list[str] = []
    seen: set[str] = set()
    for phrase in phrases:
        tokens = [token.lower() for token in _phrase_tokens(phrase)]
        for token in tokens:
            if _is_entry_numeric_token(token):
                if token in seen:
                    continue
                seen.add(token)
                anchors.append(token)
                continue
            if not any(ch.isalpha() for ch in token):
                continue
            if len(token) < 4:
                continue
            if token in ANCHOR_STOPWORDS:
                continue
            if token in ANCHOR_META_WORDS:
                continue
            if token in ANCHOR_WEAK_WORDS:
                continue
            if token in ANCHOR_FILETYPE_WORDS:
                continue
            if token in ANCHOR_GENERIC_WORDS:
                continue
            if token in seen:
                continue
            seen.add(token)
            anchors.append(token)
    return anchors


def _ordered_terms_for_phrases(phrases: list[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for phrase in phrases:
        phrase_tokens: list[str] = []
        tokens = [token.lower() for token in _phrase_tokens(phrase)]
        for token in tokens:
            if _is_entry_numeric_token(token):
                phrase_tokens.append(token)
                continue
            if not any(ch.isalpha() for ch in token):
                continue
            if len(token) < 4:
                continue
            if token in ANCHOR_STOPWORDS:
                continue
            if token in ANCHOR_META_WORDS:
                continue
            if token in ORDERED_FALLBACK_SKIP_WORDS:
                continue
            if token in ANCHOR_FILETYPE_WORDS:
                continue
            if token in ANCHOR_GENERIC_WORDS:
                continue
            phrase_tokens.append(token)
        # In longer snippets, the first token is frequently a heading/context
        # marker ("restore", "insight", etc). Prefer the trailing sequence for
        # order constraints to reduce brittle lead-token gates.
        if len(phrase_tokens) >= 3 and not _is_entry_numeric_token(phrase_tokens[0]):
            phrase_tokens = phrase_tokens[1:]
        for token in phrase_tokens:
            if token in seen:
                continue
            seen.add(token)
            ordered.append(token)
    return ordered


def _expand_anchor_variants(anchors: list[str]) -> list[str]:
    expanded: list[str] = []
    seen: set[str] = set()
    for token in anchors:
        variants = [token]
        if token.endswith("ies") and len(token) > 6:
            variants.append(token[:-3] + "y")
        elif token.endswith("es") and len(token) > 5:
            if token.endswith(("ses", "xes", "zes", "ches", "shes")):
                variants.append(token[:-2])
            else:
                variants.append(token[:-1])
        elif token.endswith("s") and len(token) > 3 and not token.endswith(("us", "ss", "is", "ics")):
            variants.append(token[:-1])
        for variant in variants:
            value = variant.strip()
            if len(value) < 4:
                continue
            if value in seen:
                continue
            seen.add(value)
            expanded.append(value)
    return expanded


def _ordered_terms_supported_by_anchors(ordered_terms: list[str], anchors: list[str]) -> list[str]:
    """Keep ordered terms only when they are backed by anchor constraints."""
    if not ordered_terms or not anchors:
        return []
    anchor_set = {token.lower() for token in anchors}
    filtered: list[str] = []
    seen: set[str] = set()
    for token in ordered_terms:
        value = token.lower().strip()
        if value.endswith("es") and len(value) > 5 and value[:-2] in anchor_set:
            value = value[:-2]
        elif value.endswith("s") and len(value) > 4 and value[:-1] in anchor_set:
            value = value[:-1]
        if value not in anchor_set:
            continue
        if value in seen:
            continue
        seen.add(value)
        filtered.append(value)
    # A single token is not a sequence; avoid turning order checks into
    # accidental hard-required singleton anchors in growth lane.
    if len(filtered) < 2:
        return []
    return filtered


def _allow_unstable_source_in_growth(
    *,
    confidence: str,
    correction_signal: bool,
    ocr_framing_signal: bool,
    anchor_terms: list[str],
    transcription_phrases: list[str],
) -> bool:
    # Keep strict set quarantined while allowing high-signal unstable rows into
    # growth lane for fail-heavy pattern tracking.
    if confidence not in {"medium", "high"}:
        return False
    if len(anchor_terms) < 4:
        return False
    if not transcription_phrases:
        return False
    return bool(correction_signal or ocr_framing_signal)


def build_from_export(
    export_root: Path,
    *,
    output_cases: Path,
    output_cases_growth: Path | None = None,
    output_cases_handwriting: Path,
    output_cases_typed: Path,
    output_cases_illustration: Path,
    output_review: Path,
    max_cases: int,
    max_growth_cases: int = 600,
) -> dict[str, int]:
    conversations_dir = export_root / "conversations"
    assets_dir = export_root / "assets"
    if not conversations_dir.is_dir():
        raise RuntimeError(f"Missing conversations directory: {conversations_dir}")
    if not assets_dir.is_dir():
        raise RuntimeError(f"Missing assets directory: {assets_dir}")

    by_name, by_token = _asset_indexes(assets_dir)

    review_rows: list[dict[str, Any]] = []
    cases: list[dict[str, Any]] = []
    growth_cases: list[dict[str, Any]] = []
    seen_case_paths: set[str] = set()
    seen_growth_case_paths: set[str] = set()
    skipped_low_confidence = 0
    skipped_duplicate_image_path = 0
    skipped_insufficient_anchor_terms = 0
    skipped_unstable_source = 0
    emitted_cases = 0
    growth_cases_written = 0
    growth_quarantine_cases_written = 0
    growth_regex_only_cases_written = 0

    conversation_files = sorted(conversations_dir.glob("*.json"))
    for conversation_path in conversation_files:
        convo = _load_json(conversation_path)
        conversation_id = str(convo.get("conversation_id", "")).strip() or conversation_path.stem
        title = str(convo.get("title", "")).strip()
        mapping = convo.get("mapping") or {}
        if not isinstance(mapping, dict):
            continue

        seq: list[Msg] = []
        for node in mapping.values():
            if not isinstance(node, dict):
                continue
            message = node.get("message")
            if not isinstance(message, dict):
                continue
            seq.append(_to_msg(message))
        seq.sort(key=lambda m: m.create_time)
        if not seq:
            continue

        for idx, msg in enumerate(seq):
            if msg.role != "user" or not msg.attachments:
                continue
            ask_signal = bool(ASK_RX.search(msg.text))

            assistant_text = ""
            followups: list[str] = []
            followup_correction_phrases: list[str] = []
            positive_signal = False
            followup_correction_signal = False
            ask_correction_signal = _has_correction_signal(msg.text)
            ask_correction_phrases = (
                _extract_candidate_phrases(msg.text) if ask_correction_signal else []
            )

            for j in range(idx + 1, min(idx + 10, len(seq))):
                probe = seq[j]
                if not assistant_text:
                    if probe.role == "assistant" and probe.text:
                        assistant_text = probe.text
                    continue
                if probe.role != "user":
                    continue
                if probe.text:
                    followups.append(probe.text)
                if POSITIVE_RX.search(probe.text):
                    positive_signal = True
                if _has_correction_signal(probe.text):
                    followup_correction_signal = True
                    followup_correction_phrases.extend(_extract_candidate_phrases(probe.text))

            if not assistant_text:
                continue
            askless_candidate_signal = bool(
                OCR_FRAMING_RX.search(assistant_text)
                or OCR_INTENT_RX.search(assistant_text)
            )
            if not ask_signal and not askless_candidate_signal:
                continue

            transcription_phrases_raw, had_code_block = _extract_transcribed_lines(assistant_text)
            resolved_paths: list[str] = []
            for attachment in msg.attachments:
                resolved_paths.extend(
                    _resolve_asset_paths(
                        attachment,
                        by_name=by_name,
                        by_token=by_token,
                    )
                )
            resolved_paths = list(dict.fromkeys(resolved_paths))
            image_path = resolved_paths[0] if resolved_paths else ""
            if not image_path:
                continue
            try:
                if Path(image_path).stat().st_size > MAX_IMAGE_BYTES:
                    continue
            except OSError:
                continue
            lane = _classify_lane(
                ask_text=msg.text,
                title=title,
                image_path=image_path,
                followups=followups,
            )
            ask_followup_text = "\n".join([msg.text, *followups])
            ocr_intent_signal = ask_signal or bool(
                OCR_INTENT_RX.search(ask_followup_text)
            )
            ocr_literal_intent_signal = bool(
                OCR_LITERAL_INTENT_RX.search(ask_followup_text)
            )
            ocr_framing_signal = bool(OCR_FRAMING_RX.search(assistant_text)) and not bool(
                NEGATED_OCR_FRAMING_RX.search(assistant_text)
            )

            confidence = "low"
            chosen_phrases: list[str] = []
            followup_correction_phrases = [p for p in followup_correction_phrases if _is_ocr_like_phrase(p)]
            followup_correction_phrases = _dedupe_phrases(followup_correction_phrases)
            ask_correction_phrases = [p for p in ask_correction_phrases if _is_ocr_like_phrase(p)]
            ask_correction_phrases = _dedupe_phrases(ask_correction_phrases)
            correction_phrases = _dedupe_phrases(followup_correction_phrases + ask_correction_phrases)
            transcription_phrases = [p for p in transcription_phrases_raw if _is_ocr_like_phrase(p)]
            correction_overlap_signal = _phrases_overlap(correction_phrases[:5], transcription_phrases[:5])
            # Treat correction as meaningful only when we extracted OCR-like phrase content.
            correction_signal = bool(correction_phrases)
            transcription_anchor_terms = _anchor_terms_for_phrases(transcription_phrases[:5])
            has_multi_token_transcription = any(
                len(_phrase_tokens(phrase)) >= 2 for phrase in transcription_phrases[:5]
            )
            strong_transcription_phrase_signal = (
                ocr_literal_intent_signal
                and lane in {"handwriting", "typed"}
                and not positive_signal
                and has_multi_token_transcription
                and len(transcription_anchor_terms) >= 3
            )
            strong_illustration_phrase_signal = (
                lane == "illustration"
                and len(transcription_anchor_terms) >= 2
            )
            askless_handwriting_signal = (
                (not ask_signal)
                and lane == "handwriting"
                and ocr_framing_signal
                and correction_overlap_signal
                and has_multi_token_transcription
                and len(transcription_anchor_terms) >= 3
            )
            strong_high_transcription_signal = (
                ocr_literal_intent_signal
                and ocr_framing_signal
                and lane in {"handwriting", "typed"}
                and not positive_signal
                and len(transcription_phrases) >= 2
                and len(transcription_anchor_terms) >= 4
            )
            medium_intent_signal = ocr_literal_intent_signal or askless_handwriting_signal or (
                ocr_intent_signal
                and (
                    strong_illustration_phrase_signal
                    or correction_signal
                    or askless_handwriting_signal
                )
            )
            if (
                followup_correction_signal
                and followup_correction_phrases
                and correction_overlap_signal
            ):
                confidence = "high"
                chosen_phrases = followup_correction_phrases[:5]
            elif strong_high_transcription_signal and transcription_phrases:
                confidence = "high"
                chosen_phrases = transcription_phrases[:5]
            elif (
                medium_intent_signal
                and transcription_phrases
                and (
                    ocr_framing_signal
                    or correction_signal
                    or had_code_block
                    or strong_transcription_phrase_signal
                    or strong_illustration_phrase_signal
                )
            ):
                confidence = "medium"
                chosen_phrases = transcription_phrases[:5]
            anchor_source_phrases = chosen_phrases[:]
            if (
                confidence == "high"
                and correction_signal
                and len(_anchor_terms_for_phrases(anchor_source_phrases)) < 3
                and transcription_phrases
            ):
                # Some high-confidence corrections are numeric-heavy (for example sequence fixes).
                # Backfill anchors from transcription phrases so valid OCR rows are not dropped.
                anchor_source_phrases = _dedupe_phrases(
                    [*anchor_source_phrases[:5], *transcription_phrases[:3]]
                )
            anchor_terms = _expand_anchor_variants(_anchor_terms_for_phrases(anchor_source_phrases)[:8])
            ordered_terms = _ordered_terms_for_phrases(transcription_phrases_raw[:1])[:4]
            ordered_phrase_fallback = ordered_terms if len(anchor_terms) < 3 else []
            low_confidence_has_ocr_signal = bool(
                ocr_literal_intent_signal
                or ocr_framing_signal
                or correction_signal
                or correction_overlap_signal
            )
            if confidence == "low" and not low_confidence_has_ocr_signal:
                # Drop non-transcription chatter from review noise.
                continue
            if confidence == "low":
                emit_status = "skipped_low_confidence"
            elif Path(image_path).name in UNSTABLE_SOURCE_NAMES:
                emit_status = "skipped_unstable_source"
            elif image_path in seen_case_paths:
                emit_status = "skipped_duplicate_image_path"
            elif len(anchor_terms) < 3 and len(ordered_phrase_fallback) < 2:
                emit_status = "skipped_insufficient_anchor_terms"
            else:
                emit_status = "emitted"

            review_rows.append(
                {
                    "conversation_id": conversation_id,
                    "conversation_title": title,
                    "conversation_json": str(conversation_path),
                    "image_path": image_path,
                    "ask_text": msg.text,
                    "query_text": msg.text,
                    "assistant_text": assistant_text,
                    "expected_text": transcription_phrases[0] if transcription_phrases else "",
                    "followup_user_messages": followups[:5],
                    "positive_signal": positive_signal,
                    "correction_signal": correction_signal,
                    "correction_overlap_signal": correction_overlap_signal,
                    "ocr_intent_signal": ocr_intent_signal,
                    "ocr_literal_intent_signal": ocr_literal_intent_signal,
                    "ocr_framing_signal": ocr_framing_signal,
                    "correction_phrases": correction_phrases,
                    "transcription_phrases": transcription_phrases,
                    "chosen_phrases": chosen_phrases,
                    "anchor_terms": anchor_terms,
                    "anchor_terms_count": len(anchor_terms),
                    "emit_status": emit_status,
                    "skip_reason": (
                        ""
                        if emit_status == "emitted"
                        else emit_status.removeprefix("skipped_")
                    ),
                    "confidence": confidence,
                    "lane": lane,
                }
            )

            growth_anchor_terms = anchor_terms[:]
            growth_ordered_terms = ordered_phrase_fallback[:]
            if not growth_anchor_terms and transcription_phrases:
                growth_anchor_terms = _expand_anchor_variants(
                    _anchor_terms_for_phrases(transcription_phrases[:3])[:8]
                )
            if not growth_ordered_terms:
                growth_ordered_terms = _ordered_terms_for_phrases(transcription_phrases_raw[:1])[:4]
            growth_ordered_terms = _ordered_terms_supported_by_anchors(
                growth_ordered_terms,
                growth_anchor_terms,
            )
            growth_regex_patterns: list[str] = []
            if not growth_anchor_terms and len(growth_ordered_terms) < 2:
                # Regex constraints are the most brittle gate in OCR growth cases.
                # Keep them only as a fallback when we have no anchor or ordered
                # constraints, and cap to a single compact pattern.
                growth_regex_patterns = _regex_patterns_for_phrases(transcription_phrases[:3])[:1]

            growth_emit_status = emit_status in {
                "emitted",
                "skipped_insufficient_anchor_terms",
                "skipped_low_confidence",
            }
            if emit_status == "skipped_low_confidence":
                # Keep low-confidence growth strict but broader than literal-only
                # asks: include correction-led examples and OCR-framed rows only
                # when there is upstream OCR intent. This avoids metadata-only
                # transcript chatter entering growth cohorts.
                growth_emit_status = bool(
                    (
                        ocr_literal_intent_signal
                        or correction_signal
                        or (ocr_framing_signal and ocr_intent_signal)
                    )
                    and transcription_phrases
                )
            if emit_status == "skipped_unstable_source":
                growth_emit_status = _allow_unstable_source_in_growth(
                    confidence=confidence,
                    correction_signal=correction_signal,
                    ocr_framing_signal=ocr_framing_signal,
                    anchor_terms=growth_anchor_terms,
                    transcription_phrases=transcription_phrases,
                )
            if emit_status == "skipped_duplicate_image_path":
                growth_emit_status = False

            has_growth_constraints = (
                bool(growth_anchor_terms)
                or len(growth_ordered_terms) >= 2
                or bool(growth_regex_patterns)
            )
            source_quarantine = emit_status == "skipped_unstable_source"
            regex_only_case = (
                not growth_anchor_terms
                and len(growth_ordered_terms) < 2
                and bool(growth_regex_patterns)
            )
            if (
                growth_emit_status
                and has_growth_constraints
                and image_path not in seen_growth_case_paths
                and len(growth_cases) < max_growth_cases
            ):
                growth_case_id = f"gx-{conversation_id[:8]}-{len(growth_cases)+1:03d}"
                growth_cases.append(
                    {
                        "id": growth_case_id,
                        "image_path": image_path,
                        "source_name": Path(image_path).name,
                        "lane": lane,
                        "transcription_mode": "verbatim",
                        "must_contain_any": growth_anchor_terms[:8],
                        "must_appear_in_order": growth_ordered_terms[:4],
                        "must_match_regex": growth_regex_patterns,
                        "must_not_contain_words": ["likely", "maybe", "guess"],
                        "min_chars": 3,
                        "source_quarantine": source_quarantine,
                    }
                )
                seen_growth_case_paths.add(image_path)
                growth_cases_written += 1
                if source_quarantine:
                    growth_quarantine_cases_written += 1
                if regex_only_case:
                    growth_regex_only_cases_written += 1

            if emit_status == "skipped_low_confidence":
                skipped_low_confidence += 1
                continue
            if emit_status == "skipped_duplicate_image_path":
                skipped_duplicate_image_path += 1
                continue
            if emit_status == "skipped_unstable_source":
                skipped_unstable_source += 1
                continue
            case_id = f"tx-{conversation_id[:8]}-{len(cases)+1:03d}"
            if emit_status == "skipped_insufficient_anchor_terms":
                skipped_insufficient_anchor_terms += 1
                continue
            cases.append(
                {
                    "id": case_id,
                    "image_path": image_path,
                    "source_name": Path(image_path).name,
                    "lane": lane,
                    "transcription_mode": "verbatim",
                    "must_contain_any": anchor_terms,
                    "must_appear_in_order": ordered_phrase_fallback,
                    "must_not_contain_words": ["likely", "maybe", "guess"],
                    "min_chars": 3,
                }
            )
            seen_case_paths.add(image_path)
            emitted_cases += 1
            if len(cases) >= max_cases:
                break
        if len(cases) >= max_cases:
            break

    review_rows.sort(
        key=lambda row: (
            0 if row["confidence"] == "high" else 1 if row["confidence"] == "medium" else 2,
            row["conversation_title"].lower(),
            row["image_path"],
        )
    )

    confidence_counts: dict[str, int] = {"high": 0, "medium": 0, "low": 0}
    lane_counts: dict[str, int] = {}
    emit_status_counts: dict[str, int] = {}
    lane_emit_status_counts: dict[str, dict[str, int]] = {}
    for row in review_rows:
        confidence = str(row.get("confidence", "low"))
        lane = str(row.get("lane", "typed"))
        emit_status = str(row.get("emit_status", "skipped_low_confidence"))
        confidence_counts[confidence] = confidence_counts.get(confidence, 0) + 1
        lane_counts[lane] = lane_counts.get(lane, 0) + 1
        emit_status_counts[emit_status] = emit_status_counts.get(emit_status, 0) + 1
        lane_bucket = lane_emit_status_counts.setdefault(lane, {})
        lane_bucket[emit_status] = lane_bucket.get(emit_status, 0) + 1

    handwriting_cases = [case for case in cases if case.get("lane") == "handwriting"]
    typed_cases = [case for case in cases if case.get("lane") == "typed"]
    illustration_cases = [case for case in cases if case.get("lane") == "illustration"]
    growth_handwriting_cases = [case for case in growth_cases if case.get("lane") == "handwriting"]
    growth_typed_cases = [case for case in growth_cases if case.get("lane") == "typed"]
    growth_illustration_cases = [case for case in growth_cases if case.get("lane") == "illustration"]
    cases_summary = {
        "conversation_files": len(conversation_files),
        "episodes": len(review_rows),
        "cases_total": len(cases),
        "growth_cases_total": len(growth_cases),
        "lane_case_counts": {
            "handwriting": len(handwriting_cases),
            "typed": len(typed_cases),
            "illustration": len(illustration_cases),
        },
        "growth_lane_case_counts": {
            "handwriting": len(growth_handwriting_cases),
            "typed": len(growth_typed_cases),
            "illustration": len(growth_illustration_cases),
        },
        "confidence_counts": confidence_counts,
        "lane_counts": lane_counts,
        "emit_status_counts": emit_status_counts,
    }
    output_cases.parent.mkdir(parents=True, exist_ok=True)
    _write_json(output_cases, {"summary": cases_summary, "cases": cases})
    _write_json(
        output_cases_handwriting,
        {
            "summary": {
                "lane": "handwriting",
                "cases_total": len(handwriting_cases),
            },
            "cases": handwriting_cases,
        },
    )
    _write_json(
        output_cases_typed,
        {
            "summary": {
                "lane": "typed",
                "cases_total": len(typed_cases),
            },
            "cases": typed_cases,
        },
    )
    _write_json(
        output_cases_illustration,
        {
            "summary": {
                "lane": "illustration",
                "cases_total": len(illustration_cases),
            },
            "cases": illustration_cases,
        },
    )
    if output_cases_growth is not None:
        _write_json(
            output_cases_growth,
            {
                "summary": {
                    "lane": "growth",
                    "cases_total": len(growth_cases),
                    "lane_case_counts": {
                        "handwriting": len(growth_handwriting_cases),
                        "typed": len(growth_typed_cases),
                        "illustration": len(growth_illustration_cases),
                    },
                },
                "cases": growth_cases,
            },
        )
    _write_json(
        output_review,
        {
            "summary": {
                "conversation_files": len(conversation_files),
                "episodes": len(review_rows),
                "confidence_counts": confidence_counts,
                "lane_counts": lane_counts,
                "emit_status_counts": emit_status_counts,
                "lane_emit_status_counts": lane_emit_status_counts,
            },
            "episodes": review_rows,
        },
    )

    high = sum(1 for row in review_rows if row["confidence"] == "high")
    medium = sum(1 for row in review_rows if row["confidence"] == "medium")
    low = sum(1 for row in review_rows if row["confidence"] == "low")
    return {
        "conversation_files": len(conversation_files),
        "episodes": len(review_rows),
        "high_confidence": high,
        "medium_confidence": medium,
        "low_confidence": low,
        "cases_written": len(cases),
        "growth_cases_written": len(growth_cases),
        "handwriting_cases_written": len(handwriting_cases),
        "typed_cases_written": len(typed_cases),
        "illustration_cases_written": len(illustration_cases),
        "growth_handwriting_cases_written": len(growth_handwriting_cases),
        "growth_typed_cases_written": len(growth_typed_cases),
        "growth_illustration_cases_written": len(growth_illustration_cases),
        "emitted_cases": emitted_cases,
        "growth_emitted_cases": growth_cases_written,
        "growth_quarantine_cases_written": growth_quarantine_cases_written,
        "growth_regex_only_cases_written": growth_regex_only_cases_written,
        "skipped_low_confidence": skipped_low_confidence,
        "skipped_duplicate_image_path": skipped_duplicate_image_path,
        "skipped_insufficient_anchor_terms": skipped_insufficient_anchor_terms,
        "skipped_unstable_source": skipped_unstable_source,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build OCR eval cases from transcript correction signals in ChatGPT export conversations."
    )
    parser.add_argument(
        "--export-root",
        required=True,
        help="Path to export root containing conversations/ and assets/.",
    )
    parser.add_argument(
        "--output-cases",
        default=".local/eval_cases/ocr_transcript_cases_all.json",
        help="Output JSON path for runnable OCR cases (combined).",
    )
    parser.add_argument(
        "--output-cases-growth",
        default=".local/eval_cases/ocr_transcript_cases_growth.json",
        help="Output JSON path for runnable OCR growth-lane cases.",
    )
    parser.add_argument(
        "--output-cases-handwriting",
        default=".local/eval_cases/ocr_handwriting_from_transcripts.json",
        help="Output JSON path for handwriting/cursive OCR cases.",
    )
    parser.add_argument(
        "--output-cases-typed",
        default=".local/eval_cases/ocr_typed_from_transcripts.json",
        help="Output JSON path for typed OCR cases.",
    )
    parser.add_argument(
        "--output-cases-illustration",
        default=".local/eval_cases/ocr_illustration_from_transcripts.json",
        help="Output JSON path for illustration/diagram OCR cases.",
    )
    parser.add_argument(
        "--output-review",
        default=".local/eval_cases/ocr_transcript_cases_review.json",
        help="Output JSON path for mined episode review data (all lanes).",
    )
    parser.add_argument(
        "--max-cases",
        type=int,
        default=200,
        help="Maximum number of runnable cases to emit.",
    )
    parser.add_argument(
        "--max-growth-cases",
        type=int,
        default=600,
        help="Maximum number of runnable growth-lane cases to emit.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_from_export(
        Path(args.export_root).expanduser().resolve(),
        output_cases=Path(args.output_cases).expanduser().resolve(),
        output_cases_growth=Path(args.output_cases_growth).expanduser().resolve(),
        output_cases_handwriting=Path(args.output_cases_handwriting).expanduser().resolve(),
        output_cases_typed=Path(args.output_cases_typed).expanduser().resolve(),
        output_cases_illustration=Path(args.output_cases_illustration).expanduser().resolve(),
        output_review=Path(args.output_review).expanduser().resolve(),
        max_cases=int(args.max_cases),
        max_growth_cases=int(args.max_growth_cases),
    )
    for key in (
        "conversation_files",
        "episodes",
        "high_confidence",
        "medium_confidence",
        "low_confidence",
        "cases_written",
        "growth_cases_written",
        "handwriting_cases_written",
        "typed_cases_written",
        "illustration_cases_written",
        "growth_handwriting_cases_written",
        "growth_typed_cases_written",
        "growth_illustration_cases_written",
        "emitted_cases",
        "growth_emitted_cases",
        "growth_quarantine_cases_written",
        "growth_regex_only_cases_written",
        "skipped_low_confidence",
        "skipped_duplicate_image_path",
        "skipped_insufficient_anchor_terms",
        "skipped_unstable_source",
    ):
        print(f"{key}={summary[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
