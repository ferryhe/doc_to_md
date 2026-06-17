from pathlib import Path
import re

from doc_to_md import __version__


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


def test_html_extra_includes_bs4_and_trafilatura() -> None:
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r"^html\s*=\s*\[(?P<body>.+?)\]$", pyproject, re.MULTILINE)

    assert match is not None
    body = match.group("body")
    assert "trafilatura" in body
    assert "beautifulsoup4" in body


def test_package_version_matches_pyproject() -> None:
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"(?P<version>[^"]+)"$', pyproject, re.MULTILINE)

    assert match is not None
    assert __version__ == match.group("version")


def _dependency_name(requirement: str) -> str:
    return re.split(r"[<>=!~ ]", requirement, maxsplit=1)[0].lower()


def _project_dependencies(pyproject_text: str) -> list[str]:
    match = re.search(
        r"^dependencies\s*=\s*\[(?P<body>.*?)^\]",
        pyproject_text,
        re.MULTILINE | re.DOTALL,
    )
    assert match is not None
    return re.findall(r'"([^"]+)"', match.group("body"))


def test_changelog_has_unreleased_and_current_version() -> None:
    changelog = PROJECT_ROOT / "CHANGELOG.md"

    assert changelog.exists()
    text = changelog.read_text(encoding="utf-8")
    assert "Keep a Changelog" in text
    assert "## [Unreleased]" in text
    assert f"## [{__version__}]" in text
    assert "release tags are created" in text


def test_release_process_documents_version_guardrails() -> None:
    release_process = PROJECT_ROOT / "docs" / "release-process.md"

    assert release_process.exists()
    text = release_process.read_text(encoding="utf-8")
    assert "vX.Y.Z" in text
    assert "pyproject.toml" in text
    assert "CHANGELOG.md" in text
    assert "test \"$TAG\" = \"$PKG_VERSION\"" in text
    assert "pyproject.toml version not found" in text
    version_guard = re.search(
        r"PKG_VERSION=\$\(python - <<'PY'.*?test \"\$TAG\" = \"\$PKG_VERSION\"",
        text,
        re.DOTALL,
    )
    assert version_guard is not None
    assert "tomllib" not in version_guard.group(0)
    assert "Rollback" in text or "rollback" in text


def test_release_docs_are_included_in_source_distribution_manifest() -> None:
    manifest = (PROJECT_ROOT / "MANIFEST.in").read_text(encoding="utf-8")

    assert "include CHANGELOG.md" in manifest
    assert "recursive-include docs *.md" in manifest


def test_runtime_dependency_policy_uses_compatible_ranges_for_routine_deps() -> None:
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    dependencies = {
        _dependency_name(requirement): requirement
        for requirement in _project_dependencies(pyproject)
    }

    compatible_range_dependencies = {
        "typer",
        "rich",
        "pydantic",
        "pydantic-settings",
        "python-dotenv",
        "requests",
        "click",
        "pypdf",
        "python-docx",
        "pillow",
        "tiktoken",
    }
    for name in compatible_range_dependencies:
        requirement = dependencies[name]
        assert "==" not in requirement
        assert ">=" in requirement
        assert "<" in requirement

    assert dependencies["click"] == "click>=8.1,<8.2"

    exact_until_covered = {"mistralai", "openai", "pytesseract"}
    for name in exact_until_covered:
        assert "==" in dependencies[name]
