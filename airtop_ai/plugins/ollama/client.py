"""Pure-Python HTTP client for the Ollama REST API.

The client relies solely on the Python standard library (``urllib``), so the
plugin has no third-party runtime dependencies and stays 100% Python. It
supports both buffered and streaming (NDJSON) responses.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Iterator, List, Optional, Union

from .config import OllamaConfig
from .exceptions import (
    ModelNotFoundError,
    OllamaConnectionError,
    OllamaError,
    OllamaHTTPError,
    OllamaResponseError,
    OllamaTimeoutError,
)
from .models import (
    ChatResponse,
    EmbeddingResponse,
    GenerateResponse,
    Message,
    ModelInfo,
)

JSONDict = Dict[str, Any]
MessageLike = Union[Message, Dict[str, Any]]


class OllamaClient:
    """Low-level client mapping Ollama HTTP endpoints to Python methods."""

    def __init__(self, config: Optional[OllamaConfig] = None) -> None:
        self.config = config or OllamaConfig()

    # -- internal helpers ----------------------------------------------------
    def _url(self, path: str) -> str:
        return f"{self.config.host}/{path.lstrip('/')}"

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    def _open(self, request: urllib.request.Request) -> Any:
        """Open a request with retry/backoff for transient failures."""

        last_exc: Optional[Exception] = None
        for attempt in range(self.config.max_retries + 1):
            try:
                return urllib.request.urlopen(request, timeout=self.config.timeout)
            except urllib.error.HTTPError:
                # HTTP errors are deterministic; don't retry them here.
                raise
            except TimeoutError as exc:  # pragma: no cover - env dependent
                raise OllamaTimeoutError(
                    f"Request to {request.full_url} timed out after "
                    f"{self.config.timeout}s"
                ) from exc
            except urllib.error.URLError as exc:
                last_exc = exc
                reason = getattr(exc, "reason", exc)
                if isinstance(reason, TimeoutError):
                    raise OllamaTimeoutError(
                        f"Request to {request.full_url} timed out after "
                        f"{self.config.timeout}s"
                    ) from exc
                if attempt < self.config.max_retries:
                    time.sleep(self.config.retry_backoff * (2 ** attempt))
                    continue
                raise OllamaConnectionError(
                    f"Could not connect to Ollama at {self.config.host}: {reason}"
                ) from exc
        # Should be unreachable, but keeps type checkers satisfied.
        raise OllamaConnectionError(  # pragma: no cover
            f"Could not connect to Ollama at {self.config.host}: {last_exc}"
        )

    def _build_request(
        self, method: str, path: str, payload: Optional[JSONDict]
    ) -> urllib.request.Request:
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
        return urllib.request.Request(
            self._url(path),
            data=data,
            headers=self._headers(),
            method=method,
        )

    @staticmethod
    def _raise_for_http_error(exc: urllib.error.HTTPError) -> None:
        body = ""
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:  # pragma: no cover - defensive
            body = ""
        message = body
        try:
            parsed = json.loads(body)
            if isinstance(parsed, dict) and "error" in parsed:
                message = str(parsed["error"])
        except (ValueError, TypeError):
            pass
        if exc.code == 404 and "model" in message.lower():
            raise ModelNotFoundError(message or "Model not found") from exc
        raise OllamaHTTPError(exc.code, message, url=exc.filename, body=body) from exc

    def request(
        self, method: str, path: str, payload: Optional[JSONDict] = None
    ) -> JSONDict:
        """Perform a buffered JSON request and return the parsed body."""

        request = self._build_request(method, path, payload)
        try:
            with self._open(request) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            self._raise_for_http_error(exc)
            raise  # pragma: no cover - _raise_for_http_error always raises
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except ValueError as exc:
            raise OllamaResponseError(
                f"Invalid JSON returned by {path}: {raw[:200]!r}"
            ) from exc

    def stream(
        self, method: str, path: str, payload: Optional[JSONDict] = None
    ) -> Iterator[JSONDict]:
        """Perform a streaming request, yielding one JSON object per line."""

        request = self._build_request(method, path, payload)
        try:
            response = self._open(request)
        except urllib.error.HTTPError as exc:
            self._raise_for_http_error(exc)
            raise  # pragma: no cover
        with response:
            for line in response:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line.decode("utf-8"))
                except ValueError as exc:
                    raise OllamaResponseError(
                        f"Invalid JSON line from {path}: {line[:200]!r}"
                    ) from exc

    # -- normalisation helpers ----------------------------------------------
    @staticmethod
    def _normalize_messages(messages: List[MessageLike]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for item in messages:
            if isinstance(item, Message):
                normalized.append(item.to_dict())
            elif isinstance(item, dict):
                normalized.append(item)
            else:  # pragma: no cover - defensive
                raise TypeError(
                    "messages must be Message instances or dicts, got "
                    f"{type(item).__name__}"
                )
        return normalized

    # -- API: generation -----------------------------------------------------
    def generate(
        self,
        model: str,
        prompt: str,
        *,
        system: Optional[str] = None,
        options: Optional[JSONDict] = None,
        context: Optional[List[int]] = None,
        format: Optional[Union[str, JSONDict]] = None,
        keep_alive: Optional[Union[str, int]] = None,
        stream: bool = False,
    ) -> Union[GenerateResponse, Iterator[GenerateResponse]]:
        """Call ``/api/generate`` for a single-prompt completion."""

        payload: JSONDict = {"model": model, "prompt": prompt, "stream": stream}
        if system is not None:
            payload["system"] = system
        if options:
            payload["options"] = options
        if context is not None:
            payload["context"] = context
        if format is not None:
            payload["format"] = format
        if keep_alive is not None:
            payload["keep_alive"] = keep_alive

        if stream:
            return (
                GenerateResponse.from_dict(chunk)
                for chunk in self.stream("POST", "/api/generate", payload)
            )
        return GenerateResponse.from_dict(self.request("POST", "/api/generate", payload))

    # -- API: chat -----------------------------------------------------------
    def chat(
        self,
        model: str,
        messages: List[MessageLike],
        *,
        options: Optional[JSONDict] = None,
        tools: Optional[List[JSONDict]] = None,
        format: Optional[Union[str, JSONDict]] = None,
        keep_alive: Optional[Union[str, int]] = None,
        stream: bool = False,
    ) -> Union[ChatResponse, Iterator[ChatResponse]]:
        """Call ``/api/chat`` with a list of messages."""

        payload: JSONDict = {
            "model": model,
            "messages": self._normalize_messages(messages),
            "stream": stream,
        }
        if options:
            payload["options"] = options
        if tools:
            payload["tools"] = tools
        if format is not None:
            payload["format"] = format
        if keep_alive is not None:
            payload["keep_alive"] = keep_alive

        if stream:
            return (
                ChatResponse.from_dict(chunk)
                for chunk in self.stream("POST", "/api/chat", payload)
            )
        return ChatResponse.from_dict(self.request("POST", "/api/chat", payload))

    # -- API: embeddings -----------------------------------------------------
    def embed(
        self,
        model: str,
        input: Union[str, List[str]],
        *,
        options: Optional[JSONDict] = None,
        truncate: Optional[bool] = None,
    ) -> EmbeddingResponse:
        """Call ``/api/embed`` to produce embeddings for one or more inputs."""

        payload: JSONDict = {"model": model, "input": input}
        if options:
            payload["options"] = options
        if truncate is not None:
            payload["truncate"] = truncate
        return EmbeddingResponse.from_dict(self.request("POST", "/api/embed", payload))

    # -- API: model management ----------------------------------------------
    def list_models(self) -> List[ModelInfo]:
        """Call ``/api/tags`` and return locally available models."""

        data = self.request("GET", "/api/tags")
        return [ModelInfo.from_dict(item) for item in data.get("models", [])]

    def show_model(self, model: str) -> JSONDict:
        """Call ``/api/show`` and return metadata for a single model."""

        return self.request("POST", "/api/show", {"model": model})

    def pull_model(
        self, model: str, *, stream: bool = False
    ) -> Union[JSONDict, Iterator[JSONDict]]:
        """Call ``/api/pull`` to download a model from the registry."""

        payload = {"model": model, "stream": stream}
        if stream:
            return self.stream("POST", "/api/pull", payload)
        return self.request("POST", "/api/pull", payload)

    def delete_model(self, model: str) -> bool:
        """Call ``/api/delete`` to remove a local model. Returns ``True``."""

        self.request("DELETE", "/api/delete", {"model": model})
        return True

    def copy_model(self, source: str, destination: str) -> bool:
        """Call ``/api/copy`` to duplicate a local model."""

        self.request("POST", "/api/copy", {"source": source, "destination": destination})
        return True

    # -- API: server --------------------------------------------------------
    def version(self) -> str:
        """Call ``/api/version`` and return the server version string."""

        data = self.request("GET", "/api/version")
        return str(data.get("version", ""))

    def is_alive(self) -> bool:
        """Return ``True`` if the server root responds without error."""

        try:
            self._open(self._build_request("GET", "/", None)).close()
            return True
        except OllamaError:
            return False
