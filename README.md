# doc-to-markdown-converter

Convert PDFs, scans, office documents, HTML, and plain text into LLM-ready Markdown with a Typer CLI, a FastAPI layer, and pluggable extraction engines.

This repository is aimed at source documents such as actuarial papers, SFCRs, ORSAs, valuation reports, internal guidance, policy documents, and other materials that need cleanup before indexing, review, chunking, or downstream RAG use.

## Highlights

- `src/` layout packaged as `doc_to_md`
- Typer CLI with `convert` and `list-engines`
- FastAPI app for HTTP conversion workflows
- Multiple local and remote extraction engines
- Format-aware `auto` engine with per-format routing from `.env`
- Built-in support for PDF, DOCX, PPTX, XLSX, HTML, images, TXT, and Markdown
- Benchmark script for side-by-side engine comparison
- MIT licensed

## Project layout

```text
doc_to_md/
|-- data/
|   |-- input/
|   `-- output/
|-- src/
|   `-- doc_to_md/
|       |-- api.py
|       |-- cli.py
|       |-- apps/
|       |   `-- conversion/
|       |       |-- cli.py
|       |       |-- logic.py
|       |       |-- router.py
|       |       `-- schemas.py
|       |-- config/
|       |   `-- settings.py
|       |-- engines/
|       |-- pipeline/
|       `-- utils/
|-- tests/
|-- benchmark.py
|-- README.md
|-- README_BENCHMARK.md
`-- pyproject.toml
```

## Python support

- Supported: Python `>=3.10,<3.13`
- Recommended: Python 3.10 or 3.11
- Intentionally unsupported: Python 3.13 and newer

Several optional OCR and ML dependencies lag behind the newest Python releases, so 3.10 or 3.11 remains the safest default.

## Installation

### From a source checkout

```bash
git clone https://github.com/ferryhe/doc_to_md.git
cd doc_to_md

# Windows
py -3.10 -m venv .venv
.venv\Scripts\activate

# Unix/macOS
python3.10 -m venv .venv
source .venv/bin/activate

pip install -e .
```

### Optional extras

Install only the extras you actually need:

```bash
pip install ".[api]"
pip install ".[html]"
pip install ".[office]"
pip install ".[markitdown]"
pip install ".[docling]"
pip install ".[paddleocr]"
pip install ".[mineru]"
pip install ".[marker]"
pip install ".[opendataloader]"
```

If you are installing from a published package instead of a source checkout, replace `".[extra]"` with `doc-to-markdown-converter[extra]`.

### Pinned dependency sets

Two requirement files are included for reproducible environments:

| File | Coverage |
| --- | --- |
| `requirements-core.txt` | Core stack plus `docling` |
| `requirements.txt` | Full stack including GPU-oriented engines |

Examples:

```bash
# CPU-oriented setup
pip install -r requirements-core.txt

# Full stack
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and fill in only the settings you need:

```bash
# Windows
copy .env.example .env

# Unix/macOS
cp .env.example .env
```

Settings are centralized in `doc_to_md.config.settings`.

### Key variables

| Variable | Purpose | Default |
| --- | --- | --- |
| `DEFAULT_ENGINE` | Default engine when `--engine` is omitted | `local` |
| `MISTRAL_API_KEY` | Required for the Mistral OCR engine | unset |
| `SILICONFLOW_API_KEY` | Required for the DeepSeek OCR engine | unset |
| `MISTRAL_DEFAULT_MODEL` | Default Mistral OCR model | `mistral-ocr-latest` |
| `SILICONFLOW_DEFAULT_MODEL` | Default DeepSeek OCR model | `deepseek-ai/DeepSeek-OCR` |
| `AUTO_PDF_ENGINE` | Auto-engine route for PDF | `local` |
| `AUTO_DOCX_ENGINE` | Auto-engine route for DOCX | `local` |
| `AUTO_PPTX_ENGINE` | Auto-engine route for PPTX | `local` |
| `AUTO_SPREADSHEET_ENGINE` | Auto-engine route for XLSX | `local` |
| `AUTO_HTML_ENGINE` | Auto-engine route for HTML and HTM | `html_local` |
| `AUTO_IMAGE_ENGINE` | Auto-engine route for PNG, JPG, and JPEG | `local` |
| `AUTO_TEXT_ENGINE` | Auto-engine route for TXT and MD | `local` |
| `OPENDATALOADER_HYBRID` | Optional hybrid backend for complex PDF pages | unset |
| `OPENDATALOADER_USE_STRUCT_TREE` | Enable structure-tree aware extraction for tagged PDFs | `false` |

### Engine dependency notes

| Engine | Install note | Notes |
| --- | --- | --- |
| `local` | Included in the base install | Internal extraction pipeline for PDF, DOCX, images, text, PPTX, and XLSX |
| `html_local` | `pip install ".[html]"` for best extraction quality | Uses `trafilatura`, then falls back to built-in HTML parsing |
| `mistral` | Base install plus `MISTRAL_API_KEY` | Remote OCR API |
| `deepseekocr` | Base install plus `SILICONFLOW_API_KEY` | Remote OCR API via SiliconFlow |
| `markitdown` | `pip install ".[markitdown]"` | Microsoft MarkItDown-based conversion |
| `docling` | `pip install ".[docling]"` | Heavy transformer stack |
| `paddleocr` | `pip install ".[paddleocr]"` | GPU-friendly OCR path |
| `mineru` | `pip install ".[mineru]"` | GPU strongly recommended |
| `marker` | `pip install ".[marker]"` | GPU strongly recommended |
| `opendataloader` | `pip install ".[opendataloader]"` | PDF-only, requires Java 11+ on `PATH` |
| `api` | `pip install ".[api]"` | FastAPI plus uvicorn |
| `office` support | `pip install ".[office]"` | Installs PPTX and XLSX helpers |

