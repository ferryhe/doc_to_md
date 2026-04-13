from pathlib import Path
from types import SimpleNamespace

from PIL import Image

import doc_to_md.engines.mineru as mineru_mod
import doc_to_md.engines.mineru_pro as mineru_pro_mod


def test_mineru_resolves_hybrid_output_folder(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        mineru_mod,
        "get_settings",
        lambda: SimpleNamespace(
            mineru_backend="hybrid-auto-engine",
            mineru_parse_method="auto",
            mineru_lang="en",
            mineru_formula_enable=True,
            mineru_table_enable=True,
            mineru_start_page=0,
            mineru_end_page=None,
            mineru_server_url=None,
        ),
    )
    monkeypatch.setattr(mineru_mod, "ensure_mineru_accelerator_env", lambda: None)
    parse_dir = tmp_path / "sample" / "hybrid_auto"
    parse_dir.mkdir(parents=True)

    engine = mineru_mod.MinerUEngine()

    assert engine._resolve_output_folder(tmp_path, "sample") == parse_dir


def test_mineru_pro_http_client_requires_server_url(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        mineru_pro_mod,
        "get_settings",
        lambda: SimpleNamespace(
            mineru_pro_model="opendatalab/MinerU2.5-Pro-2604-1.2B",
            mineru_pro_backend="http-client",
            mineru_pro_server_url=None,
            mineru_pro_render_dpi=200,
            mineru_pro_max_pages=None,
            mineru_pro_image_analysis=False,
        ),
    )

    engine = mineru_pro_mod.MinerUProEngine()

    try:
        engine._ensure_runtime()
    except RuntimeError as exc:
        assert "MINERU_PRO_SERVER_URL" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected missing server URL to fail")


def test_mineru_pro_convert_uses_json2md(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        mineru_pro_mod,
        "get_settings",
        lambda: SimpleNamespace(
            mineru_pro_model="opendatalab/MinerU2.5-Pro-2604-1.2B",
            mineru_pro_backend="http-client",
            mineru_pro_server_url="http://127.0.0.1:30000",
            mineru_pro_render_dpi=200,
            mineru_pro_max_pages=None,
            mineru_pro_image_analysis=False,
        ),
    )

    class FakeClient:
        def two_step_extract(self, image):
            return [{"type": "text", "content": f"size={image.size[0]}x{image.size[1]}"}]

    engine = mineru_pro_mod.MinerUProEngine()
    engine._runtime = (FakeClient(), lambda blocks: blocks[0]["content"])
    image_path = tmp_path / "page.png"
    Image.new("RGB", (4, 3), color="white").save(image_path)

    response = engine.convert(image_path)

    assert response.model == "http-client:opendatalab/MinerU2.5-Pro-2604-1.2B"
    assert response.markdown == "size=4x3"
