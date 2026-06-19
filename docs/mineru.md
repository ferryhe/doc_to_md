# MinerU Engine Governance

MinerU is supported as a **beta optional engine**. It is useful for complex PDF and RAG-oriented extraction workflows, but its dependency tree is heavier and more fragile than the default local, MarkItDown, OpenDataLoader, Mistral, and Mathpix paths.

## Support level

- Package extra: `mineru`
- Engine name: `mineru`
- Current support label: **beta**
- Main package dependency: not included in the base install or the recommended PDF install
- Recommended environment: isolated virtual environment with a large disk
- Python range: follows this package, `>=3.10,<3.13`
- Practical disk expectation: treat MinerU as a **20 GB+ free-disk** workflow because the pipeline install, model downloads, and benchmark artifacts can grow quickly

Use the default or recommended PDF engines first unless you specifically need MinerU's parsing pipeline.

## Current install finding

A fresh Linux / Python 3.11 probe on 2026-06-18 showed that a light `mineru` install is not enough for a real conversion:

| Probe | Installed size | Result |
| --- | ---: | --- |
| `python -m pip install -e '.[mineru]'` when the extra only installed bare `mineru` | about `598 MB` | adapter import worked, real PDF conversion failed with `ModuleNotFoundError: No module named 'torch'` |
| same install plus CPU `torch==2.2.2+cpu` / `torchvision==0.17.2+cpu` | about `1.4 GB` | conversion moved further, then failed with `ModuleNotFoundError: No module named 'transformers'` |

Root cause: MinerU 3.x keeps the actual pipeline runtime behind its own `pipeline` extra. A bare `mineru` dependency can install and import, but it does not provide the dependencies needed by `do_parse(...)` for the pipeline backend.

Decision for this repository:

- `requirements-recommended-pdf.txt` intentionally excludes MinerU.
- `pyproject.toml` maps this repository's `mineru` extra to `mineru[pipeline]` so `doc-to-markdown-converter[mineru]` is honest about the runtime it needs.
- `constraints-mineru.txt` is a CPU-pipeline constraint overlay for experimental validation, not a general-purpose lock file.
- Do not promote MinerU out of beta until a real conversion succeeds in an environment with enough free disk and the resulting model/cache footprint is recorded.

## Installation

Create an isolated environment first. Do not install MinerU into the normal development or recommended PDF environment.

CPU pipeline probe:

```bash
python -m venv .venv-mineru
. .venv-mineru/bin/activate
python -m pip install --upgrade pip
python -m pip install \
  --extra-index-url https://download.pytorch.org/whl/cpu \
  -e '.[mineru]' \
  -c constraints-mineru.txt
```

The `--extra-index-url` is important for the CPU PyTorch wheels pinned by `constraints-mineru.txt`. Without it, pip may choose much larger default Linux wheels.

For an installed package instead of an editable checkout, first download or copy the matching `constraints-mineru.txt` from this repository, then use the same pattern:

```bash
python -m pip install \
  --extra-index-url https://download.pytorch.org/whl/cpu \
  'doc-to-markdown-converter[mineru]' \
  -c constraints-mineru.txt
```

## Runtime settings

MinerU is configured through environment variables or `Settings` fields:

| Variable | Default | Purpose |
| --- | --- | --- |
| `MINERU_BACKEND` | `pipeline` | MinerU backend passed to `do_parse` |
| `MINERU_PARSE_METHOD` | `auto` | Pipeline parse method and output subfolder |
| `MINERU_LANG` | `en` | Language list value passed to MinerU |
| `MINERU_FORMULA_ENABLE` | `true` | Enable formula extraction |
| `MINERU_TABLE_ENABLE` | `true` | Enable table extraction |
| `MINERU_START_PAGE` | `0` | Zero-based start page |
| `MINERU_END_PAGE` | unset | Optional end page |

For CPU-only smoke tests, set:

```bash
export MINERU_DEVICE_MODE=cpu
```

## Smoke validation

Lightweight CI should exercise the adapter without installing MinerU's heavy runtime:

```bash
python -m pytest tests/test_mineru_engine.py -q
```

A real MinerU acceptance run requires the optional runtime, enough free disk, and a representative PDF:

```bash
python benchmark.py \
  --test-file data/input/your_document.pdf \
  --engines mineru \
  --output-dir tmp_mineru_smoke \
  --save-json
```

After the run, inspect `tmp_mineru_smoke/report.md` and `tmp_mineru_smoke/result.json`, then delete the temporary benchmark directory unless it is being intentionally archived as a reviewed benchmark artifact.

Before promoting MinerU from beta, capture the successful environment details in `PDF_ENGINE_EVALUATION.md` and update the release notes with the tested platform, Python version, install command, installed environment size, model/cache size, runtime, output quality, and any remaining limitations.

## Known constraints

- Keep MinerU isolated from the base install and from `requirements-recommended-pdf.txt`.
- Prefer minimum-version metadata in `pyproject.toml`; put experimental CPU-pipeline compatibility repair in `constraints-mineru.txt`.
- Do not make MinerU a blocking PR CI job unless the runner has the required runtime cache, enough disk, and platform dependencies.
- If a release changes MinerU behavior, mark it clearly in `CHANGELOG.md` and GitHub Release notes as beta-engine behavior.
- Do not commit ad-hoc PDFs, temporary benchmark outputs, downloaded models, or venv contents from MinerU tests.
