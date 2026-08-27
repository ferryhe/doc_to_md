# Changelog

All notable changes to `doc-to-markdown-converter` will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses semantic versioning discipline described in [docs/release-process.md](docs/release-process.md). While the project is in `0.x`, breaking changes are still allowed, but they must be explicitly called out and must bump at least the minor version.

> Link references for version comparisons will be added as release tags are created. Version `0.2.0` is the first release prepared under the formal release-governance workflow.

## [Unreleased]

## [0.2.0] - 2026-08-27

### Added

- Add a documented release process covering SemVer rules, release preparation, tag naming, changelog promotion, and rollback handling.
- Add README release-governance guidance for contributors.
- Add GitHub Actions release automation for `vX.Y.Z` tags, including version/changelog verification, wheel/sdist build, twine validation, changelog-driven release notes, and GitHub Release publishing.
- Add direct-runtime dependency security auditing with `pip-audit` in CI.
- Add PR and nightly smoke matrices for lightweight engine coverage.
- Add reusable release metadata and changelog extraction helper scripts.
- Add MinerU beta-engine governance documentation, an experimental constraint overlay, and mocked adapter smoke tests for release readiness.
- Add weekly Dependabot rules for Python and GitHub Actions updates, with converter SDK updates grouped into reviewable pull requests.
- Add a weekly optional-extra dependency-resolution matrix and a direct upstream compatibility-watch manifest.
- Add PaddleOCR 3.x result-shape coverage and Mistral SDK request-payload compatibility coverage.

### Changed

- Relax routine runtime dependency constraints in `pyproject.toml` from exact pins to compatible ranges so patch/minor fixes can be absorbed without republishing the package for every upstream release.
- Raise `pypdf` and `pillow` lower bounds in package metadata and pinned environment profiles to audited versions that clear the CI security gate.
- Narrow the recommended PDF install target to common engines only and document the real MinerU beta install findings separately.
- Point MinerU runtime dependency errors at the `mineru[pipeline]` path instead of bare `mineru`.
- Update Mistral SDK to `2.9.4` and OpenAI SDK to the MinerU-compatible `2.54.0` line.
- Raise tested optional-engine floors to MarkItDown `0.1.7`, PaddleOCR `3.7`, MinerU `3.4.5`, Docling `2.123`, and OpenDataLoader `2.5.5`, with explicit next-major caps.
- Expand the Rich compatibility range through 15.x so current Twine release tooling can coexist with the package runtime.
- Raise the Typer/Click compatibility line to Typer `0.26.8` and Click `8.3.3`, clearing the current direct-dependency audit finding.
- Bound Ruff to the tested `0.15.x` ruleset so clean release environments do not silently adopt incompatible lint rules.
- Refresh the pinned CPU/GPU profiles for Docling's current settings dependency and make the CUDA 12.1 wheel source explicit in the legacy GPU snapshot.
- **BREAKING:** Remove the `marker` package extra because current Marker releases require a Pillow range that cannot coexist with this package's audited base runtime. The adapter remains in source for existing isolated environments, and Marker releases remain monitored for a compatible dependency line.

### Fixed

- Read PaddleOCR 3.x `rec_texts` and `rec_scores` result mappings while retaining legacy nested-result support.
- Use Mistral SDK public client/model namespaces across both document and formula OCR paths, with dictionary request payloads that work across the 1.x-to-2.x transition.

## [0.1.2] - 2026-06-17

### Added

- Document the current baseline release metadata for the existing package version.
- Current package includes CLI and FastAPI entry points, local/PDF/Office/HTML conversion paths, multiple OCR/extraction engines, and API contract tests.

### Changed

- Treat `0.1.2` as the baseline version for the first formalized changelog and release-governance process.
