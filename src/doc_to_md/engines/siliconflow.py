"""Stub for SiliconFlow/DeepSeek OCR engine."""
from __future__ import annotations

from pathlib import Path

import requests

from config.settings import get_settings
from .base import Engine, EngineResponse


class SiliconFlowEngine(Engine):
    name = "siliconflow"

    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        if not settings.siliconflow_api_key:
            raise RuntimeError("SILICONFLOW_API_KEY missing")
        self.api_key = settings.siliconflow_api_key
        self.model = model or settings.siliconflow_default_model

    def convert(self, path: Path) -> EngineResponse:  # pragma: no cover - stub network
        files = {"file": path.read_bytes()}
        data = {"model": self.model}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post("https://api.siliconflow.cn/v1/ocr", files=files, data=data, headers=headers, timeout=60)
        response.raise_for_status()
        payload = response.json()
        return EngineResponse(markdown=payload.get("markdown", ""), model=payload.get("model", self.model))
