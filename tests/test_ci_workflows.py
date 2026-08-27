from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = PROJECT_ROOT / ".github" / "workflows"


def test_ci_workflow_adds_release_metadata_security_and_smoke_gates() -> None:
    workflow = (WORKFLOWS / "ci.yml").read_text(encoding="utf-8")

    assert "Release metadata consistency" in workflow
    assert "python tools/check_release_metadata.py" in workflow
    assert "security-audit:" in workflow
    assert "pip-audit" in workflow
    assert "tools/export_runtime_requirements.py" in workflow
    assert "smoke:" in workflow
    assert "engine: local" in workflow
    assert "engine: html_local" in workflow
    assert "tests/test_real_pdf_smoke.py" in workflow
    assert "tests/test_html_engine.py" in workflow


def test_release_workflow_is_tag_driven_and_publishes_changelog_notes() -> None:
    workflow = (WORKFLOWS / "release.yml").read_text(encoding="utf-8")

    assert "tags:" in workflow
    assert '"v*.*.*"' in workflow
    assert "contents: write" in workflow
    assert "python tools/check_release_metadata.py --tag" in workflow
    assert "python -m pip_audit" in workflow
    assert "python tools/export_runtime_requirements.py" in workflow
    assert "python tools/extract_changelog_section.py" in workflow
    assert "python -m build --outdir dist" in workflow
    assert "python -m twine check dist/*" in workflow
    assert "gh release create" in workflow
    assert "--verify-tag" in workflow


def test_nightly_smoke_workflow_runs_scheduled_optional_profiles() -> None:
    workflow = (WORKFLOWS / "nightly-smoke.yml").read_text(encoding="utf-8")

    assert "schedule:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "profile: core-local" in workflow
    assert "profile: html-extra" in workflow
    assert "profile: recommended-pdf" in workflow
    assert "profile: mineru-adapter" in workflow
    assert "requirements-recommended-pdf.txt" in workflow
    assert "tests/test_opendataloader_engine.py" in workflow
    assert "tests/test_mineru_engine.py" in workflow


def test_dependency_resolution_workflow_checks_optional_extras_weekly() -> None:
    workflow = (WORKFLOWS / "dependency-resolution.yml").read_text(encoding="utf-8")

    assert "schedule:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "pip install --dry-run --ignore-installed" in workflow
    assert "-r requirements-core.txt" in workflow
    for extra in ("markitdown", "paddleocr", "mineru", "docling", "opendataloader"):
        assert f"- {extra}" in workflow
    assert "tests/test_upstream_dependency_policy.py" in workflow


def test_dependabot_groups_converter_updates_without_hiding_major_releases() -> None:
    config = (PROJECT_ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")

    assert "package-ecosystem: pip" in config
    assert "package-ecosystem: github-actions" in config
    assert "converter-adapters:" in config
    assert "- marker-pdf" in config
    assert "ignore:" not in config
