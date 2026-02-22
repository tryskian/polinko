import base64
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient
from api.app_factory import create_runtime_metrics
from core.history_store import ChatHistoryStore
from core.prompts import ACTIVE_PROMPT_VERSION
from core.vector_store import VectorStore


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
        deps.ocr_provider = "scaffold"
        deps.ocr_model = "gpt-4.1-mini"
        deps.ocr_prompt = "Extract text."
        deps.ocr_client = None
        deps.vector_enabled = False
        deps.vector_top_k = 2
        deps.vector_min_similarity = 0.40
        deps.vector_max_chars = 220
        deps.vector_exclude_current_session = True
        deps.vector_embedding_model = "text-embedding-3-small"
        deps.vector_store = None
        deps.embedding_client = None
        deps.session_db_path = os.path.join(self.tmpdir.name, "test-memory.db")
        deps.history_store = ChatHistoryStore(os.path.join(self.tmpdir.name, "test-history.db"))
        deps.metrics = create_runtime_metrics()
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

        metrics_resp = self.client.get("/metrics")
        self.assertEqual(metrics_resp.status_code, 401)

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
        self.assertEqual(payload["ocr_runs"], [])
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

    def test_ocr_skill_records_run_and_links_export(self) -> None:
        run_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-ocr",
                "source_name": "scribble.txt",
                "mime_type": "text/plain",
                "text_hint": "luminous notes from a scribble",
                "attach_to_chat": True,
            },
        )
        self.assertEqual(run_resp.status_code, 200)
        run = run_resp.json()["run"]
        self.assertRegex(run["run_id"], r"^ocr-[0-9a-f]{12}$")
        self.assertEqual(run["session_id"], "s-ocr")
        self.assertEqual(run["status"], "ok")
        self.assertEqual(run["source_name"], "scribble.txt")
        self.assertEqual(run["mime_type"], "text/plain")
        self.assertIn("scribble", run["extracted_text"])
        self.assertRegex(run["result_message_id"], r"^msg_[0-9a-f]{24}$")

        messages_resp = self.client.get(
            "/chats/s-ocr/messages",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(messages_resp.status_code, 200)
        messages = messages_resp.json()["messages"]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["role"], "assistant")
        self.assertEqual(messages[0]["message_id"], run["result_message_id"])
        self.assertIn("[OCR]", messages[0]["content"])

        export_resp = self.client.get(
            "/chats/s-ocr/export",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(export_resp.status_code, 200)
        export_payload = export_resp.json()
        self.assertEqual(len(export_payload["ocr_runs"]), 1)
        self.assertEqual(export_payload["ocr_runs"][0]["run_id"], run["run_id"])
        self.assertEqual(export_payload["ocr_runs"][0]["result_message_id"], run["result_message_id"])
        self.assertEqual(export_payload["message_count"], 1)

    def test_ocr_skill_openai_provider_path(self) -> None:
        deps = server.get_runtime_deps()
        deps.ocr_provider = "openai"
        captured: dict[str, object] = {}

        class _FakeResponses:
            def create(self, **kwargs: object) -> SimpleNamespace:
                captured["kwargs"] = kwargs
                return SimpleNamespace(output_text="detected by openai ocr")

        deps.ocr_client = SimpleNamespace(responses=_FakeResponses())
        payload_b64 = base64.b64encode(b"not-really-an-image").decode("ascii")

        run_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-ocr-openai",
                "source_name": "scan.png",
                "mime_type": "image/png",
                "data_base64": payload_b64,
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_resp.status_code, 200)
        run = run_resp.json()["run"]
        self.assertEqual(run["status"], "ok")
        self.assertEqual(run["extracted_text"], "detected by openai ocr")
        self.assertIsNone(run["result_message_id"])
        self.assertIn("kwargs", captured)
        kwargs = captured["kwargs"]
        self.assertEqual(kwargs["model"], deps.ocr_model)
        self.assertIn("input", kwargs)

    def test_ocr_indexes_chunked_vectors_with_metadata(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-ocr.db"))

        class _FakeEmbeddings:
            @staticmethod
            def _embed(text: str) -> list[float]:
                lowered = text.lower()
                return [
                    1.0 if "invoice" in lowered else 0.0,
                    1.0 if "line item" in lowered else 0.0,
                    float(len(lowered) % 31) / 31.0,
                    1.0 if "total" in lowered else 0.0,
                ]

            def create(self, **kwargs: object) -> SimpleNamespace:
                inputs = kwargs["input"]
                if isinstance(inputs, str):
                    payload = [inputs]
                else:
                    payload = list(inputs)
                data = [SimpleNamespace(embedding=self._embed(text)) for text in payload]
                return SimpleNamespace(data=data)

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())

        ocr_text = "\n".join(
            [
                "Invoice archive extraction",
                "line item A: custom scanner tune",
                "line item B: calibration ledger",
                "subtotal and total noted",
            ]
            * 80
        )
        run_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-ocr-index",
                "source_name": "invoice_scan.png",
                "mime_type": "image/png",
                "text_hint": ocr_text,
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_resp.status_code, 200)
        run = run_resp.json()["run"]

        self.assertGreater(deps.vector_store.active_count(), 1)
        query_vector = _FakeEmbeddings._embed("find invoice line item totals")
        matches = deps.vector_store.search(
            query_embedding=query_vector,
            limit=10,
            min_similarity=0.0,
            roles=("assistant",),
            source_types=("ocr",),
        )
        self.assertGreater(len(matches), 1)
        self.assertTrue(all(match.source_type == "ocr" for match in matches))
        self.assertTrue(all(match.metadata.get("source") == "ocr" for match in matches))
        self.assertTrue(any(match.metadata.get("ocr_run_id") == run["run_id"] for match in matches))
        self.assertTrue(any(match.metadata.get("source_name") == "invoice_scan.png" for match in matches))

    def test_file_search_returns_ranked_ocr_matches(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-search.db"))

        class _FakeEmbeddings:
            @staticmethod
            def _embed(text: str) -> list[float]:
                lowered = text.lower()
                return [
                    1.0 if "invoice" in lowered else 0.0,
                    1.0 if "line item" in lowered else 0.0,
                    1.0 if "total" in lowered else 0.0,
                    1.0 if "shipping" in lowered else 0.0,
                    float(len(lowered) % 23) / 23.0,
                ]

            def create(self, **kwargs: object) -> SimpleNamespace:
                inputs = kwargs["input"]
                if isinstance(inputs, str):
                    payload = [inputs]
                else:
                    payload = list(inputs)
                data = [SimpleNamespace(embedding=self._embed(text)) for text in payload]
                return SimpleNamespace(data=data)

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())

        run_a = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-search-a",
                "source_name": "invoice-2026.png",
                "mime_type": "image/png",
                "text_hint": (
                    "Invoice 2026\n"
                    "line item 1: calibration\n"
                    "line item 2: scanner pass\n"
                    "total: 1840"
                ),
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_a.status_code, 200)

        run_b = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-search-b",
                "source_name": "shipping-note.png",
                "mime_type": "image/png",
                "text_hint": (
                    "Shipping note\n"
                    "dock 7\n"
                    "tracking 8841\n"
                    "no invoice reference"
                ),
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_b.status_code, 200)

        search = self.client.post(
            "/skills/file_search",
            headers={"x-api-key": "test-server-key"},
            json={
                "query": "find invoice line item totals",
                "session_id": "s-search-a",
                "limit": 3,
            },
        )
        self.assertEqual(search.status_code, 200)
        payload = search.json()
        self.assertEqual(payload["query"], "find invoice line item totals")
        self.assertGreater(len(payload["matches"]), 0)
        first = payload["matches"][0]
        self.assertEqual(first["source_type"], "ocr")
        self.assertEqual(first["session_id"], "s-search-a")
        self.assertIn("invoice", first["snippet"].lower())
        self.assertIn("ocr_run_id", first["metadata"])

    def test_file_search_requires_vector_memory(self) -> None:
        resp = self.client.post(
            "/skills/file_search",
            headers={"x-api-key": "test-server-key"},
            json={"query": "invoice totals"},
        )
        self.assertEqual(resp.status_code, 503)

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

    def test_vector_memory_retrieval_injects_prior_assistant_context(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors.db"))

        class _FakeEmbeddings:
            @staticmethod
            def _embed(text: str) -> list[float]:
                lowered = text.lower()
                return [
                    1.0 if "unicorn" in lowered else 0.0,
                    1.0 if "horn" in lowered else 0.0,
                    1.0 if "grow" in lowered or "growth" in lowered else 0.0,
                    float(len(lowered) % 17) / 17.0,
                ]

            def create(self, **kwargs: object) -> SimpleNamespace:
                inputs = kwargs["input"]
                if isinstance(inputs, str):
                    payload = [inputs]
                else:
                    payload = list(inputs)
                data = [SimpleNamespace(embedding=self._embed(text)) for text in payload]
                return SimpleNamespace(data=data)

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())

        with self._stub_runner("First assistant memory"):
            first = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "How do unicorn horns grow?", "session_id": "s-memory-a"},
            )
        self.assertEqual(first.status_code, 200)

        captured: dict[str, str] = {}
        with self._stub_runner("Second response", capture=captured):
            second = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "Do unicorn horns keep growing?", "session_id": "s-memory-b"},
            )
        self.assertEqual(second.status_code, 200)
        self.assertIn("RETRIEVED_MEMORY", captured["input"])
        self.assertIn("First assistant memory", captured["input"])

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

    def test_metrics_reports_counts_and_latency_buckets(self) -> None:
        deps = server.get_runtime_deps()
        original_limit = deps.rate_limit_per_minute
        deps.rate_limit_per_minute = 1
        with self._stub_runner("ok"):
            first = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key", "x-forwarded-for": "1.1.1.1"},
                json={"message": "first", "session_id": "s-metrics"},
            )
            second = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key", "x-forwarded-for": "1.1.1.1"},
                json={"message": "second", "session_id": "s-metrics"},
            )
        deps.rate_limit_per_minute = original_limit
        deps.rate_limiter.clear()

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)

        metrics_resp = self.client.get("/metrics", headers={"x-api-key": "test-server-key"})
        self.assertEqual(metrics_resp.status_code, 200)
        metrics = metrics_resp.json()
        self.assertEqual(metrics["requests_total"], 2)
        self.assertEqual(metrics["status_counts"]["200"], 1)
        self.assertEqual(metrics["status_counts"]["429"], 1)
        self.assertEqual(metrics["rate_limited_total"], 1)
        self.assertGreaterEqual(metrics["uptime_seconds"], 0)
        self.assertGreater(metrics["avg_latency_ms"], 0)
        self.assertEqual(sum(metrics["latency_buckets"].values()), metrics["requests_total"])

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
