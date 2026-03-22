"""Engine adapter for the OpenDataLoader PDF parser."""
from __future__ import annotations

import tempfile
from pathlib import Path

from config.settings import get_settings
from .base import Engine, EngineAsset, EngineResponse


class OpenDataLoaderEngine(Engine):
    """Convert PDF files to Markdown using the opendataloader-pdf library.

    This engine wraps the ``opendataloader-pdf`` Python package, which uses a
    Java-based layout analysis pipeline and an optional AI hybrid backend for
    complex pages (tables, scanned documents, formulas).

    .. note::
        Java 11+ must be available on the system ``PATH``.
        Each :meth:`convert` call spawns a JVM subprocess, so it is slower for
        repeated single-file calls than bulk processing.
    """

    name = "opendataloader"

    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        self._hybrid: str | None = settings.opendataloader_hybrid
        self._use_struct_tree: bool = settings.opendataloader_use_struct_tree
        self.model = model or (f"opendataloader-hybrid:{self._hybrid}" if self._hybrid else "opendataloader")

    def _ensure_package(self) -> None:
        try:
            import opendataloader_pdf  # noqa: F401
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "OpenDataLoader engine requires the `opendataloader-pdf` package and Java 11+. "
                "Install it via `pip install opendataloader-pdf` before using this engine."
            ) from exc

    def convert(self, path: Path) -> EngineResponse:  # pragma: no cover - heavy dependency
        self._ensure_package()
        import opendataloader_pdf

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                f"OpenDataLoader engine only supports PDF files; got '{path.suffix}'."
            )

        with tempfile.TemporaryDirectory(prefix="opendataloader_") as temp_dir:
            convert_kwargs: dict = {
                # The library's API accepts a list of paths (for batch processing);
                # wrap the single file path accordingly.
                "input_path": [str(path)],
                "output_dir": temp_dir,
                "format": "markdown",
            }
            if self._hybrid:
                convert_kwargs["hybrid"] = self._hybrid
            if self._use_struct_tree:
                convert_kwargs["use_struct_tree"] = True

            opendataloader_pdf.convert(**convert_kwargs)

            # The library writes <stem>.md (and optionally image assets) under output_dir.
            md_files = list(Path(temp_dir).rglob("*.md"))
            if not md_files:
                raise RuntimeError("OpenDataLoader did not produce a Markdown file.")
            markdown = md_files[0].read_text(encoding="utf-8")

            assets: list[EngineAsset] = []
            for img_path in Path(temp_dir).rglob("*"):
                if img_path.is_file() and img_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
                    assets.append(
                        EngineAsset(
                            filename=img_path.name,
                            data=img_path.read_bytes(),
                            subdir="images",
                        )
                    )

        return EngineResponse(markdown=markdown, model=self.model, assets=assets)
