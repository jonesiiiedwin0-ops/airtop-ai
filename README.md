# Airtop AI

Airtop AI is a comprehensive AI-powered API platform providing intelligent automation,
data processing, and advanced AI capabilities.

## Winston AI official server

This repository now includes the official Winston AI server scaffold. It is a
dependency-light Python HTTP service with health, status, outline, MCP context,
and assistant endpoints.

### Quickstart

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e .
winston-ai --host 127.0.0.1 --port 8000
```

### Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Basic liveness check |
| `GET` | `/v1/status` | Winston AI service metadata and capabilities |
| `GET` | `/v1/outline` | Year-one technical outline |
| `GET` | `/v1/mcp-context` | MCP systems used for context and operations |
| `POST` | `/v1/chat` | Deterministic assistant response scaffold |

Example request:

```bash
curl -sS \
  -H 'content-type: application/json' \
  -d '{"message":"create Winston AI"}' \
  http://127.0.0.1:8000/v1/chat
```

### MCP usage

The initial implementation used available MCP servers for supporting context:

- Mintlify MCP for documentation and OpenAPI reference guidance.
- Render MCP for deployment workspace discovery. No Render resource was changed
  because no workspace was selected.

See `docs/year_one_outline.md` for the technical launch outline.

### Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```
