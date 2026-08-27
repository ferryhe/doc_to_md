# doc-to-markdown-converter

Convert PDFs, scans, office documents, HTML, and plain text into Markdown for LLM and actuarial-document workflows.

This repository is optimized for one practical goal: turn messy source documents into Markdown that is usable for review, indexing, chunking, RAG, and downstream AI processing.

## What matters most

Current engine choice by document type:

| Document type | First choice | Backup | Why |
| --- | --- | --- | --- |
| General text-heavy PDF | `opendataloader` | `mistral` | Best current local default when Java is acceptable |
| General text-heavy PDF, easiest install | `markitdown` | `opendataloader` | Simplest local extra to try |
| Printed formula PDF | `mistral` | `mathpix` | Best current tracked printed-formula recovery |
| Handwritten formula PDF | `mathpix` | `mistral` | Best current tracked handwritten-formula recovery |

Important caution:

- `opendataloader` is fast and often structurally strong, but formula-heavy AI workflows should not trust it blindly.
- When it fails on formulas, it often leaves plain context or images instead of machine-readable math.
- If you see `formula_context_without_math` or `formula_image_reference`, rerun with `mistral` or `mathpix`.

## Recommended install

For the common PDF setup most users should try first:

```bash
pip install -r requirements-recommended-pdf.txt
```

That setup keeps only the engines that are currently recommended for normal use:

- `local`
- `markitdown`
- `opendataloader`
- `mistral`
- `mathpix`

Notes:

- `local`, `mistral`, and `mathpix` are part of the base package
- `mistral` needs `MISTRAL_API_KEY`
- `mathpix` needs `MATHPIX_APP_ID` and `MATHPIX_APP_KEY`
- `opendataloader` needs Java 11+ on `PATH`
- a fresh Linux / Python 3.11 install check produced a temporary venv of about `356 MB`
- heavier research/beta engines such as `docling`, `paddleocr`, `marker`, and `mineru` are intentionally excluded from this install target

Other install targets:

| Use case | Command |
| --- | --- |
| Recommended PDF setup | `pip install -r requirements-recommended-pdf.txt` |
| Docling one-off evaluation | `pip install -e ".[docling]"` |
| MinerU beta research | see [docs/mineru.md](docs/mineru.md); do not use on small disks |
| Broader CPU environment | `pip install -r requirements-core.txt` |
| Legacy GPU snapshot | `pip install -r requirements.txt` (not a single all-engine environment) |
| Dev and test overlay | `pip install -r requirements-dev.txt` |

`marker` is intentionally not exposed as an install extra in `0.2.0`. Marker 2.0 requires `Pillow<11`, while the audited base package requires `Pillow>=12.2`. Keeping those packages in one Python environment is not resolvable today. The adapter remains available for existing isolated environments, and upstream Marker versions are still monitored for a compatible release.

## Quick start

Create `.env` from the template:

```bash
cp .env.example .env
```

Minimum useful settings:

```env
DEFAULT_ENGINE=local
MISTRAL_API_KEY=...
MATHPIX_APP_ID=...
MATHPIX_APP_KEY=...
AUTO_PDF_ENGINE=opendataloader
```

The CLI batch converter reads a directory of documents. For a single file, place it in an input folder or call `POST /apps/conversion/convert-inline`.

Convert a directory:

```bash
python -m doc_to_md.cli convert \
  --input-path data/input \
  --output-path data/output \
  --engine opendataloader
```

Try the strongest handwritten-formula path:

```bash
python -m doc_to_md.cli convert \
  --input-path data/input \
  --output-path data/output \
  --engine mathpix
```

List available engines:

```bash
python -m doc_to_md.cli list-engines
```

## Interfaces

The three main ways to use this repository are:

- CLI: `python -m doc_to_md.cli ...`
- API: `doc-to-md-api`
- Agent skill: [skills/doc_to_md_agent/SKILL.md](skills/doc_to_md_agent/SKILL.md)

Useful API endpoints:

