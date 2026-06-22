"""Airtop AI plugin framework.

Exposes the :class:`~airtop_ai.plugins.base.BasePlugin` contract that all
plugins implement, plus a tiny in-process registry used to discover plugins
by name.
"""

from __future__ import annotations

from .base import BasePlugin, PluginInfo, PluginRegistry, registry

__all__ = ["BasePlugin", "PluginInfo", "PluginRegistry", "registry"]
