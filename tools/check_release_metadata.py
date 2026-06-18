"""Validate release metadata consistency for CI and tag releases."""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib  # type: ignore[no-redef]


SEMVER_TAG_RE = re.compile(r"^v(?P<version>\d+\.\d+\.\d+)$")
INIT_VERSION_RE = re.compile(r'^__version__\s*=\s*"(?P<version>[^"]+)"$', re.MULTILINE)


@dataclass(frozen=True)
class ReleaseMetadata:
    pyproject_version: str
    package_version: str
    changelog_has_unreleased: bool
    changelog_has_project_version: bool


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"Missing required file: {path}") from exc


def _project_version(pyproject_text: str) -> str:
    data = tomllib.loads(pyproject_text)
    project = data.get("project")
    if not isinstance(project, dict):
        raise ValueError("Could not find [project] table in pyproject.toml")
    version = project.get("version")
    if not isinstance(version, str) or not version:
        raise ValueError("Could not find project.version in pyproject.toml")
    return version


def _extract(pattern: re.Pattern[str], text: str, label: str) -> str:
    match = pattern.search(text)
    if match is None:
        raise ValueError(f"Could not find {label}")
    return match.group("version")


def _has_changelog_heading(changelog: str, version: str) -> bool:
    escaped = re.escape(version)
    return re.search(rf"^## \[{escaped}\](?:\s+-\s+\d{{4}}-\d{{2}}-\d{{2}})?\s*$", changelog, re.MULTILINE) is not None


def inspect_release_metadata(project_root: Path) -> ReleaseMetadata:
    pyproject = _read_text(project_root / "pyproject.toml")
    package_init = _read_text(project_root / "src" / "doc_to_md" / "__init__.py")
    changelog = _read_text(project_root / "CHANGELOG.md")

    pyproject_version = _project_version(pyproject)
    package_version = _extract(INIT_VERSION_RE, package_init, "__version__ in src/doc_to_md/__init__.py")

    return ReleaseMetadata(
        pyproject_version=pyproject_version,
        package_version=package_version,
        changelog_has_unreleased="## [Unreleased]" in changelog,
        changelog_has_project_version=_has_changelog_heading(changelog, pyproject_version),
    )


def validate_release_metadata(project_root: Path, tag: str | None = None) -> list[str]:
    errors: list[str] = []
    try:
        metadata = inspect_release_metadata(project_root)
    except ValueError as exc:
        return [str(exc)]

    if metadata.pyproject_version != metadata.package_version:
        errors.append(
            "Version mismatch: "
            f"pyproject.toml has {metadata.pyproject_version}, "
            f"src/doc_to_md/__init__.py has {metadata.package_version}"
        )

    if not metadata.changelog_has_unreleased:
        errors.append("CHANGELOG.md must contain a ## [Unreleased] section")

    if not metadata.changelog_has_project_version:
        errors.append(f"CHANGELOG.md must contain a section for [{metadata.pyproject_version}]")

    if tag:
        tag_match = SEMVER_TAG_RE.fullmatch(tag)
        if tag_match is None:
            errors.append(f"Release tag must use vX.Y.Z format: {tag}")
        elif tag_match.group("version") != metadata.pyproject_version:
            errors.append(
                "Release tag/version mismatch: "
                f"tag {tag} points to {tag_match.group('version')}, "
                f"pyproject.toml has {metadata.pyproject_version}"
            )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate release metadata before building or publishing a release.")
    parser.add_argument("--project-root", default=".", help="Repository root; defaults to the current directory.")
    parser.add_argument(
        "--tag",
        default=os.environ.get("GITHUB_REF_NAME"),
        help="Optional release tag to compare with pyproject.toml, usually GITHUB_REF_NAME.",
    )
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    errors = validate_release_metadata(project_root, tag=args.tag)
    if errors:
        for error in errors:
            print(f"release metadata error: {error}", file=sys.stderr)
        return 1

    metadata = inspect_release_metadata(project_root)
    tag_suffix = f" for tag {args.tag}" if args.tag else ""
    print(f"release metadata ok: version {metadata.pyproject_version}{tag_suffix}")
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised by CI/CLI
    raise SystemExit(main())
