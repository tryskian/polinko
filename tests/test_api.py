import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient
from core.history_store import ChatHistoryStore
from core.prompts import ACTIVE_PROMPT_VERSION


os.environ.setdefault("OPENAI_API_KEY", "sk-test-key-123456789012345")
os.environ.setdefault("POLINKO_SERVER_API_KEY", "test-server-key")

import server  # noqa: E402


class PolinkoApiTests(unittest.TestCase):
    @staticmethod
    def _stub_runner(output: str, capture: dict[str, str] | None = None):
        async def fake_run(*args: object, **kwargs: object) -> SimpleNamespace:
            del kwargs
            if capture is not None and len(args) > 1:
                capture["input"] = str(args[1])
            return SimpleNamespace(final_output=output)

        return patch.object(server.Runner, "run", new=fake_run)

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        deps = server.get_runtime_deps()
        deps.server_api_key = "test-server-key"
        deps.server_api_key_principals = {"test-server-key": "default"}
        deps.rate_limit_per_minute = 30
        deps.rate_limiter.clear()
        deps.deprecate_on_reset = False
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

        note_resp = self.client.post("/chats/s1/notes", json={"note": "test"})
        self.assertEqual(note_resp.status_code, 401)

    def test_reset_with_valid_api_key(self) -> None:
        resp = self.client.post(
            "/session/reset",
            headers={"x-api-key": "test-server-key"},
            json={"session_id": "s-reset"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")

    def test_chat_success_with_stubbed_runner(self) -> None:
        with self._stub_runner("Stubbed response"):
            resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "hello", "session_id": "s-chat"},
            )

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["output"], "Stubbed response")
        self.assertEqual(body["session_id"], "s-chat")

    def test_server_side_chat_history_persists(self) -> None:
        with self._stub_runner("History response"):
            chat_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "hello history", "session_id": "s-history"},
            )

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
        self.assertRegex(messages[0]["message_id"], r"^msg_[0-9a-f]{24}$")
        self.assertIsNone(messages[0]["parent_message_id"])
        self.assertEqual(messages[1]["parent_message_id"], messages[0]["message_id"])

    def test_messages_include_parent_lineage_across_turns(self) -> None:
        with self._stub_runner("turn-1"):
            first = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "first turn", "session_id": "s-lineage"},
            )
        self.assertEqual(first.status_code, 200)

        with self._stub_runner("turn-2"):
            second = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "second turn", "session_id": "s-lineage"},
            )
        self.assertEqual(second.status_code, 200)

        messages_resp = self.client.get(
            "/chats/s-lineage/messages",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(messages_resp.status_code, 200)
        messages = messages_resp.json()["messages"]
        self.assertEqual([m["role"] for m in messages], ["user", "assistant", "user", "assistant"])
        self.assertEqual(messages[0]["parent_message_id"], None)
        self.assertEqual(messages[1]["parent_message_id"], messages[0]["message_id"])
        self.assertEqual(messages[2]["parent_message_id"], messages[1]["message_id"])
        self.assertEqual(messages[3]["parent_message_id"], messages[2]["message_id"])

    def test_chat_export_json_and_markdown(self) -> None:
        with self._stub_runner("Export response"):
            chat_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "hello export", "session_id": "s-export"},
            )
        self.assertEqual(chat_resp.status_code, 200)

        export_resp = self.client.get(
            "/chats/s-export/export",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(export_resp.status_code, 200)
        payload = export_resp.json()
        self.assertEqual(payload["session_id"], "s-export")
        self.assertEqual(payload["status"], "active")
        self.assertEqual(payload["prompt_version"], ACTIVE_PROMPT_VERSION)
        self.assertEqual(payload["message_count"], 2)
        self.assertEqual(payload["markdown"], None)
        self.assertEqual([m["role"] for m in payload["messages"]], ["user", "assistant"])
        self.assertIn("message_id", payload["messages"][0])
        self.assertIn("parent_message_id", payload["messages"][1])

        md_resp = self.client.get(
            "/chats/s-export/export?include_markdown=true",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(md_resp.status_code, 200)
        md_payload = md_resp.json()
        self.assertIsInstance(md_payload["markdown"], str)
        self.assertIn("# Transcript: s-export", md_payload["markdown"])
        self.assertIn("## User", md_payload["markdown"])
        self.assertIn("## Assistant", md_payload["markdown"])
        self.assertIn("hello export", md_payload["markdown"])
        self.assertIn("Export response", md_payload["markdown"])

    def test_create_chat_and_reset_clears_messages(self) -> None:
        created = self.client.post("/chats", headers={"x-api-key": "test-server-key"}, json={})
        self.assertEqual(created.status_code, 200)
        session_id = created.json()["session_id"]

        with self._stub_runner("ok"):
            self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "hello", "session_id": session_id},
            )

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

    def test_reset_with_deprecate_hides_chat_and_blocks_sends(self) -> None:
        session_id = "s-deprecated"
        created = self.client.post(
            "/chats",
            headers={"x-api-key": "test-server-key"},
            json={"session_id": session_id},
        )
        self.assertEqual(created.status_code, 200)

        reset_resp = self.client.post(
            "/session/reset",
            headers={"x-api-key": "test-server-key"},
            json={"session_id": session_id, "deprecate": True},
        )
        self.assertEqual(reset_resp.status_code, 200)

        chats_resp = self.client.get("/chats", headers={"x-api-key": "test-server-key"})
        self.assertEqual(chats_resp.status_code, 200)
        self.assertEqual(chats_resp.json()["chats"], [])

        all_chats_resp = self.client.get(
            "/chats?include_deprecated=true",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(all_chats_resp.status_code, 200)
        chats = all_chats_resp.json()["chats"]
        self.assertEqual(len(chats), 1)
        self.assertEqual(chats[0]["session_id"], session_id)
        self.assertEqual(chats[0]["status"], "deprecated")
        self.assertIsInstance(chats[0]["deprecated_at"], int)

        send_resp = self.client.post(
            "/chat",
            headers={"x-api-key": "test-server-key"},
            json={"message": "hello again", "session_id": session_id},
        )
        self.assertEqual(send_resp.status_code, 409)

    def test_reset_uses_server_default_deprecate_mode(self) -> None:
        deps = server.get_runtime_deps()
        deps.deprecate_on_reset = True
        session_id = "s-default-deprecate"
        created = self.client.post(
            "/chats",
            headers={"x-api-key": "test-server-key"},
            json={"session_id": session_id},
        )
        self.assertEqual(created.status_code, 200)

        reset_resp = self.client.post(
            "/session/reset",
            headers={"x-api-key": "test-server-key"},
            json={"session_id": session_id},
        )
        self.assertEqual(reset_resp.status_code, 200)

        chats_resp = self.client.get("/chats", headers={"x-api-key": "test-server-key"})
        self.assertEqual(chats_resp.status_code, 200)
        self.assertEqual(chats_resp.json()["chats"], [])

    def test_notes_are_internal_and_not_returned_as_messages(self) -> None:
        note_resp = self.client.post(
            "/chats/s-note/notes",
            headers={"x-api-key": "test-server-key"},
            json={"note": "Use lighter rhythm and avoid full bard prose."},
        )
        self.assertEqual(note_resp.status_code, 200)

        captured = {}
        with self._stub_runner("ok", capture=captured):
            chat_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "tell me about unicorns", "session_id": "s-note"},
            )

        self.assertEqual(chat_resp.status_code, 200)
        self.assertIn("INTERNAL_STYLE_NOTES", captured["input"])
        self.assertIn("lighter rhythm", captured["input"])

        messages_resp = self.client.get(
            "/chats/s-note/messages",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(messages_resp.status_code, 200)
        roles = [m["role"] for m in messages_resp.json()["messages"]]
        self.assertEqual(roles, ["user", "assistant"])

        chats_resp = self.client.get("/chats", headers={"x-api-key": "test-server-key"})
        self.assertEqual(chats_resp.status_code, 200)
        self.assertEqual(chats_resp.json()["chats"][0]["message_count"], 2)

    def test_chat_success_with_key_ring(self) -> None:
        deps = server.get_runtime_deps()
        deps.server_api_key_principals = {
            "team-key-a": "team-a",
            "team-key-b": "team-b",
        }
        with self._stub_runner("Ring response"):
            resp = self.client.post(
                "/chat",
                headers={"x-api-key": "team-key-b"},
                json={"message": "hello", "session_id": "s-chat-ring"},
            )
        deps.server_api_key_principals = {"test-server-key": "default"}

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["output"], "Ring response")

    def test_rate_limit_includes_retry_after(self) -> None:
        deps = server.get_runtime_deps()
        original_limit = deps.rate_limit_per_minute
        deps.rate_limit_per_minute = 1
        with self._stub_runner("ok"):
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
        deps = server.get_runtime_deps()
        original_limit = deps.rate_limit_per_minute
        deps.rate_limit_per_minute = 0
        with self._stub_runner("ok"):
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
        deps.rate_limit_per_minute = original_limit
        deps.rate_limiter.clear()

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)


if __name__ == "__main__":
    unittest.main()
