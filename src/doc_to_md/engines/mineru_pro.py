"""Engine adapter for the MinerU2.5-Pro vision-language model."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable

from PIL import Image

from doc_to_md.config.settings import get_settings
from .base import Engine, EngineResponse


class MinerUProEngine(Engine):
    name = "mineru_pro"

    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        self.model_name = model or settings.mineru_pro_model
        self.backend = settings.mineru_pro_backend
        self.server_url = settings.mineru_pro_server_url
        self.render_dpi = settings.mineru_pro_render_dpi
        self.max_pages = settings.mineru_pro_max_pages
        self.image_analysis = settings.mineru_pro_image_analysis
        self.model = f"{self.backend}:{self.model_name}"
        self._runtime: tuple[Any, Callable[[Any], str]] | None = None

    def _ensure_runtime(self) -> tuple[Any, Callable[[Any], str]]:
        if self._runtime is not None:
            return self._runtime
        if self.backend == "http-client" and not self.server_url:
            raise RuntimeError(
                "MinerU2.5-Pro http-client mode requires MINERU_PRO_SERVER_URL "
                "pointing at a running OpenAI-compatible MinerU2.5-Pro service."
            )
        try:
            from mineru_vl_utils import MinerUClient  # type: ignore
            from mineru_vl_utils.post_process import json2md  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "MinerU2.5-Pro requires `mineru-vl-utils`. "
                "Install it with `pip install -e \".[mineru-pro]\"` before using this engine."
            ) from exc

        client = MinerUClient(
            backend=self.backend,
            model_name=self.model_name,
            model_path=self.model_name,
            server_url=self.server_url,
            image_analysis=self.image_analysis,
        )
        self._runtime = (client, json2md)
        return self._runtime

    def convert(self, path: Path) -> EngineResponse:  # pragma: no cover - heavy dependency
        client, json2md = self._ensure_runtime()
        markdown_parts: list[str] = []
        is_pdf = path.suffix.lower() == ".pdf"

        for page_number, image in enumerate(self._iter_images(path), start=1):
            try:
                extracted_blocks = client.two_step_extract(image)
                page_markdown = str(json2md(extracted_blocks)).strip()
            finally:
                image.close()

            if not page_markdown:
                continue
            if is_pdf:
                markdown_parts.append(f"## Page {page_number}\n\n{page_markdown}")
            else:
                markdown_parts.append(page_markdown)

        markdown = "\n\n".join(markdown_parts).strip()
        if not markdown:
            raise RuntimeError("MinerU2.5-Pro did not produce Markdown content.")
        return EngineResponse(markdown=markdown, model=self.model)

    def _iter_images(self, path: Path) -> Iterable[Image.Image]:
        suffix = path.suffix.lower()
        if suffix in {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}:
            with Image.open(path) as image:
                yield image.convert("RGB")
            return

        if suffix == ".pdf":
            yield from self._render_pdf_pages(path)
            return

        raise RuntimeError(f"MinerU2.5-Pro does not support '{path.suffix}' inputs.")

    def _render_pdf_pages(self, path: Path) -> Iterable[Image.Image]:
        try:
            import pypdfium2 as pdfium  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "PDF support for MinerU2.5-Pro requires `pypdfium2`. "
                "Install it with `pip install -e \".[mineru-pro]\"`."
            ) from exc

        pdf = pdfium.PdfDocument(str(path))
        try:
            total_pages = len(pdf)
            page_limit = min(total_pages, self.max_pages or total_pages)
            scale = self.render_dpi / 72.0
            for page_index in range(page_limit):
                page = pdf[page_index]
                bitmap = page.render(scale=scale)
                try:
                    yield bitmap.to_pil().convert("RGB")
                finally:
                    bitmap.close()
        finally:
            pdf.close()
