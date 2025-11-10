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

EngineName = Literal["mistral", "deepseekocr", "local", "markitdown", "paddleocr", "mineru", "docling", "marker"]


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

    markitdown_enable_plugins: bool | None = Field(default=True, env="MARKITDOWN_ENABLE_PLUGINS")
    markitdown_enable_builtins: bool | None = Field(default=True, env="MARKITDOWN_ENABLE_BUILTINS")

    paddleocr_lang: str = Field(default="en", env="PADDLEOCR_LANG")
    paddleocr_render_dpi: int = Field(default=220, env="PADDLEOCR_RENDER_DPI")
    paddleocr_max_pages: int | None = Field(default=None, env="PADDLEOCR_MAX_PAGES")

    docling_max_pages: int | None = Field(default=None, env="DOCLING_MAX_PAGES")
    docling_raise_on_error: bool = Field(default=True, env="DOCLING_RAISE_ON_ERROR")

    mineru_backend: str = Field(default="pipeline", env="MINERU_BACKEND")
    mineru_parse_method: str = Field(default="auto", env="MINERU_PARSE_METHOD")
    mineru_lang: str = Field(default="en", env="MINERU_LANG")
    mineru_formula_enable: bool = Field(default=True, env="MINERU_FORMULA_ENABLE")
    mineru_table_enable: bool = Field(default=True, env="MINERU_TABLE_ENABLE")
    mineru_start_page: int = Field(default=0, env="MINERU_START_PAGE")
    mineru_end_page: int | None = Field(default=None, env="MINERU_END_PAGE")

    marker_use_llm: bool = Field(default=False, env="MARKER_USE_LLM")
    marker_processors: str | None = Field(default=None, env="MARKER_PROCESSORS")
    marker_page_range: str | None = Field(default=None, env="MARKER_PAGE_RANGE")
    marker_extract_images: bool = Field(default=True, env="MARKER_EXTRACT_IMAGES")
    marker_llm_service: str | None = Field(default=None, env="MARKER_LLM_SERVICE")

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
        for directory in (self.input_dir, self.output_dir):
            directory.mkdir(parents=True, exist_ok=True)

        if self.siliconflow_chunk_overlap_tokens >= self.siliconflow_max_input_tokens:
            raise ValueError("SILICONFLOW_CHUNK_OVERLAP_TOKENS must be smaller than SILICONFLOW_MAX_INPUT_TOKENS")

        for field_name in ("mistral_retry_attempts", "siliconflow_retry_attempts"):
            value = getattr(self, field_name)
            if value < 1:
                raise ValueError(f"{field_name.upper()} must be at least 1")

        if self.paddleocr_render_dpi <= 0:
            raise ValueError("PADDLEOCR_RENDER_DPI must be positive")
        if self.paddleocr_max_pages is not None and self.paddleocr_max_pages < 1:
            raise ValueError("PADDLEOCR_MAX_PAGES must be at least 1 when provided")

        if self.docling_max_pages is not None and self.docling_max_pages < 1:
            raise ValueError("DOCLING_MAX_PAGES must be at least 1 when provided")

        if self.mineru_start_page < 0:
            raise ValueError("MINERU_START_PAGE cannot be negative")
        if self.mineru_end_page is not None and self.mineru_end_page < self.mineru_start_page:
            raise ValueError("MINERU_END_PAGE must be >= MINERU_START_PAGE")

        return self

    @field_validator("paddleocr_max_pages", "docling_max_pages", "mineru_end_page", mode="before")
    @classmethod
    def _blank_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance so imports stay cheap."""
    return Settings()
