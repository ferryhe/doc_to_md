# doc-to-markdown-converter
Convert actuarial papers, SFCRs, policy documents, and other source files into LLM-ready Markdown using pluggable OCR and extraction engines. The main purpose is to turn PDFs, scans, and office documents into text that is easier for large language models to read, chunk, index, review, and load into downstream actuarial knowledge bases or RAG workflows.

## Why this is useful for actuaries
- Prepare IAA papers, SFCRs, ORSAs, valuation reports, reserving memos, and internal guidance for LLM workflows.
- Compare multiple extraction engines because actuarial documents often mix prose, tables, appendices, and scanned pages.
- Keep Markdown and extracted assets on disk so a human can inspect the result before it is ingested elsewhere.

## Feature highlights
- Typer-based CLI with `convert` and `list-engines` commands.
- Configurable engines, timeouts, and chunk sizes via `.env` or environment variables.
- Cloud APIs (Mistral, DeepSeek-OCR), LLM-based converters (Marker, MarkItDown), and local OCR/ML stacks (PaddleOCR, Docling, MinerU) supported side-by-side.
- PDF chunking/token accounting for Mistral OCR, token-based text chunking for DeepSeek-OCR.
- Lightweight local fallback that relies on the built-in text extraction pipeline.
- Deterministic logging and metrics that summarize every conversion run.
- **Format-aware `auto` engine** that dispatches each file to its best sub-engine based on file extension — configure per-format engine selection via `.env`.
- **`html_local` engine** for extracting the main readable content from HTML pages (strips navigation, ads, and footers) using trafilatura → BeautifulSoup → regex fallback chain.
- HTML, HTM, PPTX, and XLSX files are now fully supported throughout the pipeline (loader, validation, extraction).
- PowerPoint (`.pptx`) converted slide-by-slide to Markdown sections; Excel (`.xlsx`) converted sheet-by-sheet to Markdown tables. Install via `pip install ".[office]"`.

## Architecture at a glance
- `src/doc_to_md/apps/` is where reusable application modules live; each app can expose its own `logic.py`, `cli.py`, and `router.py`.
- `src/doc_to_md/cli.py` is a compatibility entrypoint that delegates to the conversion app CLI.
- `src/doc_to_md/api.py` is the FastAPI entrypoint for HTTP-based integrations.
- `src/doc_to_md/engines/` houses the pluggable engine implementations, all of which return `EngineResponse` objects.
- `src/doc_to_md/pipeline/` contains reusable helpers: `loader`, `text_extraction`, `postprocessor`, `writer`, and `preprocessor`.
- `src/doc_to_md/utils/` holds shared logging and token utilities.
- `config/settings.py` (Pydantic) centralizes environment loading and validation so every module can call `get_settings()`.