## CLI usage

Install the package first with `pip install -e .`.

### Convert documents

```bash
python -m doc_to_md.cli convert \
  --input-path data/input \
  --output-path data/output \
  --engine local
```

Common flags:

- `--engine` / `--model`
- `--since 2025-05-01T00:00:00`
- `--dry-run`
- `--no-page-info`

### Auto engine

```bash
python -m doc_to_md.cli convert \
  --input-path data/input \
  --output-path data/output \
  --engine auto
```

Example routing:

```bash
DEFAULT_ENGINE=auto
AUTO_PDF_ENGINE=opendataloader
AUTO_HTML_ENGINE=html_local
AUTO_DOCX_ENGINE=markitdown
AUTO_PPTX_ENGINE=local
AUTO_SPREADSHEET_ENGINE=local
AUTO_IMAGE_ENGINE=local
AUTO_TEXT_ENGINE=local
```

### List engines

```bash
python -m doc_to_md.cli list-engines
# Output: local, mistral, deepseekocr, markitdown, paddleocr, mineru, docling, marker, html_local, auto, opendataloader
```

### Use the OpenDataLoader engine

`opendataloader` is a Java-backed PDF parser. Java 11 or newer must be installed and available on `PATH`.

Check Java:

```bash
java -version
```

Typical installation commands:

- Ubuntu or Debian: `sudo apt install default-jre`
- macOS with Homebrew: `brew install openjdk@17`
- Windows: <https://adoptium.net/>

Examples:

```bash
python -m doc_to_md.cli convert \
  --input-path data/input \
  --output-path data/output \
  --engine opendataloader
```

Hybrid mode for harder tables or scanned pages:

```bash
# Windows PowerShell
$env:OPENDATALOADER_HYBRID="docling-fast"
python -m doc_to_md.cli convert --input-path data/input --output-path data/output --engine opendataloader

# Unix/macOS
OPENDATALOADER_HYBRID=docling-fast \
python -m doc_to_md.cli convert --input-path data/input --output-path data/output --engine opendataloader
```

## API usage

Install the API extra first:

```bash
pip install ".[api]"
```

Start the server:

```bash
doc-to-md-api
# or
uvicorn doc_to_md.api:app --reload
```

Available endpoints:

- `GET /health`
- `GET /apps/conversion/health`
- `GET /apps/conversion/engines`
- `POST /apps/conversion/convert`

Example request:

```bash
curl -X POST http://localhost:8000/apps/conversion/convert \
  -H "Content-Type: application/json" \
  -d '{
    "input_path": "data/input",
    "output_path": "data/output",
    "engine": "mistral",
    "no_page_info": true
  }'
```

## Supported formats and validation

- Supported file types: `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.html`, `.htm`, `.png`, `.jpg`, `.jpeg`, `.txt`, `.md`
- Legacy `.doc` is rejected explicitly
- Files must be non-empty and readable
- The validation layer rejects files larger than 100 MB

## Engines

- `local`: lightweight internal extraction pipeline
- `mistral`: Mistral OCR API, with optional PDF chunking and page-aware output
- `deepseekocr`: DeepSeek OCR via SiliconFlow
- `markitdown`: Microsoft MarkItDown-based local conversion
- `paddleocr`: local PaddleOCR pipeline for PDFs and images
- `mineru`: MinerU pipeline wrapper
- `docling`: IBM Docling pipeline wrapper
- `marker`: Marker PDF integration
- `html_local`: main-content HTML extraction with `trafilatura` fallback logic
- `auto`: format-aware dispatcher configured from settings
- `opendataloader`: Java-backed PDF conversion via `opendataloader-pdf`

All engines implement `Engine.convert(Path) -> EngineResponse`.

## Benchmarking

The repository includes `benchmark.py` for comparing engines on representative documents. Usage and examples are documented in [README_BENCHMARK.md](README_BENCHMARK.md).

Quick examples:

```bash
python benchmark.py
python benchmark.py --engines local markitdown
python benchmark.py --test-file path/to/document.pdf --save-json
```

## Troubleshooting

- If `python -m doc_to_md.cli ...` fails with `ModuleNotFoundError`, install the package first with `pip install -e .`.
- If installation fails on Python 3.13 or 3.14, switch to Python 3.10, 3.11, or 3.12.
- If a remote engine fails to initialize, make sure the matching API key is set.
- If an optional engine import fails, install the matching extra or package for that engine.
- If `opendataloader` fails before conversion starts, verify `java -version` returns Java 11 or newer.
- If remote OCR times out, tune the `*_TIMEOUT_SECONDS`, `*_RETRY_ATTEMPTS`, and chunk or token settings in `.env`.

## Development and release checks

Typical local checks:

```bash
python -m ruff check src tests config benchmark.py
python -m pytest -q
python -m build
python -m twine check dist/*
pip install -e .
```

The repository also includes GitHub Actions CI for `ruff`, `pytest`, `build`, and `twine check` across Python 3.10 to 3.12.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
