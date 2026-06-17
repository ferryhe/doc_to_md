# Release Process

This project publishes versions from git tags. The goal is that a version number always maps to a changelog section, a source tree, and a GitHub Release.

## Version policy

`doc-to-markdown-converter` follows SemVer intent:

- `PATCH`: bug fixes, documentation corrections, and non-breaking dependency adjustments.
- `MINOR`: new engines, new CLI/API options, new output capabilities, or any `0.x` breaking change.
- `MAJOR`: breaking changes after the project reaches `1.0`.

During `0.x`, breaking changes are allowed but must not be silent. Any change that affects CLI flags, default behavior, Markdown output structure, Python APIs, config names, API response contracts, or optional-extra installation names must:

1. Bump at least the minor version, for example `0.1.x` to `0.2.0`.
2. Mark the entry as **BREAKING** in `CHANGELOG.md` under `Changed` or `Removed`.
3. Put upgrade impact and migration steps at the top of the GitHub Release notes.
4. Keep a compatibility alias or replacement path for at least one minor version when practical.

## Dependency policy

Published package dependencies should be compatible ranges, not deployment lock files.

- Routine runtime libraries use lower bounds plus a major-version upper bound, for example `requests>=2.32,<3.0`.
- API-sensitive, CLI-compatibility-sensitive, or system-bridge packages can stay exact or use narrower caps until targeted regression coverage exists. Current examples: `mistralai`, `openai`, `pytesseract`, and the Typer/Click compatibility cap.
- Heavy optional engines are distributed through extras and can use minimum versions; stricter constraints belong in dedicated constraints files or CI matrices.
- Development and benchmark environments may stay more tightly pinned in `requirements-*.txt` files because they describe reproducible local profiles, not package metadata.

## Release preparation checklist

1. Start from latest `main`.
2. Create a release-prep branch, for example `release/0.1.3`.
3. Update `pyproject.toml` and `src/doc_to_md/__init__.py` to the same version.
4. Promote `CHANGELOG.md` entries from `Unreleased` into `## [X.Y.Z] - YYYY-MM-DD`.
5. Confirm the changelog contains the target version and any breaking-change notes.
6. Run local verification:

   ```bash
   python -m ruff check src tests config benchmark.py tools
   python -m pytest -q
   python -m build
   python -m twine check dist/*
   ```

7. Merge the release-prep PR after checks and review comments are closed.
8. Create and push the annotated tag:

   ```bash
   git checkout main
   git pull --ff-only
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```

9. The tag-triggered release workflow builds the package, verifies version/tag consistency, and publishes GitHub Release notes from the changelog.

## Version/tag consistency rule

A release tag must match `pyproject.toml` exactly after removing the leading `v`:

```bash
TAG=${GITHUB_REF_NAME#v}
PKG_VERSION=$(python - <<'PY'
from pathlib import Path
import re

match = re.search(r'^version\s*=\s*"([^"]+)"$', Path('pyproject.toml').read_text(encoding='utf-8'), re.MULTILINE)
if match is None:
    raise SystemExit('pyproject.toml version not found')
print(match.group(1))
PY
)
test "$TAG" = "$PKG_VERSION"
```

The same version must also exist as a heading in `CHANGELOG.md`.

## Rollback and hotfix handling

If a release has a severe issue such as a broken CLI, failed primary conversion path, or data-corrupting output:

1. Pause further publishing and annotate the GitHub Release with `Known issue / Do not upgrade`.
2. Point README install examples back to the previous stable tag when needed.
3. Branch a hotfix from the last stable tag.
4. Fix the issue, add regression coverage, and publish a patch release.
5. If the issue cannot be fixed quickly, mark the affected release as pre-release or remove attached artifacts if appropriate.
6. Record the incident, affected versions, workaround, and follow-up tests in `CHANGELOG.md`.
