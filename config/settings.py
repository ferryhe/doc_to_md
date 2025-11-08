"""Centralized app settings loading .env values and CLI overrides."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = PROJECT_ROOT / "data" / "input"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "output"

EngineName = Literal["mistral", "siliconflow", "local"]


class Settings(BaseSettings):
    mistral_api_key: str | None = Field(default=None, env="MISTRAL_API_KEY")
    siliconflow_api_key: str | None = Field(default=None, env="SILICONFLOW_API_KEY")

    default_engine: EngineName = Field(default="local", env="DEFAULT_ENGINE")
    mistral_default_model: str = Field(default="mistral-ocr-latest", env="MISTRAL_DEFAULT_MODEL")
    siliconflow_default_model: str = Field(default="deepseek-ai/DeepSeek-OCR", env="SILICONFLOW_DEFAULT_MODEL")
    siliconflow_base_url: str = Field(
        default="https://api.siliconflow.cn/v1", env="SILICONFLOW_BASE_URL"
    )

    input_dir: Path = Field(default=DEFAULT_INPUT_DIR)
    output_dir: Path = Field(default=DEFAULT_OUTPUT_DIR)

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
    )

    @field_validator("input_dir", "output_dir", mode="before")
    def _coerce_path(cls, value: str | Path) -> Path:  # noqa: D401
        """Ensure directories are stored as Path objects."""
        return Path(value)

    @model_validator(mode="after")
    def _validate_environment(self) -> "Settings":
        missing_keys: list[str] = []
        if self.default_engine == "mistral" and not self.mistral_api_key:
            missing_keys.append("MISTRAL_API_KEY")
        if self.default_engine == "siliconflow" and not self.siliconflow_api_key:
            missing_keys.append("SILICONFLOW_API_KEY")

        if missing_keys:
            keys = ", ".join(missing_keys)
            raise ValueError(
                f"DEFAULT_ENGINE='{self.default_engine}' requires {keys} to be set. "
                "Update your .env or choose another default engine."
            )

        for directory in (self.input_dir, self.output_dir):
            directory.mkdir(parents=True, exist_ok=True)

        return self


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance so imports stay cheap."""
    return Settings()
