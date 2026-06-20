from __future__ import annotations

import json
import threading
import unittest
from http.client import HTTPConnection
from typing import Any

from winston_ai.server import build_server


class WinstonAIServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = build_server("127.0.0.1", 0)
        cls.host, cls.port = cls.server.server_address
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.thread.join(timeout=5)
        cls.server.server_close()

    def request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, dict[str, Any]]:
        connection = HTTPConnection(self.host, self.port, timeout=5)
        encoded_body = json.dumps(body).encode("utf-8") if body is not None else None
        connection.request(method, path, body=encoded_body, headers=headers or {})
        response = connection.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        connection.close()
        return response.status, payload

    def test_status_returns_winston_ai_metadata(self) -> None:
        status, payload = self.request("GET", "/v1/status")

        self.assertEqual(status, 200)
        self.assertEqual(payload["name"], "Winston AI")
        self.assertEqual(payload["slug"], "winston-ai")
        self.assertGreaterEqual(len(payload["capabilities"]), 3)

    def test_outline_contains_launch_horizons(self) -> None:
        status, payload = self.request("GET", "/v1/outline")

        self.assertEqual(status, 200)
        horizons = {item["horizon"] for item in payload["outline"]}
        self.assertIn("foundation", horizons)
        self.assertIn("official launch", horizons)

    def test_chat_returns_deterministic_reply(self) -> None:
        status, payload = self.request(
            "POST",
            "/v1/chat",
            body={"message": "  create   Winston AI  "},
            headers={"content-type": "application/json"},
        )

        self.assertEqual(status, 200)
        self.assertEqual(payload["server"], "Winston AI")
        self.assertIn("create Winston AI", payload["reply"])

    def test_chat_rejects_invalid_message(self) -> None:
        status, payload = self.request(
            "POST",
            "/v1/chat",
            body={"message": ""},
            headers={"content-type": "application/json"},
        )

        self.assertEqual(status, 400)
        self.assertEqual(payload["error"]["code"], "invalid_message")

    def test_unknown_route_returns_json_404(self) -> None:
        status, payload = self.request("GET", "/missing")

        self.assertEqual(status, 404)
        self.assertEqual(payload["error"]["code"], "not_found")


if __name__ == "__main__":
    unittest.main()
