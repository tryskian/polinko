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


if __name__ == "__main__":
    unittest.main()
