# airtop-ai

Airtop AI is a comprehensive AI-powered API platform providing intelligent
automation, data processing, and advanced AI capabilities.

## Official plugins

This repository includes a lightweight plugin foundation and the first official
plugin:

- **Winston AI** (`winston-ai`): assistant responses, summaries, action item
  extraction, and implementation outlines.

## Usage

```python
from airtop_ai.plugins import PluginRequest, create_default_registry

registry = create_default_registry()
winston = registry.get("winston-ai")

response = winston.run(
    PluginRequest(
        prompt="Create a new official plugin named Winston AI.",
        mode="roadmap",
    )
)

print(response.content)
```

`create_default_registry()` installs every official plugin shipped by the
package, so applications can discover and use all installed plugins through a
single registry.

## Development

```bash
python -m pytest
```

See [docs/winston-ai-1-year-outline.md](docs/winston-ai-1-year-outline.md) for
the Winston AI product and engineering outline.