## Folder structure
```text
doc_to_md/
|-- config/
|   `-- settings.py
|-- data/
|   |-- input/                # Drop source documents here by default
|   |-- output/               # Default output target
|   |-- output_local/
|   |-- output_mistral/
|   `-- output_deepseekocr/
|-- src/
|   `-- doc_to_md/
|       |-- api.py
|       |-- apps/
|       |   `-- conversion/
|       |       |-- logic.py
|       |       |-- cli.py
|       |       |-- router.py
|       |       `-- schemas.py
|       |-- cli.py
|       |-- engines/
|       |-- pipeline/
|       `-- utils/
|-- tests/
|-- .env.example
|-- pyproject.toml
|-- requirements-core.txt    ← core + docling + mistral (CPU torch, no GPU extras)
`-- requirements.txt         ← full GPU stack (+ PaddleOCR / MinerU / Marker)
```

## Installation

### Prerequisites
- Git
- Python 3.10.x recommended
- Python 3.11.x 3.12 also works

`pyproject.toml` declares Python `>=3.10,<3.13`, so Python 3.13 and newer are intentionally unsupported and standard installers should refuse to install the package on those interpreters. For the full document-conversion stack it is still safest to stay on Python 3.10 or 3.11 instead of the newest interpreter, because several optional OCR/ML dependencies lag behind new Python releases. For example, MinerU notes that on Windows its `ray` dependency does not support Python 3.13. If you want the safest baseline, use Python 3.10.11.

1. **Clone the repository**
   ```bash
   git clone https://github.com/ferryhe/doc_to_md.git
   cd doc_to_md
   ```
2. **Create and activate a virtual environment**
   ```bash
   py -3.10 -m venv .venv        # Windows
   python3.10 -m venv .venv      # Unix/macOS

   .venv\Scripts\activate        # Windows
   source .venv/bin/activate     # Unix/macOS
   ```
3. **Install the package in editable mode**
   ```bash
   pip install -e .
   ```

4. **Add only the extras or engine packages you actually need**
   ```bash
   pip install ".[api]"               # FastAPI + uvicorn
   pip install ".[html]"              # trafilatura for best-quality HTML content extraction
   pip install ".[office]"            # python-pptx + openpyxl for PPTX and XLSX support
   pip install ".[markitdown]"        # MarkItDown with PDF support
   pip install ".[paddleocr,docling]" # Example mixed setup
   ```

5. **Optional: install a pinned dependency stack**

   Two pre-built requirement files are provided so you can pin the full transitive
   dependency tree without resolving it yourself:

   | File | Engines covered | Torch variant |
   |------|-----------------|---------------|
   | `requirements-core.txt` | `local` · `mistral` · `deepseekocr` · `markitdown` · `html_local` · `auto` · `office` · **`docling`** | CPU (`torch==2.2.2`) |
   | `requirements.txt` | Everything above + `paddleocr` · `mineru` · `marker` | CUDA 12.1 (`torch==2.2.2+cu121`) |

   ```bash
   # Lightweight — no CUDA required (docling works on CPU)
   pip install -r requirements-core.txt

   # Full GPU stack — PaddleOCR / MinerU / Marker + CUDA 12.1 torch
   pip install -r requirements.txt
   ```

   Both files are annotated with comments that show which engine each package belongs
   to, so you can easily identify what you can omit if you are building a custom
   environment.

The recommended default path is `pip install -e .` plus selected extras. The pinned
requirements files are provided for reproducible environments; for GPU machines you may
need to adjust the `torch` wheel URL to match your CUDA version.

## Configuration
1. Copy and edit the example environment file:
   ```bash
   copy .env.example .env      # Windows
   cp .env.example .env        # Unix/macOS
   ```
2. Populate API keys and overrides. Key variables:

| Variable | Description | Default |
| --- | --- | --- |
| `DEFAULT_ENGINE` | Engine used when `--engine` is omitted (`local`, `mistral`, `deepseekocr`). | `local` |
| `MISTRAL_API_KEY` | Required when using the Mistral OCR engine. | _unset_ |
| `MISTRAL_DEFAULT_MODEL` | OCR model slug passed to Mistral. | `mistral-ocr-latest` |
| `SILICONFLOW_API_KEY` | Required for the DeepSeek-OCR engine (served via SiliconFlow). | _unset_ |
| `SILICONFLOW_DEFAULT_MODEL` | Model slug for DeepSeek OCR completions. | `deepseek-ai/DeepSeek-OCR` |
| `SILICONFLOW_BASE_URL` | SiliconFlow API base URL (helpful for regional gateways). | `https://api.siliconflow.cn/v1` |
| `*_TIMEOUT_SECONDS`, `*_RETRY_ATTEMPTS` | Per-engine network behavior. | See `.env.example` |
| `MISTRAL_MAX_PDF_TOKENS`, `MISTRAL_MAX_PAGES_PER_CHUNK` | Controls PDF slicing before OCR. | See `.env.example` |
| `SILICONFLOW_MAX_INPUT_TOKENS`, `SILICONFLOW_CHUNK_OVERLAP_TOKENS` | Controls text chunking before LLM calls. | See `.env.example` |
| `MARKITDOWN_*` | Toggles for MarkItDown's plugin/builtin usage. | Enabled |
| `PADDLEOCR_*` | Language and PDF render DPI. | `en`, 220 DPI |
| `DOCLING_*` | Page limits / error handling. | Unlimited, strict |
| `MINERU_*` | Backend selection, parse method, language, page range. | `pipeline`, `auto`, `en` |
| `MARKER_*` | Whether to enable LLM processors, extra processors, image extraction. | LLM off, processors unset |
| `AUTO_PDF_ENGINE` | Sub-engine used by `auto` for `.pdf` files. | `local` |
| `AUTO_DOCX_ENGINE` | Sub-engine used by `auto` for `.docx` files. | `local` |
| `AUTO_PPTX_ENGINE` | Sub-engine used by `auto` for `.pptx` files. | `local` |
| `AUTO_SPREADSHEET_ENGINE` | Sub-engine used by `auto` for `.xlsx` files. | `local` |
| `AUTO_HTML_ENGINE` | Sub-engine used by `auto` for `.html`/`.htm` files. | `html_local` |
| `AUTO_IMAGE_ENGINE` | Sub-engine used by `auto` for `.png`/`.jpg`/`.jpeg` files. | `local` |
| `AUTO_TEXT_ENGINE` | Sub-engine used by `auto` for `.txt`/`.md` files. | `local` |

