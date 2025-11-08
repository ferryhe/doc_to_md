"""Local fallback engine that attempts lightweight text extraction."""
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from .base import Engine, EngineResponse


class LocalEngine(Engine):
    name = "local"

    def convert(self, path: Path) -> EngineResponse:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            text = self._extract_pdf_text(path)
        else:
            text = path.read_text(encoding="utf-8", errors="ignore")

        if not text.strip():
            text = "_No textual content could be extracted._"

        markdown = f"# {path.stem}\n\n{text}\n"
        return EngineResponse(markdown=markdown, model="local-text-wrapper")

    def _extract_pdf_text(self, path: Path) -> str:
        """Extract a rough text representation from PDF pages."""
        reader = PdfReader(str(path))
        parts: list[str] = []
        for index, page in enumerate(reader.pages, start=1):
            try:
                page_text = page.extract_text() or ""
            except Exception as exc:  # noqa: BLE001 - best effort fallback
                page_text = f"[Page {index} extraction failed: {exc}]"
            parts.append(page_text.strip())
        return "\n\n".join(filter(None, parts))
