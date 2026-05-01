from __future__ import annotations

import base64
import mimetypes
from pathlib import Path

ONE_BY_ONE_PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+qW6QAAAAASUVORK5CYII="
)


def load_attachment_input(
    *,
    image_path_raw: str | None,
    source_name: str | None,
    mime_type: str | None,
    text_hint: str | None,
    placeholder_bytes: bytes,
    placeholder_mime_type: str,
    placeholder_source_name: str | None = None,
    file_fallback_mime_type: str = "application/octet-stream",
) -> tuple[bytes, str, str | None, str | None]:
    image_path_value = str(image_path_raw or "").strip()
    source_name_value = str(source_name or "").strip()
    text_hint_value = str(text_hint).strip() if text_hint else None

    if image_path_value:
        image_path = Path(image_path_value).expanduser()
        if not image_path.is_file():
            raise RuntimeError(f"image_path does not exist: {image_path}")
        raw_bytes = image_path.read_bytes()
        resolved_mime_type = str(
            mime_type
            or mimetypes.guess_type(str(image_path))[0]
            or file_fallback_mime_type
        )
        resolved_source_name = source_name_value or image_path.name
        return (
            raw_bytes,
            resolved_mime_type,
            resolved_source_name or None,
            text_hint_value,
        )

    resolved_mime_type = str(mime_type or placeholder_mime_type)
    resolved_source_name = source_name_value or str(placeholder_source_name or "").strip()
    return (
        placeholder_bytes,
        resolved_mime_type,
        resolved_source_name or None,
        text_hint_value,
    )


def build_data_url(*, raw_bytes: bytes, mime_type: str) -> str:
    payload = base64.b64encode(raw_bytes).decode("ascii")
    return f"data:{mime_type};base64,{payload}"
