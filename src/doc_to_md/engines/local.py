"""Local fallback engine that simply wraps plain-text documents."""
from __future__ import annotations

from pathlib import Path

from .base import Engine, EngineResponse


class LocalEngine(Engine):
    name = "local"

    def convert(self, path: Path) -> EngineResponse:
        text = path.read_text(encoding="utf-8", errors="ignore")
        markdown = f"```\n{text}\n```"
        return EngineResponse(markdown=markdown, model="local-text-wrapper")
