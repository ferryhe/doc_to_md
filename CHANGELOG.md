# Changelog

All notable changes to `doc-to-markdown-converter` will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses semantic versioning discipline described in [docs/release-process.md](docs/release-process.md). While the project is in `0.x`, breaking changes are still allowed, but they must be explicitly called out and must bump at least the minor version.

> Link references for version comparisons will be added as release tags are created. The current `0.1.2` section documents the baseline that existed before formal release governance.

## [Unreleased]

### Added

- Add a documented release process covering SemVer rules, release preparation, tag naming, changelog promotion, and rollback handling.
- Add README release-governance guidance for contributors.
- Add GitHub Actions release automation for `vX.Y.Z` tags, including version/changelog verification, wheel/sdist build, twine validation, changelog-driven release notes, and GitHub Release publishing.
- Add direct-runtime dependency security auditing with `pip-audit` in CI.
- Add PR and nightly smoke matrices for lightweight engine coverage.
- Add reusable release metadata and changelog extraction helper scripts.
- Add MinerU beta-engine governance documentation, an experimental constraint overlay, and mocked adapter smoke tests for release readiness.

### Changed

- Relax routine runtime dependency constraints in `pyproject.toml` from exact pins to compatible ranges so patch/minor fixes can be absorbed without republishing the package for every upstream release.
- Raise `pypdf` and `pillow` lower bounds in package metadata and pinned environment profiles to audited versions that clear the CI security gate.

## [0.1.2] - 2026-06-17

### Added

- Document the current baseline release metadata for the existing package version.
- Current package includes CLI and FastAPI entry points, local/PDF/Office/HTML conversion paths, multiple OCR/extraction engines, and API contract tests.

### Changed

- Treat `0.1.2` as the baseline version for the first formalized changelog and release-governance process.
