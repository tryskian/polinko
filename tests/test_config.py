import os
import unittest
from unittest.mock import patch

from config import load_config


class ConfigTests(unittest.TestCase):
    def test_loads_server_api_key_principals_from_json(self) -> None:
        env = {
            "OPENAI_API_KEY": "sk-test-key-12345678901234567890",
            "POLINKO_SERVER_API_KEY": "single-default-key",
            "POLINKO_SERVER_API_KEYS_JSON": '{"team-a":"team-a-key-12345","team-b":"team-b-key-67890"}',
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = load_config(dotenv_path="__missing__.env")

        self.assertEqual(cfg.server_api_key, "single-default-key")
        self.assertEqual(cfg.server_api_key_principals["single-default-key"], "default")
        self.assertEqual(cfg.server_api_key_principals["team-a-key-12345"], "team-a")
        self.assertEqual(cfg.server_api_key_principals["team-b-key-67890"], "team-b")

    def test_rejects_invalid_server_api_keys_json(self) -> None:
        env = {
            "OPENAI_API_KEY": "sk-test-key-12345678901234567890",
            "POLINKO_SERVER_API_KEYS_JSON": "not-json",
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(RuntimeError):
                load_config(dotenv_path="__missing__.env")

    def test_ocr_provider_defaults_to_scaffold(self) -> None:
        env = {
            "OPENAI_API_KEY": "sk-test-key-12345678901234567890",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = load_config(dotenv_path="__missing__.env")
        self.assertEqual(cfg.ocr_provider, "scaffold")

    def test_rejects_invalid_ocr_provider(self) -> None:
        env = {
            "OPENAI_API_KEY": "sk-test-key-12345678901234567890",
            "POLINKO_OCR_PROVIDER": "banana",
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(RuntimeError):
                load_config(dotenv_path="__missing__.env")

    def test_vector_defaults(self) -> None:
        env = {
            "OPENAI_API_KEY": "sk-test-key-12345678901234567890",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = load_config(dotenv_path="__missing__.env")
        self.assertFalse(cfg.vector_enabled)
        self.assertEqual(cfg.vector_db_path, ".polinko_vector.db")
        self.assertEqual(cfg.vector_embedding_model, "text-embedding-3-small")
        self.assertEqual(cfg.vector_top_k, 2)
        self.assertEqual(cfg.vector_min_similarity, 0.40)
        self.assertEqual(cfg.vector_max_chars, 220)
        self.assertTrue(cfg.vector_exclude_current_session)
        self.assertFalse(cfg.responses_orchestration_enabled)
        self.assertEqual(cfg.responses_orchestration_model, "gpt-5-chat-latest")
        self.assertIsNone(cfg.responses_vector_store_id)
        self.assertFalse(cfg.responses_include_web_search)
        self.assertEqual(cfg.responses_history_turn_limit, 12)
        self.assertTrue(cfg.governance_enabled)
        self.assertFalse(cfg.governance_allow_web_search)
        self.assertFalse(cfg.governance_log_only)
        self.assertTrue(cfg.hallucination_guardrails_enabled)

    def test_rejects_invalid_vector_min_similarity(self) -> None:
        env = {
            "OPENAI_API_KEY": "sk-test-key-12345678901234567890",
            "POLINKO_VECTOR_MIN_SIMILARITY": "1.5",
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(RuntimeError):
                load_config(dotenv_path="__missing__.env")

    def test_responses_orchestration_requires_vector_store_id(self) -> None:
        env = {
            "OPENAI_API_KEY": "sk-test-key-12345678901234567890",
            "POLINKO_RESPONSES_ORCHESTRATION_ENABLED": "true",
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(RuntimeError):
                load_config(dotenv_path="__missing__.env")


if __name__ == "__main__":
    unittest.main()
