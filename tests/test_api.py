import base64
import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from doc_to_md.api import app
from doc_to_md.apps.conversion.logic import (
    ConversionRun,
    DocumentResult,
    EngineReadinessCheck,
    InlineConversionResult,
    PreferredEngineReadiness,
    RunMetrics,
)
from doc_to_md.engines.base import EngineAsset
from doc_to_md.apps.conversion import router as conversion_router
from doc_to_md.pipeline.postprocessor import PostprocessTrace
from doc_to_md.quality import MarkdownDiagnostic, MarkdownQualityReport


client = TestClient(app)


def test_api_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_conversion_engines_endpoint() -> None:
    response = client.get("/apps/conversion/engines")
    assert response.status_code == 200
    payload = response.json()
    assert "engines" in payload
    assert "local" in payload["engines"]


def test_engine_readiness_endpoint_returns_preferred_engines(monkeypatch) -> None:
    monkeypatch.setattr(
        conversion_router,
        "list_preferred_engine_readiness",
        lambda: [
            PreferredEngineReadiness(
                engine="opendataloader",
                preferred_rank=1,
                available=False,
                summary="Blocked: Java 11+ missing on PATH.",
                checks=[
                    EngineReadinessCheck(
                        name="java_runtime",
                        ready=False,
                        message="Java 11+ missing on PATH.",
                    )
                ],
            ),
            PreferredEngineReadiness(
                engine="mistral",
                preferred_rank=2,
                available=True,
                summary="Ready for managed OCR through the Mistral API.",
                checks=[
                    EngineReadinessCheck(
                        name="api_key",
                        ready=True,
                        message="Mistral client initialized from the configured API key.",
                    )
                ],
            ),
        ],
    )

    response = client.get("/apps/conversion/engine-readiness")

    assert response.status_code == 200
    payload = response.json()
    assert payload["profile"] == "preferred_pdf"
    assert [item["engine"] for item in payload["engines"]] == ["opendataloader", "mistral"]
    assert payload["engines"][0]["available"] is False
    assert payload["engines"][1]["available"] is True


def test_conversion_endpoint_forwards_no_page_info(monkeypatch, tmp_path) -> None:
    captured: dict[str, object] = {}

    def fake_run_conversion(**kwargs):
        captured.update(kwargs)
        return ConversionRun(
            engine="mistral",
            model="mistral-ocr-latest",
            input_dir=tmp_path / "input",
            output_dir=tmp_path / "output",
            metrics=RunMetrics(),
            duration_seconds=0.01,
            results=[],
        )

    monkeypatch.setattr(conversion_router, "run_conversion", fake_run_conversion)

    response = client.post(
        "/apps/conversion/convert",
        json={
            "input_path": str(tmp_path / "input"),
            "output_path": str(tmp_path / "output"),
            "engine": "mistral",
            "no_page_info": True,
            "dry_run": True,
            "formula_ocr_enabled": True,
            "formula_ocr_provider": "mistral",
        },
    )

    assert response.status_code == 200
    assert captured["no_page_info"] is True
    assert captured["formula_ocr_enabled"] is True
    assert captured["formula_ocr_provider"] == "mistral"


