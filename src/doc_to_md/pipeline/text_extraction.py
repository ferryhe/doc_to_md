"""Helpers for extracting plain text from various document types."""
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

try:  # Optional dependency for DOCX parsing
    from docx import Document
except ImportError:  # pragma: no cover - handled in runtime guard
    Document = None  # type: ignore[assignment]

try:  # Optional dependency for image OCR
    from PIL import Image
except ImportError:  # pragma: no cover - handled in runtime guard
    Image = None  # type: ignore[assignment]

try:  # Optional dependency for image OCR
    import pytesseract
except ImportError:  # pragma: no cover - handled in runtime guard
    pytesseract = None  # type: ignore[assignment]


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(path)
    if suffix == ".docx":
        return _extract_docx(path)
    if suffix in {".png", ".jpg", ".jpeg"}:
        return _extract_image(path)
    return path.read_text(encoding="utf-8", errors="ignore")


def _extract_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    parts: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception as exc:  # noqa: BLE001 - best effort
            page_text = f"[Page {index} extraction failed: {exc}]"
        if page_text.strip():
            parts.append(page_text.strip())
    return "\n\n".join(parts)


def _extract_docx(path: Path) -> str:
    if Document is None:  # pragma: no cover - exercised only when dependency missing
        raise RuntimeError(
            "DOCX extraction requires the 'python-docx' package. "
            "Install project dependencies or run `pip install python-docx`."
        )

    try:
        document = Document(str(path))
    except Exception as exc:  # noqa: BLE001 - propagate friendly message
        return f"[DOCX extraction failed: {exc}]"

    blocks: list[str] = []
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            blocks.append(text)

    for table in document.tables:
        rows: list[str] = []
        for row in table.rows:
            cells = [" ".join(cell.text.split()) for cell in row.cells]
            row_text = " | ".join(cell for cell in cells if cell).strip()
            if row_text:
                rows.append(row_text)
        if rows:
            blocks.append("\n".join(rows))

    return "\n\n".join(blocks) or "[No textual content found in DOCX]"


def _extract_image(path: Path) -> str:
    if Image is None or pytesseract is None:  # pragma: no cover - dependency guard
        raise RuntimeError(
            "Image OCR requires Pillow and pytesseract. "
            "Install project dependencies or run `pip install pillow pytesseract`."
        )

    try:
        with Image.open(path) as image:
            grayscale = image.convert("L")  # grayscale improves OCR signal
            text = pytesseract.image_to_string(grayscale)
    except Exception as exc:  # noqa: BLE001 - best effort
        return f"[Image OCR failed: {exc}]"

    return text.strip() or "[No textual content detected in image]"
