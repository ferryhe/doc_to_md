"""Utilities for loading documents from disk."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable


def iter_documents(input_dir: Path) -> Iterable[Path]:
    """Yield supported documents under ``input_dir`` recursively."""
    supported_suffixes = {".pdf", ".png", ".jpg", ".jpeg", ".txt", ".md", ".docx"}
    for path in input_dir.rglob("*"):
        if path.suffix.lower() in supported_suffixes and path.is_file():
            yield path
