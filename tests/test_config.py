import os
import unittest
from unittest import mock

from airtop_ai.plugins.ollama.config import (
    DEFAULT_HOST,
    DEFAULT_TIMEOUT,
    OllamaConfig,
)


class ConfigTests(unittest.TestCase):
    def test_defaults(self):
        config = OllamaConfig()
        self.assertEqual(config.host, DEFAULT_HOST)
        self.assertEqual(config.timeout, DEFAULT_TIMEOUT)

    def test_host_normalisation_adds_scheme(self):
        self.assertEqual(OllamaConfig(host="localhost:11434").host,
                         "http://localhost:11434")

    def test_host_normalisation_strips_trailing_slash(self):
        self.assertEqual(OllamaConfig(host="http://x:1/").host, "http://x:1")

    def test_empty_host_falls_back_to_default(self):
        self.assertEqual(OllamaConfig(host="   ").host, DEFAULT_HOST)

    def test_negative_retries_clamped(self):
        self.assertEqual(OllamaConfig(max_retries=-5).max_retries, 0)

    def test_from_env_reads_variables(self):
        env = {
            "OLLAMA_HOST": "remote:9999",
            "OLLAMA_TIMEOUT": "5",
            "OLLAMA_API_KEY": "secret",
        }
        with mock.patch.dict(os.environ, env, clear=False):
            config = OllamaConfig.from_env()
        self.assertEqual(config.host, "http://remote:9999")
        self.assertEqual(config.timeout, 5.0)
        self.assertEqual(config.api_key, "secret")

    def test_from_env_overrides_take_precedence(self):
        with mock.patch.dict(os.environ, {"OLLAMA_HOST": "remote:1"}, clear=False):
            config = OllamaConfig.from_env(host="http://override:2")
        self.assertEqual(config.host, "http://override:2")


if __name__ == "__main__":
    unittest.main()
