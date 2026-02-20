import os
import unittest
from types import SimpleNamespace

from fastapi.testclient import TestClient


os.environ.setdefault("OPENAI_API_KEY", "sk-test-key-123456789012345")
os.environ.setdefault("POLINKO_SERVER_API_KEY", "test-server-key")

import server  # noqa: E402


class PolinkoApiTests(unittest.TestCase):
    def setUp(self) -> None:
        server.SERVER_API_KEY = "test-server-key"
        server.RATE_LIMIT_PER_MINUTE = 30
        server.rate_buckets.clear()
        self.client = TestClient(server.app)

    def test_health(self) -> None:
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["status"], "ok")
        self.assertIn("prompt_version", body)

    def test_auth_required_for_chat_and_reset(self) -> None:
        chat_resp = self.client.post("/chat", json={"message": "hello", "session_id": "s1"})
        self.assertEqual(chat_resp.status_code, 401)

        reset_resp = self.client.post("/session/reset", json={"session_id": "s1"})
        self.assertEqual(reset_resp.status_code, 401)

    def test_reset_with_valid_api_key(self) -> None:
        resp = self.client.post(
            "/session/reset",
            headers={"x-api-key": "test-server-key"},
            json={"session_id": "s-reset"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")

    def test_chat_success_with_stubbed_runner(self) -> None:
        original_run = server.Runner.run

        async def fake_run(*args, **kwargs):
            return SimpleNamespace(final_output="Stubbed response")

        server.Runner.run = fake_run
        try:
            resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "hello", "session_id": "s-chat"},
            )
        finally:
            server.Runner.run = original_run

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["output"], "Stubbed response")
        self.assertEqual(body["session_id"], "s-chat")

    def test_rate_limit_includes_retry_after(self) -> None:
        original_run = server.Runner.run
        original_limit = server.RATE_LIMIT_PER_MINUTE
        server.RATE_LIMIT_PER_MINUTE = 1

        async def fake_run(*args, **kwargs):
            return SimpleNamespace(final_output="ok")

        server.Runner.run = fake_run
        try:
            first = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key", "x-forwarded-for": "1.2.3.4"},
                json={"message": "first", "session_id": "s-rate"},
            )
            second = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key", "x-forwarded-for": "1.2.3.4"},
                json={"message": "second", "session_id": "s-rate"},
            )
        finally:
            server.Runner.run = original_run
            server.RATE_LIMIT_PER_MINUTE = original_limit
            server.rate_buckets.clear()

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)
        self.assertIn("Retry-After", second.headers)


if __name__ == "__main__":
    unittest.main()
