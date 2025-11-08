"""CLI entry point for doc-to-markdown conversions."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sys
import time
from typing import Annotated, Dict, Optional, Type, cast

import typer

# Ensure project root (where `config` lives) is importable even when running via src layout.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config.settings import EngineName, Settings, get_settings
from doc_to_md.engines.base import Engine
from doc_to_md.engines.local import LocalEngine
from doc_to_md.engines.mistral import MistralEngine
from doc_to_md.engines.siliconflow import SiliconFlowEngine
from doc_to_md.pipeline.loader import iter_documents
from doc_to_md.pipeline.postprocessor import ConversionResult, enforce_markdown
from doc_to_md.pipeline.writer import write_markdown
from doc_to_md.utils.logging import log_error, log_info

app = typer.Typer(help="Convert documentation sources into Markdown using pluggable engines.")

ENGINE_REGISTRY: Dict[EngineName, Type[Engine]] = {
    "local": LocalEngine,
    "mistral": MistralEngine,
    "siliconflow": SiliconFlowEngine,
}


@dataclass(slots=True)
class RunMetrics:
    total_candidates: int = 0
    skipped_by_since: int = 0
    dry_run: int = 0
    successes: int = 0
    failures: int = 0

    @property
    def eligible(self) -> int:
        return self.total_candidates - self.skipped_by_since


def _resolve_engine(engine: EngineName, model: str | None) -> Engine:
    if engine not in ENGINE_REGISTRY:
        raise typer.BadParameter(f"Unknown engine '{engine}'")
    engine_cls = ENGINE_REGISTRY[engine]
    if engine in {"siliconflow", "mistral"}:
        return engine_cls(model=model)
    return engine_cls()


def _normalize_engine(input_value: Optional[str], default: EngineName) -> EngineName:
    if input_value is None:
        return default
    candidate = input_value.lower()
    if candidate not in ENGINE_REGISTRY:
        raise typer.BadParameter(f"Unknown engine '{input_value}'")
    return cast(EngineName, candidate)


def _should_process(path: Path, since_timestamp: float | None) -> tuple[bool, float | None]:
    """Return whether a document should be processed and provide its mtime."""
    try:
        mtime = path.stat().st_mtime
    except FileNotFoundError:
        return False, None
    if since_timestamp is None:
        return True, mtime
    return mtime >= since_timestamp, mtime


def _format_summary(metrics: RunMetrics, elapsed_seconds: float) -> str:
    return (
        "Summary: "
        f"total={metrics.total_candidates}, "
        f"eligible={metrics.eligible}, "
        f"converted={metrics.successes}, "
        f"failed={metrics.failures}, "
        f"skipped_since={metrics.skipped_by_since}, "
        f"dry_run={metrics.dry_run}, "
        f"duration={elapsed_seconds:.2f}s"
    )


@app.command()
def convert(
    input_path: Annotated[Optional[str], typer.Option("--input-path", help="Directory of input docs; defaults to settings.input_dir")] = None,
    output_path: Annotated[Optional[str], typer.Option("--output-path", help="Where to write Markdown files")] = None,
    engine: Annotated[Optional[str], typer.Option("--engine", "-e", help="Engine name (local, mistral, siliconflow)")] = None,
    model: Annotated[Optional[str], typer.Option("--model", "-m", help="Model override for engines that support it")] = None,
    since: Annotated[
        Optional[datetime],
        typer.Option(
            "--since",
            help="Process only files modified on/after this timestamp (ISO 8601, e.g. 2025-05-01T00:00:00).",
        ),
    ] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="List eligible files without converting or writing output")] = False,
) -> None:
    settings: Settings = get_settings()
    input_dir = Path(input_path) if input_path else settings.input_dir
    output_dir = Path(output_path) if output_path else settings.output_dir
    engine_name = _normalize_engine(engine, settings.default_engine)

    try:
        engine_instance = _resolve_engine(engine_name, model)
    except Exception as exc:  # noqa: BLE001 - bubble Typer friendly errors
        raise typer.Exit(code=1) from exc

    log_info(f"Using engine '{engine_name}' (model: {getattr(engine_instance, 'model', 'n/a')})")

    since_timestamp = since.timestamp() if since else None
    metrics = RunMetrics()
    started_at = time.perf_counter()

    for source_path in iter_documents(input_dir):
        metrics.total_candidates += 1
        should_process, mtime = _should_process(source_path, since_timestamp)
        if not should_process:
            metrics.skipped_by_since += 1
            if since_timestamp is not None:
                stamp = datetime.fromtimestamp(mtime).isoformat() if mtime else "unknown"
                log_info(f"Skipping {source_path} (modified {stamp}) due to --since filter")
            continue

        if dry_run:
            metrics.dry_run += 1
            log_info(f"[dry-run] Would convert {source_path}")
            continue

        log_info(f"Converting {source_path}")
        try:
            engine_response = engine_instance.convert(source_path)
        except Exception as exc:  # noqa: BLE001
            log_error(f"Failed to convert {source_path.name}: {exc}")
            metrics.failures += 1
            continue

        result = ConversionResult(
            source_name=source_path.name,
            markdown=engine_response.markdown,
            engine=engine_instance.name,
            assets=engine_response.assets,
        )
        cleaned = enforce_markdown(result)
        target = write_markdown(cleaned, output_dir)
        log_info(f"Wrote {target}")
        metrics.successes += 1

    elapsed = time.perf_counter() - started_at
    log_info(_format_summary(metrics, elapsed))


@app.command()
def list_engines() -> None:
    """Pretty-print available engines."""
    for name in ENGINE_REGISTRY:
        log_info(name)


if __name__ == "__main__":  # pragma: no cover
    app()
