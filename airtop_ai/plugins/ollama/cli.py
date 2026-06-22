"""Command-line interface for the Ollama plugin.

Usage examples
--------------
    python -m airtop_ai.plugins.ollama.cli list
    python -m airtop_ai.plugins.ollama.cli generate llama3 "Write a haiku"
    python -m airtop_ai.plugins.ollama.cli chat llama3 "Hello there"
    python -m airtop_ai.plugins.ollama.cli embed nomic-embed-text "some text"
    python -m airtop_ai.plugins.ollama.cli version
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .config import OllamaConfig
from .exceptions import OllamaError
from .models import GenerateResponse
from .plugin import OllamaPlugin


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ollama-plugin",
        description="Interact with a local Ollama server (100% Python).",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Ollama host URL (defaults to $OLLAMA_HOST or http://127.0.0.1:11434).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Request timeout in seconds.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("version", help="Print the Ollama server version.")
    sub.add_parser("list", help="List locally available models.")

    p_gen = sub.add_parser("generate", help="Generate a completion.")
    p_gen.add_argument("model")
    p_gen.add_argument("prompt")
    p_gen.add_argument("--system", default=None)
    p_gen.add_argument("--no-stream", action="store_true")

    p_chat = sub.add_parser("chat", help="Send a single chat message.")
    p_chat.add_argument("model")
    p_chat.add_argument("message")
    p_chat.add_argument("--system", default=None)

    p_embed = sub.add_parser("embed", help="Create an embedding for text.")
    p_embed.add_argument("model")
    p_embed.add_argument("text")

    p_pull = sub.add_parser("pull", help="Download a model.")
    p_pull.add_argument("model")

    return parser


def _make_plugin(args: argparse.Namespace) -> OllamaPlugin:
    overrides = {}
    if args.host is not None:
        overrides["host"] = args.host
    if args.timeout is not None:
        overrides["timeout"] = args.timeout
    config = OllamaConfig.from_env(**overrides)
    return OllamaPlugin(config)


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    plugin = _make_plugin(args)

    try:
        if args.command == "version":
            print(plugin.server_version())
        elif args.command == "list":
            models = plugin.list_models()
            if not models:
                print("No models installed.")
            for model in models:
                size_mb = model.size / (1024 * 1024) if model.size else 0
                print(f"{model.name:<40} {size_mb:>10.1f} MB")
        elif args.command == "generate":
            stream = not args.no_stream
            result = plugin.complete(
                args.model, args.prompt, system=args.system, stream=stream
            )
            if stream:
                for chunk in result:  # type: ignore[union-attr]
                    sys.stdout.write(chunk.response)
                    sys.stdout.flush()
                sys.stdout.write("\n")
            else:
                assert isinstance(result, GenerateResponse)
                print(result.response)
        elif args.command == "chat":
            reply = plugin.ask(args.model, args.message, system=args.system)
            print(reply)
        elif args.command == "embed":
            response = plugin.embed(args.model, args.text)
            vectors = response.embeddings
            dims = len(vectors[0]) if vectors else 0
            print(f"{len(vectors)} embedding(s), {dims} dimensions")
            if vectors:
                preview = ", ".join(f"{v:.4f}" for v in vectors[0][:8])
                print(f"[{preview}, ...]")
        elif args.command == "pull":
            for chunk in plugin.pull_model(args.model, stream=True):  # type: ignore[union-attr]
                status = chunk.get("status", "")
                if status:
                    sys.stdout.write(f"\r{status}")
                    sys.stdout.flush()
            sys.stdout.write("\n")
        else:  # pragma: no cover - argparse enforces valid commands
            parser.error(f"Unknown command: {args.command}")
    except OllamaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
