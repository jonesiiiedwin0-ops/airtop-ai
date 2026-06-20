"""HTTP client for the Airtop Ai plugin."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Callable, Protocol
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .config import AirtopAiConfig


class Response(Protocol):
    def read(self) -> bytes:
        """Return the raw response payload."""


Transport = Callable[..., Response]


@dataclass
class AirtopAiClient:
    """Minimal Airtop Ai API client used by the plugin facade."""

    config: AirtopAiConfig
    transport: Transport = urlopen

    def health(self) -> dict[str, Any]:
        """Fetch Airtop Ai service health."""

        return self._request("GET", "/health")

    def run_task(
        self,
        *,
        prompt: str,
        model: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Submit an AI task to Airtop Ai."""

        if not prompt.strip():
            raise ValueError("Airtop Ai task prompt is required")

        payload: dict[str, Any] = {"prompt": prompt}
        if model:
            payload["model"] = model
        if metadata:
            payload["metadata"] = metadata

        return self._request("POST", "/v1/tasks", payload)

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        request = Request(
            self._url(path),
            data=json.dumps(payload).encode("utf-8") if payload is not None else None,
            headers=self._headers(payload is not None),
            method=method,
        )

        try:
            response = self.transport(request, timeout=self.config.timeout_seconds)
            body = response.read().decode("utf-8")
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Airtop Ai API request failed with status {error.code}: {detail}"
            ) from error

        if not body:
            return {}

        decoded = json.loads(body)
        if not isinstance(decoded, dict):
            raise RuntimeError("Airtop Ai API response must be a JSON object")

        return decoded

    def _headers(self, has_payload: bool) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Accept": "application/json",
            "User-Agent": "airtop-ai-plugin/0.1.0",
        }
        if has_payload:
            headers["Content-Type"] = "application/json"
        return headers

    def _url(self, path: str) -> str:
        normalized_path = path if path.startswith("/") else f"/{path}"
        return f"{self.config.base_url}{normalized_path}"
