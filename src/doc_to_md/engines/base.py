"""Abstractions for pluggable conversion engines."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(slots=True)
class EngineResponse:
    markdown: str
    model: str


class Engine(Protocol):
    name: str

    def convert(self, path: Path) -> EngineResponse:
        ...
