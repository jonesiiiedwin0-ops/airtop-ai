"""HTTP entrypoint for the Winston AI official server."""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from winston_ai.outline import MCP_CONTEXT, service_metadata, year_one_outline

JsonObject = dict[str, Any]


class WinstonAIHandler(BaseHTTPRequestHandler):
    server_version = "WinstonAI/0.1.0"

    def do_GET(self) -> None:
        routes = {
            "/": self._handle_root,
            "/health": self._handle_health,
            "/v1/status": self._handle_status,
            "/v1/outline": self._handle_outline,
            "/v1/mcp-context": self._handle_mcp_context,
        }
        handler = routes.get(urlparse(self.path).path)
        if handler is None:
            self._send_error(HTTPStatus.NOT_FOUND, "not_found", "Route not found.")
            return
        handler()

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/v1/chat":
            self._send_error(HTTPStatus.NOT_FOUND, "not_found", "Route not found.")
            return

        payload = self._read_json_body()
        if payload is None:
            return

        message = payload.get("message")
        if not isinstance(message, str) or not message.strip():
            self._send_error(
                HTTPStatus.BAD_REQUEST,
                "invalid_message",
                "Request body must include a non-empty string field named 'message'.",
            )
            return

        normalized = " ".join(message.strip().split())
        self._send_json(
            HTTPStatus.OK,
            {
                "server": "Winston AI",
                "reply": f"Winston AI received your request: {normalized}",
                "next_steps": [
                    "Attach authenticated model providers before production launch.",
                    "Use the MCP context registry for docs and deployment evidence.",
                ],
            },
        )

    def log_message(self, format: str, *args: Any) -> None:
        """Keep test and local command output focused on explicit responses."""

    def _handle_root(self) -> None:
        self._send_json(
            HTTPStatus.OK,
            {
                **service_metadata(),
                "links": {
                    "health": "/health",
                    "status": "/v1/status",
                    "outline": "/v1/outline",
                    "mcp_context": "/v1/mcp-context",
                    "chat": "/v1/chat",
                },
            },
        )

    def _handle_health(self) -> None:
        self._send_json(HTTPStatus.OK, {"status": "ok", "server": "Winston AI"})

    def _handle_status(self) -> None:
        self._send_json(HTTPStatus.OK, service_metadata())

    def _handle_outline(self) -> None:
        self._send_json(HTTPStatus.OK, {"outline": year_one_outline()})

    def _handle_mcp_context(self) -> None:
        self._send_json(HTTPStatus.OK, {"mcp_context": list(MCP_CONTEXT)})

    def _read_json_body(self) -> JsonObject | None:
        content_type = self.headers.get("content-type", "")
        if "application/json" not in content_type:
            self._send_error(
                HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                "unsupported_media_type",
                "Content-Type must be application/json.",
            )
            return None

        try:
            length = int(self.headers.get("content-length", "0"))
        except ValueError:
            self._send_error(HTTPStatus.BAD_REQUEST, "invalid_length", "Invalid Content-Length.")
            return None

        try:
            raw_body = self.rfile.read(length)
            payload = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_error(HTTPStatus.BAD_REQUEST, "invalid_json", "Request body must be valid JSON.")
            return None

        if not isinstance(payload, dict):
            self._send_error(HTTPStatus.BAD_REQUEST, "invalid_json", "Request body must be a JSON object.")
            return None
        return payload

    def _send_json(self, status: HTTPStatus, payload: JsonObject) -> None:
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status.value)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: HTTPStatus, code: str, message: str) -> None:
        self._send_json(status, {"error": {"code": code, "message": message}})


def build_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), WinstonAIHandler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Winston AI official server.")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind.")
    parser.add_argument("--port", default=8000, type=int, help="Port to bind.")
    args = parser.parse_args()

    server = build_server(args.host, args.port)
    print(f"Winston AI server listening on http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
