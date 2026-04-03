import base64
import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from doc_to_md.api import app
from doc_to_md.apps.conversion.logic import ConversionRun, DocumentResult, InlineConversionResult, RunMetrics
from doc_to_md.engines.base import EngineAsset
from doc_to_md.apps.conversion import router as conversion_router
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
        },
    )

    assert response.status_code == 200
    assert captured["no_page_info"] is True


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
                )
            ],
        )

    monkeypatch.setattr(conversion_router, "run_conversion", fake_run_conversion)

    response = client.post("/apps/conversion/convert", json={})

    assert response.status_code == 200
    payload = response.json()
    assert payload["results"][0]["quality"]["formula_status"] == "poor"
    assert payload["results"][0]["quality"]["diagnostics"][0]["code"] == "formula_image_reference"


def test_inline_conversion_endpoint_returns_markdown(monkeypatch) -> None:
    def fake_convert_inline_document(**kwargs):
        assert kwargs["source_name"] == "sample.txt"
        assert kwargs["no_page_info"] is True
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
        )

    monkeypatch.setattr(conversion_router, "convert_inline_document", fake_convert_inline_document)

    response = client.post(
        "/apps/conversion/convert-inline",
        json={
            "source_name": "sample.txt",
            "content_base64": base64.b64encode(b"hello").decode("ascii"),
            "engine": "local",
            "no_page_info": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "converted"
    assert payload["markdown"] == "# sample\n\nhello\n"
    assert payload["quality"]["status"] == "good"
    assert payload["asset_count"] == 0


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
