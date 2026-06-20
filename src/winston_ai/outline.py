"""Canonical Winston AI service metadata and technical outline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Capability:
    """A stable public capability exposed by the Winston AI server."""

    key: str
    name: str
    description: str
    status: str

    def to_dict(self) -> dict[str, str]:
        return {
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "status": self.status,
        }


CAPABILITIES: tuple[Capability, ...] = (
    Capability(
        key="assist",
        name="Winston Assist",
        description="Accepts structured user prompts and returns deterministic assistant responses.",
        status="available",
    ),
    Capability(
        key="outline",
        name="Year-one technical outline",
        description="Publishes the server buildout plan as API data and documentation.",
        status="available",
    ),
    Capability(
        key="mcp-context",
        name="MCP context registry",
        description="Tracks external MCP systems used for documentation, deployment, and operations context.",
        status="available",
    ),
)


YEAR_ONE_OUTLINE: tuple[dict[str, Any], ...] = (
    {
        "horizon": "foundation",
        "objective": "Make Winston AI installable, observable, and easy to run locally.",
        "deliverables": (
            "Package metadata and CLI entrypoint",
            "Health, metadata, outline, and assistant endpoints",
            "Deterministic request validation and JSON errors",
            "Automated tests for public API behavior",
        ),
        "exit_criteria": (
            "A clean clone can run the server with one command",
            "Health checks and OpenAPI-style metadata are documented",
            "Tests cover success and validation paths",
        ),
    },
    {
        "horizon": "mcp-integrated operations",
        "objective": "Use MCP systems as governed context sources rather than hidden dependencies.",
        "deliverables": (
            "MCP registry endpoint",
            "Documentation workflow aligned with Mintlify guidance",
            "Deployment readiness notes for Render workspaces",
            "Clear rules for authenticated MCP actions",
        ),
        "exit_criteria": (
            "External MCP availability is visible to operators",
            "No destructive MCP action runs without an explicit selected workspace",
            "Docs and server metadata stay in sync",
        ),
    },
    {
        "horizon": "production readiness",
        "objective": "Prepare Winston AI for stable public API use.",
        "deliverables": (
            "Authentication and rate-limit boundaries",
            "Structured audit logging",
            "Model-provider adapter interface",
            "Regression tests for compatibility guarantees",
        ),
        "exit_criteria": (
            "Public routes have explicit contracts",
            "Operational events can be inspected without exposing secrets",
            "Provider changes do not alter client-facing response shapes",
        ),
    },
    {
        "horizon": "official launch",
        "objective": "Publish Winston AI as the official AI server for the platform.",
        "deliverables": (
            "Versioned API reference",
            "Deployment runbook",
            "Support escalation paths",
            "Launch readiness checklist",
        ),
        "exit_criteria": (
            "Release artifacts are reproducible",
            "Operators can deploy, roll back, and inspect the service",
            "Users have documented integration examples",
        ),
    },
)


MCP_CONTEXT: tuple[dict[str, str], ...] = (
    {
        "server": "Mintlify",
        "purpose": "Documentation and OpenAPI reference guidance",
        "mode": "read-only documentation search",
    },
    {
        "server": "Render",
        "purpose": "Deployment and operations workspace context",
        "mode": "read-only discovery until a workspace is explicitly selected",
    },
)


def service_metadata() -> dict[str, Any]:
    return {
        "name": "Winston AI",
        "slug": "winston-ai",
        "status": "official-scaffold",
        "description": "Official AI server scaffold for Airtop AI automation and assistant workflows.",
        "version": "0.1.0",
        "capabilities": [capability.to_dict() for capability in CAPABILITIES],
    }


def year_one_outline() -> list[dict[str, Any]]:
    return [
        {
            **item,
            "deliverables": list(item["deliverables"]),
            "exit_criteria": list(item["exit_criteria"]),
        }
        for item in YEAR_ONE_OUTLINE
    ]
