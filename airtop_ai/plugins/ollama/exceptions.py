"""Exception hierarchy for the Ollama plugin."""

from __future__ import annotations

from typing import Optional


class OllamaError(Exception):
    """Base class for all Ollama plugin errors."""


class OllamaConnectionError(OllamaError):
    """Raised when the Ollama server cannot be reached."""


class OllamaTimeoutError(OllamaError):
    """Raised when a request exceeds the configured timeout."""


class OllamaHTTPError(OllamaError):
    """Raised when the Ollama server returns a non-2xx status code."""

    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        url: Optional[str] = None,
        body: Optional[str] = None,
    ) -> None:
        self.status_code = status_code
        self.url = url
        self.body = body
        detail = f"HTTP {status_code}"
        if url:
            detail += f" for {url}"
        if message:
            detail += f": {message}"
        super().__init__(detail)


class OllamaResponseError(OllamaError):
    """Raised when the server returns an unparseable or unexpected payload."""


class ModelNotFoundError(OllamaError):
    """Raised when a requested model is not available locally."""
