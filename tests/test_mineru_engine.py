from __future__ import annotations

import builtins
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from doc_to_md.engines.mineru import MinerUEngine


def _mock_settings(**overrides) -> SimpleNamespace:
    payload = {
        "mineru_backend": "pipeline",
        "mineru_parse_method": "auto",
        "mineru_lang": "en",
        "mineru_formula_enable": True,
        "mineru_table_enable": True,
        "mineru_start_page": 0,
        "mineru_end_page": None,
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def _engine(**settings) -> MinerUEngine:
    with patch("doc_to_md.engines.mineru.get_settings", return_value=_mock_settings(**settings)), patch(
        "doc_to_md.engines.mineru.ensure_mineru_accelerator_env"
    ):
        return MinerUEngine()


def test_mineru_engine_records_runtime_settings_and_model() -> None:
    with patch(
        "doc_to_md.engines.mineru.get_settings",
        return_value=_mock_settings(mineru_backend="pipeline", mineru_parse_method="ocr", mineru_lang="ch"),
    ), patch("doc_to_md.engines.mineru.ensure_mineru_accelerator_env") as ensure_accelerator:
        engine = MinerUEngine()

    assert engine.name == "mineru"
    assert engine.model == "pipeline:ocr"
    assert engine.lang == "ch"
    ensure_accelerator.assert_called_once_with()


def test_mineru_missing_runtime_raises_install_hint() -> None:
    engine = _engine()
    real_import = builtins.__import__

    def _block_mineru_import(name, *args, **kwargs):
        if name.startswith("mineru"):
            raise ImportError("No module named 'mineru'")
        return real_import(name, *args, **kwargs)

    with patch.object(builtins, "__import__", side_effect=_block_mineru_import):
        with pytest.raises(RuntimeError, match="MinerU engine requires.*mineru\\[pipeline\\]"):
            engine._ensure_runtime()


def test_mineru_resolves_pipeline_and_vlm_output_folders(tmp_path: Path) -> None:
    pipeline = _engine(mineru_backend="pipeline", mineru_parse_method="auto")
    pipeline_folder = tmp_path / "sample" / "auto"
    pipeline_folder.mkdir(parents=True)

    assert pipeline._resolve_output_folder(tmp_path, "sample") == pipeline_folder

    vlm = _engine(mineru_backend="vlm-transformers")
    vlm_folder = tmp_path / "sample" / "vlm"
    vlm_folder.mkdir(parents=True)

    assert vlm._resolve_output_folder(tmp_path, "sample") == vlm_folder


def test_mineru_convert_collects_markdown_assets_and_runtime_options(tmp_path: Path) -> None:
    engine = _engine(mineru_parse_method="auto", mineru_start_page=1, mineru_end_page=3)
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n")
    calls: dict[str, object] = {}

    def fake_read_fn(path: Path) -> bytes:
        assert path == pdf_file
        return b"pdf-bytes"

    def fake_do_parse(**kwargs) -> None:
        calls.update(kwargs)
        output_root = Path(str(kwargs["output_dir"]))
        parse_folder = output_root / "sample" / "auto"
        images = parse_folder / "images"
        images.mkdir(parents=True)
        (parse_folder / "sample.md").write_text("# Converted by MinerU\n", encoding="utf-8")
        (images / "figure.png").write_bytes(b"png-bytes")

    engine._runtime = (fake_do_parse, fake_read_fn, SimpleNamespace(MM_MD="mm_md"))

    response = engine.convert(pdf_file)

    assert response.markdown == "# Converted by MinerU\n"
    assert response.model == "pipeline:auto"
    assert [(asset.filename, asset.subdir, asset.data) for asset in response.assets] == [
        ("figure.png", "images", b"png-bytes")
    ]
    assert calls["pdf_file_names"] == ["sample"]
    assert calls["pdf_bytes_list"] == [b"pdf-bytes"]
    assert calls["p_lang_list"] == ["en"]
    assert calls["backend"] == "pipeline"
    assert calls["parse_method"] == "auto"
    assert calls["formula_enable"] is True
    assert calls["table_enable"] is True
    assert calls["start_page_id"] == 1
    assert calls["end_page_id"] == 3
    assert calls["f_dump_md"] is True
    assert calls["f_make_md_mode"] == "mm_md"


def test_mineru_convert_wraps_missing_pipeline_dependency(tmp_path: Path) -> None:
    engine = _engine()
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n")

    def fake_read_fn(path: Path) -> bytes:
        assert path == pdf_file
        return b"pdf-bytes"

    def fake_do_parse(**_kwargs) -> None:
        raise ModuleNotFoundError("No module named 'transformers'")

    engine._runtime = (fake_do_parse, fake_read_fn, SimpleNamespace(MM_MD="mm_md"))

    with pytest.raises(RuntimeError, match="MinerU pipeline runtime is incomplete.*mineru\\[pipeline\\]"):
        engine.convert(pdf_file)
