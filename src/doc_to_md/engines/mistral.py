"""Implementation of the Mistral OCR API using the official SDK."""
from __future__ import annotations

import base64
import imghdr
import re
from pathlib import Path
from typing import List, Tuple

from mistralai import Mistral
from mistralai.models.file import File
from mistralai.models.filechunk import FileChunk
from mistralai.models.ocrimageobject import OCRImageObject
from mistralai.models.ocrpageobject import OCRPageObject
from mistralai.models.ocrresponse import OCRResponse

from config.settings import get_settings
from .base import Engine, EngineAsset, EngineResponse


class MistralEngine(Engine):
    name = "mistral"

    def __init__(self, model: str | None = None, include_images: bool = True, **kwargs) -> None:
        settings = get_settings()
        if not settings.mistral_api_key:
            raise RuntimeError("MISTRAL_API_KEY missing")
        self.api_key = settings.mistral_api_key
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

        markdown, assets = self._render_markdown_and_assets(path.stem, response)
        return EngineResponse(markdown=markdown, model=response.model, assets=assets)

    def _render_markdown_and_assets(self, title: str, response: OCRResponse) -> Tuple[str, List[EngineAsset]]:
        sections: List[str] = [f"# {title}", ""]
        pages = sorted(response.pages, key=lambda page: page.index)
        assets: List[EngineAsset] = []
        normalized_stem = self._normalize_stem(title)

        for page in pages:
            sections.append(f"## Page {page.index + 1}")
            cleaned_page = self._strip_placeholder_images(page.markdown)
            sections.append(cleaned_page or "_No text extracted on this page._")

            image_snippets, page_assets = self._render_images(normalized_stem, page.images, page.index)
            if image_snippets:
                sections.extend(image_snippets)
            assets.extend(page_assets)

            sections.append("")  # blank line between pages

        return "\n".join(sections).strip(), assets

    def _render_images(
        self,
        normalized_stem: str,
        images: List[OCRImageObject],
        page_index: int,
    ) -> Tuple[List[str], List[EngineAsset]]:
        if not self.include_images or not images:
            return [], []

        snippets: List[str] = []
        assets: List[EngineAsset] = []
        assets_subdir = f"{normalized_stem}_assets"
        for idx, image in enumerate(images, start=1):
            if not image.image_base64:
                continue
            binary, extension = self._decode_image(image.image_base64)
            filename = f"{normalized_stem}_p{page_index + 1:02d}_img{idx}.{extension}"
            assets.append(EngineAsset(filename=filename, data=binary, subdir=assets_subdir))

            alt = f"Page {page_index + 1} Image {idx}"
            snippets.append(f"![{alt}]({assets_subdir}/{filename})")
        return snippets, assets

    @staticmethod
    def _normalize_stem(stem: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("_") or "document"

    @staticmethod
    def _resolve_extension(binary: bytes) -> str:
        detected = imghdr.what(None, h=binary)
        if detected == "jpeg":
            return "jpg"
        if detected:
            return detected
        return "bin"

    @staticmethod
    def _strip_placeholder_images(markdown: str) -> str:
        lines = []
        for line in (markdown or "").splitlines():
            if "](img-" in line:
                continue
            lines.append(line)
        return "\n".join(lines).strip()

    def _decode_image(self, payload: str) -> Tuple[bytes, str]:
        data_str = payload
        mime: str | None = None
        if payload.startswith("data:"):
            header, _, rest = payload.partition(",")
            data_str = rest
            if ";" in header:
                mime = header.split(";", 1)[0][5:]
            else:
                mime = header[5:]
        binary = base64.b64decode(data_str)
        extension = self._extension_from_mime(mime) or self._resolve_extension(binary)
        return binary, extension

    @staticmethod
    def _extension_from_mime(mime: str | None) -> str | None:
        if not mime:
            return None
        mapping = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
        }
        return mapping.get(mime.lower())
