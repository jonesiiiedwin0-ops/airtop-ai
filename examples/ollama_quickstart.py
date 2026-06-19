"""Quickstart for the Airtop AI Ollama plugin.

Run a local Ollama server first (``ollama serve``) and make sure a model is
available (e.g. ``ollama pull llama3``). Then:

    python examples/ollama_quickstart.py
"""

from __future__ import annotations

from airtop_ai.plugins.ollama import Message, OllamaConfig, OllamaPlugin


def main() -> None:
    # Configuration is read from $OLLAMA_HOST / $OLLAMA_TIMEOUT when present.
    plugin = OllamaPlugin(OllamaConfig.from_env())

    # `setup()` raises if the server is unreachable; the context manager calls it.
    with plugin:
        print("Ollama server version:", plugin.server_version())

        print("\nInstalled models:")
        for model in plugin.list_models():
            print(f"  - {model.name}")

        model = "llama3"
        if not plugin.has_model(model):
            print(f"\nModel {model!r} not found. Pull it with `ollama pull {model}`.")
            return

        # One-shot completion.
        result = plugin.complete(model, "Write a one-line haiku about Python.")
        print("\nCompletion:\n ", result.response.strip())

        # Multi-turn chat.
        reply = plugin.ask(
            model,
            "Name three benefits of local LLMs.",
            system="You are a concise assistant.",
        )
        print("\nChat reply:\n ", reply.strip())

        # Streaming generation.
        print("\nStreaming:")
        for chunk in plugin.complete(model, "Count from 1 to 5.", stream=True):
            print(chunk.response, end="", flush=True)
        print()

        # Embeddings (requires an embedding model such as nomic-embed-text).
        if plugin.has_model("nomic-embed-text"):
            embedding = plugin.embed("nomic-embed-text", "hello world")
            print("\nEmbedding dimensions:", len(embedding.embeddings[0]))


if __name__ == "__main__":
    main()
