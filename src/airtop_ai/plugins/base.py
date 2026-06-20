"""Shared types for Airtop AI plugins."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol


@dataclass(frozen=True)
class PluginMetadata:
    """Describes a plugin that can be registered with Airtop AI."""

    name: str
    slug: str
    version: str
    description: str
    official: bool = False
    capabilities: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PluginRequest:
    """A normalized request passed to a plugin."""

    prompt: str
    mode: str = "assistant"
    context: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PluginResponse:
    """A normalized response returned by a plugin."""

    plugin_slug: str
    mode: str
    content: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


class AirtopPlugin(Protocol):
    """Runtime contract implemented by Airtop AI plugins."""

    metadata: PluginMetadata

    def run(self, request: PluginRequest) -> PluginResponse:
        """Process a request and return a normalized response."""
