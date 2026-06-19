import json
import unittest
import urllib.error
from unittest import mock

from airtop_ai.plugins.ollama.client import OllamaClient
from airtop_ai.plugins.ollama.config import OllamaConfig
from airtop_ai.plugins.ollama.exceptions import (
    ModelNotFoundError,
    OllamaConnectionError,
    OllamaHTTPError,
    OllamaResponseError,
)
from airtop_ai.plugins.ollama.models import ChatResponse, GenerateResponse, Message
from tests._fakes import (
    RecordingOpener,
    http_error,
    json_response,
    ndjson_response,
)

CLIENT_OPEN = "airtop_ai.plugins.ollama.client.urllib.request.urlopen"


def make_client(**kwargs):
    return OllamaClient(OllamaConfig(host="http://test:11434", retry_backoff=0, **kwargs))


class GenerateTests(unittest.TestCase):
    def test_generate_buffered(self):
        opener = RecordingOpener(
            [json_response({"model": "m", "response": "hi", "done": True})]
        )
        client = make_client()
        with mock.patch(CLIENT_OPEN, opener):
            result = client.generate("m", "prompt")
        self.assertIsInstance(result, GenerateResponse)
        self.assertEqual(result.response, "hi")
        # Verify the request body was built correctly.
        body = json.loads(opener.requests[0].data.decode("utf-8"))
        self.assertEqual(body["model"], "m")
        self.assertEqual(body["prompt"], "prompt")
        self.assertFalse(body["stream"])

    def test_generate_streaming(self):
        opener = RecordingOpener(
            [
                ndjson_response(
                    [
                        {"model": "m", "response": "he", "done": False},
                        {"model": "m", "response": "llo", "done": True},
                    ]
                )
            ]
        )
        client = make_client()
        with mock.patch(CLIENT_OPEN, opener):
            chunks = list(client.generate("m", "p", stream=True))
        self.assertEqual([c.response for c in chunks], ["he", "llo"])
        self.assertTrue(chunks[-1].done)

    def test_generate_includes_system_and_options(self):
        opener = RecordingOpener(
            [json_response({"model": "m", "response": "x", "done": True})]
        )
        client = make_client()
        with mock.patch(CLIENT_OPEN, opener):
            client.generate("m", "p", system="be brief", options={"temperature": 0.1})
        body = json.loads(opener.requests[0].data.decode("utf-8"))
        self.assertEqual(body["system"], "be brief")
        self.assertEqual(body["options"], {"temperature": 0.1})


class ChatTests(unittest.TestCase):
    def test_chat_accepts_message_objects_and_dicts(self):
        opener = RecordingOpener(
            [
                json_response(
                    {
                        "model": "m",
                        "message": {"role": "assistant", "content": "ok"},
                        "done": True,
                    }
                )
            ]
        )
        client = make_client()
        messages = [
            Message(role="system", content="sys"),
            {"role": "user", "content": "hello"},
        ]
        with mock.patch(CLIENT_OPEN, opener):
            result = client.chat("m", messages)
        self.assertIsInstance(result, ChatResponse)
        self.assertEqual(result.message.content, "ok")
        body = json.loads(opener.requests[0].data.decode("utf-8"))
        self.assertEqual(body["messages"][0], {"role": "system", "content": "sys"})
        self.assertEqual(body["messages"][1], {"role": "user", "content": "hello"})


class ModelManagementTests(unittest.TestCase):
    def test_list_models(self):
        opener = RecordingOpener(
            [json_response({"models": [{"name": "a"}, {"name": "b"}]})]
        )
        client = make_client()
        with mock.patch(CLIENT_OPEN, opener):
            models = client.list_models()
        self.assertEqual([m.name for m in models], ["a", "b"])

    def test_delete_model_uses_delete_method(self):
        opener = RecordingOpener([json_response({})])
        client = make_client()
        with mock.patch(CLIENT_OPEN, opener):
            self.assertTrue(client.delete_model("m"))
        self.assertEqual(opener.requests[0].get_method(), "DELETE")

    def test_version(self):
        opener = RecordingOpener([json_response({"version": "0.5.0"})])
        client = make_client()
        with mock.patch(CLIENT_OPEN, opener):
            self.assertEqual(client.version(), "0.5.0")


class ErrorHandlingTests(unittest.TestCase):
    def test_http_error_raises(self):
        opener = RecordingOpener([http_error(500, {"error": "boom"})])
        client = make_client()
        with mock.patch(CLIENT_OPEN, opener):
            with self.assertRaises(OllamaHTTPError) as ctx:
                client.version()
        self.assertEqual(ctx.exception.status_code, 500)

    def test_model_not_found(self):
        opener = RecordingOpener([http_error(404, {"error": "model 'x' not found"})])
        client = make_client()
        with mock.patch(CLIENT_OPEN, opener):
            with self.assertRaises(ModelNotFoundError):
                client.show_model("x")

    def test_invalid_json_raises_response_error(self):
        from tests._fakes import FakeResponse

        opener = RecordingOpener([FakeResponse(b"not json")])
        client = make_client()
        with mock.patch(CLIENT_OPEN, opener):
            with self.assertRaises(OllamaResponseError):
                client.version()

    def test_connection_error_after_retries(self):
        err = urllib.error.URLError("refused")
        opener = RecordingOpener([err, err, err])
        client = make_client(max_retries=2)
        with mock.patch(CLIENT_OPEN, opener):
            with self.assertRaises(OllamaConnectionError):
                client.version()
        # 1 initial + 2 retries == 3 attempts
        self.assertEqual(len(opener.requests), 3)

    def test_retry_then_success(self):
        opener = RecordingOpener(
            [urllib.error.URLError("temporary"), json_response({"version": "1.0"})]
        )
        client = make_client(max_retries=2)
        with mock.patch(CLIENT_OPEN, opener):
            self.assertEqual(client.version(), "1.0")
        self.assertEqual(len(opener.requests), 2)

    def test_is_alive_false_on_failure(self):
        opener = RecordingOpener([urllib.error.URLError("refused")])
        client = make_client(max_retries=0)
        with mock.patch(CLIENT_OPEN, opener):
            self.assertFalse(client.is_alive())


if __name__ == "__main__":
    unittest.main()
