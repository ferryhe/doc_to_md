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

For the current recommended PDF setup:

```bash
pip install -r requirements-recommended-pdf.txt
```

That setup keeps:

- `local`
- `markitdown`
- `opendataloader`
- `docling`
- `mistral`
- `mathpix`

Notes:

- `local`, `mistral`, and `mathpix` are part of the base package
- `mistral` needs `MISTRAL_API_KEY`
- `mathpix` needs `MATHPIX_APP_ID` and `MATHPIX_APP_KEY`
- `opendataloader` needs Java 11+ on `PATH`

Other install targets:

| Use case | Command |
| --- | --- |
| Recommended PDF setup | `pip install -r requirements-recommended-pdf.txt` |
| Broader CPU environment | `pip install -r requirements-core.txt` |
| Full heavy stack | `pip install -r requirements.txt` |
| MinerU 3.x pipeline or hybrid | `pip install -e ".[mineru]"` |
| MinerU2.5-Pro remote client | `pip install -e ".[mineru-pro]"` |
| MinerU2.5-Pro local transformers | `pip install -e ".[mineru-pro-local]"` |
| Dev and test overlay | `pip install -r requirements-dev.txt` |

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
- `mineru`
- `mineru_pro`
- `marker`
- `deepseekocr`
- `html_local`
- `auto`

MinerU note:

- `mineru` now targets the MinerU 3.x package path and still represents the classic MinerU pipeline/hybrid engine.
- `mineru_pro` is a separate MinerU2.5-Pro VLM entry point. By default it expects `MINERU_PRO_SERVER_URL` for a running MinerU2.5-Pro service; local `transformers` use is intentionally opt-in through `.[mineru-pro-local]` because it is a heavy model path.
- The upstream MinerU2.5-Pro model card lists AGPL-3.0 licensing, so keep it as an explicit optional path when license boundaries matter.

## Read next

Use the rest of the docs this way:

- [PDF_ENGINE_EVALUATION.md](PDF_ENGINE_EVALUATION.md): the main evaluation document
  Includes benchmark method, install tradeoffs, routing rules, and real-PDF testing workflow.
- [benchmark_results/README.md](benchmark_results/README.md): archived benchmark artifacts
  Includes the tracked general-text, printed-formula, and handwritten-formula suites.
- [API_RESPONSE_CONTRACT.md](API_RESPONSE_CONTRACT.md): stable API field shapes
- [skills/doc_to_md_agent/SKILL.md](skills/doc_to_md_agent/SKILL.md): agent workflow guidance

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
