from contextlib import redirect_stderr
from contextlib import redirect_stdout
from io import StringIO
import json
import os
import unittest
import urllib.parse
from unittest.mock import patch

from tools import openai_account_summary


class _FakeResponse:
    def __init__(
        self,
        *,
        status_code: int = 200,
        payload: object | None = None,
        text: str = "",
    ) -> None:
        self.status = status_code
        self._payload = payload if payload is not None else {}
        self._text = text

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        if self._text:
            return self._text.encode("utf-8")
        return json.dumps(self._payload).encode("utf-8")


def _run_main(argv: list[str]) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    with (
        redirect_stdout(stdout),
        redirect_stderr(stderr),
        patch.object(openai_account_summary, "load_dotenv", lambda dotenv_path: None),
    ):
        code = openai_account_summary.main(argv)
    return code, stdout.getvalue(), stderr.getvalue()


class OpenAIAccountSummaryTests(unittest.TestCase):
    def test_missing_admin_key_fails_without_project_key_hint(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            code, stdout, stderr = _run_main(["costs"])

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("OPENAI_ADMIN_KEY is required", stderr)
        self.assertNotIn("OPENAI_API_KEY", stderr)

    def test_costs_fetches_organization_costs_and_prints_total(self) -> None:
        payload = {
            "object": "page",
            "data": [
                {
                    "object": "bucket",
                    "start_time": 0,
                    "end_time": 86_400,
                    "results": [
                        {"amount": {"value": 1.25, "currency": "usd"}},
                        {"amount": {"value": 2, "currency": "usd"}},
                    ],
                }
            ],
            "has_more": False,
        }

        with (
            patch.dict(os.environ, {"OPENAI_ADMIN_KEY": "sk-admin"}, clear=True),
            patch("tools.openai_account_summary.time.time", return_value=86_400),
            patch(
                "tools.openai_account_summary.urllib.request.urlopen",
                return_value=_FakeResponse(payload=payload),
            ) as urlopen_mock,
        ):
            code, stdout, stderr = _run_main(
                ["--base-url", "https://api.openai.test/v1", "costs", "--days", "1"]
            )

        self.assertEqual(code, 0, stderr)
        self.assertIn("OpenAI costs: last 1d", stdout)
        self.assertIn("USD: 3.25", stdout)
        urlopen_mock.assert_called_once()
        request = urlopen_mock.call_args.args[0]
        parsed_url = urllib.parse.urlparse(request.full_url)
        params = urllib.parse.parse_qs(parsed_url.query)
        self.assertEqual(
            f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}",
            "https://api.openai.test/v1/organization/costs",
        )
        self.assertEqual(params["start_time"], ["0"])
        self.assertEqual(
            request.get_header("Authorization"),
            "Bearer sk-admin",
        )

    def test_usage_fetches_selected_usage_kind_and_prints_totals(self) -> None:
        payload = {
            "object": "page",
            "data": [
                {
                    "object": "bucket",
                    "results": [
                        {
                            "object": "organization.usage.completions.result",
                            "num_model_requests": 3,
                            "input_tokens": 100,
                            "output_tokens": 40,
                        }
                    ],
                }
            ],
            "has_more": False,
        }

        with (
            patch.dict(os.environ, {"OPENAI_ADMIN_KEY": "sk-admin"}, clear=True),
            patch("tools.openai_account_summary.time.time", return_value=172_800),
            patch(
                "tools.openai_account_summary.urllib.request.urlopen",
                return_value=_FakeResponse(payload=payload),
            ) as urlopen_mock,
        ):
            code, stdout, stderr = _run_main(
                [
                    "--base-url",
                    "https://api.openai.test/v1",
                    "usage",
                    "--kind",
                    "completions",
                    "--days",
                    "2",
                ]
            )

        self.assertEqual(code, 0, stderr)
        self.assertIn("OpenAI usage: completions last 2d", stdout)
        self.assertIn("num_model_requests: 3", stdout)
        self.assertIn("input_tokens: 100", stdout)
        request = urlopen_mock.call_args.args[0]
        parsed_url = urllib.parse.urlparse(request.full_url)
        self.assertEqual(
            f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}",
            "https://api.openai.test/v1/organization/usage/completions",
        )

    def test_limits_requires_project_id(self) -> None:
        with patch.dict(os.environ, {"OPENAI_ADMIN_KEY": "sk-admin"}, clear=True):
            code, stdout, stderr = _run_main(["limits"])

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("OPENAI_PROJECT_ID or --project-id is required", stderr)

    def test_limits_fetches_project_rate_limits(self) -> None:
        payload = {
            "object": "list",
            "data": [
                {
                    "object": "project.rate_limit",
                    "id": "rl_model",
                    "model": "gpt-test",
                    "max_requests_per_1_minute": 600,
                    "max_tokens_per_1_minute": 150_000,
                }
            ],
            "has_more": False,
        }

        with (
            patch.dict(os.environ, {"OPENAI_ADMIN_KEY": "sk-admin"}, clear=True),
            patch(
                "tools.openai_account_summary.urllib.request.urlopen",
                return_value=_FakeResponse(payload=payload),
            ) as urlopen_mock,
        ):
            code, stdout, stderr = _run_main(
                [
                    "--base-url",
                    "https://api.openai.test/v1",
                    "limits",
                    "--project-id",
                    "proj_test",
                ]
            )

        self.assertEqual(code, 0, stderr)
        self.assertIn("OpenAI project limits: proj_test", stdout)
        self.assertIn("gpt-test", stdout)
        self.assertIn("max_requests_per_1_minute=600", stdout)
        request = urlopen_mock.call_args.args[0]
        parsed_url = urllib.parse.urlparse(request.full_url)
        self.assertEqual(
            f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}",
            "https://api.openai.test/v1/organization/projects/proj_test/rate_limits",
        )

    def test_summary_skips_limits_without_project_id(self) -> None:
        costs_payload = {
            "object": "page",
            "data": [{"results": [{"amount": {"value": 0.5, "currency": "usd"}}]}],
            "has_more": False,
        }
        usage_payload = {
            "object": "page",
            "data": [{"results": [{"num_model_requests": 1}]}],
            "has_more": False,
        }

        with (
            patch.dict(os.environ, {"OPENAI_ADMIN_KEY": "sk-admin"}, clear=True),
            patch("tools.openai_account_summary.time.time", return_value=86_400),
            patch(
                "tools.openai_account_summary.urllib.request.urlopen",
                side_effect=[
                    _FakeResponse(payload=costs_payload),
                    _FakeResponse(payload=usage_payload),
                ],
            ) as urlopen_mock,
        ):
            code, stdout, stderr = _run_main(["summary"])

        self.assertEqual(code, 0, stderr)
        self.assertEqual(urlopen_mock.call_count, 2)
        self.assertIn("OpenAI costs: last 30d", stdout)
        self.assertIn("OpenAI usage: completions last 7d", stdout)
        self.assertIn("OpenAI project limits: skipped", stdout)


if __name__ == "__main__":
    unittest.main()
