from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_tool(module_name: str):
    path = PROJECT_ROOT / "tools" / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _write_minimal_release_project(root: Path, *, version: str = "0.1.2", init_version: str | None = None) -> None:
    (root / "src" / "doc_to_md").mkdir(parents=True)
    (root / "pyproject.toml").write_text(
        f'[project]\nname = "doc-to-markdown-converter"\nversion = "{version}"\ndependencies = [\n    "requests>=2.32,<3.0",\n]\n',
        encoding="utf-8",
    )
    (root / "src" / "doc_to_md" / "__init__.py").write_text(
        f'__version__ = "{init_version or version}"\n',
        encoding="utf-8",
    )
    (root / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [Unreleased]\n\n### Added\n\n- Next change.\n\n## [0.1.2] - 2026-06-17\n\n### Added\n\n- Baseline.\n",
        encoding="utf-8",
    )


def test_release_metadata_validator_accepts_matching_project_and_tag(tmp_path: Path) -> None:
    tool = _load_tool("check_release_metadata")
    _write_minimal_release_project(tmp_path)

    assert tool.validate_release_metadata(tmp_path, tag="v0.1.2") == []


def test_release_metadata_validator_rejects_tag_version_mismatch(tmp_path: Path) -> None:
    tool = _load_tool("check_release_metadata")
    _write_minimal_release_project(tmp_path)

    errors = tool.validate_release_metadata(tmp_path, tag="v0.1.3")

    assert any("Release tag/version mismatch" in error for error in errors)


def test_release_metadata_validator_rejects_package_version_mismatch(tmp_path: Path) -> None:
    tool = _load_tool("check_release_metadata")
    _write_minimal_release_project(tmp_path, init_version="0.1.1")

    errors = tool.validate_release_metadata(tmp_path, tag="v0.1.2")

    assert any("Version mismatch" in error for error in errors)


def test_extract_changelog_section_returns_requested_version_only() -> None:
    tool = _load_tool("extract_changelog_section")
    changelog = (
        "# Changelog\n\n"
        "## [Unreleased]\n\n- Future.\n\n"
        "## [0.1.2] - 2026-06-17\n\n### Added\n\n- Baseline.\n\n"
        "## [0.1.1] - 2026-06-16\n\n### Fixed\n\n- Earlier.\n"
    )

    section = tool.extract_changelog_section(changelog, "0.1.2")

    assert section.startswith("## [0.1.2]")
    assert "Baseline" in section
    assert "Earlier" not in section


def test_export_runtime_requirements_reads_project_dependencies() -> None:
    tool = _load_tool("export_runtime_requirements")
    pyproject = '''
[project]
dependencies = [
    'typer>=0.12,<1.0',
    "click>=8.1,<8.2",
]
'''

    assert tool.project_dependencies(pyproject) == ["typer>=0.12,<1.0", "click>=8.1,<8.2"]


def test_release_metadata_validator_accepts_current_repository_tag() -> None:
    tool = _load_tool("check_release_metadata")
    metadata = tool.inspect_release_metadata(PROJECT_ROOT)

    assert tool.validate_release_metadata(PROJECT_ROOT, tag=f"v{metadata.pyproject_version}") == []
