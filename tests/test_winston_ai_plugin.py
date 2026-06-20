import json
import unittest
from pathlib import Path

from airtop_ai.plugins import WinstonAIPlugin


ROOT = Path(__file__).resolve().parents[1]


class WinstonAIPluginTest(unittest.TestCase):
    def test_build_one_year_outline_uses_all_installed_plugins(self):
        installed_plugins = (
            "data-importer",
            "workflow-runner",
            "notification-hub",
        )

        plan = WinstonAIPlugin().build_one_year_outline(installed_plugins)

        self.assertEqual(plan.plugin_id, "winston-ai")
        self.assertEqual(plan.plugin_name, "Winston AI")
        self.assertTrue(plan.uses_all_installed_plugins)
        for milestone in plan.milestones:
            self.assertEqual(milestone.plugin_usage, installed_plugins)

    def test_build_one_year_outline_deduplicates_and_ignores_blank_plugins(self):
        plan = WinstonAIPlugin().build_one_year_outline(
            [" data-importer ", "", "workflow-runner", "data-importer"]
        )

        self.assertEqual(plan.installed_plugins, ("data-importer", "workflow-runner"))
        self.assertTrue(plan.uses_all_installed_plugins)

    def test_build_one_year_outline_defaults_to_winston_ai_when_empty(self):
        plan = WinstonAIPlugin().build_one_year_outline([])

        self.assertEqual(plan.installed_plugins, ("winston-ai",))
        self.assertTrue(plan.uses_all_installed_plugins)

    def test_registry_and_manifest_are_consistent(self):
        registry = json.loads((ROOT / "plugins/official/registry.json").read_text())
        manifest_path = ROOT / "plugins/official/winston-ai/plugin.json"
        manifest = json.loads(manifest_path.read_text())

        self.assertEqual(registry["registryVersion"], 1)
        self.assertIn(
            {
                "id": "winston-ai",
                "name": "Winston AI",
                "manifest": "plugins/official/winston-ai/plugin.json",
                "entrypoint": "airtop_ai.plugins.winston_ai:WinstonAIPlugin",
                "status": "official",
            },
            registry["officialPlugins"],
        )
        self.assertEqual(manifest["id"], "winston-ai")
        self.assertEqual(manifest["name"], "Winston AI")
        self.assertEqual(manifest["status"], "official")
        self.assertTrue(manifest["requirements"]["usesAllInstalledPlugins"])


if __name__ == "__main__":
    unittest.main()