**Per-engine dependencies — install only what you use**

Each engine requires its own set of packages. Install only the ones you plan to use:

| Engine | Install command | Notes |
|--------|----------------|-------|
| `local` | _(included in base install)_ | PDF · DOCX · images · text; pytesseract for OCR |
| `html_local` | `pip install ".[html]"` | trafilatura for best-quality extraction; falls back to bs4 (built-in) |
| `office` extra | `pip install ".[office]"` | python-pptx (PPTX) + openpyxl (XLSX) |
| `auto` | _(no extra packages)_ | Routes files to the engine above per format |
| `mistral` | _(included in base install)_ | API key: `MISTRAL_API_KEY` |
| `deepseekocr` | `pip install pypdfium2` | API key: `SILICONFLOW_API_KEY`; pypdfium2 renders PDFs |
| `markitdown` | `pip install ".[markitdown]"` | Pulls in `markitdown[pdf]` |
| `docling` | `pip install ".[docling]"` | Heavy transformer stack; CPU torch works, GPU optional |
| `paddleocr` | `pip install ".[paddleocr]"` | Requires CUDA GPU; installs opencv + pyclipper |
| `mineru` | `pip install ".[mineru]"` | GPU strongly recommended |
| `marker` | `pip install ".[marker]"` | GPU strongly recommended |
| `api` server | `pip install ".[api]"` | FastAPI + uvicorn |

Quick pick-and-mix examples:

```bash
pip install ".[api]"               # FastAPI + uvicorn HTTP interface
pip install ".[html]"              # trafilatura for richer HTML content extraction
pip install ".[office]"            # python-pptx + openpyxl for PPTX and XLSX
pip install ".[markitdown]"        # MarkItDown with PDF support
pip install ".[paddleocr,docling]" # PaddleOCR + Docling together
pip install ".[api,html]"          # API server + best-quality HTML extraction
pip install ".[api,office]"        # API server + PPTX/XLSX support
```

**Remote engines vs. secrets**

API keys are validated when their engine spins up (either because it is the default or because you explicitly pass `--engine`). You can leave `DEFAULT_ENGINE` pointing at a remote engine without its keys, but any conversion that uses that engine will still fail fast with a friendly error until the secrets are set.

`config/settings.py` automatically creates the configured `input_dir` and `output_dir` if they do not exist.

