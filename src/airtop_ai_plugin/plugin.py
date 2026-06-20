"""Plugin facade for Airtop Ai."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .client import AirtopAiClient
from .config import AirtopAiConfig


PLUGIN_MANIFEST = {
    "name": "Airtop Ai",
    "slug": "airtop-ai",
    "version": "0.1.0",
    "description": (
        "AI-powered automation plugin for running Airtop Ai tasks from a host "
        "application."
    ),
    "entrypoint": "airtop_ai_plugin:AirtopAiPlugin",
    "capabilities": ["ai-tasks", "automation", "data-processing"],
    "configuration": [
        {
            "name": "AIRTOP_AI_API_KEY",
            "required": True,
            "description": "API key used to authenticate Airtop Ai requests.",
        },
        {
            "name": "AIRTOP_AI_BASE_URL",
            "required": False,
            "default": "https://api.airtop.ai",
            "description": "Base URL for the Airtop Ai API.",
        },
        {
            "name": "AIRTOP_AI_TIMEOUT_SECONDS",
            "required": False,
            "default": 30,
            "description": "HTTP request timeout in seconds.",
        },
    ],
}


@dataclass
class AirtopAiPlugin:
    """Airtop Ai plugin entry point."""

    config: AirtopAiConfig
    client: AirtopAiClient

    @classmethod
    def from_env(cls) -> "AirtopAiPlugin":
        """Create a plugin instance from environment variables."""

        return cls.from_config(AirtopAiConfig.from_env())

    @classmethod
    def from_config(cls, config: AirtopAiConfig) -> "AirtopAiPlugin":
        """Create a plugin instance from explicit configuration."""

        return cls(config=config, client=AirtopAiClient(config))

    @staticmethod
    def manifest() -> dict[str, Any]:
        """Return host-readable plugin metadata."""

        return dict(PLUGIN_MANIFEST)

    def health(self) -> dict[str, Any]:
        """Check Airtop Ai service health."""

        return self.client.health()

    def run(
        self,
        prompt: str,
        *,
        model: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run an Airtop Ai task."""

        return self.client.run_task(prompt=prompt, model=model, metadata=metadata)
