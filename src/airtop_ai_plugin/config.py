"""Configuration helpers for the Airtop Ai plugin."""

from __future__ import annotations

from dataclasses import dataclass
import os


DEFAULT_BASE_URL = "https://api.airtop.ai"
DEFAULT_TIMEOUT_SECONDS = 30


@dataclass(frozen=True)
class AirtopAiConfig:
    """Runtime configuration for connecting to the Airtop Ai API."""

    api_key: str
    base_url: str = DEFAULT_BASE_URL
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        api_key = self.api_key.strip()
        base_url = self.base_url.strip().rstrip("/")

        if not api_key:
            raise ValueError("Airtop Ai API key is required")
        if not base_url:
            raise ValueError("Airtop Ai base URL is required")
        if self.timeout_seconds <= 0:
            raise ValueError("Airtop Ai timeout must be greater than zero")

        object.__setattr__(self, "api_key", api_key)
        object.__setattr__(self, "base_url", base_url)

    @classmethod
    def from_env(
        cls,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout_seconds: int | None = None,
    ) -> "AirtopAiConfig":
        """Build configuration from explicit values or environment variables."""

        resolved_timeout = timeout_seconds
        if resolved_timeout is None:
            raw_timeout = os.getenv("AIRTOP_AI_TIMEOUT_SECONDS")
            resolved_timeout = (
                int(raw_timeout) if raw_timeout else DEFAULT_TIMEOUT_SECONDS
            )

        return cls(
            api_key=api_key or os.getenv("AIRTOP_AI_API_KEY", ""),
            base_url=base_url or os.getenv("AIRTOP_AI_BASE_URL", DEFAULT_BASE_URL),
            timeout_seconds=resolved_timeout,
        )
