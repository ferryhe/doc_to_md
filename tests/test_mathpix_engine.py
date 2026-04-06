from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
import requests

from doc_to_md.config.settings import Settings
from doc_to_md.engines.mathpix import MathpixEngine


class _FakeResponse:
    def __init__(self, *, status_code: int = 200, payload: dict | None = None, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}", response=self)

    def json(self) -> dict:
        if self._payload is None:
            raise ValueError("No JSON payload")
        return self._payload


def _mock_settings(tmp_path: Path, **overrides) -> Settings:
    payload = {
        "input_dir": tmp_path / "input",
        "output_dir": tmp_path / "output",
        "mathpix_app_id": "test-id",
        "mathpix_app_key": "test-key",
        "mathpix_timeout_seconds": 1.0,
        "mathpix_retry_attempts": 2,
        "mathpix_poll_interval_seconds": 0.01,
        "mathpix_output_format": "md",
    }
    payload.update(overrides)
    return Settings(_env_file=None, **payload)


def test_mathpix_requires_app_id(tmp_path: Path) -> None:
    with patch(
        "doc_to_md.engines.mathpix.get_settings",
        return_value=_mock_settings(tmp_path, mathpix_app_id=None),
    ):
        with pytest.raises(RuntimeError, match="MATHPIX_APP_ID missing"):
            MathpixEngine()


def test_mathpix_document_flow_downloads_markdown(tmp_path: Path) -> None:
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n")
    statuses = iter(
        [
            _FakeResponse(payload={"status": "processing"}),
            _FakeResponse(payload={"status": "completed"}),
            _FakeResponse(text="# Converted by Mathpix\n"),
        ]
    )

    with patch(
        "doc_to_md.engines.mathpix.get_settings",
        return_value=_mock_settings(tmp_path),
    ), patch(
        "doc_to_md.engines.mathpix.requests.post",
        return_value=_FakeResponse(payload={"pdf_id": "job-123"}),
    ), patch(
        "doc_to_md.engines.mathpix.requests.get",
        side_effect=lambda *args, **kwargs: next(statuses),
    ):
        response = MathpixEngine().convert(pdf_file)

    assert response.model == "mathpix"
    assert "# Converted by Mathpix" in response.markdown


def test_mathpix_image_flow_uses_text_endpoint(tmp_path: Path) -> None:
    image_file = tmp_path / "sample.png"
    image_file.write_bytes(b"\x89PNG\r\n\x1a\n")

    with patch(
        "doc_to_md.engines.mathpix.get_settings",
        return_value=_mock_settings(tmp_path),
    ), patch(
        "doc_to_md.engines.mathpix.requests.post",
        return_value=_FakeResponse(payload={"text": "alpha + beta"}),
    ):
        response = MathpixEngine().convert(image_file)

    assert response.markdown == "alpha + beta"
    assert response.model == "mathpix"


def test_mathpix_rejects_unsupported_suffix(tmp_path: Path) -> None:
    unsupported = tmp_path / "notes.txt"
    unsupported.write_text("hello", encoding="utf-8")

    with patch(
        "doc_to_md.engines.mathpix.get_settings",
        return_value=_mock_settings(tmp_path),
    ):
        engine = MathpixEngine()

    with pytest.raises(RuntimeError, match="currently supports PDFs, DOCX, PPTX"):
        engine.convert(unsupported)


def test_mathpix_raises_on_error_status(tmp_path: Path) -> None:
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n")
    responses = iter(
        [
            _FakeResponse(payload={"status": "error", "error": "quota exceeded"}),
        ]
    )

    with patch(
        "doc_to_md.engines.mathpix.get_settings",
        return_value=_mock_settings(tmp_path),
    ), patch(
        "doc_to_md.engines.mathpix.requests.post",
        return_value=_FakeResponse(payload={"pdf_id": "job-123"}),
    ), patch(
        "doc_to_md.engines.mathpix.requests.get",
        side_effect=lambda *args, **kwargs: next(responses),
    ):
        with pytest.raises(RuntimeError, match="quota exceeded"):
            MathpixEngine().convert(pdf_file)


def test_mathpix_rejects_model_override(tmp_path: Path) -> None:
    with patch(
        "doc_to_md.engines.mathpix.get_settings",
        return_value=_mock_settings(tmp_path),
    ):
        with pytest.raises(ValueError, match="does not support model overrides"):
            MathpixEngine(model="custom-mathpix-model")
