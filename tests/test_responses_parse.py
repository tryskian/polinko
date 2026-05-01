import unittest
from types import SimpleNamespace

from pydantic import BaseModel

from core.responses_parse import parse_structured_output


class _Payload(BaseModel):
    value: str


class ResponsesParseTests(unittest.TestCase):
    def test_parse_structured_output_returns_typed_payload(self) -> None:
        class _FakeResponses:
            def parse(self, **kwargs: object) -> SimpleNamespace:
                self.kwargs = kwargs
                return SimpleNamespace(output_parsed=_Payload(value="ok"))

        fake = SimpleNamespace(responses=_FakeResponses())
        payload = parse_structured_output(
            responses_client=fake,
            model="gpt-test",
            input="prompt",
            text_format=_Payload,
            missing_payload_message="payload missing",
        )
        self.assertEqual(payload.value, "ok")
        self.assertEqual(fake.responses.kwargs["model"], "gpt-test")
        self.assertEqual(fake.responses.kwargs["input"], "prompt")
        self.assertIs(fake.responses.kwargs["text_format"], _Payload)

    def test_parse_structured_output_raises_for_missing_payload(self) -> None:
        class _FakeResponses:
            def parse(self, **kwargs: object) -> SimpleNamespace:
                del kwargs
                return SimpleNamespace(output_parsed=None)

        with self.assertRaisesRegex(RuntimeError, "payload missing"):
            parse_structured_output(
                responses_client=SimpleNamespace(responses=_FakeResponses()),
                model="gpt-test",
                input="prompt",
                text_format=_Payload,
                missing_payload_message="payload missing",
            )

    def test_parse_structured_output_raises_for_wrong_payload_type(self) -> None:
        class _WrongPayload(BaseModel):
            other: str

        class _FakeResponses:
            def parse(self, **kwargs: object) -> SimpleNamespace:
                del kwargs
                return SimpleNamespace(output_parsed=_WrongPayload(other="nope"))

        with self.assertRaisesRegex(RuntimeError, "Structured payload must be _Payload"):
            parse_structured_output(
                responses_client=SimpleNamespace(responses=_FakeResponses()),
                model="gpt-test",
                input="prompt",
                text_format=_Payload,
                missing_payload_message="payload missing",
            )


if __name__ == "__main__":
    unittest.main()
