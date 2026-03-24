from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_release_metadata_is_not_placeholder() -> None:
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert "Your Name" not in pyproject
    assert "you@example.com" not in pyproject
    assert "https://github.com/ferryhe/doc_to_md" in pyproject
    assert 'license = "MIT"' in pyproject
    assert 'license-files = ["LICENSE"]' in pyproject


def test_license_file_exists() -> None:
    license_file = PROJECT_ROOT / "LICENSE"

    assert license_file.exists()
    assert "MIT License" in license_file.read_text(encoding="utf-8")
