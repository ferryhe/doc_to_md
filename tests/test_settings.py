from pathlib import Path

import pytest

from doc_to_md.config.settings import Settings


def test_settings_allows_remote_default_without_secret(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    monkeypatch.delenv("SILICONFLOW_API_KEY", raising=False)
    monkeypatch.delenv("MATHPIX_APP_ID", raising=False)
    monkeypatch.delenv("MATHPIX_APP_KEY", raising=False)

    settings = Settings(
        _env_file=None,
        default_engine="mistral",
        mistral_api_key=None,
        input_dir=tmp_path / "input",
        output_dir=tmp_path / "output",
    )

    assert settings.default_engine == "mistral"
    assert settings.input_dir.exists()
    assert settings.output_dir.exists()


def test_settings_allows_mathpix_default_without_secret(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MATHPIX_APP_ID", raising=False)
    monkeypatch.delenv("MATHPIX_APP_KEY", raising=False)

    settings = Settings(
        _env_file=None,
        default_engine="mathpix",
        mathpix_app_id=None,
        mathpix_app_key=None,
        input_dir=tmp_path / "input",
        output_dir=tmp_path / "output",
    )

    assert settings.default_engine == "mathpix"
    assert settings.input_dir.exists()
    assert settings.output_dir.exists()


def test_settings_validates_mathpix_output_format(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="MATHPIX_OUTPUT_FORMAT"):
        Settings(
            _env_file=None,
            input_dir=tmp_path / "input",
            output_dir=tmp_path / "output",
            mathpix_output_format="html",
        )


def test_package_settings_module_is_importable() -> None:
    from doc_to_md.config import settings

    assert settings.Settings.__name__ == "Settings"


def test_settings_with_overrides_preserves_base_and_applies_updates(tmp_path: Path) -> None:
    settings = Settings(
        _env_file=None,
        input_dir=tmp_path / "input",
        output_dir=tmp_path / "output",
        formula_ocr_enabled=False,
        formula_ocr_provider="mistral",
    )

    overridden = settings.with_overrides(
        formula_ocr_enabled=True,
        formula_ocr_provider="deepseekocr",
    )

    assert settings.formula_ocr_enabled is False
    assert settings.formula_ocr_provider == "mistral"
    assert overridden.formula_ocr_enabled is True
    assert overridden.formula_ocr_provider == "deepseekocr"


def test_settings_accepts_mineru_pro_engine_and_defaults(tmp_path: Path) -> None:
    settings = Settings(
        _env_file=None,
        default_engine="mineru_pro",
        input_dir=tmp_path / "input",
        output_dir=tmp_path / "output",
    )

    assert settings.default_engine == "mineru_pro"
    assert settings.mineru_pro_model == "opendatalab/MinerU2.5-Pro-2604-1.2B"
    assert settings.mineru_pro_backend == "http-client"


def test_settings_validates_mineru_pro_max_pages(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="MINERU_PRO_MAX_PAGES"):
        Settings(
            _env_file=None,
            input_dir=tmp_path / "input",
            output_dir=tmp_path / "output",
            mineru_pro_max_pages=0,
        )
