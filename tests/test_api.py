import os
import tempfile
import unittest
from types import SimpleNamespace

from fastapi.testclient import TestClient
from core.history_store import ChatHistoryStore


os.environ.setdefault("OPENAI_API_KEY", "sk-test-key-123456789012345")
os.environ.setdefault("POLINKO_SERVER_API_KEY", "test-server-key")

import server  # noqa: E402


class PolinkoApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        deps = server.get_runtime_deps()
        deps.server_api_key = "test-server-key"
        deps.server_api_key_principals = {"test-server-key": "default"}
        deps.rate_limit_per_minute = 30
        deps.rate_limiter.clear()
        deps.session_db_path = os.path.join(self.tmpdir.name, "test-memory.db")
        deps.history_store = ChatHistoryStore(os.path.join(self.tmpdir.name, "test-history.db"))
        self.client = TestClient(server.app)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

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

        chats_resp = self.client.get("/chats")
        self.assertEqual(chats_resp.status_code, 401)

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

    def test_server_side_chat_history_persists(self) -> None:
        original_run = server.Runner.run

        async def fake_run(*args, **kwargs):
            return SimpleNamespace(final_output="History response")

        server.Runner.run = fake_run
        try:
            chat_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "hello history", "session_id": "s-history"},
            )
        finally:
            server.Runner.run = original_run

        self.assertEqual(chat_resp.status_code, 200)

        chats_resp = self.client.get("/chats", headers={"x-api-key": "test-server-key"})
        self.assertEqual(chats_resp.status_code, 200)
        chats = chats_resp.json()["chats"]
        self.assertEqual(len(chats), 1)
        self.assertEqual(chats[0]["session_id"], "s-history")
        self.assertEqual(chats[0]["message_count"], 2)

        messages_resp = self.client.get(
            "/chats/s-history/messages",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(messages_resp.status_code, 200)
        messages = messages_resp.json()["messages"]
        self.assertEqual([m["role"] for m in messages], ["user", "assistant"])
        self.assertEqual(messages[0]["content"], "hello history")
        self.assertEqual(messages[1]["content"], "History response")

    def test_create_chat_and_reset_clears_messages(self) -> None:
        created = self.client.post("/chats", headers={"x-api-key": "test-server-key"}, json={})
        self.assertEqual(created.status_code, 200)
        session_id = created.json()["session_id"]

        original_run = server.Runner.run

        async def fake_run(*args, **kwargs):
            return SimpleNamespace(final_output="ok")

        server.Runner.run = fake_run
        try:
            self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "hello", "session_id": session_id},
            )
        finally:
            server.Runner.run = original_run

        before_reset = self.client.get(
            f"/chats/{session_id}/messages",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(len(before_reset.json()["messages"]), 2)

        reset_resp = self.client.post(
            "/session/reset",
            headers={"x-api-key": "test-server-key"},
            json={"session_id": session_id},
        )
        self.assertEqual(reset_resp.status_code, 200)

        after_reset = self.client.get(
            f"/chats/{session_id}/messages",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(after_reset.status_code, 200)
        self.assertEqual(after_reset.json()["messages"], [])

    def test_chat_success_with_key_ring(self) -> None:
        original_run = server.Runner.run
        deps = server.get_runtime_deps()
        deps.server_api_key_principals = {
            "team-key-a": "team-a",
            "team-key-b": "team-b",
        }

        async def fake_run(*args, **kwargs):
            return SimpleNamespace(final_output="Ring response")

        server.Runner.run = fake_run
        try:
            resp = self.client.post(
                "/chat",
                headers={"x-api-key": "team-key-b"},
                json={"message": "hello", "session_id": "s-chat-ring"},
            )
        finally:
            server.Runner.run = original_run
            deps.server_api_key_principals = {"test-server-key": "default"}

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["output"], "Ring response")

    def test_rate_limit_includes_retry_after(self) -> None:
        original_run = server.Runner.run
        deps = server.get_runtime_deps()
        original_limit = deps.rate_limit_per_minute
        deps.rate_limit_per_minute = 1

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
            deps.rate_limit_per_minute = original_limit
            deps.rate_limiter.clear()

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)
        self.assertIn("Retry-After", second.headers)

    def test_chat_rejects_empty_message(self) -> None:
        resp = self.client.post(
            "/chat",
            headers={"x-api-key": "test-server-key"},
            json={"message": "", "session_id": "s-empty"},
        )
        self.assertEqual(resp.status_code, 422)

    def test_chat_rejects_malformed_json(self) -> None:
        resp = self.client.post(
            "/chat",
            headers={"x-api-key": "test-server-key", "Content-Type": "application/json"},
            content='{"message": "hello", "session_id": "oops"',
        )
        self.assertEqual(resp.status_code, 422)

    def test_rate_limit_zero_disables_limiting(self) -> None:
        original_run = server.Runner.run
        deps = server.get_runtime_deps()
        original_limit = deps.rate_limit_per_minute
        deps.rate_limit_per_minute = 0

        async def fake_run(*args, **kwargs):
            return SimpleNamespace(final_output="ok")

        server.Runner.run = fake_run
        try:
            first = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key", "x-forwarded-for": "9.9.9.9"},
                json={"message": "first", "session_id": "s-no-limit"},
            )
            second = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key", "x-forwarded-for": "9.9.9.9"},
                json={"message": "second", "session_id": "s-no-limit"},
            )
        finally:
            server.Runner.run = original_run
            deps.rate_limit_per_minute = original_limit
            deps.rate_limiter.clear()

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)


if __name__ == "__main__":
    unittest.main()
