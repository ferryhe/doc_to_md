from pathlib import Path
from types import SimpleNamespace

import benchmark


FIXTURE_PDF = Path(__file__).parent / "fixtures" / "real_smoke.pdf"


def test_benchmark_local_engine_records_quality_and_trace(tmp_path: Path) -> None:
    runner = benchmark.EngineBenchmark([("local", None)])

    result = runner.run_benchmark(FIXTURE_PDF, tmp_path)

    assert len(result.results) == 1
    item = result.results[0]
    assert item.success is True
    assert item.engine_name == "local"
    assert item.quality_status == "good"
    assert item.formula_status == "not_applicable"
    assert item.diagnostic_codes == []
    assert item.trace is not None
    assert item.trace["formula_ocr_enabled"] is False
    assert item.trace["formula_ocr_attempted"] is False
    assert item.markdown_path is not None
    assert (tmp_path / item.markdown_path).exists()


def test_benchmark_report_mentions_agent_readiness_fields(tmp_path: Path) -> None:
    runner = benchmark.EngineBenchmark([("local", None)])
    result = runner.run_benchmark(FIXTURE_PDF, tmp_path)

    report = benchmark.MarkdownReportGenerator(result).generate_markdown_report()

    assert "## Agent-readiness findings" in report
    assert "| Engine | Model | Status | Time | Markdown chars | Assets | Quality | Formula | Diagnostics | Artifact |" in report
    assert "Fastest engine with acceptable formula judgment" in report
    assert "- Overall quality: `good`" in report
    assert "- Formula quality: `not_applicable`" in report


def test_benchmark_report_mentions_reference_formula_alignment() -> None:
    result = benchmark.BenchmarkResult(
        timestamp="2026-04-03T00:00:00+00:00",
        test_file="sample.pdf",
        file_size_bytes=2048,
        reference_markdown="reviewed.md",
        results=[
            benchmark.EngineResult(
                engine_name="mistral",
                model="mistral-ocr-latest",
                success=True,
                conversion_time=1.2,
                markdown_length=120,
                num_assets=0,
                quality_status="review",
                formula_status="review",
                reference_formula_status="review",
                reference_formula_recall=0.9,
                reference_formula_similarity=0.88,
                reference_formula_diagnostics=["reference_formula_fragmented_tokens"],
            )
        ],
    )

    report = benchmark.MarkdownReportGenerator(result).generate_markdown_report()

    assert "Reference Markdown: `reviewed.md`" in report
    assert "Strongest reference-aligned formula output" in report
    assert "Reference formula alignment: `review` (recall=90%, similarity=88%)" in report
    assert "Reference diagnostics: `reference_formula_fragmented_tokens`" in report


def test_resolve_engines_preferred_pdf_profile_uses_opendataloader_and_mistral() -> None:
    selected = benchmark.resolve_engines(None, profile="preferred-pdf")

    assert selected is not None
    assert [engine for engine, _ in selected] == ["opendataloader", "mistral"]


def test_default_benchmark_engines_include_mathpix(monkeypatch) -> None:
    monkeypatch.setattr(
        benchmark,
        "get_settings",
        lambda: SimpleNamespace(
            mistral_default_model="mistral-ocr-latest",
            siliconflow_default_model="deepseek-ai/DeepSeek-OCR",
            mathpix_default_model="mathpix-pdf",
        ),
    )

    runner = benchmark.EngineBenchmark()

    assert ("mathpix", "mathpix-pdf") in runner.engines_to_test


def test_resolve_engines_formula_pdf_profile_includes_mathpix(monkeypatch) -> None:
    monkeypatch.setattr(
        benchmark,
        "get_settings",
        lambda: SimpleNamespace(
            mistral_default_model="mistral-ocr-latest",
            siliconflow_default_model="deepseek-ai/DeepSeek-OCR",
            mathpix_default_model="mathpix-pdf",
        ),
    )

    selected = benchmark.resolve_engines(None, profile="formula-pdf")

    assert selected is not None
    assert selected == [
        ("opendataloader", None),
        ("mistral", "mistral-ocr-latest"),
        ("mathpix", "mathpix-pdf"),
    ]
