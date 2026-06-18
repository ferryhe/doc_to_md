# MinerU Engine Governance

MinerU is supported as a **beta optional engine**. It is useful for complex PDF and RAG-oriented extraction workflows, but its dependency tree is heavier and more fragile than the default local, MarkItDown, OpenDataLoader, Mistral, and Mathpix paths.

## Support level

- Package extra: `mineru`
- Engine name: `mineru`
- Current support label: **beta**
- Main package dependency: not included in the base install
- Recommended environment: isolated virtual environment
- Python range: follows this package, `>=3.10,<3.13`

Use the default or recommended PDF engines first unless you specifically need MinerU's parsing pipeline.

## Installation

Start with the normal extra:

```bash
python -m pip install 'doc-to-markdown-converter[mineru]'
```

For a more controlled experimental baseline, install with the repository constraint overlay:

```bash
python -m pip install -e '.[mineru]' -c constraints-mineru.txt
```

The constraint file is not a lock file and should not be applied to the base package install. It records the known repair packages from the latest tracked evaluation so MinerU can be tested without relaxing the main package dependency policy.

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

## Smoke validation

Lightweight CI should exercise the adapter without installing MinerU's heavy runtime:

```bash
python -m pytest tests/test_mineru_engine.py -q
```

A real MinerU acceptance run requires the optional runtime and a representative PDF:

```bash
python benchmark.py \
  --test-file data/input/your_document.pdf \
  --engines mineru \
  --output-dir tmp_mineru_smoke \
  --save-json
```

Before promoting MinerU from beta, capture the successful environment details in `PDF_ENGINE_EVALUATION.md` and update the release notes with the tested platform, Python version, install command, and any remaining limitations.

## Known constraints

- Keep MinerU isolated from the base install. Do not add MinerU or its heavy transitive dependencies to `[project].dependencies`.
- Prefer minimum-version metadata in `pyproject.toml`; put experimental compatibility repair in `constraints-mineru.txt`.
- Do not make MinerU a blocking PR CI job unless the runner has the required runtime cache and platform dependencies.
- If a release changes MinerU behavior, mark it clearly in `CHANGELOG.md` and GitHub Release notes as beta-engine behavior.
