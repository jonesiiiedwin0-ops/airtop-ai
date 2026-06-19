import io
import unittest
from contextlib import redirect_stdout
from unittest import mock

from airtop_ai.plugins.ollama import cli
from airtop_ai.plugins.ollama.models import (
    EmbeddingResponse,
    GenerateResponse,
    ModelInfo,
)


class FakeCliPlugin:
    def __init__(self):
        self.pulled = None

    def server_version(self):
        return "1.2.3"

    def list_models(self):
        return [ModelInfo.from_dict({"name": "llama3", "size": 2 * 1024 * 1024})]

    def complete(self, model, prompt, system=None, stream=False):
        if stream:
            return iter(
                [
                    GenerateResponse.from_dict({"model": model, "response": "a", "done": False}),
                    GenerateResponse.from_dict({"model": model, "response": "b", "done": True}),
                ]
            )
        return GenerateResponse.from_dict({"model": model, "response": "full", "done": True})

    def ask(self, model, message, system=None):
        return f"answer:{message}"

    def embed(self, model, text):
        return EmbeddingResponse.from_dict({"model": model, "embeddings": [[0.1, 0.2, 0.3]]})


def run(argv, plugin=None):
    plugin = plugin or FakeCliPlugin()
    buffer = io.StringIO()
    with mock.patch.object(cli, "_make_plugin", return_value=plugin):
        with redirect_stdout(buffer):
            code = cli.main(argv)
    return code, buffer.getvalue()


class CliTests(unittest.TestCase):
    def test_version(self):
        code, out = run(["version"])
        self.assertEqual(code, 0)
        self.assertIn("1.2.3", out)

    def test_list(self):
        code, out = run(["list"])
        self.assertEqual(code, 0)
        self.assertIn("llama3", out)
        self.assertIn("MB", out)

    def test_generate_streaming(self):
        code, out = run(["generate", "llama3", "hello"])
        self.assertEqual(code, 0)
        self.assertIn("ab", out)

    def test_generate_no_stream(self):
        code, out = run(["generate", "llama3", "hello", "--no-stream"])
        self.assertEqual(code, 0)
        self.assertIn("full", out)

    def test_chat(self):
        code, out = run(["chat", "llama3", "ping"])
        self.assertEqual(code, 0)
        self.assertIn("answer:ping", out)

    def test_embed(self):
        code, out = run(["embed", "m", "text"])
        self.assertEqual(code, 0)
        self.assertIn("3 dimensions", out)


if __name__ == "__main__":
    unittest.main()
