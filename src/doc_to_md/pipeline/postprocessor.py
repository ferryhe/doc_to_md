"""Post-processing helpers after engine response."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ConversionResult:
    source_name: str
    markdown: str
    engine: str


def enforce_markdown(result: ConversionResult) -> ConversionResult:
    """Placeholder hook to normalize Markdown (e.g., strip trailing spaces)."""
    cleaned = result.markdown.strip()
    return ConversionResult(source_name=result.source_name, markdown=cleaned, engine=result.engine)
