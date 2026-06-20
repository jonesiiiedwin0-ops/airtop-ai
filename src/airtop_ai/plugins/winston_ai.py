"""Official Winston AI plugin.

Winston AI coordinates Airtop AI's installed plugin ecosystem into a staged
execution outline. The implementation is intentionally deterministic so plans
can be compared, tested, and rendered in documentation without calling an LLM.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


PLUGIN_ID = "winston-ai"
PLUGIN_NAME = "Winston AI"
PLUGIN_VERSION = "0.1.0"


@dataclass(frozen=True)
class PluginMilestone:
    """A staged milestone in Winston AI's official rollout outline."""

    stage: str
    focus: str
    outcomes: tuple[str, ...]
    plugin_usage: tuple[str, ...]


@dataclass(frozen=True)
class WinstonAIPlan:
    """A complete official rollout outline for Winston AI."""

    plugin_id: str
    plugin_name: str
    version: str
    installed_plugins: tuple[str, ...]
    milestones: tuple[PluginMilestone, ...] = field(default_factory=tuple)

    @property
    def uses_all_installed_plugins(self) -> bool:
        """Return true when every installed plugin appears in the outline."""

        planned_usage = {
            plugin
            for milestone in self.milestones
            for plugin in milestone.plugin_usage
        }
        return set(self.installed_plugins).issubset(planned_usage)


class WinstonAIPlugin:
    """Official orchestration plugin for Airtop AI."""

    plugin_id = PLUGIN_ID
    name = PLUGIN_NAME
    version = PLUGIN_VERSION
    official = True
    capabilities = (
        "plugin-orchestration",
        "execution-planning",
        "automation-governance",
        "ecosystem-reporting",
    )

    def build_one_year_outline(
        self,
        installed_plugins: Iterable[str],
    ) -> WinstonAIPlan:
        """Create a staged official rollout outline.

        Args:
            installed_plugins: Plugin names or identifiers available to Airtop AI.

        Returns:
            A deterministic Winston AI plan that references every installed
            plugin in at least one milestone.
        """

        normalized_plugins = self._normalize_plugins(installed_plugins)
        milestones = (
            PluginMilestone(
                stage="Foundation",
                focus="Define official plugin contracts, safety boundaries, and registry publication.",
                outcomes=(
                    "Publish the Winston AI manifest as an official plugin.",
                    "Document plugin activation, ownership, and compatibility expectations.",
                    "Establish acceptance checks for installed-plugin coverage.",
                ),
                plugin_usage=normalized_plugins,
            ),
            PluginMilestone(
                stage="Integration",
                focus="Connect Winston AI to every installed plugin and expose shared orchestration workflows.",
                outcomes=(
                    "Map each installed plugin to supported Winston AI workflows.",
                    "Add cross-plugin execution reports for platform operators.",
                    "Validate that no installed plugin is omitted from orchestration plans.",
                ),
                plugin_usage=normalized_plugins,
            ),
            PluginMilestone(
                stage="Automation",
                focus="Turn repeatable cross-plugin workflows into governed automations.",
                outcomes=(
                    "Introduce approval gates for sensitive plugin actions.",
                    "Record execution summaries for audit and rollback review.",
                    "Standardize failure handling across the installed plugin set.",
                ),
                plugin_usage=normalized_plugins,
            ),
            PluginMilestone(
                stage="Optimization",
                focus="Improve quality, observability, and official release readiness.",
                outcomes=(
                    "Measure workflow coverage across installed plugins.",
                    "Tune priority routing for high-value plugin combinations.",
                    "Prepare promotion criteria for the next official plugin release.",
                ),
                plugin_usage=normalized_plugins,
            ),
        )

        plan = WinstonAIPlan(
            plugin_id=self.plugin_id,
            plugin_name=self.name,
            version=self.version,
            installed_plugins=normalized_plugins,
            milestones=milestones,
        )

        if not plan.uses_all_installed_plugins:
            raise ValueError("Winston AI outline must use every installed plugin.")

        return plan

    @staticmethod
    def _normalize_plugins(installed_plugins: Iterable[str]) -> tuple[str, ...]:
        normalized = tuple(
            dict.fromkeys(
                plugin.strip()
                for plugin in installed_plugins
                if plugin and plugin.strip()
            )
        )
        if not normalized:
            return (PLUGIN_ID,)
        return normalized
