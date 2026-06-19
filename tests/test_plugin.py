import unittest

from airtop_ai.plugins import BasePlugin, PluginRegistry
from airtop_ai.plugins.ollama import OllamaPlugin
from airtop_ai.plugins.ollama.exceptions import OllamaError
from airtop_ai.plugins.ollama.models import (
    ChatResponse,
    EmbeddingResponse,
    GenerateResponse,
    Message,
    ModelInfo,
)


class FakeClient:
    """A stand-in client so the plugin can be tested without a server."""

    def __init__(self, *, alive=True):
        self._alive = alive
        self.calls = []

    def is_alive(self):
        return self._alive

    def version(self):
        return "9.9.9"

    def generate(self, model, prompt, **kwargs):
        self.calls.append(("generate", model, prompt, kwargs))
        return GenerateResponse.from_dict(
            {"model": model, "response": f"echo:{prompt}", "done": True}
        )

    def chat(self, model, messages, **kwargs):
        self.calls.append(("chat", model, messages, kwargs))
        last = messages[-1]
        content = last.content if isinstance(last, Message) else last["content"]
        return ChatResponse.from_dict(
            {
                "model": model,
                "message": {"role": "assistant", "content": f"reply:{content}"},
                "done": True,
            }
        )

    def embed(self, model, text, **kwargs):
        self.calls.append(("embed", model, text, kwargs))
        return EmbeddingResponse.from_dict({"model": model, "embeddings": [[0.1, 0.2]]})

    def list_models(self):
        return [ModelInfo.from_dict({"name": "llama3:latest"})]


def make_plugin(**kwargs):
    return OllamaPlugin(client=FakeClient(**kwargs))


class PluginContractTests(unittest.TestCase):
    def test_is_base_plugin(self):
        self.assertIsInstance(make_plugin(), BasePlugin)

    def test_info_metadata(self):
        plugin = make_plugin()
        self.assertEqual(plugin.info.name, "ollama")
        self.assertIn("chat", plugin.capabilities())

    def test_health_check(self):
        self.assertTrue(make_plugin().health_check())
        self.assertFalse(make_plugin(alive=False).health_check())

    def test_setup_raises_when_server_down(self):
        with self.assertRaises(OllamaError):
            make_plugin(alive=False).setup()

    def test_context_manager_runs_setup(self):
        plugin = make_plugin()
        with plugin as p:
            self.assertIs(p, plugin)


class PluginBehaviourTests(unittest.TestCase):
    def test_complete(self):
        plugin = make_plugin()
        result = plugin.complete("llama3", "hi")
        self.assertEqual(result.response, "echo:hi")

    def test_ask_returns_text(self):
        plugin = make_plugin()
        reply = plugin.ask("llama3", "ping", system="be nice")
        self.assertEqual(reply, "reply:ping")
        # The system prompt should have been prepended.
        chat_call = plugin.client.calls[-1]
        messages = chat_call[2]
        self.assertEqual(messages[0].role, "system")

    def test_embed(self):
        plugin = make_plugin()
        result = plugin.embed("m", "text")
        self.assertEqual(result.embeddings, [[0.1, 0.2]])

    def test_has_model(self):
        plugin = make_plugin()
        self.assertTrue(plugin.has_model("llama3"))
        self.assertTrue(plugin.has_model("llama3:latest"))
        self.assertFalse(plugin.has_model("mistral"))

    def test_server_version(self):
        self.assertEqual(make_plugin().server_version(), "9.9.9")


class RegistryTests(unittest.TestCase):
    def test_register_and_get(self):
        reg = PluginRegistry()
        plugin = make_plugin()
        reg.register(plugin)
        self.assertIs(reg.get("ollama"), plugin)
        self.assertIn("ollama", reg)
        self.assertEqual(reg.names(), ["ollama"])

    def test_duplicate_registration_rejected(self):
        reg = PluginRegistry()
        reg.register(make_plugin())
        with self.assertRaises(ValueError):
            reg.register(make_plugin())

    def test_replace(self):
        reg = PluginRegistry()
        reg.register(make_plugin())
        replacement = make_plugin()
        reg.register(replacement, replace=True)
        self.assertIs(reg.get("ollama"), replacement)


if __name__ == "__main__":
    unittest.main()
