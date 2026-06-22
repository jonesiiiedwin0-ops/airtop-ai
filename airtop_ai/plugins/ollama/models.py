"""Typed data models for Ollama requests and responses.

These dataclasses provide a friendly, attribute-based interface over the raw
JSON returned by the Ollama REST API while remaining tolerant of unknown
fields (forward compatibility with newer server versions).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Message:
    """A single chat message."""

    role: str
    content: str
    images: Optional[List[str]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {"role": self.role, "content": self.content}
        if self.images:
            data["images"] = self.images
        if self.tool_calls:
            data["tool_calls"] = self.tool_calls
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            role=data.get("role", ""),
            content=data.get("content", ""),
            images=data.get("images"),
            tool_calls=data.get("tool_calls"),
        )


@dataclass
class GenerateResponse:
    """Response from the ``/api/generate`` endpoint."""

    model: str
    response: str
    done: bool
    created_at: str = ""
    context: Optional[List[int]] = None
    total_duration: Optional[int] = None
    eval_count: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerateResponse":
        return cls(
            model=data.get("model", ""),
            response=data.get("response", ""),
            done=bool(data.get("done", False)),
            created_at=data.get("created_at", ""),
            context=data.get("context"),
            total_duration=data.get("total_duration"),
            eval_count=data.get("eval_count"),
            prompt_eval_count=data.get("prompt_eval_count"),
            raw=data,
        )


@dataclass
class ChatResponse:
    """Response from the ``/api/chat`` endpoint."""

    model: str
    message: Message
    done: bool
    created_at: str = ""
    total_duration: Optional[int] = None
    eval_count: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatResponse":
        message_data = data.get("message") or {}
        return cls(
            model=data.get("model", ""),
            message=Message.from_dict(message_data),
            done=bool(data.get("done", False)),
            created_at=data.get("created_at", ""),
            total_duration=data.get("total_duration"),
            eval_count=data.get("eval_count"),
            prompt_eval_count=data.get("prompt_eval_count"),
            raw=data,
        )


@dataclass
class EmbeddingResponse:
    """Response from the ``/api/embed`` endpoint."""

    model: str
    embeddings: List[List[float]]
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmbeddingResponse":
        # Newer servers return "embeddings" (list of lists); older ones use
        # the singular "embedding" (a single list) on /api/embeddings.
        if "embeddings" in data:
            embeddings = data["embeddings"]
        elif "embedding" in data:
            embeddings = [data["embedding"]]
        else:
            embeddings = []
        return cls(
            model=data.get("model", ""),
            embeddings=embeddings,
            raw=data,
        )


@dataclass
class ModelInfo:
    """Summary of a locally available model (from ``/api/tags``)."""

    name: str
    size: int = 0
    digest: str = ""
    modified_at: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelInfo":
        return cls(
            name=data.get("name") or data.get("model", ""),
            size=int(data.get("size", 0) or 0),
            digest=data.get("digest", ""),
            modified_at=data.get("modified_at", ""),
            details=data.get("details", {}) or {},
            raw=data,
        )
