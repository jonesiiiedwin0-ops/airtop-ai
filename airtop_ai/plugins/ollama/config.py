"""Configuration for the Ollama plugin.

Defaults follow the upstream Ollama server (``http://127.0.0.1:11434``) and
can be overridden explicitly or via environment variables.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_HOST = "http://127.0.0.1:11434"
DEFAULT_TIMEOUT = 120.0

ENV_HOST = "OLLAMA_HOST"
ENV_TIMEOUT = "OLLAMA_TIMEOUT"


def _normalize_host(host: str) -> str:
    """Return a fully-qualified base URL without a trailing slash.

    Ollama's ``OLLAMA_HOST`` is frequently set to ``host:port`` without a
    scheme; we add ``http://`` in that case for convenience.
    """

    host = host.strip().rstrip("/")
    if not host:
        return DEFAULT_HOST
    if "://" not in host:
        host = f"http://{host}"
    return host


@dataclass
class OllamaConfig:
    """Runtime configuration for the Ollama client."""

    host: str = DEFAULT_HOST
    timeout: float = DEFAULT_TIMEOUT
    #: Number of automatic retries for transient connection failures.
    max_retries: int = 2
    #: Base delay (seconds) for exponential backoff between retries.
    retry_backoff: float = 0.5
    #: Optional bearer token for gateways that sit in front of Ollama.
    api_key: str = ""

    def __post_init__(self) -> None:
        self.host = _normalize_host(self.host)
        self.timeout = float(self.timeout)
        self.max_retries = max(0, int(self.max_retries))
        self.retry_backoff = max(0.0, float(self.retry_backoff))

    @classmethod
    def from_env(cls, **overrides: object) -> "OllamaConfig":
        """Build a config from environment variables, applying overrides."""

        host = os.environ.get(ENV_HOST, DEFAULT_HOST)
        timeout_raw = os.environ.get(ENV_TIMEOUT)
        timeout = float(timeout_raw) if timeout_raw else DEFAULT_TIMEOUT
        api_key = os.environ.get("OLLAMA_API_KEY", "")
        base = {
            "host": host,
            "timeout": timeout,
            "api_key": api_key,
        }
        base.update(overrides)
        return cls(**base)  # type: ignore[arg-type]
