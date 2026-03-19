"""Compatibility CLI entry point for doc_to_md."""
from __future__ import annotations

from doc_to_md.apps.conversion.cli import app
from doc_to_md.apps.conversion.logic import (
    ENGINE_REGISTRY,
    ENGINES_REQUIRING_MODEL,
    RunMetrics,
    _format_summary,
    _normalize_engine,
    _resolve_engine,
    _should_process,
)


if __name__ == "__main__":  # pragma: no cover
    app()
