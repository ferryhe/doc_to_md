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
    mistral_timeout_seconds: float = Field(default=60.0, env="MISTRAL_TIMEOUT_SECONDS")
    mistral_retry_attempts: int = Field(default=3, env="MISTRAL_RETRY_ATTEMPTS")
    mistral_max_pdf_tokens: int = Field(default=9000, env="MISTRAL_MAX_PDF_TOKENS")
    mistral_max_pages_per_chunk: int = Field(default=25, env="MISTRAL_MAX_PAGES_PER_CHUNK")

    siliconflow_timeout_seconds: float = Field(default=60.0, env="SILICONFLOW_TIMEOUT_SECONDS")
    siliconflow_retry_attempts: int = Field(default=3, env="SILICONFLOW_RETRY_ATTEMPTS")
    siliconflow_max_input_tokens: int = Field(default=3500, env="SILICONFLOW_MAX_INPUT_TOKENS")
    siliconflow_chunk_overlap_tokens: int = Field(default=200, env="SILICONFLOW_CHUNK_OVERLAP_TOKENS")

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

        if self.siliconflow_chunk_overlap_tokens >= self.siliconflow_max_input_tokens:
            raise ValueError("SILICONFLOW_CHUNK_OVERLAP_TOKENS must be smaller than SILICONFLOW_MAX_INPUT_TOKENS")

        for field_name in ("mistral_retry_attempts", "siliconflow_retry_attempts"):
            value = getattr(self, field_name)
            if value < 1:
                raise ValueError(f"{field_name.upper()} must be at least 1")

        return self


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance so imports stay cheap."""
    return Settings()
