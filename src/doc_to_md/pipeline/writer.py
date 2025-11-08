"""Write conversion outputs to disk."""
from __future__ import annotations

from pathlib import Path

from .postprocessor import ConversionResult


def write_markdown(result: ConversionResult, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"{Path(result.source_name).stem}.md"
    target.write_text(result.markdown, encoding="utf-8")
    return target
