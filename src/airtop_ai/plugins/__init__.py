"""Installed Airtop AI plugins."""

from airtop_ai.plugins.base import AirtopPlugin, PluginMetadata, PluginRequest, PluginResponse
from airtop_ai.plugins.registry import PluginRegistry
from airtop_ai.plugins.winston_ai import WinstonAIPlugin


def create_default_registry() -> PluginRegistry:
    """Create a registry containing every installed official plugin."""

    return PluginRegistry([WinstonAIPlugin()])


__all__ = [
    "AirtopPlugin",
    "PluginMetadata",
    "PluginRegistry",
    "PluginRequest",
    "PluginResponse",
    "WinstonAIPlugin",
    "create_default_registry",
]
