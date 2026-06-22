"""High-level Ollama plugin integrating with the Airtop AI framework."""

from __future__ import annotations

from typing import Iterator, List, Optional, Union

from ..base import BasePlugin, PluginInfo
from .client import MessageLike, OllamaClient
from .config import OllamaConfig
from .exceptions import OllamaError
from .models import (
    ChatResponse,
    EmbeddingResponse,
    GenerateResponse,
    Message,
    ModelInfo,
)

JSONDict = dict


class OllamaPlugin(BasePlugin):
    """Airtop AI plugin exposing local Ollama models.

    Example
    -------
    >>> plugin = OllamaPlugin()
    >>> with plugin:                                  # doctest: +SKIP
    ...     reply = plugin.complete("llama3", "Hello!")
    ...     print(reply.response)
    """

    info = PluginInfo(
        name="ollama",
        version="0.1.0",
        description="Run and manage local LLMs through an Ollama server.",
        author="Airtop AI",
        homepage="https://ollama.com",
        tags=("llm", "local", "chat", "embeddings"),
    )

    def __init__(
        self,
        config: Optional[OllamaConfig] = None,
        *,
        client: Optional[OllamaClient] = None,
    ) -> None:
        self.config = config or OllamaConfig()
        self.client = client or OllamaClient(self.config)

    # -- lifecycle -----------------------------------------------------------
    def setup(self) -> None:
        """Verify the server is reachable before the plugin is used."""

        if not self.client.is_alive():
            raise OllamaError(
                f"Ollama server is not reachable at {self.config.host}. "
                "Start it with `ollama serve`."
            )

    # -- framework contract --------------------------------------------------
    def health_check(self) -> bool:
        return self.client.is_alive()

    def capabilities(self) -> List[str]:
        return ["generate", "chat", "embed", "list_models", "manage_models"]

    # -- text generation -----------------------------------------------------
    def complete(
        self,
        model: str,
        prompt: str,
        *,
        system: Optional[str] = None,
        options: Optional[JSONDict] = None,
        stream: bool = False,
        **kwargs: object,
    ) -> Union[GenerateResponse, Iterator[GenerateResponse]]:
        """Generate a completion for ``prompt`` using ``model``."""

        return self.client.generate(
            model,
            prompt,
            system=system,
            options=options,
            stream=stream,
            **kwargs,  # type: ignore[arg-type]
        )

    def chat(
        self,
        model: str,
        messages: List[MessageLike],
        *,
        options: Optional[JSONDict] = None,
        tools: Optional[List[JSONDict]] = None,
        stream: bool = False,
        **kwargs: object,
    ) -> Union[ChatResponse, Iterator[ChatResponse]]:
        """Hold a multi-turn conversation with ``model``."""

        return self.client.chat(
            model,
            messages,
            options=options,
            tools=tools,
            stream=stream,
            **kwargs,  # type: ignore[arg-type]
        )

    def ask(
        self,
        model: str,
        question: str,
        *,
        system: Optional[str] = None,
        options: Optional[JSONDict] = None,
    ) -> str:
        """Convenience helper returning just the assistant's text reply."""

        messages: List[MessageLike] = []
        if system:
            messages.append(Message(role="system", content=system))
        messages.append(Message(role="user", content=question))
        response = self.chat(model, messages, options=options, stream=False)
        assert isinstance(response, ChatResponse)
        return response.message.content

    # -- embeddings ----------------------------------------------------------
    def embed(
        self,
        model: str,
        text: Union[str, List[str]],
        *,
        options: Optional[JSONDict] = None,
    ) -> EmbeddingResponse:
        """Return embeddings for one or more strings."""

        return self.client.embed(model, text, options=options)

    # -- model management ----------------------------------------------------
    def list_models(self) -> List[ModelInfo]:
        return self.client.list_models()

    def has_model(self, model: str) -> bool:
        """Return ``True`` when ``model`` (optionally without ``:tag``) exists."""

        wanted = model if ":" in model else f"{model}:"
        for info in self.client.list_models():
            if info.name == model or info.name.startswith(wanted):
                return True
        return False

    def show_model(self, model: str) -> JSONDict:
        return self.client.show_model(model)

    def pull_model(
        self, model: str, *, stream: bool = False
    ) -> Union[JSONDict, Iterator[JSONDict]]:
        return self.client.pull_model(model, stream=stream)

    def delete_model(self, model: str) -> bool:
        return self.client.delete_model(model)

    def copy_model(self, source: str, destination: str) -> bool:
        return self.client.copy_model(source, destination)

    # -- server info ---------------------------------------------------------
    def server_version(self) -> str:
        return self.client.version()
