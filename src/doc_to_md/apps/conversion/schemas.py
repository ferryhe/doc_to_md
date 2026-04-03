"""Pydantic models for the conversion FastAPI app."""
from __future__ import annotations

from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field


class ConvertRequest(BaseModel):
    input_path: str | None = Field(default=None, description="Directory of input documents")
    output_path: str | None = Field(default=None, description="Directory where Markdown files should be written")
    engine: str | None = Field(default=None, description="Engine name override")
    model: str | None = Field(default=None, description="Model override for engines that support it")
    since: datetime | None = Field(default=None, description="Process only files modified on or after this timestamp")
    no_page_info: bool = Field(default=False, description="Disable page headings and footer cleanup when supported by the engine")
    dry_run: bool = Field(default=False, description="List eligible files without converting or writing output")


class InlineConvertRequest(BaseModel):
    source_name: str = Field(description="Original filename including extension, for example sample.pdf")
    content_base64: str = Field(description="Base64-encoded document bytes")
    engine: str | None = Field(default=None, description="Engine name override")
    model: str | None = Field(default=None, description="Model override for engines that support it")
    no_page_info: bool = Field(default=False, description="Disable page headings and footer cleanup when supported by the engine")
    include_assets: bool = Field(default=False, description="Include generated asset bytes as base64 in the response")


class MarkdownDiagnosticResponse(BaseModel):
    code: str
    severity: str
    message: str
    count: int = 1


class MarkdownQualityResponse(BaseModel):
    status: str
    formula_status: str
    headings: int
    bullet_lines: int
    table_lines: int
    image_references: int
    formula_image_references: int
    inline_math_segments: int
    block_math_segments: int
    diagnostics: list[MarkdownDiagnosticResponse]


class InlineAssetResponse(BaseModel):
    filename: str
    subdir: str | None = None
    media_type: str | None = None
    content_base64: str | None = None


class DocumentResultResponse(BaseModel):
    source_path: str
    status: str
    output_path: str | None = None
    error: str | None = None
    modified_at: datetime | None = None
    quality: MarkdownQualityResponse | None = None


class InlineConvertResponse(BaseModel):
    status: Literal["converted"] = "converted"
    source_name: str
    engine: str
    model: str | None = None
    markdown: str
    quality: MarkdownQualityResponse
    asset_count: int
    assets: list[InlineAssetResponse]
    duration_seconds: float


class ConvertResponse(BaseModel):
    engine: str
    model: str | None = None
    input_dir: str
    output_dir: str
    total_candidates: int
    eligible: int
    converted: int
    failed: int
    skipped_since: int
    dry_run: int
    duration_seconds: float
    results: list[DocumentResultResponse]


class EnginesResponse(BaseModel):
    engines: list[str]


class HealthResponse(BaseModel):
    status: str = "ok"
