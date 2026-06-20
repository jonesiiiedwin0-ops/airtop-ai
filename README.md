# Airtop Ai

Airtop Ai is a Python plugin for API-driven AI automation workflows. It provides
a small host-facing facade, environment-backed configuration, and a lightweight
HTTP client for submitting Airtop Ai tasks.

## Installation

```bash
python -m pip install .
```

## Configuration

Set the Airtop Ai API key before loading the plugin:

```bash
export AIRTOP_AI_API_KEY="your-api-key"
```

Optional settings:

- `AIRTOP_AI_BASE_URL`: Airtop Ai API base URL. Defaults to
  `https://api.airtop.ai`.
- `AIRTOP_AI_TIMEOUT_SECONDS`: HTTP timeout in seconds. Defaults to `30`.

## Usage

```python
from airtop_ai_plugin import AirtopAiPlugin

plugin = AirtopAiPlugin.from_env()
result = plugin.run(
    "Summarize the latest automation workflow output.",
    metadata={"source": "workflow-runner"},
)
print(result)
```

## Plugin manifest

The plugin can be discovered through either:

- `plugin.json`
- Python entry point: `airtop.plugins = airtop-ai`

The plugin name is `Airtop Ai` and its slug is `airtop-ai`.