def test_conversion_endpoint_includes_quality_payload(monkeypatch, tmp_path) -> None:
    def fake_run_conversion(**kwargs):
        del kwargs
        return ConversionRun(
            engine="opendataloader",
            model=None,
            input_dir=tmp_path / "input",
            output_dir=tmp_path / "output",
            metrics=RunMetrics(total_candidates=1, successes=1),
            duration_seconds=0.02,
            results=[
                DocumentResult(
                    source_path=tmp_path / "input" / "sample.pdf",
                    status="converted",
                    output_path=tmp_path / "output" / "sample.md",
                    quality=MarkdownQualityReport(
                        status="review",
                        formula_status="poor",
                        headings=1,
                        bullet_lines=0,
                        table_lines=0,
                        image_references=1,
                        formula_image_references=1,
                        inline_math_segments=0,
                        block_math_segments=0,
                        diagnostics=[
                            MarkdownDiagnostic(
                                code="formula_image_reference",
                                severity="error",
                                message="Potential formula images remain in the Markdown output.",
                                count=1,
                            )
                        ],
                    ),
                    trace=PostprocessTrace(
                        math_normalization_changed=True,
                        formula_ocr_enabled=True,
                        formula_ocr_provider="mistral",
                        formula_ocr_attempted=True,
                        formula_ocr_applied=False,
                        formula_image_references_before=1,
                        formula_image_references_after=1,
                        asset_count_before=1,
                        asset_count_after=1,
                        postprocess_changed=True,
                    ),
                )
            ],
        )

    monkeypatch.setattr(conversion_router, "run_conversion", fake_run_conversion)

    response = client.post("/apps/conversion/convert", json={})

    assert response.status_code == 200
    payload = response.json()
    assert payload["results"][0]["quality"]["formula_status"] == "poor"
    assert payload["results"][0]["quality"]["diagnostics"][0]["code"] == "formula_image_reference"
    assert payload["results"][0]["trace"]["formula_ocr_attempted"] is True


def test_conversion_endpoint_hides_internal_errors(monkeypatch) -> None:
    def fake_run_conversion(**kwargs):
        del kwargs
        raise RuntimeError("secret stack detail")

    monkeypatch.setattr(conversion_router, "run_conversion", fake_run_conversion)

    response = client.post("/apps/conversion/convert", json={})

    assert response.status_code == 500
    assert response.json() == {"detail": "Batch conversion failed."}


