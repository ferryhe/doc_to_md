"""OCR engine backed by PaddleOCR."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from PIL import Image

from config.settings import get_settings
from .base import Engine, EngineResponse


class PaddleOCREngine(Engine):
    name = "paddleocr"

    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        self.lang = settings.paddleocr_lang
        self.render_dpi = settings.paddleocr_render_dpi
        self.max_pages = settings.paddleocr_max_pages
        self.model = model or f"paddleocr-{self.lang}"
        self._ocr = None

    def _ensure_ocr(self):
        if self._ocr is not None:
            return self._ocr
        try:
            from paddleocr import PaddleOCR  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "PaddleOCR engine requires the `paddleocr` package. "
                "Install it via `pip install paddleocr` before using this engine."
            ) from exc

        self._ocr = PaddleOCR(use_angle_cls=True, lang=self.lang)
        return self._ocr

    def convert(self, path: Path) -> EngineResponse:  # pragma: no cover - heavy dependency
        images = list(self._load_images(path))
        if not images:
            raise RuntimeError(f"PaddleOCR does not support '{path.suffix}' inputs.")

        markdown_parts: list[str] = [f"# {path.stem}"]
        ocr = self._ensure_ocr()

        for index, image in enumerate(images, start=1):
            markdown_parts.append(f"\n## Page {index}\n")
            page_lines = self._run_ocr(ocr, image)
            if not page_lines:
                markdown_parts.append("_No text detected._\n")
            else:
                markdown_parts.extend(page_lines)

        markdown = "\n".join(markdown_parts).strip()
        return EngineResponse(markdown=markdown, model=self.model)

    def _load_images(self, path: Path) -> Iterable[Image.Image]:
        suffix = path.suffix.lower()
        if suffix in {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}:
            yield self._open_image(path)
            return

        if suffix == ".pdf":
            yield from self._render_pdf_pages(path)

    @staticmethod
    def _open_image(path: Path) -> Image.Image:
        with Image.open(path) as image:
            return image.convert("RGB")

    def _render_pdf_pages(self, path: Path) -> Iterable[Image.Image]:
        try:
            import pypdfium2 as pdfium  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "PDF support for PaddleOCR requires `pypdfium2`. "
                "Install it via `pip install pypdfium2`."
            ) from exc

        pdf = pdfium.PdfDocument(str(path))
        try:
            total_pages = len(pdf)
            limit = min(total_pages, self.max_pages or total_pages)
            scale = self.render_dpi / 72.0
            for page_index in range(limit):
                page = pdf[page_index]
                bitmap = page.render(scale=scale)
                try:
                    yield bitmap.to_pil()
                finally:
                    bitmap.close()
        finally:
            pdf.close()

    @staticmethod
    def _run_ocr(ocr, image: Image.Image) -> List[str]:
        import numpy as np

        data = np.array(image)
        results = ocr.ocr(data, cls=True)
        lines: list[str] = []
        normalized = results
        if normalized and isinstance(normalized[0], tuple):
            normalized = [normalized]

        for page_result in normalized or []:
            for block in page_result:
                if not isinstance(block, (list, tuple)) or len(block) < 2:
                    continue
                text_meta = block[1]
                if not isinstance(text_meta, (list, tuple)) or len(text_meta) < 2:
                    continue
                text = str(text_meta[0]).strip()
                if not text:
                    continue
                confidence = float(text_meta[1])
                lines.append(f"- {text} _(conf {confidence:.2f})_")
        return lines