- `GET /apps/conversion/engines`
- `GET /apps/conversion/engine-readiness`
- `POST /apps/conversion/convert`
- `POST /apps/conversion/convert-inline`

The HTTP response contract is documented in [API_RESPONSE_CONTRACT.md](API_RESPONSE_CONTRACT.md).

If you are calling the library directly in Python, the main helpers are:

- `doc_to_md.apps.conversion.logic.run_conversion(...)`
- `doc_to_md.apps.conversion.logic.convert_inline_document(...)`
- `doc_to_md.apps.conversion.logic.list_preferred_engine_readiness(...)`

## Supported formats

Supported input types:

- `.pdf`
- `.docx`
- `.pptx`
- `.xlsx`
- `.html`
- `.htm`
- `.png`
- `.jpg`
- `.jpeg`
- `.txt`
- `.md`

Validation rules:

- files must be readable and non-empty
- legacy `.doc` is rejected
- files larger than `100 MB` are rejected

## Engines

Main engines:

- `local`: fast built-in baseline
- `markitdown`: easiest local extra
- `opendataloader`: strongest local default for prose-heavy PDFs
- `mistral`: strongest managed OCR path for general PDFs and printed formulas
- `mathpix`: strongest tracked path for handwritten formulas

Other supported engines:

- `docling`
- `paddleocr`
- `mineru` (beta optional engine; see [docs/mineru.md](docs/mineru.md))
- `marker` (existing isolated environments only; no package extra in `0.2.0`)
- `deepseekocr`
- `html_local`
- `auto`

## Read next

Use the rest of the docs this way:

- [PDF_ENGINE_EVALUATION.md](PDF_ENGINE_EVALUATION.md): the main evaluation document
  Includes benchmark method, install tradeoffs, routing rules, and real-PDF testing workflow.
- [benchmark_results/README.md](benchmark_results/README.md): archived benchmark artifacts
  Includes the tracked general-text, printed-formula, and handwritten-formula suites.
- [API_RESPONSE_CONTRACT.md](API_RESPONSE_CONTRACT.md): stable API field shapes
- [CHANGELOG.md](CHANGELOG.md): release history and current `Unreleased` changes
- [docs/release-process.md](docs/release-process.md): SemVer, changelog, tag, and rollback process
- [docs/mineru.md](docs/mineru.md): MinerU beta engine install constraints, smoke checks, and release-governance status
- [skills/doc_to_md_agent/SKILL.md](skills/doc_to_md_agent/SKILL.md): agent workflow guidance

## Release governance

The project uses `pyproject.toml` as the package version source and `CHANGELOG.md` as the user-facing release history.

Release rules:

- Tags use `vX.Y.Z` and must match the package version after removing the leading `v`.
- Every release must promote `CHANGELOG.md` entries out of `Unreleased` into a dated version section.
- During `0.x`, breaking changes are allowed only when they are explicitly marked as **BREAKING** and bump at least the minor version.
- Routine runtime dependencies use compatible version ranges in package metadata; reproducible local environments live in the `requirements-*.txt` files.
- CI validates release metadata, audits direct runtime dependencies with `pip-audit`, and runs lightweight smoke matrices before merge.
- Dependabot checks Python packages and GitHub Actions weekly. Compatible converter updates are grouped, next-major updates are surfaced separately for explicit adapter review, and `Dependency Resolution` verifies each optional extra in isolation.
- `requirements-upstream-watch.txt` records the direct converter versions under active compatibility monitoring; it is not a combined install profile.
- Pushing a matching `vX.Y.Z` tag runs the release workflow, builds wheel/sdist artifacts, extracts notes from `CHANGELOG.md`, and publishes a GitHub Release.

See [docs/release-process.md](docs/release-process.md) for the full checklist.

## Development

Typical local checks before a release:

```bash
python -m ruff check src tests config benchmark.py tools
python -m pytest -q
python -m build
python -m twine check dist/*
```

## License

MIT. See [LICENSE](LICENSE).