## Usage
Because this project uses a `src/` layout, run `pip install -e .` first. After that, you can invoke the CLI either through the module (`python -m doc_to_md.cli ...`) or via the console script (`doc-to-md ...`).

### Convert documents
```bash
python -m doc_to_md.cli convert \
  --input-path data/input \
  --output-path data/output_mistral \
  --engine mistral \
  --model mistral-ocr-latest
```

Common flags:
- `--since 2025-05-01T00:00:00`: skip files modified before the timestamp.
- `--dry-run`: list candidates without converting or writing files.
- `--engine` / `--model`: override the defaults defined in `.env`.

### Convert HTML files

Use `html_local` to extract the main readable content from a web page, stripping navigation, footers, and ads:

```bash
# Extract core content from a saved HTML file
python -m doc_to_md.cli convert \
  --input-path data/input \
  --output-path data/output_html \
  --engine html_local

# Optionally install trafilatura for best-quality article extraction
pip install ".[html]"
```

### Use the auto engine (format-aware routing)

The `auto` engine inspects each file's extension and dispatches it to the best sub-engine automatically:

```bash
# Convert a mixed folder (PDFs, DOCX, HTML, images) in one command
python -m doc_to_md.cli convert \
  --input-path data/input \
  --output-path data/output \
  --engine auto
```

You can customise per-format routing in `.env`:

```bash
DEFAULT_ENGINE=auto

# Use Mistral OCR for all PDFs, html_local for HTML, MarkItDown for DOCX
AUTO_PDF_ENGINE=mistral
AUTO_HTML_ENGINE=html_local
AUTO_DOCX_ENGINE=markitdown
AUTO_PPTX_ENGINE=local
AUTO_SPREADSHEET_ENGINE=local
AUTO_IMAGE_ENGINE=local
AUTO_TEXT_ENGINE=local
```

### List available engines
```bash
python -m doc_to_md.cli list-engines
# Output: local, mistral, deepseekocr, markitdown, paddleocr, mineru, docling, marker, html_local, auto
```

### Run the FastAPI server
Install the API extra first:

```bash
pip install ".[api]"
```

Then start the server with either command:

```bash
doc-to-md-api
uvicorn doc_to_md.api:app --reload
```

Available endpoints:
- `GET /health`
- `GET /apps/conversion/health`
- `GET /apps/conversion/engines`
- `POST /apps/conversion/convert`

Example: convert a folder with the `auto` engine via the HTTP API:

```bash
curl -X POST http://localhost:8000/apps/conversion/convert \
  -H "Content-Type: application/json" \
  -d '{
    "input_path": "data/input",
    "output_path": "data/output",
    "engine": "auto"
  }'
```

Example: extract HTML content via the API:

```bash
curl -X POST http://localhost:8000/apps/conversion/convert \
  -H "Content-Type: application/json" \
  -d '{
    "input_path": "data/input",
    "output_path": "data/output_html",
    "engine": "html_local"
  }'
```

### CLI + FastAPI app structure
The conversion app is intentionally split so the same business logic can be reused from both terminal and HTTP entrypoints:

- `src/doc_to_md/apps/conversion/logic.py`: shared conversion workflow, engine resolution, metrics, and file processing
- `src/doc_to_md/apps/conversion/cli.py`: Typer wrapper around the shared conversion logic
- `src/doc_to_md/apps/conversion/router.py`: FastAPI router exposing the same conversion workflow over HTTP
- `src/doc_to_md/api.py`: FastAPI application bootstrap
- `src/doc_to_md/cli.py`: backward-compatible CLI entrypoint

### File Size and Format Limits
- **Maximum file size:** 100MB per file
- **Maximum image size:** 100 megapixels
- **Supported formats:** `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.html`, `.htm`, `.png`, `.jpg`, `.jpeg`, `.txt`, `.md`
- **Not supported:** legacy `.doc` and `.xls` formats (please convert to `.docx` / `.xlsx` first)
- **Optional extras needed:** `.pptx` and `.xlsx` require `pip install ".[office]"`; `.html`/`.htm` uses built-in bs4 by default (install `".[html]"` for best-quality extraction with trafilatura)

