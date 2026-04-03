import base64
from pathlib import Path

import doc_to_md.apps.conversion.logic as conversion_logic
import pytest

from doc_to_md.apps.conversion.logic import convert_inline_document, list_engine_names, run_conversion
from doc_to_md.pipeline.postprocessor import ConversionResult, PostprocessOutcome, PostprocessTrace
from doc_to_md.quality import evaluate_markdown_quality


def test_list_engine_names_contains_core_engines() -> None:
    engines = list_engine_names()
    assert "local" in engines
    assert "mistral" in engines
    assert "markitdown" in engines


def test_run_conversion_dry_run(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    (input_dir / "sample.txt").write_text("hello", encoding="utf-8")

    summary = run_conversion(
        input_path=input_dir,
        output_path=output_dir,
        engine="local",
        dry_run=True,
    )

    assert summary.metrics.total_candidates == 1
    assert summary.metrics.dry_run == 1
    assert summary.metrics.successes == 0
    assert summary.results[0].status == "dry_run"


def test_run_conversion_local_writes_markdown(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    (input_dir / "sample.txt").write_text("hello markdown", encoding="utf-8")

    summary = run_conversion(
        input_path=input_dir,
        output_path=output_dir,
        engine="local",
    )

    assert summary.metrics.successes == 1
    assert summary.results[0].output_path is not None
    assert summary.results[0].output_path.exists()
    assert summary.results[0].quality is not None
    assert summary.results[0].quality.status == "good"
    assert summary.results[0].quality.formula_status == "not_applicable"
    assert summary.results[0].trace is not None
    assert summary.results[0].trace.postprocess_changed is False


def test_convert_inline_document_returns_markdown_and_quality() -> None:
    encoded = base64.b64encode(b"hello inline world").decode("ascii")

    result = convert_inline_document(
        source_name="sample.txt",
        content_base64=encoded,
        engine="local",
    )

    assert result.source_name == "sample.txt"
    assert "# sample" in result.markdown
    assert "hello inline world" in result.markdown
    assert result.quality.status == "good"
    assert result.quality.formula_status == "not_applicable"
    assert result.trace is not None
    assert result.trace.formula_ocr_enabled is False


def test_convert_inline_document_rejects_invalid_base64() -> None:
    with pytest.raises(ValueError, match="valid base64"):
        convert_inline_document(
            source_name="sample.txt",
            content_base64="not-base64",
            engine="local",
        )


def test_run_conversion_applies_formula_ocr_request_overrides(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    (input_dir / "sample.txt").write_text("hello markdown", encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_postprocess(result: ConversionResult, *, settings=None) -> PostprocessOutcome:
        assert settings is not None
        captured["formula_ocr_enabled"] = settings.formula_ocr_enabled
        captured["formula_ocr_provider"] = settings.formula_ocr_provider
        quality = evaluate_markdown_quality(result.markdown)
        return PostprocessOutcome(
            result=result,
            quality=quality,
            trace=PostprocessTrace(
                math_normalization_changed=False,
                formula_ocr_enabled=settings.formula_ocr_enabled,
                formula_ocr_provider=settings.formula_ocr_provider if settings.formula_ocr_enabled else None,
                formula_ocr_attempted=False,
                formula_ocr_applied=False,
                formula_image_references_before=0,
                formula_image_references_after=0,
                asset_count_before=len(result.assets),
                asset_count_after=len(result.assets),
                postprocess_changed=False,
            ),
        )

    monkeypatch.setattr(conversion_logic, "postprocess_conversion_result", fake_postprocess)

    run_conversion(
        input_path=input_dir,
        output_path=output_dir,
        engine="local",
        formula_ocr_enabled=True,
        formula_ocr_provider="deepseekocr",
    )

    assert captured == {
        "formula_ocr_enabled": True,
        "formula_ocr_provider": "deepseekocr",
    }
