import unittest

from airtop_ai.plugins.ollama.models import (
    ChatResponse,
    EmbeddingResponse,
    GenerateResponse,
    Message,
    ModelInfo,
)


class MessageTests(unittest.TestCase):
    def test_round_trip(self):
        msg = Message(role="user", content="hi", images=["b64"])
        data = msg.to_dict()
        self.assertEqual(data["role"], "user")
        self.assertEqual(data["images"], ["b64"])
        restored = Message.from_dict(data)
        self.assertEqual(restored.content, "hi")

    def test_to_dict_omits_empty_optionals(self):
        self.assertNotIn("images", Message("user", "hi").to_dict())


class ResponseTests(unittest.TestCase):
    def test_generate_response(self):
        resp = GenerateResponse.from_dict(
            {"model": "llama3", "response": "hello", "done": True, "eval_count": 7}
        )
        self.assertEqual(resp.model, "llama3")
        self.assertEqual(resp.response, "hello")
        self.assertTrue(resp.done)
        self.assertEqual(resp.eval_count, 7)

    def test_chat_response(self):
        resp = ChatResponse.from_dict(
            {
                "model": "llama3",
                "message": {"role": "assistant", "content": "hi there"},
                "done": True,
            }
        )
        self.assertEqual(resp.message.role, "assistant")
        self.assertEqual(resp.message.content, "hi there")

    def test_embedding_response_plural(self):
        resp = EmbeddingResponse.from_dict(
            {"model": "m", "embeddings": [[0.1, 0.2], [0.3, 0.4]]}
        )
        self.assertEqual(len(resp.embeddings), 2)

    def test_embedding_response_singular_legacy(self):
        resp = EmbeddingResponse.from_dict({"model": "m", "embedding": [0.1, 0.2]})
        self.assertEqual(resp.embeddings, [[0.1, 0.2]])

    def test_model_info(self):
        info = ModelInfo.from_dict(
            {"name": "llama3:latest", "size": 4096, "digest": "abc"}
        )
        self.assertEqual(info.name, "llama3:latest")
        self.assertEqual(info.size, 4096)


if __name__ == "__main__":
    unittest.main()
