from pathlib import Path

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
