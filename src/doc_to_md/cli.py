"""CLI entry point for doc-to-markdown conversions."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Type

import typer

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


def _resolve_engine(engine: EngineName, model: str | None) -> Engine:
    if engine not in ENGINE_REGISTRY:
        raise typer.BadParameter(f"Unknown engine '{engine}'")
    engine_cls = ENGINE_REGISTRY[engine]
    if engine == "siliconflow":
        return engine_cls(model=model)
    return engine_cls()


@app.command()
def convert(
    input_path: Path = typer.Option(None, help="Directory of input docs; defaults to settings.input_dir"),
    output_path: Path = typer.Option(None, help="Where to write Markdown files"),
    engine: EngineName = typer.Option(None, help="Engine name (local, mistral, siliconflow)"),
    model: str | None = typer.Option(None, help="Model override for engines that support it"),
) -> None:
    settings: Settings = get_settings()
    input_dir = input_path or settings.input_dir
    output_dir = output_path or settings.output_dir
    engine_name = engine or settings.default_engine

    try:
        engine_instance = _resolve_engine(engine_name, model)
    except Exception as exc:  # noqa: BLE001 - bubble Typer friendly errors
        raise typer.Exit(code=1) from exc

    log_info(f"Using engine '{engine_name}' (model: {getattr(engine_instance, 'model', 'n/a')})")

    for source_path in iter_documents(input_dir):
        log_info(f"Converting {source_path}")
        try:
            engine_response = engine_instance.convert(source_path)
        except Exception as exc:  # noqa: BLE001
            log_error(f"Failed to convert {source_path.name}: {exc}")
            continue

        result = ConversionResult(
            source_name=source_path.name,
            markdown=engine_response.markdown,
            engine=engine_instance.name,
        )
        cleaned = enforce_markdown(result)
        target = write_markdown(cleaned, output_dir)
        log_info(f"Wrote {target}")


@app.command()
def list_engines() -> None:
    """Pretty-print available engines."""
    for name in ENGINE_REGISTRY:
        log_info(name)


if __name__ == "__main__":  # pragma: no cover
    app()
