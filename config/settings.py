"""Centralized app settings loading .env values and CLI overrides."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseSettings, Field, validator

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = PROJECT_ROOT / "data" / "input"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "output"

EngineName = Literal["mistral", "siliconflow", "local"]


class Settings(BaseSettings):
    minstral_api_key: str | None = Field(default=None, env="MINSTRAL_API_KEY")
    siliconflow_api_key: str | None = Field(default=None, env="SILICONFLOW_API_KEY")

    default_engine: EngineName = Field(default="local")
    default_model: str = Field(default="deepseek-ai/DeepSeek-OCR")

    input_dir: Path = Field(default=DEFAULT_INPUT_DIR)
    output_dir: Path = Field(default=DEFAULT_OUTPUT_DIR)

    class Config:
        env_file = PROJECT_ROOT / ".env"
        env_file_encoding = "utf-8"

    @validator("input_dir", "output_dir", pre=True)
    def _coerce_path(cls, value: str | Path) -> Path:  # noqa: D401
        """Ensure directories are stored as Path objects."""
        return Path(value)


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance so imports stay cheap."""
    return Settings()
