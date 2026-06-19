"""Core plugin contract and registry for Airtop AI.

The framework intentionally keeps zero third-party dependencies so that any
plugin built on top of it remains 100% Python and trivially installable.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional


@dataclass(frozen=True)
class PluginInfo:
    """Static metadata describing a plugin."""

    name: str
    version: str
    description: str = ""
    author: str = ""
    homepage: str = ""
    tags: tuple = ()

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "homepage": self.homepage,
            "tags": list(self.tags),
        }


class BasePlugin(abc.ABC):
    """Abstract base class every Airtop AI plugin must implement.

    A plugin owns its lifecycle (``setup``/``teardown``) and advertises a
    small, stable surface so the host platform can treat every integration
    uniformly regardless of the provider behind it.
    """

    #: Subclasses must override with a :class:`PluginInfo` instance.
    info: PluginInfo

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if abc.ABC not in cls.__bases__ and not getattr(cls, "info", None):
            raise TypeError(
                f"{cls.__name__} must define a class-level `info` PluginInfo"
            )

    # -- lifecycle -----------------------------------------------------------
    def setup(self) -> None:
        """Prepare the plugin for use. Override if initialisation is needed."""

    def teardown(self) -> None:
        """Release any resources held by the plugin."""

    def __enter__(self) -> "BasePlugin":
        self.setup()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.teardown()

    # -- health --------------------------------------------------------------
    @abc.abstractmethod
    def health_check(self) -> bool:
        """Return ``True`` when the backing service is reachable and usable."""
        raise NotImplementedError

    # -- capabilities --------------------------------------------------------
    def capabilities(self) -> List[str]:
        """List the high-level capabilities this plugin offers."""
        return []


@dataclass
class PluginRegistry:
    """A minimal name -> plugin-instance registry."""

    _plugins: Dict[str, BasePlugin] = field(default_factory=dict)

    def register(self, plugin: BasePlugin, *, replace: bool = False) -> BasePlugin:
        name = plugin.info.name
        if name in self._plugins and not replace:
            raise ValueError(f"Plugin {name!r} is already registered")
        self._plugins[name] = plugin
        return plugin

    def unregister(self, name: str) -> None:
        self._plugins.pop(name, None)

    def get(self, name: str) -> Optional[BasePlugin]:
        return self._plugins.get(name)

    def names(self) -> List[str]:
        return sorted(self._plugins)

    def __iter__(self) -> Iterator[BasePlugin]:
        return iter(self._plugins.values())

    def __len__(self) -> int:
        return len(self._plugins)

    def __contains__(self, name: object) -> bool:
        return name in self._plugins


#: Process-wide default registry.
registry = PluginRegistry()
