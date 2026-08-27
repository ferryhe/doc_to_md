from types import SimpleNamespace
from unittest.mock import patch

from doc_to_md.engines.mistral import MistralEngine, _DocumentChunk


class _FakeMistralClient:
    def __init__(self, *args, **kwargs) -> None:
        pass


def _mock_settings() -> SimpleNamespace:
    return SimpleNamespace(
        mistral_api_key="test-key",
        mistral_default_model="mistral-ocr-latest",
        mistral_timeout_seconds=60.0,
        mistral_retry_attempts=3,
        mistral_max_pdf_tokens=9000,
        mistral_max_pages_per_chunk=25,
    )


def test_mistral_omits_page_headers_by_default() -> None:
    with patch("doc_to_md.engines.mistral.get_settings", return_value=_mock_settings()), patch(
        "doc_to_md.engines.mistral.Mistral", _FakeMistralClient
    ):
        engine = MistralEngine()

    assert engine.include_page_headers is False


def test_strip_page_artifacts_removes_page_headers_and_standalone_page_numbers() -> None:
    text = "\n".join(
        [
            "正文第一段",
            "",
            "## Page 2",
            "2",
            "正文第二段",
            "- 3 -",
            "Page 4",
            "正文第三段",
        ]
    )

    cleaned = MistralEngine._strip_page_artifacts(text)

    assert "## Page 2" not in cleaned
    assert "\n2\n" not in f"\n{cleaned}\n"
    assert "- 3 -" not in cleaned
    assert "Page 4" not in cleaned
    assert "正文第一段" in cleaned
    assert "正文第二段" in cleaned
    assert "正文第三段" in cleaned


def test_process_chunk_uses_sdk_public_dict_payloads() -> None:
    calls: dict[str, object] = {}

    class _Files:
        def upload(self, **kwargs):
            calls["upload"] = kwargs
            return SimpleNamespace(id="file-123")

        def delete(self, **kwargs) -> None:
            calls["delete"] = kwargs

    class _OCR:
        def process(self, **kwargs):
            calls["process"] = kwargs
            return "response"

    client = SimpleNamespace(files=_Files(), ocr=_OCR())
    with patch("doc_to_md.engines.mistral.get_settings", return_value=_mock_settings()), patch(
        "doc_to_md.engines.mistral.Mistral", return_value=client
    ):
        engine = MistralEngine()

    response = engine._process_chunk(_DocumentChunk(data=b"pdf", label="sample.pdf"), 1)

    assert response == "response"
    assert calls["upload"] == {
        "file": {"file_name": "sample.pdf", "content": b"pdf"},
        "purpose": "ocr",
    }
    assert calls["process"] == {
        "model": "mistral-ocr-latest",
        "document": {"file_id": "file-123", "type": "file"},
        "include_image_base64": True,
    }
    assert calls["delete"] == {"file_id": "file-123"}
