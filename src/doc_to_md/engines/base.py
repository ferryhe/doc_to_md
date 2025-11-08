"""Abstractions for pluggable conversion engines."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


@dataclass(slots=True)
class EngineAsset:
    """Binary artifact generated alongside Markdown output (e.g., images)."""

    filename: str
    data: bytes
    subdir: str | None = None


@dataclass(slots=True)
class EngineResponse:
    markdown: str
    model: str
    assets: list[EngineAsset] = field(default_factory=list)


class Engine(Protocol):
    name: str

    def convert(self, path: Path) -> EngineResponse:
        ...
