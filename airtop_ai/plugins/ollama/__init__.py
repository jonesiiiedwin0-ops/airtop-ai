"""Ollama plugin for Airtop AI.

A 100% Python, dependency-free integration with a local `Ollama
<https://ollama.com>`_ server for text generation, chat, and embeddings.
"""

from __future__ import annotations

from .client import OllamaClient
from .config import OllamaConfig
from .exceptions import (
    ModelNotFoundError,
    OllamaConnectionError,
    OllamaError,
    OllamaHTTPError,
    OllamaResponseError,
    OllamaTimeoutError,
)
from .models import (
    ChatResponse,
    EmbeddingResponse,
    GenerateResponse,
    Message,
    ModelInfo,
)
from .plugin import OllamaPlugin

__all__ = [
    "OllamaClient",
    "OllamaConfig",
    "OllamaPlugin",
    "Message",
    "GenerateResponse",
    "ChatResponse",
    "EmbeddingResponse",
    "ModelInfo",
    "OllamaError",
    "OllamaConnectionError",
    "OllamaTimeoutError",
    "OllamaHTTPError",
    "OllamaResponseError",
    "ModelNotFoundError",
]
