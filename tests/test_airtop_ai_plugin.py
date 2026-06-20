import json
import os
import unittest
from unittest.mock import patch

from airtop_ai_plugin import AirtopAiConfig, AirtopAiPlugin
from airtop_ai_plugin.client import AirtopAiClient


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class CapturingTransport:
    def __init__(self, payload):
        self.payload = payload
        self.request = None
        self.timeout = None

    def __call__(self, request, *, timeout):
        self.request = request
        self.timeout = timeout
        return FakeResponse(self.payload)


class AirtopAiPluginTests(unittest.TestCase):
    def test_manifest_describes_airtop_ai_plugin(self):
        manifest = AirtopAiPlugin.manifest()

        self.assertEqual(manifest["name"], "Airtop Ai")
        self.assertEqual(manifest["slug"], "airtop-ai")
        self.assertEqual(
            manifest["entrypoint"], "airtop_ai_plugin:AirtopAiPlugin"
        )
        self.assertIn("automation", manifest["capabilities"])

    def test_config_from_env_trims_values_and_uses_defaults(self):
        with patch.dict(
            os.environ,
            {
                "AIRTOP_AI_API_KEY": " test-key ",
                "AIRTOP_AI_BASE_URL": " https://example.test/ ",
            },
            clear=True,
        ):
            config = AirtopAiConfig.from_env()

        self.assertEqual(config.api_key, "test-key")
        self.assertEqual(config.base_url, "https://example.test")
        self.assertEqual(config.timeout_seconds, 30)

    def test_config_requires_api_key(self):
        with self.assertRaisesRegex(ValueError, "API key is required"):
            AirtopAiConfig(api_key="")

    def test_client_posts_task_with_authentication(self):
        transport = CapturingTransport({"task_id": "task-123", "status": "queued"})
        config = AirtopAiConfig(
            api_key="secret-token",
            base_url="https://example.test",
            timeout_seconds=7,
        )
        client = AirtopAiClient(config=config, transport=transport)

        result = client.run_task(
            prompt="Analyze this dataset",
            model="airtop-fast",
            metadata={"source": "unit-test"},
        )

        self.assertEqual(result["task_id"], "task-123")
        self.assertEqual(transport.timeout, 7)
        self.assertEqual(transport.request.full_url, "https://example.test/v1/tasks")
        self.assertEqual(transport.request.get_method(), "POST")
        self.assertEqual(
            transport.request.get_header("Authorization"), "Bearer secret-token"
        )
        self.assertEqual(
            transport.request.get_header("Content-type"), "application/json"
        )
        self.assertEqual(
            json.loads(transport.request.data.decode("utf-8")),
            {
                "prompt": "Analyze this dataset",
                "model": "airtop-fast",
                "metadata": {"source": "unit-test"},
            },
        )

    def test_plugin_run_delegates_to_client(self):
        class FakeClient:
            def run_task(self, *, prompt, model=None, metadata=None):
                return {
                    "prompt": prompt,
                    "model": model,
                    "metadata": metadata,
                    "status": "complete",
                }

        config = AirtopAiConfig(api_key="secret-token")
        plugin = AirtopAiPlugin(config=config, client=FakeClient())

        result = plugin.run(
            "Generate an automation plan",
            model="airtop-accurate",
            metadata={"request_id": "req-1"},
        )

        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["prompt"], "Generate an automation plan")
        self.assertEqual(result["model"], "airtop-accurate")
        self.assertEqual(result["metadata"], {"request_id": "req-1"})


if __name__ == "__main__":
    unittest.main()
