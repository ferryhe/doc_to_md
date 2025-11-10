from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config.settings import Settings


def test_settings_allows_remote_default_without_secret(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    monkeypatch.delenv("SILICONFLOW_API_KEY", raising=False)

    settings = Settings(
        default_engine="mistral",
        mistral_api_key=None,
        input_dir=tmp_path / "input",
        output_dir=tmp_path / "output",
    )

    assert settings.default_engine == "mistral"
    assert settings.input_dir.exists()
    assert settings.output_dir.exists()
