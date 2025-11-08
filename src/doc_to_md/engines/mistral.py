"""Stub implementation for the Mistral API."""
from __future__ import annotations

from pathlib import Path

import requests

from config.settings import get_settings
from .base import Engine, EngineResponse


class MistralEngine(Engine):
    name = "mistral"

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.minstral_api_key:
            raise RuntimeError("MINSTRAL_API_KEY missing")
        self.api_key = settings.minstral_api_key

    def convert(self, path: Path) -> EngineResponse:  # pragma: no cover - stub network
        payload = {"model": "mistral-large", "input": path.read_text(encoding="utf-8", errors="ignore")}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post("https://api.mistral.ai/v1/convert", json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return EngineResponse(markdown=data.get("markdown", ""), model=data.get("model", "unknown"))
