"""Official Winston AI plugin."""

from __future__ import annotations

import re
from collections.abc import Callable

from airtop_ai.plugins.base import PluginMetadata, PluginRequest, PluginResponse


class WinstonAIPlugin:
    """Official Airtop AI assistant plugin for planning and analysis workflows."""

    metadata = PluginMetadata(
        name="Winston AI",
        slug="winston-ai",
        version="0.1.0",
        description=(
            "Official Airtop AI plugin for assistant responses, summaries, "
            "action extraction, and implementation outlines."
        ),
        official=True,
        capabilities=("assistant", "summarize", "extract_actions", "plan"),
    )

    _mode_aliases = {
        "action_items": "extract_actions",
        "actions": "extract_actions",
        "outline": "plan",
        "roadmap": "plan",
        "summary": "summarize",
    }

    def run(self, request: PluginRequest) -> PluginResponse:
        """Process a Winston AI request."""

        prompt = request.prompt.strip()
        if not prompt:
            raise ValueError("Winston AI requires a non-empty prompt.")

        mode = self._normalize_mode(request.mode)
        handlers: dict[str, Callable[[str], str]] = {
            "assistant": self._assistant_response,
            "summarize": self._summarize,
            "extract_actions": self._extract_actions,
            "plan": self._plan,
        }

        content = handlers[mode](prompt)
        return PluginResponse(
            plugin_slug=self.metadata.slug,
            mode=mode,
            content=content,
            metadata={
                "official": self.metadata.official,
                "capabilities": self.metadata.capabilities,
            },
        )

    def _normalize_mode(self, mode: str) -> str:
        normalized = mode.strip().lower().replace("-", "_")
        normalized = self._mode_aliases.get(normalized, normalized)
        if normalized not in self.metadata.capabilities:
            capabilities = ", ".join(self.metadata.capabilities)
            raise ValueError(f"Unsupported Winston AI mode: {mode}. Use one of: {capabilities}.")
        return normalized

    def _assistant_response(self, prompt: str) -> str:
        focus = self._first_sentence(prompt)
        return (
            f"Winston AI is ready to help with: {focus}\n\n"
            "Recommended next step: provide the target inputs, success criteria, "
            "and any operational constraints so Winston AI can produce an actionable result."
        )

    def _summarize(self, prompt: str) -> str:
        sentences = self._sentences(prompt)
        summary = " ".join(sentences[:2]) if sentences else prompt
        if len(summary) <= 320:
            return summary
        return f"{summary[:317].rstrip()}..."

    def _extract_actions(self, prompt: str) -> str:
        actions = []
        for line in prompt.splitlines():
            normalized = line.strip(" -\t")
            if not normalized:
                continue
            if self._looks_actionable(normalized):
                actions.append(normalized.rstrip("."))

        if not actions:
            return "No explicit action items found."

        return "Action items:\n" + "\n".join(f"- {action}" for action in actions)

    def _plan(self, prompt: str) -> str:
        focus = self._first_sentence(prompt)
        return "\n".join(
            (
                f"Winston AI implementation outline for: {focus}",
                "",
                "1. Foundation: define plugin contracts, safety boundaries, and registration metadata.",
                "2. Intelligence: add summarization, action extraction, and planning workflows.",
                "3. Integrations: connect installed Airtop AI plugins through the registry.",
                "4. Governance: add evaluations, audit logging, and release readiness checks.",
                "5. Scale: harden operational metrics, documentation, and partner extension paths.",
            )
        )

    @staticmethod
    def _sentences(prompt: str) -> list[str]:
        return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", prompt) if sentence.strip()]

    @classmethod
    def _first_sentence(cls, prompt: str) -> str:
        sentences = cls._sentences(prompt)
        return sentences[0] if sentences else prompt

    @staticmethod
    def _looks_actionable(line: str) -> bool:
        actionable_prefixes = (
            "add ",
            "build ",
            "create ",
            "document ",
            "ensure ",
            "fix ",
            "implement ",
            "plan ",
            "ship ",
            "test ",
            "update ",
        )
        lowered = line.lower()
        return lowered.startswith(actionable_prefixes) or any(
            marker in lowered for marker in (" must ", " need ", " needs ", " should ", " todo")
        )
