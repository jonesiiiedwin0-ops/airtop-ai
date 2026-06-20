"""Plugin registration and discovery helpers."""

from __future__ import annotations

from collections.abc import Iterable

from airtop_ai.plugins.base import AirtopPlugin


class PluginRegistry:
    """In-memory registry for installed Airtop AI plugins."""

    def __init__(self, plugins: Iterable[AirtopPlugin] | None = None) -> None:
        self._plugins: dict[str, AirtopPlugin] = {}
        for plugin in plugins or ():
            self.register(plugin)

    def register(self, plugin: AirtopPlugin) -> None:
        """Register a plugin by slug."""

        slug = plugin.metadata.slug
        if not slug:
            raise ValueError("Plugin metadata slug must not be empty.")
        if slug in self._plugins:
            raise ValueError(f"Plugin already registered: {slug}")

        self._plugins[slug] = plugin

    def get(self, slug: str) -> AirtopPlugin:
        """Return a registered plugin by slug."""

        try:
            return self._plugins[slug]
        except KeyError as exc:
            raise KeyError(f"Unknown plugin: {slug}") from exc

    def all(self) -> tuple[AirtopPlugin, ...]:
        """Return all registered plugins sorted by display name."""

        return tuple(sorted(self._plugins.values(), key=lambda plugin: plugin.metadata.name))

    def official(self) -> tuple[AirtopPlugin, ...]:
        """Return all installed official plugins."""

        return tuple(plugin for plugin in self.all() if plugin.metadata.official)
