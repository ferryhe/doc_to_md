"""Implementation of the Mistral OCR API using the official SDK."""
from __future__ import annotations

from pathlib import Path
from typing import List

from mistralai import Mistral
from mistralai.models.file import File
from mistralai.models.filechunk import FileChunk
from mistralai.models.ocrimageobject import OCRImageObject
from mistralai.models.ocrpageobject import OCRPageObject
from mistralai.models.ocrresponse import OCRResponse

from config.settings import get_settings
from .base import Engine, EngineResponse


class MistralEngine(Engine):
    name = "mistral"

    def __init__(self, model: str | None = None, include_images: bool = False) -> None:
        settings = get_settings()
        if not settings.minstral_api_key:
            raise RuntimeError("MINSTRAL_API_KEY missing")
        self.api_key = settings.minstral_api_key
        self.model = model or settings.mistral_default_model
        self.include_images = include_images
        self.client = Mistral(api_key=self.api_key)

    def convert(self, path: Path) -> EngineResponse:  # pragma: no cover - network call
        upload = self.client.files.upload(
            file=File(file_name=path.name, content=path.read_bytes()),
            purpose="ocr",
        )

        try:
            response = self.client.ocr.process(
                model=self.model,
                document=FileChunk(file_id=upload.id),
                include_image_base64=self.include_images,
            )
        finally:
            # Clean up uploaded file to avoid cluttering the user's account.
            try:
                self.client.files.delete(file_id=upload.id)
            except Exception:
                pass

        markdown = self._render_markdown(path.stem, response)
        return EngineResponse(markdown=markdown, model=response.model)

    def _render_markdown(self, title: str, response: OCRResponse) -> str:
        sections: List[str] = [f"# {title}", ""]
        pages = sorted(response.pages, key=lambda page: page.index)

        for page in pages:
            sections.append(f"## Page {page.index + 1}")
            sections.append(page.markdown.strip() or "_No text extracted on this page._")

            image_snippets = self._render_images(page.images, page.index)
            if image_snippets:
                sections.extend(image_snippets)

            sections.append("")  # blank line between pages

        return "\n".join(sections).strip()

    def _render_images(self, images: List[OCRImageObject], page_index: int) -> List[str]:
        if not self.include_images or not images:
            return []

        snippets: List[str] = []
        for idx, image in enumerate(images, start=1):
            if not image.image_base64:
                continue
            alt = f"Page {page_index + 1} Image {idx}"
            snippets.append(f"![{alt}](data:image/png;base64,{image.image_base64})")
        return snippets
