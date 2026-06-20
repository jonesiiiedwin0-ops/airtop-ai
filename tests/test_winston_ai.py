"""Tests for the official Winston AI plugin."""

from __future__ import annotations

import pytest

from airtop_ai.plugins import PluginRequest, WinstonAIPlugin, create_default_registry


def test_default_registry_installs_winston_ai_as_official_plugin() -> None:
    registry = create_default_registry()

    plugin = registry.get("winston-ai")

    assert isinstance(plugin, WinstonAIPlugin)
    assert plugin.metadata.name == "Winston AI"
    assert plugin.metadata.official is True
    assert registry.official() == (plugin,)


def test_winston_ai_generates_plan_outline() -> None:
    plugin = WinstonAIPlugin()

    response = plugin.run(
        PluginRequest(
            prompt="Create a new official plugin named Winston AI.",
            mode="roadmap",
        )
    )

    assert response.plugin_slug == "winston-ai"
    assert response.mode == "plan"
    assert "Foundation" in response.content
    assert "Integrations" in response.content
    assert response.metadata["official"] is True


def test_winston_ai_extracts_action_items() -> None:
    plugin = WinstonAIPlugin()

    response = plugin.run(
        PluginRequest(
            prompt="\n".join(
                (
                    "Discuss release readiness.",
                    "Create plugin metadata.",
                    "Ensure tests cover registry behavior.",
                    "Ship documentation.",
                )
            ),
            mode="actions",
        )
    )

    assert response.content.splitlines() == [
        "Action items:",
        "- Create plugin metadata",
        "- Ensure tests cover registry behavior",
        "- Ship documentation",
    ]


def test_winston_ai_rejects_empty_prompt() -> None:
    plugin = WinstonAIPlugin()

    with pytest.raises(ValueError, match="non-empty prompt"):
        plugin.run(PluginRequest(prompt="   "))
