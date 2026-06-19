"""Shared test helpers: fake HTTP responses for the Ollama client.

These let the test-suite exercise the real client code paths (URL building,
JSON parsing, streaming, retries) without any network access.
"""

from __future__ import annotations

import io
import json
import urllib.error
from typing import Any, Dict, List, Optional


class FakeResponse:
    """Mimics the object returned by ``urllib.request.urlopen``."""

    def __init__(self, body: bytes) -> None:
        self._stream = io.BytesIO(body)

    def read(self) -> bytes:
        return self._stream.read()

    def __iter__(self):
        return iter(self._stream)

    def close(self) -> None:
        self._stream.close()

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


def json_response(payload: Dict[str, Any]) -> FakeResponse:
    return FakeResponse(json.dumps(payload).encode("utf-8"))


def ndjson_response(chunks: List[Dict[str, Any]]) -> FakeResponse:
    body = "\n".join(json.dumps(chunk) for chunk in chunks).encode("utf-8")
    return FakeResponse(body)


def http_error(
    code: int, payload: Optional[Dict[str, Any]] = None, url: str = "http://test"
) -> urllib.error.HTTPError:
    body = json.dumps(payload or {}).encode("utf-8")
    return urllib.error.HTTPError(url, code, "error", hdrs=None, fp=io.BytesIO(body))


class RecordingOpener:
    """A callable that records requests and returns queued responses."""

    def __init__(self, responses: List[Any]) -> None:
        self._responses = list(responses)
        self.requests: List[Any] = []

    def __call__(self, request, timeout=None):  # noqa: ANN001
        self.requests.append(request)
        result = self._responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result
