# Changelog

All notable changes to `doc-to-markdown-converter` will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses semantic versioning discipline described in [docs/release-process.md](docs/release-process.md). While the project is in `0.x`, breaking changes are still allowed, but they must be explicitly called out and must bump at least the minor version.

> Link references for version comparisons will be added as release tags are created. The current `0.1.2` section documents the baseline that existed before formal release governance.

## [Unreleased]

### Added

- Add a documented release process covering SemVer rules, release preparation, tag naming, changelog promotion, and rollback handling.
- Add README release-governance guidance for contributors.

### Changed

- Relax routine runtime dependency constraints in `pyproject.toml` from exact pins to compatible ranges so patch/minor fixes can be absorbed without republishing the package for every upstream release.

## [0.1.2] - 2026-06-17

### Added

- Document the current baseline release metadata for the existing package version.
- Current package includes CLI and FastAPI entry points, local/PDF/Office/HTML conversion paths, multiple OCR/extraction engines, and API contract tests.

### Changed

- Treat `0.1.2` as the baseline version for the first formalized changelog and release-governance process.
