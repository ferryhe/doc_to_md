# doc-to-markdown-converter
CLI tool that ingests documents, runs them through pluggable OCR/LLM engines (Mistral, DeepSeek-OCR, or a local extractor), and emits normalized Markdown plus optional assets.

## Feature highlights
- Typer-based CLI with `convert` and `list-engines` commands.
- Configurable engines, timeouts, and chunk sizes via `.env` or environment variables.
- Cloud APIs (Mistral, DeepSeek-OCR), LLM-based converters (Marker, MarkItDown), and local OCR/ML stacks (PaddleOCR, Docling, MinerU) supported side-by-side.
- PDF chunking/token accounting for Mistral OCR, token-based text chunking for DeepSeek-OCR.
- Lightweight local fallback that relies on the built-in text extraction pipeline.
- Deterministic logging and metrics that summarize every conversion run.

## Architecture at a glance
- `src/doc_to_md/cli.py` wires together configuration, document discovery, engine dispatch, post-processing, and writers.
- `src/doc_to_md/engines/` houses engine implementations (`mistral`, `deepseekocr`, `local`) that all return `EngineResponse` objects.
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
|       |-- cli.py
|       |-- engines/
|       |-- pipeline/
|       `-- utils/
|-- tests/
|-- .env.example
|-- pyproject.toml
`-- requirements.txt
```

## Installation
1. **Create environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Unix
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Install the package in editable mode for the console script:
   ```bash
   pip install -e .
   ```

## Configuration
1. Copy and edit the example environment file:
   ```bash
   cp .env.example .env
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
| `PADDLEOCR_*` | Language and PDF render DPI. | `en`, 220 DPI |
| `DOCLING_*` | Page limits / error handling. | Unlimited, strict |
| `MINERU_*` | Backend selection, parse method, language, page range. | `pipeline`, `auto`, `en` |
| `MARKER_*` | Whether to enable LLM processors, extra processors, image extraction. | LLM off, processors unset |

> ℹ️ **Optional dependencies**  
> New engines pull in sizeable third-party stacks. Install only what you need:
> ```bash
> # Pick any subset
> pip install markitdown            # MarkItDownEngine
> pip install paddleocr pypdfium2   # PaddleOCREngine (PDF support)
> pip install docling               # DoclingEngine
> pip install mineru                # MinerUEngine (GPU strongly recommended)
> pip install marker-pdf            # MarkerEngine
> pip install pypdfium2             # DeepSeek-OCR PDF rendering
> ```
> Each of these packages may have additional requirements (CUDA, LLM API keys, etc.); consult their upstream READMEs.
> Some stacks (e.g., MinerU vs. Marker) currently demand incompatible Pillow versions—install only what you plan to use in a given virtualenv.
> You can also rely on the extras defined in `pyproject.toml`, for example: `pip install ".[markitdown,paddleocr]"`, to pull in only the engines you need in a single command.

> ⚠️ **Remote engines vs. secrets**
> API keys are validated when their engine spins up (either because it is the default or because you explicitly pass `--engine`). You can leave `DEFAULT_ENGINE` pointing at a remote engine without its keys, but any conversion that uses that engine will still fail fast with a friendly error until the secrets are set.

`config/settings.py` automatically creates the configured `input_dir` and `output_dir` if they do not exist.

## Usage
You can invoke the CLI either through the module (`python -m doc_to_md.cli ...`) or via the console script (`doc-to-md ...` if installed with `pip install -e .`).

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

### List available engines
```bash
python -m doc_to_md.cli list-engines
```

## Docker Deployment

The project includes Docker support for easy deployment and consistent environments.

### Quick Start with Docker

1. **Build the image:**
   ```bash
   docker build -t doc-to-md:latest .
   ```

2. **Run a conversion:**
   ```bash
   mkdir -p data/input data/output
   # Place your documents in data/input/
   
   docker run --rm \
     -v $(pwd)/data:/app/data \
     doc-to-md:latest \
     doc-to-md convert \
     --input-path /app/data/input \
     --output-path /app/data/output \
     --engine local
   ```

### Using Docker Compose (Recommended)

1. **Configure environment:**
   Create a `.env` file (see `.env.example`)

2. **Run with docker-compose:**
   ```bash
   # Start with local engine
   docker-compose up doc-to-md
   
   # Or with Mistral OCR (requires API key)
   docker-compose --profile mistral up doc-to-md-mistral
   ```

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

### File Size and Format Limits

- **Maximum file size:** 100MB per file
- **Maximum image size:** 100 megapixels
- **Supported formats:** `.pdf`, `.docx`, `.png`, `.jpg`, `.jpeg`, `.txt`, `.md`
- **Not supported:** Legacy `.doc` format (please convert to `.docx` first)

### List available engines
```bash
python -m doc_to_md.cli list-engines
```

## Engines
- **Local** (`local`): wraps the internal text extraction pipeline and produces simple Markdown; great for smoke tests when APIs are unavailable.
- **Mistral** (`mistral`): uploads PDFs (optionally split to stay under token limits) and images to the Mistral OCR API, returning Markdown plus extracted page images.
- **DeepSeek OCR** (`deepseekocr`): renders PDFs/images and streams them to the DeepSeek-OCR vision model (falls back to local text extraction for unsupported formats).
- **MarkItDown** (`markitdown`): invokes Microsoft's MarkItDown library for high fidelity conversions across office formats without leaving your machine.
- **PaddleOCR** (`paddleocr`): runs PaddleOCR locally (CPU or GPU) against PDFs or images to reconstruct page-by-page Markdown summaries.
- **MinerU** (`mineru`): wraps the MinerU CLI pipeline, capturing the generated Markdown plus image assets from its output folders.
- **Docling** (`docling`): feeds documents into IBM's Docling pipeline and exports the resulting structured document back to Markdown.
- **Marker** (`marker`): drives the Marker PDF stack (without touching disk) and exposes its Markdown renderer alongside extracted images.

All engines implement `Engine.convert(Path) -> EngineResponse`, so adding another engine only requires subclassing the `Engine` protocol.

## Troubleshooting
- **Settings crash on startup**: Secret checks now happen inside each engine. If a remote engine fails to initialize, either export the matching API key (`MISTRAL_API_KEY`, `SILICONFLOW_API_KEY`, etc.) or run `convert --engine local` until the keys are available.
- **Engine import errors**: Optional stacks (Marker, MinerU, PaddleOCR, Docling, MarkItDown) are not installed automatically. Install the specific packages or use extras such as `pip install ".[marker,mineru]"` before invoking that engine.
- **Remote OCR timeouts**: Tune the `*_TIMEOUT_SECONDS`, `*_RETRY_ATTEMPTS`, and token/chunk settings in `.env` (e.g., `SILICONFLOW_MAX_INPUT_TOKENS`, `MISTRAL_MAX_PDF_TOKENS`) to match document sizes; each maps directly to validators in `config/settings.py`.

## Development & tests
- Run the unit tests: `pytest`
- Lint/format according to your preferred tooling (e.g., `ruff`, `black`) if you add them.
- When creating new engines, update `.env.example`, `ENGINE_REGISTRY` in `cli.py`, and extend the README/usage docs.

## Outputs
Converted Markdown files land in the `output_dir` you pass (or the default from `.env`). Binary artifacts (e.g., images rendered by Mistral) are written into `<stem>_assets/` subfolders beside the Markdown file so they can be embedded via relative links.