## Actuarial example: one IAA paper, two very different outputs
The [IAA Artificial Intelligence Governance Framework paper](https://actuaries.org/app/uploads/2025/12/AITF_Governance_Framework_Paper_Final_Approved.pdf) is a good test document because it looks like many real actuarial inputs: a long PDF with headings, tables of contents, page furniture, and layout-sensitive content.

1. Save the PDF as `data/examples/iaa-ai-governance-framework.pdf`.
2. Convert it with two engines:
   ```bash
   python -m doc_to_md.cli convert --input-path data/examples --output-path data/output_markitdown --engine markitdown
   python -m doc_to_md.cli convert --input-path data/examples --output-path data/output_mistral --engine mistral --model mistral-ocr-latest
   ```
3. Compare the two Markdown files.

In a real run on that paper:
- `markitdown` produced flatter, text-first Markdown with fewer structural markers and no extracted page images.
- `mistral` produced page-aware Markdown with explicit page headings, stronger heading recovery, and image assets beside the `.md` file.

Example snippets:

```md
# MarkItDown-style excerpt
Artificial Intelligence Governance Framework

Table of Contents
1. Introduction ...
```

```md
# Mistral-style excerpt
## Page 2
# IAA Paper
# Artificial Intelligence Governance Framework
![Page 2 Image 1](...)
```

For actuarial work, that difference matters. If your downstream task is mostly semantic search over narrative text, a flatter output may be enough. If page structure, embedded figures, or layout fidelity matter, test a layout-aware engine such as `mistral` on a representative sample before bulk-converting SFCRs or internal reports.

## Engines
- **Local** (`local`): wraps the internal text extraction pipeline and produces simple Markdown; great for smoke tests when APIs are unavailable.
- **Mistral** (`mistral`): uploads PDFs (optionally split to stay under token limits) and images to the Mistral OCR API, returning Markdown plus extracted page images.
- **DeepSeek OCR** (`deepseekocr`): renders PDFs/images and streams them to the DeepSeek-OCR vision model (falls back to local text extraction for unsupported formats).
- **MarkItDown** (`markitdown`): invokes Microsoft's MarkItDown library for local conversions across office formats and PDFs.
- **PaddleOCR** (`paddleocr`): runs PaddleOCR locally (CPU or GPU) against PDFs or images to reconstruct page-by-page Markdown summaries.
- **MinerU** (`mineru`): wraps the MinerU CLI pipeline, capturing the generated Markdown plus image assets from its output folders.
- **Docling** (`docling`): feeds documents into IBM's Docling pipeline and exports the resulting structured document back to Markdown.
- **Marker** (`marker`): drives the Marker PDF stack (without touching disk) and exposes its Markdown renderer alongside extracted images.
- **HTML Local** (`html_local`): purpose-built HTML content extractor. Extracts the main readable body of a web page, discarding navigation, sidebars, ads, and footers. Uses a three-tier fallback — trafilatura (best, optional) → BeautifulSoup (built-in) → regex tag-stripper (zero-dep). Install `trafilatura` via `pip install ".[html]"` for highest-quality article extraction.
- **Auto** (`auto`): format-aware dispatcher that routes each file to the best-configured sub-engine based on its extension. Defaults: HTML/HTM → `html_local`, all others → `local`. Fully configurable via `AUTO_*_ENGINE` settings in `.env` (including `AUTO_PPTX_ENGINE` and `AUTO_SPREADSHEET_ENGINE`).

All engines implement `Engine.convert(Path) -> EngineResponse`, so adding another engine only requires subclassing the `Engine` protocol.

## Troubleshooting
- **`python -m doc_to_md.cli ...` fails with `ModuleNotFoundError`**: run `pip install -e .` from the repository root first.
- **Python 3.13 or 3.14 installation fails**: this project intentionally declares `>=3.10,<3.13` in `pyproject.toml`. Use Python 3.10.x or 3.11.x instead; if you want the most conservative choice, use Python 3.10.11.
- **Some engines work on one Python version and fail on another**: optional OCR/ML engines have their own dependency trees. For example, MinerU notes that its Windows install is limited to Python 3.10-3.12 because `ray` does not support Python 3.13 there.
- **MarkItDown cannot read PDFs**: install the PDF extra with `pip install "markitdown[pdf]"`.
- **Settings crash on startup**: secret checks now happen inside each engine. If a remote engine fails to initialize, either export the matching API key (`MISTRAL_API_KEY`, `SILICONFLOW_API_KEY`, etc.) or run `convert --engine local` until the keys are available.
- **Engine import errors**: optional stacks (Marker, MinerU, PaddleOCR, Docling, MarkItDown) are not installed automatically. Install the specific packages or use extras such as `pip install ".[marker,mineru]"` before invoking that engine.
- **Remote OCR timeouts**: tune the `*_TIMEOUT_SECONDS`, `*_RETRY_ATTEMPTS`, and token/chunk settings in `.env` (for example `SILICONFLOW_MAX_INPUT_TOKENS`, `MISTRAL_MAX_PDF_TOKENS`) to match document sizes; each maps directly to validators in `config/settings.py`.

## Engine Benchmarking
The project includes a benchmarking tool for comparing engines on representative documents. The generated comparison report is currently written in Chinese, while the maintained usage guide lives in [README_BENCHMARK.md](README_BENCHMARK.md).

### Quick Start
```bash
# Test all available engines
python benchmark.py

# Test specific engines
python benchmark.py --engines local markitdown paddleocr

# Use your own test file
python benchmark.py --test-file path/to/document.pdf --engines local mistral

# Save results in both Markdown and JSON
python benchmark.py --save-json --output-dir my_results
```

### Features
- **Automated Testing**: tests multiple engines with a single command
- **Performance Metrics**: measures conversion time, success rate, and output characteristics (Markdown length and asset count)
- **Chinese Report**: generates comprehensive comparison reports in Chinese (中文对比报告)
- **Engine Analysis**: provides detailed pros/cons and use case recommendations
- **Flexible Configuration**: test specific engines or all available ones

> **Note**: The script `benchmark.py` is for use from a source checkout. Run it from the project root directory.

### Report Contents
The generated report includes:
- Overall statistics and success rates
- Performance rankings by conversion time
- Detailed engine characteristics analysis
- Recommendations for different use cases
- Error diagnostics for failed conversions

### Example Usage Scenarios
1. **Choosing the right engine**: compare all engines to find the best one for your documents
2. **Performance validation**: verify engine performance before production deployment
3. **Quality assessment**: compare output quality across different engines
4. **Cost analysis**: evaluate free vs. paid engine options

## Development & tests
- Run the full test suite: `pytest`
- Current baseline in this branch: `85 passed, 2 skipped`
- Test coverage currently includes CLI behavior, FastAPI endpoints, shared conversion logic, settings validation, file validation, extraction/pipeline helpers, HTML engine, auto-routing engine, and PPTX/XLSX extraction
- Run engine benchmarks: `python benchmark.py`
- Run the API locally: `uvicorn doc_to_md.api:app --reload` after `pip install ".[api]"`
- Lint/format according to your preferred tooling (for example `ruff`, `black`) if you add them.
- When creating new engines, update `.env.example`, `ENGINE_REGISTRY` in `logic.py`, and extend the README/usage docs.

## Outputs
Converted Markdown files land in the `output_dir` you pass (or the default from `.env`). Binary artifacts (for example images rendered by Mistral) are written into `<stem>_assets/` subfolders beside the Markdown file so they can be embedded via relative links.
