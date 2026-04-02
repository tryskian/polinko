import unittest
from unittest.mock import patch

import requests

from tools.eval_retrieval import _request_json
from tools.eval_retrieval import build_parser


class _FakeResponse:
    def __init__(
        self, status_code: int, payload: object | None = None, text: str = ""
    ) -> None:
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.text = text

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300

    def json(self) -> object:
        return self._payload


class EvalRetrievalTests(unittest.TestCase):
    def test_build_parser_defaults_retry_controls(self) -> None:
        args = build_parser().parse_args([])
        self.assertEqual(args.request_retries, 2)
        self.assertEqual(args.request_retry_delay_ms, 750)

    def test_request_json_retries_on_retryable_http_status(self) -> None:
        responses = [
            _FakeResponse(status_code=429, payload={"detail": "rate limit"}),
            _FakeResponse(status_code=200, payload={"status": "ok"}),
        ]
        with (
            patch(
                "tools.eval_retrieval.requests.request", side_effect=responses
            ) as request_mock,
            patch("tools.eval_retrieval.time.sleep") as sleep_mock,
        ):
            payload = _request_json(
                method="GET",
                base_url="http://127.0.0.1:8000",
                path="/health",
                headers={},
                retries=1,
                retry_delay_ms=10,
            )

        self.assertEqual(payload, {"status": "ok"})
        self.assertEqual(request_mock.call_count, 2)
        sleep_mock.assert_called_once()

    def test_request_json_retries_on_connection_error(self) -> None:
        with (
            patch(
                "tools.eval_retrieval.requests.request",
                side_effect=[
                    requests.RequestException("socket timeout"),
                    _FakeResponse(status_code=200, payload={"value": 1}),
                ],
            ) as request_mock,
            patch("tools.eval_retrieval.time.sleep") as sleep_mock,
        ):
            payload = _request_json(
                method="POST",
                base_url="http://127.0.0.1:8000",
                path="/chat",
                headers={},
                payload={"message": "hello"},
                retries=1,
                retry_delay_ms=5,
            )

        self.assertEqual(payload, {"value": 1})
        self.assertEqual(request_mock.call_count, 2)
        sleep_mock.assert_called_once()

    def test_request_json_raises_after_retry_budget_exhausted(self) -> None:
        with patch(
            "tools.eval_retrieval.requests.request",
            side_effect=[
                _FakeResponse(status_code=429, payload={"detail": "rate limit"})
            ],
        ):
            with self.assertRaises(RuntimeError) as ctx:
                _request_json(
                    method="GET",
                    base_url="http://127.0.0.1:8000",
                    path="/health",
                    headers={},
                    retries=0,
                    retry_delay_ms=0,
                )

        self.assertIn("HTTP 429", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
