# airtop-ai

Airtop AI - A comprehensive AI-powered API platform providing intelligent automation, data processing, and advanced AI capabilities.

## Ollama Plugin (100% Python)

A dependency-free integration with a local [Ollama](https://ollama.com) server for
text generation, chat, and embeddings. It is written entirely in Python and uses
**only the standard library** (`urllib`, `json`, `argparse`) — no third-party
runtime dependencies.

### Features

- Text generation (`/api/generate`) with optional streaming
- Multi-turn chat (`/api/chat`) with tool-calling support and streaming
- Embeddings (`/api/embed`, with legacy `/api/embeddings` compatibility)
- Model management: list, show, pull, copy, delete
- Typed responses via lightweight dataclasses
- Automatic retries with exponential backoff for transient connection failures
- Clear exception hierarchy (`OllamaConnectionError`, `OllamaHTTPError`, `ModelNotFoundError`, ...)
- A small plugin framework (`BasePlugin` + `PluginRegistry`) the integration plugs into
- A CLI: `python -m airtop_ai.plugins.ollama.cli ...`

### Requirements

- Python 3.8+
- A running Ollama server (`ollama serve`) — by default at `http://127.0.0.1:11434`

### Installation

The package is pure Python; install it (editable) with pip:

```bash
pip install -e .
```

No runtime dependencies are pulled in.

### Quick start

```python
from airtop_ai.plugins.ollama import OllamaPlugin, OllamaConfig

# Reads $OLLAMA_HOST / $OLLAMA_TIMEOUT when set.
plugin = OllamaPlugin(OllamaConfig.from_env())

with plugin:  # verifies the server is reachable
    # One-shot completion
    result = plugin.complete("llama3", "Write a haiku about Python.")
    print(result.response)

    # Multi-turn chat (returns just the text)
    answer = plugin.ask("llama3", "Why use local LLMs?", system="Be concise.")
    print(answer)

    # Streaming
    for chunk in plugin.complete("llama3", "Count to five.", stream=True):
        print(chunk.response, end="", flush=True)

    # Embeddings
    emb = plugin.embed("nomic-embed-text", ["hello", "world"])
    print(len(emb.embeddings), "vectors")
```

See [`examples/ollama_quickstart.py`](examples/ollama_quickstart.py) for a runnable demo.

### Command line

```bash
# Installed entry point
ollama-plugin list
ollama-plugin generate llama3 "Write a haiku"
ollama-plugin chat llama3 "Hello there" --system "Be terse"
ollama-plugin embed nomic-embed-text "some text"
ollama-plugin version

# Or without installing
python -m airtop_ai.plugins.ollama.cli list
```

Use `--host` / `--timeout` to override the server location and request timeout.

### Configuration

| Setting        | Env var          | Default                     |
| -------------- | ---------------- | --------------------------- |
| `host`         | `OLLAMA_HOST`    | `http://127.0.0.1:11434`    |
| `timeout`      | `OLLAMA_TIMEOUT` | `120` (seconds)             |
| `api_key`      | `OLLAMA_API_KEY` | _(none)_                    |
| `max_retries`  | —                | `2`                         |
| `retry_backoff`| —                | `0.5` (seconds, exponential)|

### Project layout

```
airtop_ai/
  plugins/
    base.py                  # BasePlugin contract + PluginRegistry
    ollama/
      client.py              # stdlib-only HTTP client (buffered + streaming)
      config.py              # OllamaConfig (+ from_env)
      models.py              # typed request/response dataclasses
      exceptions.py          # error hierarchy
      plugin.py              # OllamaPlugin (BasePlugin implementation)
      cli.py                 # command-line interface
examples/ollama_quickstart.py
tests/                       # unittest suite (no network required)
```

### Running the tests

The suite mocks the HTTP layer, so no Ollama server or network access is needed:

```bash
python -m unittest discover -s tests -v
# or, if you prefer pytest:
pytest
```
