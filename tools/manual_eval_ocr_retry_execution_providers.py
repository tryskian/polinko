from __future__ import annotations

import base64
import mimetypes
import os
from pathlib import Path
from typing import Any, cast

from tools.manual_eval_ocr_retry_execution_requests import (
    OcrRetryExecutionProviderError,
    short_text_preview,
)


def response_retry_after_from_openai_error(exc: Exception) -> str:
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None)
    if headers is None:
        return ""
    retry_after = headers.get("retry-after") or headers.get("Retry-After")
    return str(retry_after or "").strip()


def ocr_retry_request_source(request: dict[str, Any]) -> dict[str, Any]:
    source = request.get("source")
    if isinstance(source, dict):
        return source
    return {}


def run_scaffold_ocr_retry_request(request: dict[str, Any]) -> dict[str, Any]:
    source = ocr_retry_request_source(request)
    resolved_path = Path(str(source.get("resolved_path") or "")).expanduser()
    raw_bytes = resolved_path.read_bytes()
    extracted_text = raw_bytes.decode("utf-8", errors="ignore").strip()
    status = "ok" if extracted_text else "stub"
    if not extracted_text:
        extracted_text = (
            "[OCR scaffold] Binary payload received. Configure "
            "POLINKO_OCR_PROVIDER=openai for text extraction."
        )
    return {
        "status": status,
        "provider": "scaffold",
        "model": "scaffold",
        "extracted_text": extracted_text,
        "extracted_text_preview": short_text_preview(extracted_text),
        "chars": len(extracted_text),
    }


def run_openai_ocr_retry_request(
    request: dict[str, Any],
    *,
    ocr_model: str,
    ocr_prompt: str,
) -> dict[str, Any]:
    try:
        from openai import (
            APIConnectionError,
            APIStatusError,
            AuthenticationError,
            OpenAI,
            RateLimitError,
        )
    except ImportError as exc:  # pragma: no cover - package is present in repo env
        raise OcrRetryExecutionProviderError(
            "openai package is not installed",
            status="provider_not_configured",
        ) from exc

    api_key = str(os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise OcrRetryExecutionProviderError(
            "OPENAI_API_KEY is not set",
            status="provider_not_configured",
        )

    source = ocr_retry_request_source(request)
    resolved_path = Path(str(source.get("resolved_path") or "")).expanduser()
    mime_type = str(
        source.get("mime_type")
        or mimetypes.guess_type(str(resolved_path))[0]
        or "application/octet-stream"
    )
    if not mime_type.startswith("image/"):
        raise OcrRetryExecutionProviderError(
            f"OpenAI OCR expects image input, got {mime_type}",
            status="invalid_request",
        )
    data_url = (
        f"data:{mime_type};base64,"
        f"{base64.b64encode(resolved_path.read_bytes()).decode('ascii')}"
    )
    client = OpenAI(api_key=api_key)
    ocr_input = cast(
        Any,
        [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": ocr_prompt},
                    {"type": "input_image", "image_url": data_url},
                ],
            }
        ],
    )
    try:
        response = client.responses.create(
            model=ocr_model,
            input=ocr_input,
            temperature=0,
        )
    except AuthenticationError as exc:
        raise OcrRetryExecutionProviderError(
            "OpenAI authentication failed",
            status="authentication_error",
        ) from exc
    except RateLimitError as exc:
        raise OcrRetryExecutionProviderError(
            "OpenAI OCR rate limit reached",
            status="rate_limited",
            retry_after=response_retry_after_from_openai_error(exc),
        ) from exc
    except APIConnectionError as exc:
        raise OcrRetryExecutionProviderError(
            "Connection error reaching OpenAI OCR provider",
            status="provider_unavailable",
        ) from exc
    except APIStatusError as exc:
        status = "provider_unavailable" if exc.status_code >= 500 else "provider_error"
        if exc.status_code == 429:
            status = "rate_limited"
        if exc.status_code in {400, 413, 415, 422}:
            status = "invalid_request"
        if exc.status_code in {401, 403}:
            status = "authentication_error"
        raise OcrRetryExecutionProviderError(
            f"OpenAI OCR error ({exc.status_code})",
            status=status,
            retry_after=response_retry_after_from_openai_error(exc),
        ) from exc

    output_text = getattr(response, "output_text", None)
    extracted_text = (
        str(output_text).strip()
        if isinstance(output_text, str) and output_text.strip()
        else "[OCR] No text detected."
    )
    return {
        "status": "ok",
        "provider": "openai",
        "model": ocr_model,
        "extracted_text": extracted_text,
        "extracted_text_preview": short_text_preview(extracted_text),
        "chars": len(extracted_text),
    }


def run_default_ocr_retry_request(
    request: dict[str, Any],
    *,
    ocr_provider: str,
    ocr_model: str,
    ocr_prompt: str,
) -> dict[str, Any]:
    provider = (ocr_provider or "scaffold").strip().lower()
    if provider == "openai":
        return run_openai_ocr_retry_request(
            request,
            ocr_model=ocr_model,
            ocr_prompt=ocr_prompt,
        )
    if provider == "scaffold":
        return run_scaffold_ocr_retry_request(request)
    raise OcrRetryExecutionProviderError(
        f"unsupported OCR retry provider: {provider}",
        status="provider_not_configured",
    )
