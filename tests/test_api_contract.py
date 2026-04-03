import base64
import shutil
from pathlib import Path

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from doc_to_md.api import app


FIXTURE_PDF = Path(__file__).parent / "fixtures" / "real_smoke.pdf"

INLINE_KEYS = {
    "asset_count",
    "assets",
    "duration_seconds",
    "engine",
    "markdown",
    "model",
    "quality",
    "source_name",
    "status",
    "trace",
}

BATCH_KEYS = {
    "converted",
    "dry_run",
    "duration_seconds",
    "eligible",
    "engine",
    "failed",
    "input_dir",
    "model",
    "output_dir",
    "results",
    "skipped_since",
    "total_candidates",
}

QUALITY_KEYS = {
    "block_math_segments",
    "bullet_lines",
    "diagnostics",
    "formula_image_references",
    "formula_status",
    "headings",
    "image_references",
    "inline_math_segments",
    "status",
    "table_lines",
}

TRACE_KEYS = {
    "asset_count_after",
    "asset_count_before",
    "formula_image_references_after",
    "formula_image_references_before",
    "formula_ocr_applied",
    "formula_ocr_attempted",
    "formula_ocr_enabled",
    "formula_ocr_provider",
    "math_normalization_changed",
    "postprocess_changed",
}

BATCH_RESULT_KEYS = {
    "error",
    "modified_at",
    "output_path",
    "quality",
    "source_path",
    "status",
    "trace",
}

client = TestClient(app)


def _build_inline_json_request() -> dict[str, str]:
    return {
        "source_name": FIXTURE_PDF.name,
        "content_base64": base64.b64encode(FIXTURE_PDF.read_bytes()).decode("ascii"),
        "engine": "local",
    }


def test_inline_json_response_contract_real_pdf() -> None:
    response = client.post("/apps/conversion/convert-inline", json=_build_inline_json_request())

    assert response.status_code == 200
    payload = response.json()

    assert set(payload) == INLINE_KEYS
    assert payload["status"] == "converted"
    assert payload["source_name"] == FIXTURE_PDF.name
    assert payload["engine"] == "local"
    assert payload["model"] is None
    assert payload["asset_count"] == 0
    assert payload["assets"] == []
    assert isinstance(payload["duration_seconds"], float)
    assert "doc_to_md smoke PDF" in payload["markdown"]
    assert set(payload["quality"]) == QUALITY_KEYS
    assert set(payload["trace"]) == TRACE_KEYS


def test_inline_multipart_response_contract_real_pdf() -> None:
    response = client.post(
        "/apps/conversion/convert-inline",
        data={"engine": "local"},
        files={"file": (FIXTURE_PDF.name, FIXTURE_PDF.read_bytes(), "application/pdf")},
    )

    assert response.status_code == 200
    payload = response.json()

    assert set(payload) == INLINE_KEYS
    assert payload["status"] == "converted"
    assert payload["source_name"] == FIXTURE_PDF.name
    assert set(payload["quality"]) == QUALITY_KEYS
    assert set(payload["trace"]) == TRACE_KEYS


def test_batch_response_contract_real_pdf(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    shutil.copy2(FIXTURE_PDF, input_dir / FIXTURE_PDF.name)

    response = client.post(
        "/apps/conversion/convert",
        json={
            "input_path": str(input_dir),
            "output_path": str(output_dir),
            "engine": "local",
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert set(payload) == BATCH_KEYS
    assert payload["engine"] == "local"
    assert payload["model"] is None
    assert payload["total_candidates"] == 1
    assert payload["eligible"] == 1
    assert payload["converted"] == 1
    assert payload["failed"] == 0
    assert payload["skipped_since"] == 0
    assert payload["dry_run"] == 0
    assert isinstance(payload["duration_seconds"], float)
    assert len(payload["results"]) == 1

    result = payload["results"][0]
    assert set(result) == BATCH_RESULT_KEYS
    assert result["status"] == "converted"
    assert result["error"] is None
    assert result["output_path"].endswith("real_smoke.md")
    assert set(result["quality"]) == QUALITY_KEYS
    assert set(result["trace"]) == TRACE_KEYS
