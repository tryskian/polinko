import base64
import hashlib
import json
import os
import tempfile
import unittest
import httpx
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from fastapi.testclient import TestClient
from openai import APIConnectionError, APIStatusError, AuthenticationError, RateLimitError
from api.app_factory import create_runtime_metrics
from api import app_factory
from core.history_store import ChatHistoryStore
from core.history_store import MessageFeedback
from core.prompts import ACTIVE_PROMPT_VERSION
from core.vector_store import VectorStore


os.environ.setdefault("OPENAI_API_KEY", "sk-test-key-123456789012345")
os.environ.setdefault("POLINKO_SERVER_API_KEY", "test-server-key")

import server  # noqa: E402


class PolinkoApiTests(unittest.TestCase):
    @staticmethod
    def _stub_runner(output: str, capture: dict[str, str] | None = None):
        async def fake_run(*args: object, **kwargs: Any) -> SimpleNamespace:
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
        deps.image_context_enabled = False
        deps.image_context_model = "gpt-4.1-mini"
        deps.image_context_prompt = "Summarize the visual scene for retrieval."
        deps.ocr_client = None
        deps.vector_enabled = False
        deps.vector_top_k = 2
        deps.vector_top_k_global = 2
        deps.vector_top_k_session = 2
        deps.vector_min_similarity = 0.40
        deps.vector_min_similarity_global = 0.40
        deps.vector_min_similarity_session = 0.40
        deps.vector_max_chars = 220
        deps.vector_exclude_current_session = True
        deps.vector_embedding_model = "text-embedding-3-small"
        deps.vector_store = None
        deps.embedding_client = None
        deps.responses_orchestration_enabled = False
        deps.responses_orchestration_model = "gpt-5-chat-latest"
        deps.responses_vector_store_id = None
        deps.responses_include_web_search = False
        deps.responses_history_turn_limit = 12
        deps.responses_pdf_ingest_enabled = False
        deps.responses_client = None
        deps.extraction_structured_enabled = False
        deps.extraction_structured_model = "gpt-4.1-mini"
        deps.governance_enabled = True
        deps.governance_allow_web_search = False
        deps.governance_log_only = False
        deps.hallucination_guardrails_enabled = True
        deps.personalization_default_memory_scope = "global"
        deps.clip_proxy_file_search_enabled = False
        deps.session_db_path = os.path.join(self.tmpdir.name, "test-memory.db")
        deps.history_store = ChatHistoryStore(os.path.join(self.tmpdir.name, "test-history.db"))
        deps.metrics = create_runtime_metrics()
        self.client = TestClient(server.app)

    def tearDown(self) -> None:
        self.client.close()
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
        self.assertEqual(body["memory_scope"], "global")
        self.assertEqual(body["context_scope"], "global")
        self.assertEqual(body["memory_used"], [])
        self.assertTrue(body["assistant_message_id"])

    def test_submit_and_list_message_feedback(self) -> None:
        with self._stub_runner("Feedback candidate"):
            chat_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "hello", "session_id": "s-feedback"},
            )
        self.assertEqual(chat_resp.status_code, 200)
        assistant_message_id = chat_resp.json()["assistant_message_id"]
        self.assertTrue(assistant_message_id)

        submit_resp = self.client.post(
            "/chats/s-feedback/feedback",
            headers={"x-api-key": "test-server-key"},
            json={
                "message_id": assistant_message_id,
                "outcome": "pass",
                "positive_tags": ["accurate", "grounded"],
                "note": "Clean response.",
            },
        )
        self.assertEqual(submit_resp.status_code, 200)
        payload = submit_resp.json()
        self.assertEqual(payload["outcome"], "pass")
        self.assertEqual(payload["status"], "closed")
        self.assertEqual(payload["positive_tags"], ["accurate", "grounded"])
        self.assertEqual(payload["negative_tags"], [])
        self.assertEqual(payload["tags"], ["accurate", "grounded"])
        self.assertIsNone(payload["recommended_action"])

        list_resp = self.client.get(
            "/chats/s-feedback/feedback",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(list_resp.status_code, 200)
        listed = list_resp.json()["feedback"]
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0]["message_id"], assistant_message_id)

    def test_submit_fail_feedback_with_em_dash_style_penalty(self) -> None:
        with self._stub_runner("Style candidate"):
            chat_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "style prompt", "session_id": "s-feedback-emdash"},
            )
        self.assertEqual(chat_resp.status_code, 200)
        assistant_message_id = chat_resp.json()["assistant_message_id"]
        self.assertTrue(assistant_message_id)

        submit_resp = self.client.post(
            "/chats/s-feedback-emdash/feedback",
            headers={"x-api-key": "test-server-key"},
            json={
                "message_id": assistant_message_id,
                "outcome": "fail",
                "negative_tags": ["em_dash_style"],
                "note": "Great answer, but avoid em-dashes.",
            },
        )
        self.assertEqual(submit_resp.status_code, 200)
        payload = submit_resp.json()
        self.assertEqual(payload["outcome"], "fail")
        self.assertEqual(payload["positive_tags"], [])
        self.assertEqual(payload["negative_tags"], ["em_dash_style"])
        self.assertEqual(payload["status"], "open")
        self.assertIn("style", str(payload["recommended_action"]).lower())

    def test_submit_pass_feedback_with_em_dash_style_penalty(self) -> None:
        with self._stub_runner("Style candidate pass"):
            chat_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "style prompt", "session_id": "s-feedback-pass-emdash"},
            )
        self.assertEqual(chat_resp.status_code, 200)
        assistant_message_id = chat_resp.json()["assistant_message_id"]
        self.assertTrue(assistant_message_id)

        submit_resp = self.client.post(
            "/chats/s-feedback-pass-emdash/feedback",
            headers={"x-api-key": "test-server-key"},
            json={
                "message_id": assistant_message_id,
                "outcome": "pass",
                "positive_tags": ["style", "high_value", "grounded"],
                "negative_tags": ["em_dash_style"],
                "note": "High-value response; em-dash usage was over target.",
            },
        )
        self.assertEqual(submit_resp.status_code, 400)
        self.assertIn("Pass cannot include negative reason tags", submit_resp.text)
        self.assertIn("em_dash_style", submit_resp.text)

    def test_submit_pass_feedback_with_default_style_penalty(self) -> None:
        with self._stub_runner("Style candidate pass with soft penalty"):
            chat_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "style prompt", "session_id": "s-feedback-pass-default-style"},
            )
        self.assertEqual(chat_resp.status_code, 200)
        assistant_message_id = chat_resp.json()["assistant_message_id"]
        self.assertTrue(assistant_message_id)

        submit_resp = self.client.post(
            "/chats/s-feedback-pass-default-style/feedback",
            headers={"x-api-key": "test-server-key"},
            json={
                "message_id": assistant_message_id,
                "outcome": "pass",
                "positive_tags": ["style", "medium_value", "grounded"],
                "negative_tags": ["default_style"],
                "note": "Pass quality overall, but response felt default/straight.",
            },
        )
        self.assertEqual(submit_resp.status_code, 200)
        payload = submit_resp.json()
        self.assertEqual(payload["outcome"], "pass")
        self.assertEqual(payload["status"], "closed")
        self.assertEqual(payload["positive_tags"], ["style", "medium_value", "grounded"])
        self.assertEqual(payload["negative_tags"], ["default_style"])
        self.assertIsNone(payload["recommended_action"])

    def test_submit_and_list_eval_feedback_checkpoints(self) -> None:
        with self._stub_runner("Checkpoint candidate one"):
            first_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "first prompt", "session_id": "s-feedback-checkpoint"},
            )
        self.assertEqual(first_resp.status_code, 200)
        first_assistant_id = first_resp.json()["assistant_message_id"]

        with self._stub_runner("Checkpoint candidate two"):
            second_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "second prompt", "session_id": "s-feedback-checkpoint"},
            )
        self.assertEqual(second_resp.status_code, 200)
        second_assistant_id = second_resp.json()["assistant_message_id"]

        pass_submit = self.client.post(
            "/chats/s-feedback-checkpoint/feedback",
            headers={"x-api-key": "test-server-key"},
            json={
                "message_id": first_assistant_id,
                "outcome": "pass",
                "positive_tags": ["accurate"],
            },
        )
        self.assertEqual(pass_submit.status_code, 200)

        fail_submit = self.client.post(
            "/chats/s-feedback-checkpoint/feedback",
            headers={"x-api-key": "test-server-key"},
            json={
                "message_id": second_assistant_id,
                "outcome": "fail",
                "negative_tags": ["grounding_gap"],
            },
        )
        self.assertEqual(fail_submit.status_code, 200)

        checkpoint_submit = self.client.post(
            "/chats/s-feedback-checkpoint/feedback/checkpoints",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(checkpoint_submit.status_code, 200)
        checkpoint_payload = checkpoint_submit.json()
        self.assertTrue(checkpoint_payload["checkpoint_id"].startswith("eval-"))
        self.assertEqual(checkpoint_payload["session_id"], "s-feedback-checkpoint")
        self.assertEqual(checkpoint_payload["total_count"], 2)
        self.assertEqual(checkpoint_payload["pass_count"], 1)
        self.assertEqual(checkpoint_payload["fail_count"], 1)
        self.assertEqual(checkpoint_payload["non_binary_count"], 0)
        self.assertEqual(checkpoint_payload["schema_version"], "polinko.eval_checkpoint.v2")

        listed = self.client.get(
            "/chats/s-feedback-checkpoint/feedback/checkpoints",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(listed.status_code, 200)
        checkpoints = listed.json()["checkpoints"]
        self.assertEqual(len(checkpoints), 1)
        self.assertEqual(checkpoints[0]["checkpoint_id"], checkpoint_payload["checkpoint_id"])
        self.assertEqual(checkpoints[0]["total_count"], 2)
        self.assertEqual(checkpoints[0]["schema_version"], "polinko.eval_checkpoint.v2")

    def test_submit_eval_checkpoint_counts_by_outcome_for_fail_feedback_with_positive_tags(self) -> None:
        session_id = "s-feedback-checkpoint-streams"
        with self._stub_runner("Checkpoint stream candidate"):
            chat_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "stream prompt", "session_id": session_id},
            )
        self.assertEqual(chat_resp.status_code, 200)
        assistant_message_id = chat_resp.json()["assistant_message_id"]

        submit_resp = self.client.post(
            f"/chats/{session_id}/feedback",
            headers={"x-api-key": "test-server-key"},
            json={
                "message_id": assistant_message_id,
                "outcome": "fail",
                "positive_tags": ["style"],
                "negative_tags": ["hallucination_risk"],
            },
        )
        self.assertEqual(submit_resp.status_code, 200)

        checkpoint_submit = self.client.post(
            f"/chats/{session_id}/feedback/checkpoints",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(checkpoint_submit.status_code, 200)
        checkpoint_payload = checkpoint_submit.json()
        self.assertEqual(checkpoint_payload["total_count"], 1)
        self.assertEqual(checkpoint_payload["pass_count"], 0)
        self.assertEqual(checkpoint_payload["fail_count"], 1)
        self.assertEqual(checkpoint_payload["non_binary_count"], 0)
        self.assertEqual(checkpoint_payload["schema_version"], "polinko.eval_checkpoint.v2")

    def test_submit_eval_checkpoint_requires_existing_feedback(self) -> None:
        with self._stub_runner("No eval yet"):
            chat_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "hello", "session_id": "s-feedback-empty-checkpoint"},
            )
        self.assertEqual(chat_resp.status_code, 200)

        checkpoint_submit = self.client.post(
            "/chats/s-feedback-empty-checkpoint/feedback/checkpoints",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(checkpoint_submit.status_code, 400)
        self.assertIn("No saved evals", checkpoint_submit.json()["detail"])

    def test_submit_eval_checkpoint_errors_on_non_binary_feedback_rows(self) -> None:
        session_id = "s-feedback-nonbinary-block"
        with self._stub_runner("checkpoint candidate"):
            chat_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "checkpoint prompt", "session_id": session_id},
            )
        self.assertEqual(chat_resp.status_code, 200)
        assistant_message_id = chat_resp.json()["assistant_message_id"]

        deps = server.get_runtime_deps()
        bad_entry = MessageFeedback(
            session_id=session_id,
            message_id=assistant_message_id,
            outcome="partial",
            positive_tags=["style"],
            negative_tags=[],
            tags=["style"],
            note=None,
            recommended_action=None,
            action_taken=None,
            status="open",
            created_at=1773000200000,
            updated_at=1773000200000,
        )
        with patch.object(deps.history_store, "list_message_feedback", return_value=[bad_entry]):
            checkpoint_submit = self.client.post(
                f"/chats/{session_id}/feedback/checkpoints",
                headers={"x-api-key": "test-server-key"},
            )
        self.assertEqual(checkpoint_submit.status_code, 500)
        self.assertIn("non-binary outcomes", checkpoint_submit.json()["detail"])

    def test_fail_feedback_generates_recommended_action_and_logs_inbox(self) -> None:
        with self._stub_runner("Please inspect this OCR output."):
            chat_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "run OCR", "session_id": "s-feedback-fail"},
            )
        self.assertEqual(chat_resp.status_code, 200)
        assistant_message_id = chat_resp.json()["assistant_message_id"]

        bad_target_resp = self.client.get(
            "/chats/s-feedback-fail/messages",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(bad_target_resp.status_code, 200)
        user_message_id = bad_target_resp.json()["messages"][0]["message_id"]
        user_feedback_resp = self.client.post(
            "/chats/s-feedback-fail/feedback",
            headers={"x-api-key": "test-server-key"},
            json={"message_id": user_message_id, "outcome": "pass"},
        )
        self.assertEqual(user_feedback_resp.status_code, 400)

        submit_resp = self.client.post(
            "/chats/s-feedback-fail/feedback",
            headers={"x-api-key": "test-server-key"},
            json={
                "message_id": assistant_message_id,
                "outcome": "fail",
                "negative_tags": ["ocr_miss"],
                "note": "Handwriting token mismatch.",
            },
        )
        self.assertEqual(submit_resp.status_code, 200)
        payload = submit_resp.json()
        self.assertEqual(payload["outcome"], "fail")
        self.assertEqual(payload["status"], "open")
        self.assertEqual(payload["positive_tags"], [])
        self.assertEqual(payload["negative_tags"], ["ocr_miss"])
        self.assertIn("Retry OCR", payload["recommended_action"])

    def test_feedback_rejects_missing_or_invalid_reason_tags(self) -> None:
        with self._stub_runner("Feedback candidate"):
            chat_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "hello", "session_id": "s-feedback-tags"},
            )
        self.assertEqual(chat_resp.status_code, 200)
        assistant_message_id = chat_resp.json()["assistant_message_id"]

        missing_tags_resp = self.client.post(
            "/chats/s-feedback-tags/feedback",
            headers={"x-api-key": "test-server-key"},
            json={"message_id": assistant_message_id, "outcome": "pass", "positive_tags": []},
        )
        self.assertEqual(missing_tags_resp.status_code, 400)

        invalid_tags_resp = self.client.post(
            "/chats/s-feedback-tags/feedback",
            headers={"x-api-key": "test-server-key"},
            json={
                "message_id": assistant_message_id,
                "outcome": "pass",
                "positive_tags": ["ocr_miss"],
            },
        )
        self.assertEqual(invalid_tags_resp.status_code, 400)

        pass_with_hard_negative_resp = self.client.post(
            "/chats/s-feedback-tags/feedback",
            headers={"x-api-key": "test-server-key"},
            json={
                "message_id": assistant_message_id,
                "outcome": "pass",
                "positive_tags": ["accurate"],
                "negative_tags": ["ocr_miss"],
            },
        )
        self.assertEqual(pass_with_hard_negative_resp.status_code, 400)

        fail_with_positive_resp = self.client.post(
            "/chats/s-feedback-tags/feedback",
            headers={"x-api-key": "test-server-key"},
            json={
                "message_id": assistant_message_id,
                "outcome": "fail",
                "positive_tags": ["accurate"],
                "negative_tags": ["ocr_miss"],
            },
        )
        self.assertEqual(fail_with_positive_resp.status_code, 200)
        fail_with_positive_payload = fail_with_positive_resp.json()
        self.assertEqual(fail_with_positive_payload["outcome"], "fail")
        self.assertEqual(fail_with_positive_payload["status"], "open")
        self.assertEqual(fail_with_positive_payload["positive_tags"], ["accurate"])
        self.assertEqual(fail_with_positive_payload["negative_tags"], ["ocr_miss"])
        self.assertEqual(fail_with_positive_payload["tags"], ["accurate", "ocr_miss"])

        invalid_outcome_resp = self.client.post(
            "/chats/s-feedback-tags/feedback",
            headers={"x-api-key": "test-server-key"},
            json={
                "message_id": assistant_message_id,
                "outcome": "unknown",
                "positive_tags": ["accurate"],
                "negative_tags": ["ocr_miss"],
            },
        )
        self.assertEqual(invalid_outcome_resp.status_code, 400)
        self.assertIn("outcome must be 'pass' or 'fail'", invalid_outcome_resp.json()["detail"])

        partial_outcome_resp = self.client.post(
            "/chats/s-feedback-tags/feedback",
            headers={"x-api-key": "test-server-key"},
            json={
                "message_id": assistant_message_id,
                "outcome": "partial",
                "positive_tags": ["accurate"],
            },
        )
        self.assertEqual(partial_outcome_resp.status_code, 400)

    def test_fail_feedback_keeps_status_open_and_logs_action(self) -> None:
        with self._stub_runner("Candidate with uneven quality"):
            chat_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "run OCR", "session_id": "s-feedback-fail-tags"},
            )
        self.assertEqual(chat_resp.status_code, 200)
        assistant_message_id = chat_resp.json()["assistant_message_id"]

        submit_resp = self.client.post(
            "/chats/s-feedback-fail-tags/feedback",
            headers={"x-api-key": "test-server-key"},
            json={
                "message_id": assistant_message_id,
                "outcome": "fail",
                "negative_tags": ["ocr_miss"],
                "note": "Grounded framing but token decode failed.",
            },
        )
        self.assertEqual(submit_resp.status_code, 200)
        payload = submit_resp.json()
        self.assertEqual(payload["outcome"], "fail")
        self.assertEqual(payload["status"], "open")
        self.assertEqual(payload["positive_tags"], [])
        self.assertEqual(payload["negative_tags"], ["ocr_miss"])
        self.assertIn("Retry OCR", payload["recommended_action"])

    def test_chat_attachment_indexes_global_memory_lane(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-chat-attachments.db"))
        deps.vector_min_similarity = 0.0
        deps.vector_min_similarity_global = 0.0
        deps.vector_min_similarity_session = 0.0

        class _FakeEmbeddings:
            @staticmethod
            def _embed(text: str) -> list[float]:
                lowered = text.lower()
                return [
                    1.0 if "tensor" in lowered else 0.0,
                    1.0 if "field" in lowered else 0.0,
                    1.0 if "perspective" in lowered else 0.0,
                    float(len(lowered) % 19) / 19.0,
                ]

            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=self._embed(text)) for text in payload]
                return SimpleNamespace(data=data)

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())

        payload_b64 = base64.b64encode(b"placeholder").decode("ascii")
        captured: dict[str, str] = {}
        with self._stub_runner("Attachment stored", capture=captured):
            resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={
                    "message": "Store this attachment context for future recall.",
                    "session_id": "s-attach-global",
                    "attachments": [
                        {
                            "source_name": "tensor-note.png",
                            "mime_type": "image/png",
                            "data_base64": payload_b64,
                            "text_hint": "knotted tensor field of perspective",
                            "memory_scope": "global",
                        }
                    ],
                },
            )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("ATTACHMENT_CONTEXT", captured["input"])

        query_vector = _FakeEmbeddings._embed("tensor field perspective")
        matches = deps.vector_store.search(
            query_embedding=query_vector,
            limit=10,
            min_similarity=0.0,
            roles=("assistant",),
            include_session_id="__global_memory__",
            source_types=("ocr", "image"),
        )
        self.assertGreaterEqual(len(matches), 1)
        self.assertTrue(any(match.metadata.get("origin_session_id") == "s-attach-global" for match in matches))

    def test_chat_attachment_global_memory_is_retrievable_across_chats(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(
            os.path.join(self.tmpdir.name, "test-vectors-chat-attachments-retrieval.db")
        )
        deps.vector_min_similarity = 0.0
        deps.vector_min_similarity_global = 0.0
        deps.vector_min_similarity_session = 0.0

        class _FakeEmbeddings:
            @staticmethod
            def _embed(text: str) -> list[float]:
                lowered = text.lower()
                return [
                    1.0 if "tensor" in lowered else 0.0,
                    1.0 if "field" in lowered else 0.0,
                    1.0 if "perspective" in lowered else 0.0,
                    float(len(lowered) % 23) / 23.0,
                ]

            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=self._embed(text)) for text in payload]
                return SimpleNamespace(data=data)

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())
        payload_b64 = base64.b64encode(b"placeholder").decode("ascii")

        with self._stub_runner("Seeded response"):
            seeded = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={
                    "message": "Store this phrase in memory for later retrieval.",
                    "session_id": "s-attach-seed",
                    "attachments": [
                        {
                            "source_name": "seed.png",
                            "mime_type": "image/png",
                            "data_base64": payload_b64,
                            "text_hint": "scalar tensor field supports perspective invariance",
                            "memory_scope": "global",
                        }
                    ],
                },
            )
        self.assertEqual(seeded.status_code, 200)

        captured: dict[str, str] = {}
        with self._stub_runner("Cross-chat response", capture=captured):
            followup = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={
                    "message": "From earlier scanned notes, what phrase described tensor field perspective invariance?",
                    "session_id": "s-attach-followup",
                },
            )
        self.assertEqual(followup.status_code, 200)
        payload = followup.json()
        self.assertGreaterEqual(len(payload["memory_used"]), 1)
        self.assertTrue(any(item["source_type"] == "ocr" for item in payload["memory_used"]))
        self.assertTrue(any(item["session_id"] == "s-attach-seed" for item in payload["memory_used"]))
        self.assertIn("RETRIEVED_MEMORY", captured["input"])

    def test_chat_attachment_ocr_dedups_identical_requests(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-chat-attachments-dedup.db"))
        deps.vector_min_similarity = 0.0
        deps.vector_min_similarity_global = 0.0
        deps.vector_min_similarity_session = 0.0

        class _FakeEmbeddings:
            @staticmethod
            def _embed(text: str) -> list[float]:
                lowered = text.lower()
                return [
                    1.0 if "dedup" in lowered else 0.0,
                    1.0 if "attachment" in lowered else 0.0,
                    1.0 if "context" in lowered else 0.0,
                    float(len(lowered) % 29) / 29.0,
                ]

            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=self._embed(text)) for text in payload]
                return SimpleNamespace(data=data)

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())

        payload_b64 = base64.b64encode(b"placeholder").decode("ascii")
        request_payload = {
            "message": "Store this attachment for dedup.",
            "session_id": "s-attach-dedup",
            "attachments": [
                {
                    "source_name": "dedup-attachment.png",
                    "mime_type": "image/png",
                    "data_base64": payload_b64,
                    "text_hint": "dedup attachment context",
                    "memory_scope": "global",
                }
            ],
        }
        with self._stub_runner("Attachment stored"):
            first = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json=request_payload,
            )
        self.assertEqual(first.status_code, 200)
        vector_count_after_first = deps.vector_store.active_count()
        self.assertGreater(vector_count_after_first, 0)
        runs_after_first = deps.history_store.list_ocr_runs(session_id="s-attach-dedup")
        self.assertEqual(len(runs_after_first), 1)
        ocr_query_vector = _FakeEmbeddings._embed("dedup attachment context")
        ocr_matches_after_first = deps.vector_store.search(
            query_embedding=ocr_query_vector,
            limit=50,
            min_similarity=0.0,
            roles=("assistant",),
            include_session_id="__global_memory__",
            source_types=("ocr", "image"),
        )
        ocr_match_count_after_first = len(
            [match for match in ocr_matches_after_first if match.metadata.get("origin_session_id") == "s-attach-dedup"]
        )
        self.assertGreater(ocr_match_count_after_first, 0)

        with (
            patch("api.app_factory._extract_text", side_effect=AssertionError("should not re-extract OCR text")),
            patch(
                "api.app_factory._extract_image_context",
                side_effect=AssertionError("should not re-run image context extraction"),
            ),
            self._stub_runner("Attachment reused"),
        ):
            second = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json=request_payload,
            )
        self.assertEqual(second.status_code, 200)
        self.assertGreater(deps.vector_store.active_count(), vector_count_after_first)
        runs_after_second = deps.history_store.list_ocr_runs(session_id="s-attach-dedup")
        self.assertEqual(len(runs_after_second), 1)
        self.assertEqual(runs_after_second[0].run_id, runs_after_first[0].run_id)
        ocr_matches_after_second = deps.vector_store.search(
            query_embedding=ocr_query_vector,
            limit=50,
            min_similarity=0.0,
            roles=("assistant",),
            include_session_id="__global_memory__",
            source_types=("ocr", "image"),
        )
        ocr_match_count_after_second = len(
            [match for match in ocr_matches_after_second if match.metadata.get("origin_session_id") == "s-attach-dedup"]
        )
        self.assertEqual(ocr_match_count_after_second, ocr_match_count_after_first)

    def test_chat_attachment_ocr_query_uses_literal_transcription_reply(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-chat-attachments-literal.db"))
        deps.embedding_client = SimpleNamespace(
            embeddings=SimpleNamespace(create=lambda **_: SimpleNamespace(data=[SimpleNamespace(embedding=[0.1, 0.2])]))
        )

        payload_b64 = base64.b64encode(b"placeholder").decode("ascii")

        async def _runner_should_not_be_called(*args: object, **kwargs: Any) -> SimpleNamespace:
            del args, kwargs
            raise AssertionError("Runner.run should not be called for literal OCR attachment reply.")

        with patch.object(server.Runner, "run", new=_runner_should_not_be_called):
            resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={
                    "message": "what does this say?",
                    "session_id": "s-attach-literal",
                    "attachments": [
                        {
                            "source_name": "sample.png",
                            "mime_type": "image/png",
                            "data_base64": payload_b64,
                            "text_hint": "gyrus folds within",
                            "memory_scope": "global",
                        }
                    ],
                },
            )
        self.assertEqual(resp.status_code, 200)
        output = resp.json()["output"]
        self.assertIn("[OCR]", output)
        self.assertIn("gyrus folds within", output)

    def test_chat_ocr_followup_without_new_image_blocks_reguessing(self) -> None:
        async def _runner_should_not_be_called(*args: object, **kwargs: Any) -> SimpleNamespace:
            del args, kwargs
            raise AssertionError("Runner.run should not be called for no-new-image OCR follow-up.")

        with patch.object(server.Runner, "run", new=_runner_should_not_be_called):
            resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={
                    "message": "try again without using memory",
                    "session_id": "s-ocr-followup-no-image",
                },
            )
        self.assertEqual(resp.status_code, 200)
        output = resp.json()["output"].lower()
        self.assertIn("no new image evidence", output)
        self.assertIn("attach a new image", output)

    def test_chat_short_non_ocr_reply_does_not_trigger_ocr_followup_block(self) -> None:
        with self._stub_runner("Normal conversational reply"):
            resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={
                    "message": "haha yeah, that totally makes sense!",
                    "session_id": "s-non-ocr-short-reply",
                },
            )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["output"], "Normal conversational reply")

    def test_chat_regular_what_does_query_is_not_misclassified_as_ocr(self) -> None:
        with self._stub_runner("Grounded retrieval answer"):
            resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={
                    "message": "What does nimbus grid attach to anomaly scores first?",
                    "session_id": "s-non-ocr-what-does",
                },
            )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["output"], "Grounded retrieval answer")
        self.assertNotIn("no new image evidence", resp.json()["output"].lower())

    def test_chat_ocr_numeric_correction_without_new_image_blocks_after_recent_ocr(self) -> None:
        deps = server.get_runtime_deps()
        deps.history_store.ensure_chat(session_id="s-ocr-correction-no-image")
        deps.history_store.record_ocr_run(
            run_id="ocr-test-recent",
            session_id="s-ocr-correction-no-image",
            source_name="sample.png",
            mime_type="image/png",
            source_message_id=None,
            result_message_id=None,
            status="ok",
            extracted_text="1914",
        )

        async def _runner_should_not_be_called(*args: object, **kwargs: Any) -> SimpleNamespace:
            del args, kwargs
            raise AssertionError("Runner.run should not be called for no-new-image OCR correction.")

        with patch.object(server.Runner, "run", new=_runner_should_not_be_called):
            resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={
                    "message": "1916",
                    "session_id": "s-ocr-correction-no-image",
                },
            )
        self.assertEqual(resp.status_code, 200)
        output = resp.json()["output"].lower()
        self.assertIn("no new image evidence", output)
        self.assertIn("attach a new image", output)

    def test_chat_success_with_responses_orchestration(self) -> None:
        deps = server.get_runtime_deps()
        deps.responses_orchestration_enabled = True
        deps.responses_orchestration_model = "gpt-5-chat-latest"
        deps.responses_vector_store_id = "vs_test_123"
        deps.responses_include_web_search = True
        deps.governance_allow_web_search = True
        deps.responses_history_turn_limit = 8
        captured: dict[str, Any] = {}

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                captured["kwargs"] = kwargs
                return SimpleNamespace(output_text="Orchestrated response")

        deps.responses_client = SimpleNamespace(responses=_FakeResponses())

        first = self.client.post(
            "/chat",
            headers={"x-api-key": "test-server-key"},
            json={"message": "first orchestration prompt", "session_id": "s-rag"},
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json()["output"], "Orchestrated response")
        self.assertIn("kwargs", captured)

        kwargs = captured["kwargs"]
        self.assertEqual(kwargs["model"], "gpt-5-chat-latest")
        self.assertIn("input", kwargs)
        self.assertIn("[USER_MESSAGE]", kwargs["input"])
        tools = kwargs["tools"]
        self.assertEqual(tools[0]["type"], "file_search")
        self.assertEqual(tools[0]["vector_store_ids"], ["vs_test_123"])
        self.assertTrue(any(tool.get("type") == "web_search_preview" for tool in tools))

        second = self.client.post(
            "/chat",
            headers={"x-api-key": "test-server-key"},
            json={"message": "follow-up orchestration", "session_id": "s-rag"},
        )
        self.assertEqual(second.status_code, 200)
        second_kwargs = captured["kwargs"]
        self.assertIn("RECENT_CHAT_CONTEXT", second_kwargs["input"])
        self.assertIn("ASSISTANT: Orchestrated response", second_kwargs["input"])

    def test_chat_orchestration_requires_vector_store_id(self) -> None:
        deps = server.get_runtime_deps()
        deps.responses_orchestration_enabled = True
        deps.responses_vector_store_id = None

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                return SimpleNamespace(output_text="unused")

        deps.responses_client = SimpleNamespace(responses=_FakeResponses())
        resp = self.client.post(
            "/chat",
            headers={"x-api-key": "test-server-key"},
            json={"message": "hello", "session_id": "s-rag-missing-vs"},
        )
        self.assertEqual(resp.status_code, 503)

    def test_chat_orchestration_blocks_web_search_when_governed(self) -> None:
        deps = server.get_runtime_deps()
        deps.responses_orchestration_enabled = True
        deps.responses_orchestration_model = "gpt-5-chat-latest"
        deps.responses_vector_store_id = "vs_test_block"
        deps.responses_include_web_search = True
        deps.governance_enabled = True
        deps.governance_allow_web_search = False
        deps.governance_log_only = False
        captured: dict[str, Any] = {}

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                captured["kwargs"] = kwargs
                return SimpleNamespace(output_text="Governed response")

        deps.responses_client = SimpleNamespace(responses=_FakeResponses())
        resp = self.client.post(
            "/chat",
            headers={"x-api-key": "test-server-key"},
            json={"message": "What's latest in AI safety policy?", "session_id": "s-rag-governed"},
        )
        self.assertEqual(resp.status_code, 200)
        tools = captured["kwargs"]["tools"]
        self.assertEqual(tools[0]["type"], "file_search")
        self.assertFalse(any(tool.get("type") == "web_search_preview" for tool in tools))

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
        self.assertEqual(chats[0]["memory_scope"], "global")
        self.assertEqual(chats[0]["context_scope"], "global")

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
        self.assertRegex(messages[0]["content_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(messages[1]["content_sha256"], r"^[0-9a-f]{64}$")
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

    def test_chat_retry_variant_branches_under_existing_user_message(self) -> None:
        with self._stub_runner("turn-1"):
            first = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "first turn", "session_id": "s-variant"},
            )
        self.assertEqual(first.status_code, 200)

        initial_messages_resp = self.client.get(
            "/chats/s-variant/messages",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(initial_messages_resp.status_code, 200)
        initial_messages = initial_messages_resp.json()["messages"]
        self.assertEqual([m["role"] for m in initial_messages], ["user", "assistant"])
        source_user_message_id = initial_messages[0]["message_id"]

        with self._stub_runner("turn-1 retry"):
            retry_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={
                    "message": "first turn",
                    "session_id": "s-variant",
                    "source_user_message_id": source_user_message_id,
                },
            )
        self.assertEqual(retry_resp.status_code, 200)

        messages_resp = self.client.get(
            "/chats/s-variant/messages",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(messages_resp.status_code, 200)
        messages = messages_resp.json()["messages"]
        self.assertEqual([m["role"] for m in messages], ["user", "assistant", "assistant"])
        self.assertEqual(messages[1]["parent_message_id"], source_user_message_id)
        self.assertEqual(messages[2]["parent_message_id"], source_user_message_id)
        self.assertEqual(messages[2]["content"], "turn-1 retry")

    def test_chat_retry_variant_rejects_invalid_source_user_message_id(self) -> None:
        with self._stub_runner("base turn"):
            base = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "base", "session_id": "s-variant-invalid"},
            )
        self.assertEqual(base.status_code, 200)

        missing_source = self.client.post(
            "/chat",
            headers={"x-api-key": "test-server-key"},
            json={
                "message": "retry",
                "session_id": "s-variant-invalid",
                "source_user_message_id": "msg_missing_source_000000000000",
            },
        )
        self.assertEqual(missing_source.status_code, 404)

        messages_resp = self.client.get(
            "/chats/s-variant-invalid/messages",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(messages_resp.status_code, 200)
        assistant_message_id = messages_resp.json()["messages"][1]["message_id"]

        assistant_as_source = self.client.post(
            "/chat",
            headers={"x-api-key": "test-server-key"},
            json={
                "message": "retry",
                "session_id": "s-variant-invalid",
                "source_user_message_id": assistant_message_id,
            },
        )
        self.assertEqual(assistant_as_source.status_code, 400)

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
        self.assertEqual(payload["memory_scope"], "global")
        self.assertEqual(payload["context_scope"], "global")
        self.assertEqual(payload["prompt_version"], ACTIVE_PROMPT_VERSION)
        self.assertEqual(payload["message_count"], 2)
        self.assertEqual(payload["markdown"], None)
        self.assertEqual(payload["ocr_runs"], [])
        self.assertEqual([m["role"] for m in payload["messages"]], ["user", "assistant"])
        self.assertIn("message_id", payload["messages"][0])
        self.assertIn("parent_message_id", payload["messages"][1])
        self.assertRegex(payload["messages"][0]["content_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(payload["messages"][1]["content_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(payload["transcript_sha256"], r"^[0-9a-f]{64}$")

        expected_parts = [
            (
                f"{m['message_id']}\x1f{m['parent_message_id'] or ''}\x1f"
                f"{m['role']}\x1f{m['created_at']}\x1f{m['content_sha256']}"
            )
            for m in payload["messages"]
        ]
        expected_transcript_sha = hashlib.sha256("\x1e".join(expected_parts).encode("utf-8")).hexdigest()
        self.assertEqual(payload["transcript_sha256"], expected_transcript_sha)

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
        structured = run["structured"]
        self.assertEqual(structured["schema_version"], "v1")
        self.assertEqual(structured["source_type"], "ocr")
        self.assertEqual(structured["source_name"], "scribble.txt")
        self.assertEqual(structured["mime_type"], "text/plain")
        self.assertEqual(structured["char_count"], len(run["extracted_text"]))
        self.assertEqual(
            structured["text_sha256"],
            hashlib.sha256(run["extracted_text"].encode("utf-8")).hexdigest(),
        )
        self.assertGreaterEqual(structured["word_count"], 1)
        self.assertGreaterEqual(structured["line_count"], 1)

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
        captured: dict[str, Any] = {}

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
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
        self.assertEqual(run["structured"]["source_type"], "ocr")
        self.assertEqual(run["structured"]["schema_version"], "v1")
        self.assertIn("kwargs", captured)
        kwargs = captured["kwargs"]
        self.assertEqual(kwargs["model"], deps.ocr_model)
        self.assertIn("input", kwargs)
        ocr_prompt_text = kwargs["input"][0]["content"][0]["text"]
        self.assertIn("Output mode: verbatim.", ocr_prompt_text)

    def test_ocr_skill_openai_strips_commentary_preface_lines(self) -> None:
        deps = server.get_runtime_deps()
        deps.ocr_provider = "openai"

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                return SimpleNamespace(
                    output_text=(
                        'The text appears to read: "gyrus-fold-within."\n'
                        "All lowercase, each word in sequence with dashes marking the steps."
                    )
                )

        deps.ocr_client = SimpleNamespace(responses=_FakeResponses())
        payload_b64 = base64.b64encode(b"not-really-an-image").decode("ascii")

        run_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-ocr-openai-cleanup",
                "source_name": "scan.png",
                "mime_type": "image/png",
                "data_base64": payload_b64,
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_resp.status_code, 200)
        run = run_resp.json()["run"]
        self.assertEqual(run["status"], "ok")
        self.assertEqual(run["extracted_text"], "gyrus-fold-within.")

    def test_ocr_coerce_disambiguates_um_to_llm_in_model_context(self) -> None:
        raw = (
            "This not only creates a model\n"
            "that reasons through its own reasoning but also requires\n"
            "the user to adjust + transform\n"
            "their own output so\n"
            "that the UM can understand\n"
            "human semiotics + lexeme."
        )
        out = app_factory._coerce_literal_ocr_output(raw)
        self.assertIn("LLM", out)
        self.assertNotIn(" UM ", f" {out} ")

    def test_ocr_skill_openai_uncertain_guesses_become_unknown(self) -> None:
        deps = server.get_runtime_deps()
        deps.ocr_provider = "openai"
        deps.ocr_uncertainty_safe = True

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                return SimpleNamespace(
                    output_text='The second word likely represents "sulcin" or "sulcus" with missing letters.'
                )

        deps.ocr_client = SimpleNamespace(responses=_FakeResponses())
        payload_b64 = base64.b64encode(b"not-really-an-image").decode("ascii")

        run_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-ocr-openai-uncertain",
                "source_name": "scan.png",
                "mime_type": "image/png",
                "data_base64": payload_b64,
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_resp.status_code, 200)
        run = run_resp.json()["run"]
        self.assertEqual(run["status"], "ok")
        self.assertEqual(run["extracted_text"], "[?]")

    def test_ocr_skill_openai_uncertainty_safety_can_be_disabled(self) -> None:
        deps = server.get_runtime_deps()
        deps.ocr_provider = "openai"
        deps.ocr_uncertainty_safe = False
        uncertain_line = 'The second word likely represents "sulcin" or "sulcus" with missing letters.'

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                return SimpleNamespace(output_text=uncertain_line)

        deps.ocr_client = SimpleNamespace(responses=_FakeResponses())
        payload_b64 = base64.b64encode(b"not-really-an-image").decode("ascii")

        run_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-ocr-openai-uncertain-off",
                "source_name": "scan.png",
                "mime_type": "image/png",
                "data_base64": payload_b64,
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_resp.status_code, 200)
        run = run_resp.json()["run"]
        self.assertEqual(run["status"], "ok")
        self.assertEqual(run["extracted_text"], uncertain_line)

    def test_ocr_skill_dedups_identical_requests(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-ocr-dedup.db"))

        class _FakeEmbeddings:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=[0.1, 0.2, 0.3, float(len(text) % 17) / 17.0]) for text in payload]
                return SimpleNamespace(data=data)

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())

        request_payload = {
            "session_id": "s-ocr-dedup",
            "source_name": "dedup-note.txt",
            "mime_type": "text/plain",
            "text_hint": "dedup check line one\ndedup check line two",
            "attach_to_chat": True,
        }
        first_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json=request_payload,
        )
        self.assertEqual(first_resp.status_code, 200)
        first_run = first_resp.json()["run"]
        vector_count_after_first = deps.vector_store.active_count()
        self.assertGreater(vector_count_after_first, 0)

        second_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json=request_payload,
        )
        self.assertEqual(second_resp.status_code, 200)
        second_run = second_resp.json()["run"]
        self.assertEqual(second_run["run_id"], first_run["run_id"])
        self.assertEqual(second_run["result_message_id"], first_run["result_message_id"])
        self.assertEqual(deps.vector_store.active_count(), vector_count_after_first)

        messages_resp = self.client.get(
            "/chats/s-ocr-dedup/messages",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(messages_resp.status_code, 200)
        messages = messages_resp.json()["messages"]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["message_id"], first_run["result_message_id"])

    def test_ocr_skill_openai_normalized_mode_applies_normalization(self) -> None:
        deps = server.get_runtime_deps()
        deps.ocr_provider = "openai"

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                return SimpleNamespace(output_text="  line   one  \n\nline   two  ")

        deps.ocr_client = SimpleNamespace(responses=_FakeResponses())
        payload_b64 = base64.b64encode(b"not-really-an-image").decode("ascii")

        run_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-ocr-openai-normalized",
                "source_name": "scan.png",
                "mime_type": "image/png",
                "data_base64": payload_b64,
                "transcription_mode": "normalized",
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_resp.status_code, 200)
        run = run_resp.json()["run"]
        self.assertEqual(run["extracted_text"], "line one\nline two")

    def test_ocr_skill_openai_rejects_non_image_payload(self) -> None:
        deps = server.get_runtime_deps()
        deps.ocr_provider = "openai"
        deps.ocr_client = SimpleNamespace(responses=SimpleNamespace(create=lambda **_: None))
        payload_b64 = base64.b64encode(b"plain-text-payload").decode("ascii")

        run_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-ocr-openai-non-image",
                "mime_type": "text/plain",
                "data_base64": payload_b64,
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_resp.status_code, 422)
        self.assertIn("expects image input", run_resp.json()["detail"])

    def test_ocr_skill_rejects_oversized_payload(self) -> None:
        raw_bytes = b"A" * 64
        payload_b64 = base64.b64encode(raw_bytes).decode("ascii")
        with patch("api.app_factory._OCR_MAX_BYTES", 32):
            run_resp = self.client.post(
                "/skills/ocr",
                headers={"x-api-key": "test-server-key"},
                json={
                    "session_id": "s-ocr-too-big",
                    "mime_type": "image/png",
                    "data_base64": payload_b64,
                    "attach_to_chat": False,
                },
            )
        self.assertEqual(run_resp.status_code, 413)
        self.assertIn("too large", run_resp.json()["detail"])

    def test_ocr_openai_rate_limit_sets_retry_after(self) -> None:
        deps = server.get_runtime_deps()
        deps.ocr_provider = "openai"
        request = httpx.Request("POST", "https://api.openai.com/v1/responses")
        response = httpx.Response(429, request=request, headers={"Retry-After": "7"})

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                raise RateLimitError("rate limited", response=response, body={})

        deps.ocr_client = SimpleNamespace(responses=_FakeResponses())
        payload_b64 = base64.b64encode(b"fake-image").decode("ascii")
        run_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-ocr-openai-rate-limit",
                "mime_type": "image/png",
                "data_base64": payload_b64,
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_resp.status_code, 429)
        self.assertEqual(run_resp.headers.get("Retry-After"), "7")

    def test_ocr_openai_provider_5xx_sets_retry_after(self) -> None:
        deps = server.get_runtime_deps()
        deps.ocr_provider = "openai"
        request = httpx.Request("POST", "https://api.openai.com/v1/responses")
        response = httpx.Response(503, request=request, headers={"Retry-After": "2"})

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                raise APIStatusError("upstream unavailable", response=response, body={})

        deps.ocr_client = SimpleNamespace(responses=_FakeResponses())
        payload_b64 = base64.b64encode(b"fake-image").decode("ascii")
        run_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-ocr-openai-5xx",
                "mime_type": "image/png",
                "data_base64": payload_b64,
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_resp.status_code, 503)
        self.assertEqual(run_resp.headers.get("Retry-After"), "2")

    def test_ocr_openai_connection_error_sets_retry_after(self) -> None:
        deps = server.get_runtime_deps()
        deps.ocr_provider = "openai"
        request = httpx.Request("POST", "https://api.openai.com/v1/responses")

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                raise APIConnectionError(message="connection error", request=request)

        deps.ocr_client = SimpleNamespace(responses=_FakeResponses())
        payload_b64 = base64.b64encode(b"fake-image").decode("ascii")
        run_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-ocr-openai-conn",
                "mime_type": "image/png",
                "data_base64": payload_b64,
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_resp.status_code, 503)
        self.assertEqual(run_resp.headers.get("Retry-After"), "3")

    def test_ocr_structured_preview_enrichment_via_responses(self) -> None:
        deps = server.get_runtime_deps()
        deps.extraction_structured_enabled = True
        captured: dict[str, Any] = {}
        source_text = "line one from scan\nline two from scan"
        expected_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                captured["kwargs"] = kwargs
                payload = {
                    "schema_version": "v1",
                    "source_type": "ocr",
                    "source_name": "scan.png",
                    "mime_type": "image/png",
                    "text_sha256": expected_hash,
                    "char_count": len(source_text),
                    "word_count": 8,
                    "line_count": 2,
                    "preview": "Model-tuned preview.",
                }
                return SimpleNamespace(output_text=json.dumps(payload))

        deps.responses_client = SimpleNamespace(responses=_FakeResponses())

        run_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-ocr-structured",
                "source_name": "scan.png",
                "mime_type": "image/png",
                "text_hint": source_text,
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_resp.status_code, 200)
        run = run_resp.json()["run"]
        self.assertEqual(run["structured"]["preview"], "Model-tuned preview.")
        self.assertEqual(run["structured"]["text_sha256"], expected_hash)
        self.assertEqual(run["structured"]["char_count"], len(source_text))
        self.assertEqual(run["structured"]["enrichment_status"], "enriched")
        self.assertIsNone(run["structured"]["fallback_reason"])
        kwargs = captured["kwargs"]
        self.assertEqual(kwargs["model"], deps.extraction_structured_model)
        self.assertEqual(kwargs["text"]["format"]["type"], "json_schema")
        self.assertEqual(kwargs["text"]["format"]["name"], "extraction_structured_ocr_v1")
        self.assertEqual(
            kwargs["text"]["format"]["schema"]["properties"]["source_type"]["const"],
            "ocr",
        )

    def test_ocr_structured_falls_back_when_model_output_is_invalid_json(self) -> None:
        deps = server.get_runtime_deps()
        deps.extraction_structured_enabled = True
        source_text = "alpha line\nbeta line"
        expected_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                return SimpleNamespace(output_text="{not-json")

        deps.responses_client = SimpleNamespace(responses=_FakeResponses())
        run_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-ocr-structured-invalid-json",
                "source_name": "scan-invalid.png",
                "mime_type": "image/png",
                "text_hint": source_text,
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_resp.status_code, 200)
        structured = run_resp.json()["run"]["structured"]
        self.assertEqual(structured["text_sha256"], expected_hash)
        self.assertEqual(structured["char_count"], len(source_text))
        self.assertEqual(structured["source_name"], "scan-invalid.png")
        self.assertEqual(structured["source_type"], "ocr")
        self.assertEqual(structured["preview"], "alpha line beta line")
        self.assertEqual(structured["enrichment_status"], "fallback")
        self.assertEqual(structured["fallback_reason"], "invalid_json")

    def test_ocr_structured_falls_back_when_model_schema_mismatches_source_type(self) -> None:
        deps = server.get_runtime_deps()
        deps.extraction_structured_enabled = True
        source_text = "source text that should remain grounded"
        expected_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                payload = {
                    "schema_version": "v1",
                    "source_type": "pdf",
                    "source_name": "wrong-type.pdf",
                    "mime_type": "application/pdf",
                    "text_sha256": expected_hash,
                    "char_count": len(source_text),
                    "word_count": 6,
                    "line_count": 1,
                    "preview": "This should be rejected by OCR schema.",
                }
                return SimpleNamespace(output_text=json.dumps(payload))

        deps.responses_client = SimpleNamespace(responses=_FakeResponses())
        run_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-ocr-structured-type-mismatch",
                "source_name": "scan-mismatch.png",
                "mime_type": "image/png",
                "text_hint": source_text,
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_resp.status_code, 200)
        structured = run_resp.json()["run"]["structured"]
        self.assertEqual(structured["source_type"], "ocr")
        self.assertEqual(structured["source_name"], "scan-mismatch.png")
        self.assertEqual(structured["mime_type"], "image/png")
        self.assertEqual(structured["text_sha256"], expected_hash)
        self.assertEqual(structured["preview"], "source text that should remain grounded")
        self.assertEqual(structured["enrichment_status"], "fallback")
        self.assertEqual(structured["fallback_reason"], "metadata_mismatch")

    def test_ocr_structured_uses_only_preview_and_clamps_length(self) -> None:
        deps = server.get_runtime_deps()
        deps.extraction_structured_enabled = True
        source_text = "trusted source text"
        expected_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
        long_preview = "model preview " * 60

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                payload = {
                    "schema_version": "v1",
                    "source_type": "ocr",
                    "source_name": "scan-clamp.png",
                    "mime_type": "image/png",
                    "text_sha256": expected_hash,
                    "char_count": len(source_text),
                    "word_count": 3,
                    "line_count": 1,
                    "preview": long_preview,
                }
                return SimpleNamespace(output_text=json.dumps(payload))

        deps.responses_client = SimpleNamespace(responses=_FakeResponses())
        run_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-ocr-structured-clamp",
                "source_name": "scan-clamp.png",
                "mime_type": "image/png",
                "text_hint": source_text,
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_resp.status_code, 200)
        structured = run_resp.json()["run"]["structured"]
        self.assertEqual(structured["text_sha256"], expected_hash)
        self.assertEqual(structured["char_count"], len(source_text))
        self.assertEqual(structured["source_name"], "scan-clamp.png")
        self.assertLessEqual(len(structured["preview"]), 240)
        self.assertTrue(structured["preview"].startswith("model preview"))
        self.assertEqual(structured["enrichment_status"], "enriched")
        self.assertIsNone(structured["fallback_reason"])

    def test_ocr_structured_unexpected_error_falls_back_to_base_schema(self) -> None:
        deps = server.get_runtime_deps()
        deps.extraction_structured_enabled = True
        source_text = "fallback when enrichment fails unexpectedly"
        expected_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                raise RuntimeError("unexpected parser failure")

        deps.responses_client = SimpleNamespace(responses=_FakeResponses())
        run_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-ocr-structured-unexpected",
                "source_name": "scan-unexpected.png",
                "mime_type": "image/png",
                "text_hint": source_text,
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_resp.status_code, 200)
        structured = run_resp.json()["run"]["structured"]
        self.assertEqual(structured["text_sha256"], expected_hash)
        self.assertEqual(structured["char_count"], len(source_text))
        self.assertEqual(structured["source_name"], "scan-unexpected.png")
        self.assertEqual(structured["source_type"], "ocr")
        self.assertTrue(structured["preview"].startswith("fallback when enrichment"))
        self.assertEqual(structured["enrichment_status"], "fallback")
        self.assertEqual(structured["fallback_reason"], "unexpected_error")

    def test_ocr_optionally_indexes_image_context_vectors(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-image-context.db"))
        deps.image_context_enabled = True
        deps.image_context_model = "gpt-4.1-mini"
        deps.image_context_prompt = "Summarize scene."

        class _FakeEmbeddings:
            @staticmethod
            def _embed(text: str) -> list[float]:
                lowered = text.lower()
                return [
                    1.0 if "nimbus" in lowered else 0.0,
                    1.0 if "awning" in lowered else 0.0,
                    1.0 if "clinic" in lowered else 0.0,
                    float(len(lowered) % 23) / 23.0,
                ]

            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=self._embed(text)) for text in payload]
                return SimpleNamespace(data=data)

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                return SimpleNamespace(
                    output_text="A storefront sign reads Nimbus Clinic under a blue awning."
                )

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())
        deps.responses_client = SimpleNamespace(responses=_FakeResponses())

        payload_b64 = base64.b64encode(b"\x89PNG fake").decode("ascii")
        run_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-ocr-image-context",
                "source_name": "storefront.png",
                "mime_type": "image/png",
                "data_base64": payload_b64,
                "text_hint": "OCR baseline text",
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_resp.status_code, 200)
        run = run_resp.json()["run"]
        self.assertIn("Nimbus Clinic", run["visual_context"])

        search = self.client.post(
            "/skills/file_search",
            headers={"x-api-key": "test-server-key"},
            json={
                "query": "nimbus clinic blue awning",
                "session_id": "s-ocr-image-context",
                "source_types": ["image"],
                "limit": 3,
            },
        )
        self.assertEqual(search.status_code, 200)
        matches = search.json()["matches"]
        self.assertGreater(len(matches), 0)
        first = matches[0]
        self.assertEqual(first["source_type"], "image")
        self.assertEqual(first["metadata"]["source"], "image_context")
        self.assertEqual(first["metadata"]["source_name"], "storefront.png")

    def test_ocr_visual_context_hint_indexes_image_vectors_when_image_context_disabled(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-image-context-hint.db"))
        deps.image_context_enabled = False

        class _FakeEmbeddings:
            @staticmethod
            def _embed(text: str) -> list[float]:
                lowered = text.lower()
                return [
                    1.0 if "nimbus" in lowered else 0.0,
                    1.0 if "awning" in lowered else 0.0,
                    1.0 if "clinic" in lowered else 0.0,
                    float(len(lowered) % 23) / 23.0,
                ]

            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=self._embed(text)) for text in payload]
                return SimpleNamespace(data=data)

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())
        deps.responses_client = None

        payload_b64 = base64.b64encode(b"\x89PNG fake").decode("ascii")
        run_resp = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-ocr-image-context-hint",
                "source_name": "storefront-hint.png",
                "mime_type": "image/png",
                "data_base64": payload_b64,
                "text_hint": "OCR baseline text",
                "visual_context_hint": "Storefront sign reads Nimbus Clinic under a blue awning.",
                "attach_to_chat": False,
            },
        )
        self.assertEqual(run_resp.status_code, 200)
        run = run_resp.json()["run"]
        self.assertIn("Nimbus Clinic", run["visual_context"])

        search = self.client.post(
            "/skills/file_search",
            headers={"x-api-key": "test-server-key"},
            json={
                "query": "nimbus clinic blue awning",
                "session_id": "s-ocr-image-context-hint",
                "source_types": ["image"],
                "limit": 3,
            },
        )
        self.assertEqual(search.status_code, 200)
        matches = search.json()["matches"]
        self.assertGreater(len(matches), 0)
        first = matches[0]
        self.assertEqual(first["source_type"], "image")
        self.assertEqual(first["metadata"]["source"], "image_context")
        self.assertEqual(first["metadata"]["source_name"], "storefront-hint.png")

    def test_pdf_ingest_indexes_vectors_and_is_searchable(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-pdf.db"))

        class _FakeEmbeddings:
            @staticmethod
            def _embed(text: str) -> list[float]:
                lowered = text.lower()
                return [
                    1.0 if "invoice" in lowered else 0.0,
                    1.0 if "retainer" in lowered else 0.0,
                    1.0 if "total" in lowered else 0.0,
                    float(len(lowered) % 19) / 19.0,
                ]

            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                if isinstance(inputs, str):
                    payload = [inputs]
                else:
                    payload = list(inputs)
                data = [SimpleNamespace(embedding=self._embed(text)) for text in payload]
                return SimpleNamespace(data=data)

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())

        pdf_text = (
            "Invoice archive\n"
            "retainer services listed\n"
            "subtotal and total included"
        )
        payload_b64 = base64.b64encode(b"%PDF-1.7 fake-payload").decode("ascii")
        with patch("api.app_factory._extract_text_from_pdf_bytes", return_value=pdf_text):
            ingest_resp = self.client.post(
                "/skills/pdf_ingest",
                headers={"x-api-key": "test-server-key"},
                json={
                    "session_id": "s-pdf",
                    "source_name": "invoice-2026.pdf",
                    "mime_type": "application/pdf",
                    "data_base64": payload_b64,
                    "attach_to_chat": False,
                },
            )

        self.assertEqual(ingest_resp.status_code, 200)
        ingest = ingest_resp.json()
        self.assertRegex(ingest["ingest_id"], r"^pdf-[0-9a-f]{12}$")
        self.assertEqual(ingest["status"], "ok")
        self.assertGreaterEqual(ingest["vector_chunks"], 1)
        self.assertGreater(ingest["extracted_chars"], 20)
        self.assertEqual(ingest["responses_index_status"], "disabled")
        self.assertEqual(ingest["responses_index_reason"], "feature_disabled")
        self.assertIsNone(ingest["responses_vector_store_file_id"])
        structured = ingest["structured"]
        self.assertEqual(structured["schema_version"], "v1")
        self.assertEqual(structured["source_type"], "pdf")
        self.assertEqual(structured["source_name"], "invoice-2026.pdf")
        self.assertEqual(structured["mime_type"], "application/pdf")
        self.assertEqual(structured["char_count"], len(pdf_text))
        self.assertEqual(
            structured["text_sha256"],
            hashlib.sha256(pdf_text.encode("utf-8")).hexdigest(),
        )

        search = self.client.post(
            "/skills/file_search",
            headers={"x-api-key": "test-server-key"},
            json={
                "query": "find invoice retainer total",
                "session_id": "s-pdf",
                "source_types": ["pdf"],
                "limit": 3,
            },
        )
        self.assertEqual(search.status_code, 200)
        matches = search.json()["matches"]
        self.assertGreater(len(matches), 0)
        first = matches[0]
        self.assertEqual(first["source_type"], "pdf")
        self.assertEqual(first["session_id"], "s-pdf")
        self.assertIn("pdf_ingest_id", first["metadata"])
        self.assertEqual(first["metadata"]["source_name"], "invoice-2026.pdf")

    def test_pdf_ingest_structured_unexpected_error_falls_back(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-pdf-fallback.db"))
        deps.extraction_structured_enabled = True

        class _FakeEmbeddings:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=[0.2, 0.1, 0.3, 0.4]) for _ in payload]
                return SimpleNamespace(data=data)

        class _BrokenResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                raise RuntimeError("unexpected structured failure")

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())
        deps.responses_client = SimpleNamespace(responses=_BrokenResponses())

        pdf_text = "Fallback PDF structured text with invoice totals"
        expected_hash = hashlib.sha256(pdf_text.encode("utf-8")).hexdigest()
        payload_b64 = base64.b64encode(b"%PDF-1.7 fake-payload").decode("ascii")
        with patch("api.app_factory._extract_text_from_pdf_bytes", return_value=pdf_text):
            ingest_resp = self.client.post(
                "/skills/pdf_ingest",
                headers={"x-api-key": "test-server-key"},
                json={
                    "session_id": "s-pdf-fallback",
                    "source_name": "fallback.pdf",
                    "mime_type": "application/pdf",
                    "data_base64": payload_b64,
                    "attach_to_chat": False,
                },
            )

        self.assertEqual(ingest_resp.status_code, 200)
        structured = ingest_resp.json()["structured"]
        self.assertEqual(structured["source_type"], "pdf")
        self.assertEqual(structured["source_name"], "fallback.pdf")
        self.assertEqual(structured["text_sha256"], expected_hash)
        self.assertEqual(structured["char_count"], len(pdf_text))
        self.assertTrue(structured["preview"].startswith("Fallback PDF structured text"))
        self.assertEqual(structured["enrichment_status"], "fallback")
        self.assertEqual(structured["fallback_reason"], "unexpected_error")

    def test_pdf_ingest_dedups_identical_requests(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-pdf-dedup.db"))

        class _FakeEmbeddings:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=[0.3, 0.2, 0.1, float(len(text) % 13) / 13.0]) for text in payload]
                return SimpleNamespace(data=data)

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())

        pdf_text = "Invoice archive\nretainer line item\ntotal due"
        payload_b64 = base64.b64encode(b"%PDF-1.7 fake-dedup-payload").decode("ascii")
        request_payload = {
            "session_id": "s-pdf-dedup",
            "source_name": "dedup.pdf",
            "mime_type": "application/pdf",
            "data_base64": payload_b64,
            "attach_to_chat": False,
        }
        with patch("api.app_factory._extract_text_from_pdf_bytes", return_value=pdf_text):
            first_resp = self.client.post(
                "/skills/pdf_ingest",
                headers={"x-api-key": "test-server-key"},
                json=request_payload,
            )
        self.assertEqual(first_resp.status_code, 200)
        first_ingest = first_resp.json()
        vector_count_after_first = deps.vector_store.active_count()
        self.assertGreater(vector_count_after_first, 0)

        with patch("api.app_factory._extract_text_from_pdf_bytes", side_effect=AssertionError("should not re-extract")):
            second_resp = self.client.post(
                "/skills/pdf_ingest",
                headers={"x-api-key": "test-server-key"},
                json=request_payload,
            )
        self.assertEqual(second_resp.status_code, 200)
        second_ingest = second_resp.json()
        self.assertEqual(second_ingest["ingest_id"], first_ingest["ingest_id"])
        self.assertEqual(second_ingest["vector_chunks"], first_ingest["vector_chunks"])
        self.assertEqual(deps.vector_store.active_count(), vector_count_after_first)

    def test_pdf_ingest_structured_falls_back_when_model_mime_mismatches(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-pdf-mime-mismatch.db"))
        deps.extraction_structured_enabled = True
        pdf_text = "PDF content must keep mime as application/pdf."
        expected_hash = hashlib.sha256(pdf_text.encode("utf-8")).hexdigest()

        class _FakeEmbeddings:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=[0.1, 0.2, 0.3, 0.4]) for _ in payload]
                return SimpleNamespace(data=data)

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                payload = {
                    "schema_version": "v1",
                    "source_type": "pdf",
                    "source_name": "invoice.pdf",
                    "mime_type": "text/plain",
                    "text_sha256": expected_hash,
                    "char_count": len(pdf_text),
                    "word_count": 7,
                    "line_count": 1,
                    "preview": "Model suggested non-pdf mime.",
                }
                return SimpleNamespace(output_text=json.dumps(payload))

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())
        deps.responses_client = SimpleNamespace(responses=_FakeResponses())

        payload_b64 = base64.b64encode(b"%PDF-1.7 fake-payload").decode("ascii")
        with patch("api.app_factory._extract_text_from_pdf_bytes", return_value=pdf_text):
            ingest_resp = self.client.post(
                "/skills/pdf_ingest",
                headers={"x-api-key": "test-server-key"},
                json={
                    "session_id": "s-pdf-mime-mismatch",
                    "source_name": "invoice.pdf",
                    "mime_type": "application/pdf",
                    "data_base64": payload_b64,
                    "attach_to_chat": False,
                },
            )

        self.assertEqual(ingest_resp.status_code, 200)
        structured = ingest_resp.json()["structured"]
        self.assertEqual(structured["source_type"], "pdf")
        self.assertEqual(structured["mime_type"], "application/pdf")
        self.assertEqual(structured["source_name"], "invoice.pdf")
        self.assertEqual(structured["text_sha256"], expected_hash)
        self.assertEqual(structured["preview"], "PDF content must keep mime as application/pdf.")
        self.assertEqual(structured["enrichment_status"], "fallback")
        self.assertEqual(structured["fallback_reason"], "metadata_mismatch")

    def test_pdf_ingest_structured_enrichment_uses_pdf_schema(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-pdf-structured.db"))
        deps.extraction_structured_enabled = True
        captured: dict[str, Any] = {}
        pdf_text = "Invoice policy text with independent signals and audit markers."
        expected_hash = hashlib.sha256(pdf_text.encode("utf-8")).hexdigest()

        class _FakeEmbeddings:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=[0.1, 0.2, 0.3, 0.4]) for _ in payload]
                return SimpleNamespace(data=data)

        class _FakeResponses:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                captured["kwargs"] = kwargs
                payload = {
                    "schema_version": "v1",
                    "source_type": "pdf",
                    "source_name": "policy.pdf",
                    "mime_type": "application/pdf",
                    "text_sha256": expected_hash,
                    "char_count": len(pdf_text),
                    "word_count": 9,
                    "line_count": 1,
                    "preview": "PDF preview tuned.",
                }
                return SimpleNamespace(output_text=json.dumps(payload))

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())
        deps.responses_client = SimpleNamespace(responses=_FakeResponses())

        payload_b64 = base64.b64encode(b"%PDF-1.7 fake-payload").decode("ascii")
        with patch("api.app_factory._extract_text_from_pdf_bytes", return_value=pdf_text):
            ingest_resp = self.client.post(
                "/skills/pdf_ingest",
                headers={"x-api-key": "test-server-key"},
                json={
                    "session_id": "s-pdf-structured",
                    "source_name": "policy.pdf",
                    "mime_type": "application/pdf",
                    "data_base64": payload_b64,
                    "attach_to_chat": False,
                },
            )

        self.assertEqual(ingest_resp.status_code, 200)
        self.assertEqual(ingest_resp.json()["structured"]["preview"], "PDF preview tuned.")
        self.assertEqual(ingest_resp.json()["structured"]["enrichment_status"], "enriched")
        self.assertIsNone(ingest_resp.json()["structured"]["fallback_reason"])
        kwargs = captured["kwargs"]
        self.assertEqual(kwargs["model"], deps.extraction_structured_model)
        self.assertEqual(kwargs["text"]["format"]["name"], "extraction_structured_pdf_v1")
        self.assertEqual(
            kwargs["text"]["format"]["schema"]["properties"]["source_type"]["const"],
            "pdf",
        )
        self.assertEqual(
            kwargs["text"]["format"]["schema"]["properties"]["mime_type"]["const"],
            "application/pdf",
        )

    def test_pdf_ingest_optionally_indexes_in_responses_vector_store(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-pdf-responses.db"))
        deps.responses_pdf_ingest_enabled = True
        deps.responses_vector_store_id = "vs_pdf_test_123"
        captured: dict[str, Any] = {}

        class _FakeEmbeddings:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=[0.1, 0.2, 0.3, 0.4]) for _ in payload]
                return SimpleNamespace(data=data)

        class _FakeVectorStoreFiles:
            def upload_and_poll(self, **kwargs: Any) -> SimpleNamespace:
                captured["vector_store_id"] = kwargs["vector_store_id"]
                upload_file = kwargs["file"]
                captured["file_name"] = getattr(upload_file, "name", "")
                captured["file_head"] = upload_file.read(5)
                upload_file.seek(0)
                return SimpleNamespace(id="vsf_test_456")

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())
        deps.responses_client = SimpleNamespace(
            vector_stores=SimpleNamespace(files=_FakeVectorStoreFiles())
        )

        payload = b"%PDF-1.7 fake-payload-for-responses"
        payload_b64 = base64.b64encode(payload).decode("ascii")
        with patch("api.app_factory._extract_text_from_pdf_bytes", return_value="PDF text for indexing"):
            resp = self.client.post(
                "/skills/pdf_ingest",
                headers={"x-api-key": "test-server-key"},
                json={
                    "session_id": "s-pdf-responses",
                    "source_name": "retrieval-brief.pdf",
                    "mime_type": "application/pdf",
                    "data_base64": payload_b64,
                    "attach_to_chat": False,
                },
            )

        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertEqual(captured["vector_store_id"], "vs_pdf_test_123")
        self.assertEqual(captured["file_name"], "retrieval-brief.pdf")
        self.assertEqual(captured["file_head"], b"%PDF-")
        self.assertEqual(payload["responses_index_status"], "indexed")
        self.assertIsNone(payload["responses_index_reason"])
        self.assertEqual(payload["responses_vector_store_file_id"], "vsf_test_456")

    def test_pdf_ingest_reports_responses_index_failure_reason(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-pdf-responses-failure.db"))
        deps.responses_pdf_ingest_enabled = True
        deps.responses_vector_store_id = "vs_pdf_test_fail_123"

        class _FakeEmbeddings:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=[0.1, 0.2, 0.3, 0.4]) for _ in payload]
                return SimpleNamespace(data=data)

        class _BrokenVectorStoreFiles:
            def upload_and_poll(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                raise RuntimeError("responses upload unavailable")

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())
        deps.responses_client = SimpleNamespace(
            vector_stores=SimpleNamespace(files=_BrokenVectorStoreFiles())
        )

        payload = b"%PDF-1.7 fake-payload-for-responses-failure"
        payload_b64 = base64.b64encode(payload).decode("ascii")
        with patch("api.app_factory._extract_text_from_pdf_bytes", return_value="PDF text for indexing"):
            resp = self.client.post(
                "/skills/pdf_ingest",
                headers={"x-api-key": "test-server-key"},
                json={
                    "session_id": "s-pdf-responses-failure",
                    "source_name": "retrieval-brief.pdf",
                    "mime_type": "application/pdf",
                    "data_base64": payload_b64,
                    "attach_to_chat": False,
                },
            )

        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertEqual(payload["responses_index_status"], "failed")
        self.assertEqual(payload["responses_index_reason"], "unexpected_error")
        self.assertIsNone(payload["responses_vector_store_file_id"])

    def test_pdf_ingest_reports_classified_responses_index_failure_reasons(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-pdf-responses-failure-map.db"))
        deps.responses_pdf_ingest_enabled = True
        deps.responses_vector_store_id = "vs_pdf_test_fail_map_123"

        class _FakeEmbeddings:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=[0.1, 0.2, 0.3, 0.4]) for _ in payload]
                return SimpleNamespace(data=data)

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())

        request = httpx.Request("POST", "https://api.openai.com/v1/vector_stores/vs_pdf_test_fail_map_123/files")

        cases = (
            (
                "authentication_error",
                lambda: AuthenticationError(
                    "auth failed",
                    response=httpx.Response(401, request=request),
                    body={},
                ),
            ),
            (
                "rate_limited",
                lambda: RateLimitError(
                    "rate limited",
                    response=httpx.Response(429, request=request),
                    body={},
                ),
            ),
            (
                "connection_error",
                lambda: APIConnectionError(message="connection error", request=request),
            ),
            (
                "api_status_503",
                lambda: APIStatusError(
                    "upstream unavailable",
                    response=httpx.Response(503, request=request),
                    body={},
                ),
            ),
        )

        payload = b"%PDF-1.7 fake-payload-for-responses-failure-map"
        payload_b64 = base64.b64encode(payload).decode("ascii")

        for expected_reason, build_error in cases:
            with self.subTest(expected_reason=expected_reason):

                class _BrokenVectorStoreFiles:
                    def upload_and_poll(self, **kwargs: Any) -> SimpleNamespace:
                        del kwargs
                        raise build_error()

                deps.responses_client = SimpleNamespace(
                    vector_stores=SimpleNamespace(files=_BrokenVectorStoreFiles())
                )

                with patch("api.app_factory._extract_text_from_pdf_bytes", return_value="PDF text for indexing"):
                    resp = self.client.post(
                        "/skills/pdf_ingest",
                        headers={"x-api-key": "test-server-key"},
                        json={
                            "session_id": f"s-pdf-responses-failure-{expected_reason}",
                            "source_name": "retrieval-brief.pdf",
                            "mime_type": "application/pdf",
                            "data_base64": payload_b64,
                            "attach_to_chat": False,
                        },
                    )

                self.assertEqual(resp.status_code, 200)
                body = resp.json()
                self.assertEqual(body["responses_index_status"], "failed")
                self.assertEqual(body["responses_index_reason"], expected_reason)
                self.assertIsNone(body["responses_vector_store_file_id"])

    def test_pdf_ingest_reports_missing_responses_file_id(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-pdf-responses-missing-file-id.db"))
        deps.responses_pdf_ingest_enabled = True
        deps.responses_vector_store_id = "vs_pdf_test_missing_file_123"

        class _FakeEmbeddings:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=[0.1, 0.2, 0.3, 0.4]) for _ in payload]
                return SimpleNamespace(data=data)

        class _MissingFileIdVectorStoreFiles:
            def upload_and_poll(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                return SimpleNamespace(id=None)

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())
        deps.responses_client = SimpleNamespace(
            vector_stores=SimpleNamespace(files=_MissingFileIdVectorStoreFiles())
        )

        payload = b"%PDF-1.7 fake-payload-for-responses-missing-file-id"
        payload_b64 = base64.b64encode(payload).decode("ascii")
        with patch("api.app_factory._extract_text_from_pdf_bytes", return_value="PDF text for indexing"):
            resp = self.client.post(
                "/skills/pdf_ingest",
                headers={"x-api-key": "test-server-key"},
                json={
                    "session_id": "s-pdf-responses-missing-file-id",
                    "source_name": "retrieval-brief.pdf",
                    "mime_type": "application/pdf",
                    "data_base64": payload_b64,
                    "attach_to_chat": False,
                },
            )

        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["responses_index_status"], "failed")
        self.assertEqual(body["responses_index_reason"], "missing_file_id")
        self.assertIsNone(body["responses_vector_store_file_id"])

    def test_pdf_ingest_reports_not_configured_when_responses_indexing_unavailable(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-pdf-responses-not-configured.db"))
        deps.responses_pdf_ingest_enabled = True
        deps.responses_vector_store_id = None
        deps.responses_client = None

        class _FakeEmbeddings:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=[0.1, 0.2, 0.3, 0.4]) for _ in payload]
                return SimpleNamespace(data=data)

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())

        payload = b"%PDF-1.7 fake-payload-for-responses-not-configured"
        payload_b64 = base64.b64encode(payload).decode("ascii")
        with patch("api.app_factory._extract_text_from_pdf_bytes", return_value="PDF text for indexing"):
            resp = self.client.post(
                "/skills/pdf_ingest",
                headers={"x-api-key": "test-server-key"},
                json={
                    "session_id": "s-pdf-responses-not-configured",
                    "source_name": "retrieval-brief.pdf",
                    "mime_type": "application/pdf",
                    "data_base64": payload_b64,
                    "attach_to_chat": False,
                },
            )

        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertEqual(payload["responses_index_status"], "disabled")
        self.assertEqual(payload["responses_index_reason"], "not_configured")
        self.assertIsNone(payload["responses_vector_store_file_id"])

    def test_pdf_ingest_rejects_non_pdf_payload(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-pdf-reject.db"))

        payload_b64 = base64.b64encode(b"plain-text").decode("ascii")
        resp = self.client.post(
            "/skills/pdf_ingest",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-pdf-bad",
                "source_name": "notes.txt",
                "mime_type": "text/plain",
                "data_base64": payload_b64,
                "attach_to_chat": False,
            },
        )
        self.assertEqual(resp.status_code, 422)
        self.assertIn("application/pdf", resp.json()["detail"])

    def test_pdf_ingest_rejects_oversized_payload(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-pdf-size.db"))

        payload_b64 = base64.b64encode(b"%PDF" + (b"A" * 64)).decode("ascii")
        with patch("api.app_factory._PDF_MAX_BYTES", 32):
            resp = self.client.post(
                "/skills/pdf_ingest",
                headers={"x-api-key": "test-server-key"},
                json={
                    "session_id": "s-pdf-size",
                    "source_name": "oversized.pdf",
                    "mime_type": "application/pdf",
                    "data_base64": payload_b64,
                    "attach_to_chat": False,
                },
            )
        self.assertEqual(resp.status_code, 413)
        self.assertIn("too large", resp.json()["detail"])

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

            def create(self, **kwargs: Any) -> SimpleNamespace:
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

            def create(self, **kwargs: Any) -> SimpleNamespace:
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

    def test_file_search_returns_ranked_pdf_matches(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-search-pdf.db"))

        class _FakeEmbeddings:
            @staticmethod
            def _embed(text: str) -> list[float]:
                lowered = text.lower()
                return [
                    1.0 if "policy" in lowered else 0.0,
                    1.0 if "join" in lowered else 0.0,
                    1.0 if "signal" in lowered else 0.0,
                    float(len(lowered) % 29) / 29.0,
                ]

            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=self._embed(text)) for text in payload]
                return SimpleNamespace(data=data)

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())

        payload_b64 = base64.b64encode(b"%PDF-1.7 fake-policy").decode("ascii")
        with patch(
            "api.app_factory._extract_text_from_pdf_bytes",
            return_value="Policy update: joins require two independent signals.",
        ):
            ingest_resp = self.client.post(
                "/skills/pdf_ingest",
                headers={"x-api-key": "test-server-key"},
                json={
                    "session_id": "s-search-pdf",
                    "source_name": "policy-joins.pdf",
                    "mime_type": "application/pdf",
                    "data_base64": payload_b64,
                    "attach_to_chat": False,
                },
            )

        self.assertEqual(ingest_resp.status_code, 200)
        ingest_id = ingest_resp.json()["ingest_id"]

        search = self.client.post(
            "/skills/file_search",
            headers={"x-api-key": "test-server-key"},
            json={
                "query": "policy join signals",
                "session_id": "s-search-pdf",
                "source_types": ["pdf"],
                "limit": 3,
            },
        )
        self.assertEqual(search.status_code, 200)
        payload = search.json()
        self.assertEqual(payload["backend"], "local_vector_store")
        self.assertIsNone(payload["fallback_reason"])
        self.assertGreater(payload["candidate_count"], 0)
        self.assertGreater(len(payload["matches"]), 0)
        first = payload["matches"][0]
        self.assertEqual(first["source_type"], "pdf")
        self.assertEqual(first["session_id"], "s-search-pdf")
        self.assertIn("policy", first["snippet"].lower())
        self.assertEqual(first["metadata"].get("source"), "pdf")
        self.assertEqual(first["metadata"].get("pdf_ingest_id"), ingest_id)

    def test_file_search_prefers_responses_vector_store_for_pdf(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-search-pdf-responses.db"))
        deps.responses_pdf_ingest_enabled = True
        deps.responses_vector_store_id = "vs_pdf_search_123"
        captured: dict[str, Any] = {}

        class _FailEmbeddings:
            def create(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                raise AssertionError("Local embeddings path should not be used when responses search succeeds.")

        class _FakeVectorStores:
            def search(self, **kwargs: Any) -> SimpleNamespace:
                captured["kwargs"] = kwargs
                return SimpleNamespace(
                    data=[
                        SimpleNamespace(
                            file_id="file_abc123",
                            filename="policy-joins.pdf",
                            score=0.91,
                            attributes={
                                "session_id": "s-rag-pdf",
                                "source": "pdf",
                                "pdf_ingest_id": "pdf-abc123",
                                "source_ref": "pdf-abc123:chunk-0",
                            },
                            content=[
                                SimpleNamespace(
                                    type="text",
                                    text="Policy joins are disallowed unless two independent signals agree.",
                                )
                            ],
                        )
                    ]
                )

        deps.embedding_client = SimpleNamespace(embeddings=_FailEmbeddings())
        deps.responses_client = SimpleNamespace(vector_stores=_FakeVectorStores())

        search = self.client.post(
            "/skills/file_search",
            headers={"x-api-key": "test-server-key"},
            json={
                "query": "policy join signals",
                "session_id": "s-rag-pdf",
                "source_types": ["pdf"],
                "limit": 3,
            },
        )
        self.assertEqual(search.status_code, 200)
        payload = search.json()
        self.assertEqual(payload["query"], "policy join signals")
        self.assertEqual(payload["backend"], "responses_vector_store")
        self.assertIsNone(payload["fallback_reason"])
        self.assertEqual(payload["candidate_count"], 1)
        self.assertGreater(len(payload["matches"]), 0)
        first = payload["matches"][0]
        self.assertTrue(first["vector_id"].startswith("resp:file_abc123:"))
        self.assertEqual(first["source_type"], "pdf")
        self.assertEqual(first["session_id"], "s-rag-pdf")
        self.assertIn("independent signals", first["snippet"].lower())
        self.assertEqual(first["metadata"].get("file_id"), "file_abc123")
        self.assertEqual(first["metadata"].get("filename"), "policy-joins.pdf")
        kwargs = captured["kwargs"]
        self.assertEqual(kwargs["vector_store_id"], "vs_pdf_search_123")
        self.assertEqual(kwargs["query"], "policy join signals")

    def test_file_search_falls_back_to_local_pdf_vectors_on_responses_failure(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-search-pdf-fallback.db"))
        deps.responses_pdf_ingest_enabled = False

        class _FakeEmbeddings:
            @staticmethod
            def _embed(text: str) -> list[float]:
                lowered = text.lower()
                return [
                    1.0 if "policy" in lowered else 0.0,
                    1.0 if "join" in lowered else 0.0,
                    1.0 if "signal" in lowered else 0.0,
                    float(len(lowered) % 29) / 29.0,
                ]

            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=self._embed(text)) for text in payload]
                return SimpleNamespace(data=data)

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())

        payload_b64 = base64.b64encode(b"%PDF-1.7 fallback-policy").decode("ascii")
        with patch(
            "api.app_factory._extract_text_from_pdf_bytes",
            return_value="Policy joins require two independent signals before approval.",
        ):
            ingest_resp = self.client.post(
                "/skills/pdf_ingest",
                headers={"x-api-key": "test-server-key"},
                json={
                    "session_id": "s-pdf-fallback-search",
                    "source_name": "policy-fallback.pdf",
                    "mime_type": "application/pdf",
                    "data_base64": payload_b64,
                    "attach_to_chat": False,
                },
            )
        self.assertEqual(ingest_resp.status_code, 200)

        class _BrokenVectorStores:
            def search(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                raise RuntimeError("responses search unavailable")

        deps.responses_pdf_ingest_enabled = True
        deps.responses_vector_store_id = "vs_pdf_fallback_123"
        deps.responses_client = SimpleNamespace(vector_stores=_BrokenVectorStores())

        search = self.client.post(
            "/skills/file_search",
            headers={"x-api-key": "test-server-key"},
            json={
                "query": "policy join signals",
                "session_id": "s-pdf-fallback-search",
                "source_types": ["pdf"],
                "limit": 3,
            },
        )
        self.assertEqual(search.status_code, 200)
        payload = search.json()
        self.assertEqual(payload["backend"], "local_vector_store")
        self.assertEqual(payload["fallback_reason"], "unexpected_error")
        self.assertGreater(payload["candidate_count"], 0)
        self.assertGreater(len(payload["matches"]), 0)
        first = payload["matches"][0]
        self.assertEqual(first["source_type"], "pdf")
        self.assertEqual(first["session_id"], "s-pdf-fallback-search")
        self.assertIn("policy", first["snippet"].lower())

    def test_file_search_falls_back_with_reason_when_responses_has_no_matches(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-search-pdf-no-match.db"))
        deps.responses_pdf_ingest_enabled = True
        deps.responses_vector_store_id = "vs_pdf_no_match_123"

        class _FakeEmbeddings:
            @staticmethod
            def _embed(text: str) -> list[float]:
                lowered = text.lower()
                return [
                    1.0 if "policy" in lowered else 0.0,
                    1.0 if "join" in lowered else 0.0,
                    1.0 if "signal" in lowered else 0.0,
                    float(len(lowered) % 29) / 29.0,
                ]

            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=self._embed(text)) for text in payload]
                return SimpleNamespace(data=data)

        class _FakeVectorStores:
            def search(self, **kwargs: Any) -> SimpleNamespace:
                del kwargs
                return SimpleNamespace(
                    data=[
                        SimpleNamespace(
                            file_id="file_other",
                            filename="other.pdf",
                            score=0.88,
                            attributes={
                                "session_id": "different-session",
                                "source": "pdf",
                            },
                            content=[SimpleNamespace(type="text", text="Unrelated policy text.")],
                        )
                    ]
                )

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())
        deps.responses_client = SimpleNamespace(vector_stores=_FakeVectorStores())

        payload_b64 = base64.b64encode(b"%PDF-1.7 local-no-match-policy").decode("ascii")
        with patch(
            "api.app_factory._extract_text_from_pdf_bytes",
            return_value="Policy joins require two independent signals before approval.",
        ):
            ingest_resp = self.client.post(
                "/skills/pdf_ingest",
                headers={"x-api-key": "test-server-key"},
                json={
                    "session_id": "s-pdf-no-match-search",
                    "source_name": "policy-local.pdf",
                    "mime_type": "application/pdf",
                    "data_base64": payload_b64,
                    "attach_to_chat": False,
                },
            )
        self.assertEqual(ingest_resp.status_code, 200)

        search = self.client.post(
            "/skills/file_search",
            headers={"x-api-key": "test-server-key"},
            json={
                "query": "policy join signals",
                "session_id": "s-pdf-no-match-search",
                "source_types": ["pdf"],
                "limit": 3,
            },
        )
        self.assertEqual(search.status_code, 200)
        payload = search.json()
        self.assertEqual(payload["backend"], "local_vector_store")
        self.assertEqual(payload["fallback_reason"], "responses_no_matches")
        self.assertGreater(payload["candidate_count"], 0)
        self.assertGreater(len(payload["matches"]), 0)

    def test_file_search_falls_back_with_classified_responses_failure_reasons(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-search-pdf-fallback-map.db"))

        class _FakeEmbeddings:
            @staticmethod
            def _embed(text: str) -> list[float]:
                lowered = text.lower()
                return [
                    1.0 if "policy" in lowered else 0.0,
                    1.0 if "join" in lowered else 0.0,
                    1.0 if "signal" in lowered else 0.0,
                    float(len(lowered) % 29) / 29.0,
                ]

            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=self._embed(text)) for text in payload]
                return SimpleNamespace(data=data)

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())

        payload_b64 = base64.b64encode(b"%PDF-1.7 fallback-policy-map").decode("ascii")
        with patch(
            "api.app_factory._extract_text_from_pdf_bytes",
            return_value="Policy joins require two independent signals before approval.",
        ):
            ingest_resp = self.client.post(
                "/skills/pdf_ingest",
                headers={"x-api-key": "test-server-key"},
                json={
                    "session_id": "s-pdf-fallback-map",
                    "source_name": "policy-fallback-map.pdf",
                    "mime_type": "application/pdf",
                    "data_base64": payload_b64,
                    "attach_to_chat": False,
                },
            )
        self.assertEqual(ingest_resp.status_code, 200)

        deps.responses_pdf_ingest_enabled = True
        deps.responses_vector_store_id = "vs_pdf_fallback_map_123"
        request = httpx.Request("POST", "https://api.openai.com/v1/vector_stores/vs_pdf_fallback_map_123/search")
        cases = (
            (
                "authentication_error",
                lambda: AuthenticationError(
                    "auth failed",
                    response=httpx.Response(401, request=request),
                    body={},
                ),
            ),
            (
                "rate_limited",
                lambda: RateLimitError(
                    "rate limited",
                    response=httpx.Response(429, request=request),
                    body={},
                ),
            ),
            (
                "connection_error",
                lambda: APIConnectionError(message="connection error", request=request),
            ),
            (
                "api_status_502",
                lambda: APIStatusError(
                    "upstream unavailable",
                    response=httpx.Response(502, request=request),
                    body={},
                ),
            ),
        )

        for expected_reason, build_error in cases:
            with self.subTest(expected_reason=expected_reason):

                class _BrokenVectorStores:
                    def search(self, **kwargs: Any) -> SimpleNamespace:
                        del kwargs
                        raise build_error()

                deps.responses_client = SimpleNamespace(vector_stores=_BrokenVectorStores())

                search = self.client.post(
                    "/skills/file_search",
                    headers={"x-api-key": "test-server-key"},
                    json={
                        "query": "policy join signals",
                        "session_id": "s-pdf-fallback-map",
                        "source_types": ["pdf"],
                        "limit": 3,
                    },
                )
                self.assertEqual(search.status_code, 200)
                body = search.json()
                self.assertEqual(body["backend"], "local_vector_store")
                self.assertEqual(body["fallback_reason"], expected_reason)
                self.assertGreater(body["candidate_count"], 0)
                self.assertGreater(len(body["matches"]), 0)

    def test_file_search_requires_vector_memory(self) -> None:
        resp = self.client.post(
            "/skills/file_search",
            headers={"x-api-key": "test-server-key"},
            json={"query": "invoice totals"},
        )
        self.assertEqual(resp.status_code, 503)

    def test_file_search_rejects_blank_query_after_trim(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-search-query.db"))
        deps.embedding_client = SimpleNamespace(
            embeddings=SimpleNamespace(create=lambda **_: SimpleNamespace(data=[SimpleNamespace(embedding=[0.1, 0.2])]))
        )

        resp = self.client.post(
            "/skills/file_search",
            headers={"x-api-key": "test-server-key"},
            json={"query": "   "},
        )
        self.assertEqual(resp.status_code, 422)
        self.assertEqual(resp.json()["detail"], "query cannot be blank.")

    def test_file_search_rejects_blank_session_id_after_trim(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-search-session.db"))
        deps.embedding_client = SimpleNamespace(
            embeddings=SimpleNamespace(create=lambda **_: SimpleNamespace(data=[SimpleNamespace(embedding=[0.1, 0.2])]))
        )

        resp = self.client.post(
            "/skills/file_search",
            headers={"x-api-key": "test-server-key"},
            json={"query": "invoice", "session_id": "   "},
        )
        self.assertEqual(resp.status_code, 422)
        self.assertEqual(resp.json()["detail"], "session_id cannot be blank.")

    def test_file_search_rejects_unsupported_source_types(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-search-source-types.db"))
        deps.embedding_client = SimpleNamespace(
            embeddings=SimpleNamespace(create=lambda **_: SimpleNamespace(data=[SimpleNamespace(embedding=[0.1, 0.2])]))
        )

        resp = self.client.post(
            "/skills/file_search",
            headers={"x-api-key": "test-server-key"},
            json={"query": "invoice", "source_types": ["ocr", "banana"]},
        )
        self.assertEqual(resp.status_code, 422)
        self.assertIn("Unsupported source_types", resp.json()["detail"])

    def test_file_search_rejects_clip_proxy_profile_when_disabled(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-search-clip-disabled.db"))
        deps.embedding_client = SimpleNamespace(
            embeddings=SimpleNamespace(create=lambda **_: SimpleNamespace(data=[SimpleNamespace(embedding=[0.1, 0.2])]))
        )
        deps.clip_proxy_file_search_enabled = False

        resp = self.client.post(
            "/skills/file_search",
            headers={"x-api-key": "test-server-key"},
            json={
                "query": "awning",
                "retrieval_profile": "clip_proxy_image_only",
            },
        )
        self.assertEqual(resp.status_code, 409)
        self.assertIn("clip_proxy_image_only is disabled", resp.json()["detail"])

    def test_file_search_clip_proxy_profile_forces_image_only_retrieval(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-search-clip-enabled.db"))
        deps.clip_proxy_file_search_enabled = True

        class _FakeEmbeddings:
            @staticmethod
            def _embed(text: str) -> list[float]:
                lowered = text.lower()
                return [
                    1.0 if "invoice" in lowered else 0.0,
                    1.0 if "awning" in lowered else 0.0,
                    1.0 if "target" in lowered else 0.0,
                    float(len(lowered) % 31) / 31.0,
                ]

            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=self._embed(text)) for text in payload]
                return SimpleNamespace(data=data)

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())

        ingest = self.client.post(
            "/skills/ocr",
            headers={"x-api-key": "test-server-key"},
            json={
                "session_id": "s-search-clip-enabled",
                "source_name": "clip-slice.png",
                "mime_type": "image/png",
                "text_hint": "target invoice text only",
                "visual_context_hint": "target storefront under blue awning",
                "attach_to_chat": False,
            },
        )
        self.assertEqual(ingest.status_code, 200)

        resp = self.client.post(
            "/skills/file_search",
            headers={"x-api-key": "test-server-key"},
            json={
                "query": "awning target",
                "session_id": "s-search-clip-enabled",
                "source_types": ["ocr"],
                "retrieval_profile": "clip_proxy_image_only",
                "limit": 5,
            },
        )
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertGreater(len(payload["matches"]), 0)
        self.assertTrue(all(match["source_type"] == "image" for match in payload["matches"]))

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

    def test_feedback_style_signals_add_soft_internal_style_notes(self) -> None:
        session_id = "s-style-adaptive"
        message_ids: list[str] = []
        for prompt in ("first turn", "second turn"):
            with self._stub_runner("style candidate"):
                chat_resp = self.client.post(
                    "/chat",
                    headers={"x-api-key": "test-server-key"},
                    json={"message": prompt, "session_id": session_id},
                )
            self.assertEqual(chat_resp.status_code, 200)
            message_ids.append(chat_resp.json()["assistant_message_id"])

        for message_id in message_ids:
            feedback_resp = self.client.post(
                f"/chats/{session_id}/feedback",
                headers={"x-api-key": "test-server-key"},
                json={
                    "message_id": message_id,
                    "outcome": "pass",
                    "positive_tags": ["style", "grounded", "high_value"],
                    "note": "Target style match.",
                },
            )
            self.assertEqual(feedback_resp.status_code, 200)

        captured: dict[str, str] = {}
        with self._stub_runner("adaptive style output", capture=captured):
            final_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "continue this thread", "session_id": session_id},
            )
        self.assertEqual(final_resp.status_code, 200)
        self.assertIn("INTERNAL_STYLE_NOTES", captured["input"])
        self.assertIn("Soft style target: mirror the user's language", captured["input"])
        self.assertIn("Soft style target: keep replies concise", captured["input"])

    def test_recovered_pass_suppresses_caution_note_and_adds_recovery_note(self) -> None:
        session_id = "s-style-recovery"

        with self._stub_runner("style candidate risk"):
            first_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "first turn", "session_id": session_id},
            )
        self.assertEqual(first_resp.status_code, 200)
        first_message_id = first_resp.json()["assistant_message_id"]

        risk_feedback = self.client.post(
            f"/chats/{session_id}/feedback",
            headers={"x-api-key": "test-server-key"},
            json={
                "message_id": first_message_id,
                "outcome": "fail",
                "negative_tags": ["hallucination_risk"],
                "note": "Good style, but a risky specific claim.",
            },
        )
        self.assertEqual(risk_feedback.status_code, 200)

        with self._stub_runner("style candidate recovered"):
            second_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "second turn", "session_id": session_id},
            )
        self.assertEqual(second_resp.status_code, 200)
        second_message_id = second_resp.json()["assistant_message_id"]

        recovery_feedback = self.client.post(
            f"/chats/{session_id}/feedback",
            headers={"x-api-key": "test-server-key"},
            json={
                "message_id": second_message_id,
                "outcome": "pass",
                "positive_tags": ["style", "grounded", "recovered", "high_value"],
                "note": "Recovered cleanly with grounded tone continuity.",
            },
        )
        self.assertEqual(recovery_feedback.status_code, 200)

        captured: dict[str, str] = {}
        with self._stub_runner("adaptive style output", capture=captured):
            final_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "continue this thread", "session_id": session_id},
            )
        self.assertEqual(final_resp.status_code, 200)
        self.assertIn("INTERNAL_STYLE_NOTES", captured["input"])
        self.assertIn("Soft style recovery: after a brief uncertainty clause", captured["input"])
        self.assertNotIn("Soft style guardrail: if specifics are uncertain", captured["input"])

    def test_adaptive_style_notes_decay_downweights_stale_signal(self) -> None:
        entries: list[MessageFeedback] = []
        now = 1773000000000
        for idx in range(8):
            entries.append(
                MessageFeedback(
                    session_id="s-style-decay",
                    message_id=f"msg_decay_recent_{idx}",
                    outcome="FAIL",
                    positive_tags=["style"],
                    negative_tags=["needs_retry"],
                    tags=["style", "needs_retry"],
                    note=None,
                    recommended_action=None,
                    action_taken=None,
                    status="OPEN",
                    created_at=now - idx,
                    updated_at=now - idx,
                )
            )
        entries.append(
            MessageFeedback(
                session_id="s-style-decay",
                message_id="msg_decay_old_style",
                outcome="PASS",
                positive_tags=["style", "grounded", "high_value"],
                negative_tags=[],
                tags=["style", "grounded", "high_value"],
                note=None,
                recommended_action=None,
                action_taken=None,
                status="CLOSED",
                created_at=now - 9999,
                updated_at=now - 9999,
            )
        )

        notes = app_factory._derive_adaptive_style_notes(entries)
        self.assertEqual(notes, [])

    def test_adaptive_style_notes_caps_to_two_active_notes(self) -> None:
        now = 1773000100000
        entries = [
            MessageFeedback(
                session_id="s-style-cap",
                message_id="msg_risk",
                outcome="FAIL",
                positive_tags=["style", "grounded"],
                negative_tags=["hallucination_risk"],
                tags=["style", "grounded", "hallucination_risk"],
                note=None,
                recommended_action=None,
                action_taken=None,
                status="OPEN",
                created_at=now,
                updated_at=now,
            ),
            MessageFeedback(
                session_id="s-style-cap",
                message_id="msg_pass_1",
                outcome="PASS",
                positive_tags=["style", "grounded", "high_value"],
                negative_tags=[],
                tags=["style", "grounded", "high_value"],
                note=None,
                recommended_action=None,
                action_taken=None,
                status="CLOSED",
                created_at=now - 1,
                updated_at=now - 1,
            ),
            MessageFeedback(
                session_id="s-style-cap",
                message_id="msg_pass_2",
                outcome="PASS",
                positive_tags=["style", "grounded", "high_value"],
                negative_tags=[],
                tags=["style", "grounded", "high_value"],
                note=None,
                recommended_action=None,
                action_taken=None,
                status="CLOSED",
                created_at=now - 2,
                updated_at=now - 2,
            ),
        ]

        notes = app_factory._derive_adaptive_style_notes(entries)
        self.assertLessEqual(len(notes), 2)
        self.assertTrue(any("Soft style target:" in item for item in notes))

    def test_near_duplicate_note_detection(self) -> None:
        first = "Soft style target: keep replies concise (usually 1-3 sentences), vivid, and continuity-first."
        second = "Soft style target keep replies concise vivid and continuity first."
        different = "Soft style guardrail: if specifics are uncertain, use one brief uncertainty clause."
        self.assertTrue(app_factory._notes_are_near_duplicate(first, second))
        self.assertFalse(app_factory._notes_are_near_duplicate(first, different))

    def test_adaptive_style_note_transitions_are_logged_once(self) -> None:
        session_id = "s-style-log"
        with self._stub_runner("style candidate"):
            first_chat_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "first turn", "session_id": session_id},
            )
        self.assertEqual(first_chat_resp.status_code, 200)
        first_message_id = first_chat_resp.json()["assistant_message_id"]

        feedback_resp = self.client.post(
            f"/chats/{session_id}/feedback",
            headers={"x-api-key": "test-server-key"},
            json={
                "message_id": first_message_id,
                "outcome": "pass",
                "positive_tags": ["style", "grounded", "high_value"],
            },
        )
        self.assertEqual(feedback_resp.status_code, 200)

        with self._stub_runner("style candidate second"):
            second_seed_chat_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "second seed turn", "session_id": session_id},
            )
        self.assertEqual(second_seed_chat_resp.status_code, 200)
        second_seed_message_id = second_seed_chat_resp.json()["assistant_message_id"]

        second_feedback_resp = self.client.post(
            f"/chats/{session_id}/feedback",
            headers={"x-api-key": "test-server-key"},
            json={
                "message_id": second_seed_message_id,
                "outcome": "pass",
                "positive_tags": ["style", "grounded", "high_value"],
            },
        )
        self.assertEqual(second_feedback_resp.status_code, 200)

        events: list[tuple[str, dict[str, Any]]] = []

        def _capture_event(event_name: str, **kwargs: Any) -> None:
            events.append((event_name, kwargs))

        with patch("api.app_factory._log_event", new=_capture_event):
            with self._stub_runner("style followup"):
                third_chat_resp = self.client.post(
                    "/chat",
                    headers={"x-api-key": "test-server-key"},
                    json={"message": "third turn", "session_id": session_id},
                )
            self.assertEqual(third_chat_resp.status_code, 200)

            with self._stub_runner("style followup again"):
                fourth_chat_resp = self.client.post(
                    "/chat",
                    headers={"x-api-key": "test-server-key"},
                    json={"message": "fourth turn", "session_id": session_id},
                )
            self.assertEqual(fourth_chat_resp.status_code, 200)

        note_events = [item for item in events if item[0] == "adaptive_style_notes_updated"]
        self.assertEqual(len(note_events), 1)
        self.assertGreaterEqual(note_events[0][1].get("active_count", 0), 1)

    def test_collaboration_handoff_persists_and_injects_context(self) -> None:
        handoff_resp = self.client.post(
            "/chats/s-collab/collaboration/handoff",
            headers={"x-api-key": "test-server-key"},
            json={
                "to_agent_id": "portfolio_strategist",
                "to_role": "Portfolio Strategist",
                "objective": "Shape clear strategic options for portfolio narratives.",
                "reason": "Switching from general ideation to structured planning.",
            },
        )
        self.assertEqual(handoff_resp.status_code, 200)
        payload = handoff_resp.json()
        self.assertEqual(payload["session_id"], "s-collab")
        self.assertEqual(payload["active"]["active_agent_id"], "portfolio_strategist")
        self.assertEqual(payload["active"]["active_role"], "Portfolio Strategist")
        self.assertEqual(len(payload["handoffs"]), 1)
        self.assertIsNone(payload["handoffs"][0]["from_agent_id"])

        timeline = self.client.get(
            "/chats/s-collab/collaboration",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(timeline.status_code, 200)
        timeline_payload = timeline.json()
        self.assertEqual(timeline_payload["active"]["active_agent_id"], "portfolio_strategist")
        self.assertEqual(len(timeline_payload["handoffs"]), 1)

        captured: dict[str, str] = {}
        with self._stub_runner("collab-response", capture=captured):
            chat_resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "give me three architecture options", "session_id": "s-collab"},
            )
        self.assertEqual(chat_resp.status_code, 200)
        self.assertIn("COLLABORATION_CONTEXT", captured["input"])
        self.assertIn("portfolio_strategist", captured["input"])
        self.assertIn("Portfolio Strategist", captured["input"])

    def test_collaboration_handoff_tracks_transitions(self) -> None:
        first = self.client.post(
            "/chats/s-collab-2/collaboration/handoff",
            headers={"x-api-key": "test-server-key"},
            json={"to_agent_id": "researcher", "to_role": "Research Partner"},
        )
        self.assertEqual(first.status_code, 200)
        second = self.client.post(
            "/chats/s-collab-2/collaboration/handoff",
            headers={"x-api-key": "test-server-key"},
            json={"to_agent_id": "editor", "to_role": "Tone Editor"},
        )
        self.assertEqual(second.status_code, 200)
        payload = self.client.get(
            "/chats/s-collab-2/collaboration",
            headers={"x-api-key": "test-server-key"},
        ).json()
        self.assertEqual(payload["active"]["active_agent_id"], "editor")
        self.assertEqual(len(payload["handoffs"]), 2)
        self.assertEqual(payload["handoffs"][1]["from_agent_id"], "researcher")
        self.assertEqual(payload["handoffs"][1]["to_agent_id"], "editor")

    def test_hallucination_guardrail_injected_for_factual_query(self) -> None:
        deps = server.get_runtime_deps()
        deps.hallucination_guardrails_enabled = True
        captured: dict[str, str] = {}
        with self._stub_runner("guarded", capture=captured):
            resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "What is the latest GDP for Canada in 2025?", "session_id": "s-guardrail"},
            )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("HALLUCINATION_GUARDRAIL", captured["input"])
        self.assertIn("do not fabricate", captured["input"].lower())
        self.assertIn("unknown/fictional events", captured["input"].lower())

    def test_fictional_factual_query_short_circuits_without_runner(self) -> None:
        deps = server.get_runtime_deps()
        deps.hallucination_guardrails_enabled = True

        async def _runner_should_not_be_called(*args: object, **kwargs: Any) -> SimpleNamespace:
            del args, kwargs
            raise AssertionError("Runner.run should not be called for fictional low-evidence factual query.")

        with patch.object(server.Runner, "run", new=_runner_should_not_be_called):
            resp = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={
                    "message": "Who won the fictional 2029 Aurora Prize in computational mythology?",
                    "session_id": "s-fictional-guardrail",
                },
            )
        self.assertEqual(resp.status_code, 200)
        output = resp.json()["output"].lower()
        self.assertIn("fictional", output)
        self.assertIn("no grounding evidence", output)

    def test_personalization_endpoint_sets_scope(self) -> None:
        resp = self.client.post(
            "/chats/s-personal/personalization",
            headers={"x-api-key": "test-server-key"},
            json={"memory_scope": "session"},
        )
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertEqual(payload["session_id"], "s-personal")
        self.assertEqual(payload["memory_scope"], "session")
        self.assertEqual(payload["updated_by"], "default")

    def test_personalization_get_returns_default_when_not_set(self) -> None:
        deps = server.get_runtime_deps()
        deps.personalization_default_memory_scope = "global"
        deps.history_store.ensure_chat("s-personal-default")
        resp = self.client.get(
            "/chats/s-personal-default/personalization",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertEqual(payload["session_id"], "s-personal-default")
        self.assertEqual(payload["memory_scope"], "global")
        self.assertIsNone(payload["updated_by"])

    def test_personalization_get_returns_persisted_scope(self) -> None:
        set_resp = self.client.post(
            "/chats/s-personal-get/personalization",
            headers={"x-api-key": "test-server-key"},
            json={"memory_scope": "session"},
        )
        self.assertEqual(set_resp.status_code, 200)
        resp = self.client.get(
            "/chats/s-personal-get/personalization",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertEqual(payload["session_id"], "s-personal-get")
        self.assertEqual(payload["memory_scope"], "session")
        self.assertEqual(payload["updated_by"], "default")

    def test_chat_summary_and_export_include_personalization_scope(self) -> None:
        set_resp = self.client.post(
            "/chats/s-personal-summary/personalization",
            headers={"x-api-key": "test-server-key"},
            json={"memory_scope": "session"},
        )
        self.assertEqual(set_resp.status_code, 200)

        chats_resp = self.client.get("/chats", headers={"x-api-key": "test-server-key"})
        self.assertEqual(chats_resp.status_code, 200)
        chats = chats_resp.json()["chats"]
        target = next(chat for chat in chats if chat["session_id"] == "s-personal-summary")
        self.assertEqual(target["memory_scope"], "session")
        self.assertEqual(target["context_scope"], "local")

        export_resp = self.client.get(
            "/chats/s-personal-summary/export",
            headers={"x-api-key": "test-server-key"},
        )
        self.assertEqual(export_resp.status_code, 200)
        export_payload = export_resp.json()
        self.assertEqual(export_payload["memory_scope"], "session")
        self.assertEqual(export_payload["context_scope"], "local")

    def test_personalization_session_scope_limits_retrieval_to_same_chat(self) -> None:
        deps = server.get_runtime_deps()
        deps.vector_enabled = True
        deps.vector_store = VectorStore(os.path.join(self.tmpdir.name, "test-vectors-personal.db"))
        deps.personalization_default_memory_scope = "global"
        deps.vector_min_similarity = 0.0
        deps.vector_min_similarity_global = 0.0
        deps.vector_min_similarity_session = 0.0

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

            def create(self, **kwargs: Any) -> SimpleNamespace:
                inputs = kwargs["input"]
                payload = [inputs] if isinstance(inputs, str) else list(inputs)
                data = [SimpleNamespace(embedding=self._embed(text)) for text in payload]
                return SimpleNamespace(data=data)

        deps.embedding_client = SimpleNamespace(embeddings=_FakeEmbeddings())

        with self._stub_runner("From chat A"):
            first_a = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "How do unicorn horns grow over time?", "session_id": "s-person-a"},
            )
        self.assertEqual(first_a.status_code, 200)

        with self._stub_runner("From chat B"):
            first_b = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "How do unicorn horns grow over time?", "session_id": "s-person-b"},
            )
        self.assertEqual(first_b.status_code, 200)

        set_scope = self.client.post(
            "/chats/s-person-b/personalization",
            headers={"x-api-key": "test-server-key"},
            json={"memory_scope": "session"},
        )
        self.assertEqual(set_scope.status_code, 200)

        captured: dict[str, str] = {}
        with self._stub_runner("Scoped response", capture=captured):
            second_b = self.client.post(
                "/chat",
                headers={"x-api-key": "test-server-key"},
                json={"message": "Do unicorn horns keep growing in adulthood?", "session_id": "s-person-b"},
            )
        self.assertEqual(second_b.status_code, 200)
        response_payload = second_b.json()
        citations = response_payload["memory_used"]
        self.assertGreaterEqual(len(citations), 1)
        self.assertTrue(all(citation["session_id"] == "s-person-b" for citation in citations))
        self.assertTrue(all(citation["source_type"] == "chat" for citation in citations))
        self.assertTrue(all("From chat A" not in citation["snippet"] for citation in citations))
        self.assertIn("RETRIEVED_MEMORY", captured["input"])
        self.assertIn("From chat B", captured["input"])
        self.assertNotIn("From chat A", captured["input"])

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

            def create(self, **kwargs: Any) -> SimpleNamespace:
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
        response_payload = second.json()
        citations = response_payload["memory_used"]
        self.assertGreaterEqual(len(citations), 1)
        self.assertRegex(citations[0]["vector_id"], r"^vec-[0-9a-f]{12}$")
        self.assertEqual(citations[0]["source_type"], "chat")
        self.assertIn("First assistant memory", citations[0]["snippet"])
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
