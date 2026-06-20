# Winston AI 1-Year Outline

Winston AI is the first official Airtop AI plugin. Its purpose is to provide a
trusted assistant layer for planning, summarization, action extraction, and
workflow orchestration across installed Airtop AI plugins.

## Year 1 objective

Deliver Winston AI as the official plugin that helps users turn unstructured
requests into reliable Airtop AI workflows. Winston AI should remain discoverable
through the default plugin registry and should coordinate with every installed
official plugin through shared metadata and capability contracts.

## Execution tracks

### 1. Plugin foundation

- Define stable plugin metadata for name, slug, version, description,
  official status, and capabilities.
- Provide normalized request and response types for consistent plugin
  invocation.
- Add a registry that can discover all installed official plugins and retrieve
  them by slug.
- Keep the core dependency-free so new environments can bootstrap quickly.

### 2. Winston AI core capabilities

- Assistant mode for general guidance.
- Summarization mode for compacting long user input.
- Action extraction mode for turning natural language into task lists.
- Planning mode for implementation outlines and roadmap-style responses.
- Mode aliases so user-facing names such as `roadmap` and `actions` map to the
  canonical plugin capabilities.

### 3. Installed plugin orchestration

- Use the default registry as the integration surface for all installed official
  plugins.
- Keep capability metadata machine-readable so Winston AI can route tasks to
  compatible plugins as the catalog grows.
- Preserve deterministic local behavior when external providers or hosted AI
  services are unavailable.

### 4. Quality and governance

- Add unit tests for registration, official plugin discovery, mode aliases, and
  error handling.
- Introduce evaluation fixtures for summarization quality and action extraction
  precision as the plugin gains model-backed behavior.
- Document release readiness checks, safety constraints, and operational
  ownership before enabling hosted integrations.

### 5. Adoption and scale

- Publish copy-paste examples for common workflows.
- Expand documentation for plugin authors who want Winston AI to orchestrate
  their capabilities.
- Add telemetry hooks for success metrics after the platform has an approved
  observability contract.
- Maintain backward-compatible plugin contracts once external users depend on
  them.

## Completed in this branch

- Added the Python package scaffold for Airtop AI.
- Added shared plugin types and an in-memory plugin registry.
- Added the official `WinstonAIPlugin` with assistant, summarize,
  extract-actions, and plan modes.
- Registered Winston AI in `create_default_registry()`, which is the entry point
  for all installed official plugins.
- Added focused tests for official plugin discovery, roadmap alias handling,
  action extraction, and prompt validation.
- Updated the README with usage instructions.
