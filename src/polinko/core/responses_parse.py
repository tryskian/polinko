from typing import Any, Protocol, TypeVar

from pydantic import BaseModel

StructuredModelT = TypeVar("StructuredModelT", bound=BaseModel)


class _SupportsResponsesParse(Protocol):
    def parse(self, **kwargs: Any) -> Any: ...


class SupportsResponsesClientParse(Protocol):
    responses: _SupportsResponsesParse


def parse_structured_output(
    *,
    responses_client: SupportsResponsesClientParse,
    model: str,
    input: str,
    text_format: type[StructuredModelT],
    missing_payload_message: str,
) -> StructuredModelT:
    response = responses_client.responses.parse(
        model=model,
        input=input,
        text_format=text_format,
    )
    payload = getattr(response, "output_parsed", None)
    if payload is None:
        raise RuntimeError(missing_payload_message)
    if not isinstance(payload, text_format):
        raise RuntimeError(
            f"Structured payload must be {text_format.__name__}, got {type(payload).__name__}."
        )
    return payload
