# doc-to-markdown-converter
CLI tool that ingests documents, runs them through pluggable OCR/LLM engines (Mistral, SiliconFlow/DeepSeek-OCR, or a local extractor), and emits normalized Markdown plus optional assets.

## Feature highlights
- Typer-based CLI with `convert` and `list-engines` commands.
- Configurable engines, timeouts, and chunk sizes via `.env` or environment variables.
- PDF chunking/token accounting for Mistral OCR, token-based text chunking for SiliconFlow.
- Lightweight local fallback that relies on the built-in text extraction pipeline.
- Deterministic logging and metrics that summarize every conversion run.

## Architecture at a glance
- `src/doc_to_md/cli.py` wires together configuration, document discovery, engine dispatch, post-processing, and writers.
- `src/doc_to_md/engines/` houses engine implementations (`mistral`, `siliconflow`, `local`) that all return `EngineResponse` objects.
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
|   `-- output_siliconflow/
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
| `DEFAULT_ENGINE` | Engine used when `--engine` is omitted (`local`, `mistral`, `siliconflow`). | `local` |
| `MISTRAL_API_KEY` | Required when using the Mistral OCR engine. | _unset_ |
| `MISTRAL_DEFAULT_MODEL` | OCR model slug passed to Mistral. | `mistral-ocr-latest` |
| `SILICONFLOW_API_KEY` | Required for SiliconFlow / DeepSeek OCR. | _unset_ |
| `SILICONFLOW_DEFAULT_MODEL` | Model slug for SiliconFlow completions. | `deepseek-ai/DeepSeek-OCR` |
| `SILICONFLOW_BASE_URL` | API base URL (helpful for self-hosted gateways). | `https://api.siliconflow.cn/v1` |
| `*_TIMEOUT_SECONDS`, `*_RETRY_ATTEMPTS` | Per-engine network behavior. | See `.env.example` |
| `MISTRAL_MAX_PDF_TOKENS`, `MISTRAL_MAX_PAGES_PER_CHUNK` | Controls PDF slicing before OCR. | See `.env.example` |
| `SILICONFLOW_MAX_INPUT_TOKENS`, `SILICONFLOW_CHUNK_OVERLAP_TOKENS` | Controls text chunking before LLM calls. | See `.env.example` |

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

## Engines
- **Local** (`local`): wraps the internal text extraction pipeline and produces simple Markdown; great for smoke tests when APIs are unavailable.
- **Mistral** (`mistral`): uploads PDFs (optionally split to stay under token limits) and images to the Mistral OCR API, returning Markdown plus extracted page images.
- **SiliconFlow / DeepSeek OCR** (`siliconflow`): extracts raw text locally, chunks by tokens, and calls SiliconFlow's OpenAI-compatible completions endpoint to rebuild Markdown.

All engines implement `Engine.convert(Path) -> EngineResponse`, so adding another engine only requires subclassing the `Engine` protocol.

## Development & tests
- Run the unit tests: `pytest`
- Lint/format according to your preferred tooling (e.g., `ruff`, `black`) if you add them.
- When creating new engines, update `.env.example`, `ENGINE_REGISTRY` in `cli.py`, and extend the README/usage docs.

## Outputs
Converted Markdown files land in the `output_dir` you pass (or the default from `.env`). Binary artifacts (e.g., images rendered by Mistral) are written into `<stem>_assets/` subfolders beside the Markdown file so they can be embedded via relative links.