def test_inline_conversion_endpoint_returns_markdown(monkeypatch) -> None:
    def fake_convert_inline_document(**kwargs):
        assert kwargs["source_name"] == "sample.txt"
        assert kwargs["no_page_info"] is True
        assert kwargs["formula_ocr_enabled"] is True
        assert kwargs["formula_ocr_provider"] == "deepseekocr"
        return InlineConversionResult(
            source_name="sample.txt",
            engine="local",
            model="local-text-wrapper",
            markdown="# sample\n\nhello\n",
            quality=MarkdownQualityReport(
                status="good",
                formula_status="not_applicable",
                headings=1,
                bullet_lines=0,
                table_lines=0,
                image_references=0,
                formula_image_references=0,
                inline_math_segments=0,
                block_math_segments=0,
                diagnostics=[],
            ),
            duration_seconds=0.01,
            assets=[],
            trace=PostprocessTrace(
                math_normalization_changed=False,
                formula_ocr_enabled=True,
                formula_ocr_provider="deepseekocr",
                formula_ocr_attempted=False,
                formula_ocr_applied=False,
                formula_image_references_before=0,
                formula_image_references_after=0,
                asset_count_before=0,
                asset_count_after=0,
                postprocess_changed=False,
            ),
        )

    monkeypatch.setattr(conversion_router, "convert_inline_document", fake_convert_inline_document)

    response = client.post(
        "/apps/conversion/convert-inline",
        json={
            "source_name": "sample.txt",
            "content_base64": base64.b64encode(b"hello").decode("ascii"),
            "engine": "local",
            "no_page_info": True,
            "formula_ocr_enabled": True,
            "formula_ocr_provider": "deepseekocr",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "converted"
    assert payload["markdown"] == "# sample\n\nhello\n"
    assert payload["quality"]["status"] == "good"
    assert payload["asset_count"] == 0
    assert payload["trace"]["formula_ocr_provider"] == "deepseekocr"


def test_inline_conversion_endpoint_can_include_assets(monkeypatch) -> None:
    def fake_convert_inline_document(**kwargs):
        del kwargs
        return InlineConversionResult(
            source_name="sample.pdf",
            engine="mistral",
            model="mistral-ocr-latest",
            markdown="![img](assets/a.png)",
            quality=MarkdownQualityReport(
                status="review",
                formula_status="review",
                headings=0,
                bullet_lines=0,
                table_lines=0,
                image_references=1,
                formula_image_references=0,
                inline_math_segments=0,
                block_math_segments=0,
                diagnostics=[],
            ),
            duration_seconds=0.02,
            assets=[EngineAsset(filename="a.png", data=b"png-bytes", subdir="assets")],
            trace=PostprocessTrace(
                math_normalization_changed=False,
                formula_ocr_enabled=False,
                formula_ocr_provider=None,
                formula_ocr_attempted=False,
                formula_ocr_applied=False,
                formula_image_references_before=0,
                formula_image_references_after=0,
                asset_count_before=1,
                asset_count_after=1,
                postprocess_changed=False,
            ),
        )

    monkeypatch.setattr(conversion_router, "convert_inline_document", fake_convert_inline_document)

    response = client.post(
        "/apps/conversion/convert-inline",
        json={
            "source_name": "sample.pdf",
            "content_base64": base64.b64encode(b"%PDF-1.4").decode("ascii"),
            "include_assets": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["asset_count"] == 1
    assert payload["assets"][0]["filename"] == "a.png"
    assert payload["assets"][0]["content_base64"] == base64.b64encode(b"png-bytes").decode("ascii")


def test_inline_conversion_endpoint_rejects_invalid_base64() -> None:
    response = client.post(
        "/apps/conversion/convert-inline",
        json={
            "source_name": "sample.txt",
            "content_base64": "not-base64",
        },
    )

    assert response.status_code == 400
    assert "valid base64" in response.json()["detail"]


def test_inline_conversion_endpoint_hides_internal_errors(monkeypatch) -> None:
    def fake_convert_inline_document(**kwargs):
        del kwargs
        raise RuntimeError("secret stack detail")

    monkeypatch.setattr(conversion_router, "convert_inline_document", fake_convert_inline_document)

    response = client.post(
        "/apps/conversion/convert-inline",
        json={
            "source_name": "sample.txt",
            "content_base64": base64.b64encode(b"hello").decode("ascii"),
        },
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Inline conversion failed."}


def test_inline_conversion_endpoint_accepts_multipart_upload(monkeypatch) -> None:
    def fake_convert_inline_document(**kwargs):
        assert kwargs["source_name"] == "uploaded.txt"
        assert kwargs["engine"] == "local"
        assert kwargs["formula_ocr_enabled"] is True
        assert kwargs["formula_ocr_provider"] == "mistral"
        return InlineConversionResult(
            source_name="uploaded.txt",
            engine="local",
            model="local-text-wrapper",
            markdown="# uploaded\n\nhello multipart\n",
            quality=MarkdownQualityReport(
                status="good",
                formula_status="not_applicable",
                headings=1,
                bullet_lines=0,
                table_lines=0,
                image_references=0,
                formula_image_references=0,
                inline_math_segments=0,
                block_math_segments=0,
                diagnostics=[],
            ),
            duration_seconds=0.01,
            assets=[],
            trace=PostprocessTrace(
                math_normalization_changed=False,
                formula_ocr_enabled=True,
                formula_ocr_provider="mistral",
                formula_ocr_attempted=False,
                formula_ocr_applied=False,
                formula_image_references_before=0,
                formula_image_references_after=0,
                asset_count_before=0,
                asset_count_after=0,
                postprocess_changed=False,
            ),
        )

    monkeypatch.setattr(conversion_router, "convert_inline_document", fake_convert_inline_document)

    response = client.post(
        "/apps/conversion/convert-inline",
        data={
            "engine": "local",
            "formula_ocr_enabled": "true",
            "formula_ocr_provider": "mistral",
        },
        files={"file": ("uploaded.txt", b"hello multipart", "text/plain")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source_name"] == "uploaded.txt"
    assert payload["markdown"] == "# uploaded\n\nhello multipart\n"
    assert payload["trace"]["formula_ocr_provider"] == "mistral"


def test_inline_conversion_endpoint_rejects_invalid_multipart_boolean() -> None:
    response = client.post(
        "/apps/conversion/convert-inline",
        data={"formula_ocr_enabled": "maybe"},
        files={"file": ("uploaded.txt", b"hello multipart", "text/plain")},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "formula_ocr_enabled"]
