import base64
import shutil
from pathlib import Path

import pytest

from doc_to_md.api import app
from doc_to_md.apps.conversion.logic import convert_inline_document, run_conversion


FIXTURE_PDF = Path(__file__).parent / "fixtures" / "real_smoke.pdf"


def test_real_pdf_fixture_exists_and_looks_valid() -> None:
    assert FIXTURE_PDF.exists()
    header = FIXTURE_PDF.read_bytes()[:8]
    assert header.startswith(b"%PDF-")


def test_convert_inline_document_real_pdf_smoke() -> None:
    payload = base64.b64encode(FIXTURE_PDF.read_bytes()).decode("ascii")

    result = convert_inline_document(
        source_name=FIXTURE_PDF.name,
        content_base64=payload,
        engine="local",
    )

    assert "doc_to_md smoke PDF" in result.markdown
    assert "real PDF fixture" in result.markdown
    assert result.quality.status in {"good", "review"}


pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

client = TestClient(app)


def test_convert_inline_json_real_pdf_smoke() -> None:
    response = client.post(
        "/apps/conversion/convert-inline",
        json={
            "source_name": FIXTURE_PDF.name,
            "content_base64": base64.b64encode(FIXTURE_PDF.read_bytes()).decode("ascii"),
            "engine": "local",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "doc_to_md smoke PDF" in payload["markdown"]
    assert payload["quality"]["status"] in {"good", "review"}


def test_convert_inline_multipart_real_pdf_smoke() -> None:
    response = client.post(
        "/apps/conversion/convert-inline",
        data={"engine": "local"},
        files={"file": (FIXTURE_PDF.name, FIXTURE_PDF.read_bytes(), "application/pdf")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source_name"] == FIXTURE_PDF.name
    assert "doc_to_md smoke PDF" in payload["markdown"]


def test_batch_conversion_real_pdf_smoke(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    shutil.copy2(FIXTURE_PDF, input_dir / FIXTURE_PDF.name)

    summary = run_conversion(
        input_path=input_dir,
        output_path=output_dir,
        engine="local",
    )

    assert summary.metrics.successes == 1
    assert summary.results[0].output_path is not None
    assert summary.results[0].output_path.exists()
    written = summary.results[0].output_path.read_text(encoding="utf-8")
    assert "doc_to_md smoke PDF" in written
