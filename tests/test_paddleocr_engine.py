import sys
from types import SimpleNamespace

import pytest
from PIL import Image

from doc_to_md.engines.paddleocr import PaddleOCREngine


class _PaddleV3:
    def predict(self, image):
        del image
        return [
            {
                "rec_texts": ["First line", "", "Second line"],
                "rec_scores": [0.98, 0.10, 0.875],
            }
        ]


class _PaddleV3Wrapped:
    def predict(self, image):
        del image
        return [{"res": {"rec_texts": ["Wrapped"], "rec_scores": [0.91]}}]


class _PaddleLegacy:
    def ocr(self, image):
        del image
        return [[[[0, 0, 1, 1], ("Legacy", 0.93)]]]


@pytest.fixture(autouse=True)
def _stub_optional_numpy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "numpy", SimpleNamespace(array=lambda value: value))


def test_run_ocr_reads_paddle_v3_result_mapping() -> None:
    lines = PaddleOCREngine._run_ocr(_PaddleV3(), Image.new("RGB", (2, 2)))

    assert lines == ["- First line _(conf 0.98)_", "- Second line _(conf 0.88)_"]


def test_run_ocr_reads_wrapped_paddle_v3_result_mapping() -> None:
    lines = PaddleOCREngine._run_ocr(_PaddleV3Wrapped(), Image.new("RGB", (2, 2)))

    assert lines == ["- Wrapped _(conf 0.91)_"]


def test_run_ocr_keeps_legacy_result_compatibility() -> None:
    lines = PaddleOCREngine._run_ocr(_PaddleLegacy(), Image.new("RGB", (2, 2)))

    assert lines == ["- Legacy _(conf 0.93)_"]
