# Engine Benchmark Tool Guide

## Overview

`benchmark.py` compares document conversion engines on a chosen input file and generates Markdown and optional JSON reports, plus per-engine output artifacts.

If you want recommendation conclusions, install-cost analysis, or dependency-conflict notes, see [PDF_ENGINE_EVALUATION.md](PDF_ENGINE_EVALUATION.md). This guide is only about how to run the benchmark tool itself.

Curated tracked benchmark suites live in [benchmark_results/README.md](benchmark_results/README.md).

Use it when you want to:

- compare output behavior across engines
- measure conversion time and success rate
- compare `quality` and `formula_status` on the final Markdown that agents will actually consume
- compare recovered formulas against a reviewed Markdown reference when AI formula readability matters
- validate a production-like sample before bulk conversion
- evaluate free, local, and API-based engines side by side

> Note: `benchmark.py` is intended for use from a source checkout. Run it from the project root.

## Quick start

```bash
# Test specific engines
python benchmark.py --test-file path/to/document.pdf --engines local markitdown

# Test the preferred PDF profile
python benchmark.py --test-file path/to/document.pdf --profile preferred-pdf

# Score formulas against a reviewed Markdown reference
python benchmark.py --test-file path/to/document.pdf --profile preferred-pdf --reference-markdown path/to/reviewed.md

# Use a custom test file
python benchmark.py --test-file path/to/your/document.pdf

# Save JSON output too
python benchmark.py --test-file path/to/your/document.pdf --save-json
```

## More examples

```bash
# Save results to a custom directory
python benchmark.py \
  --test-file path/to/document.pdf \
  --engines local markitdown paddleocr docling \
  --output-dir my_test_results \
  --save-json

# Compare OCR-oriented engines on a PDF
python benchmark.py \
  --test-file document.pdf \
  --engines mistral deepseekocr paddleocr opendataloader

# Run the preferred PDF profile
python benchmark.py \
  --test-file document.pdf \
  --profile preferred-pdf

# Run the preferred profile and compare formulas to a reviewed Markdown
python benchmark.py \
  --test-file document.pdf \
  --profile preferred-pdf \
  --reference-markdown reviewed.md

# Test only local engines
python benchmark.py \
  --test-file document.pdf \
  --engines local markitdown paddleocr docling marker mineru
```

## Supported engines

### Local engines

1. `local`
2. `markitdown`
3. `paddleocr`
4. `docling`
5. `marker`
6. `mineru`
7. `opendataloader`

### API-based engines

8. `mistral`
9. `deepseekocr`

## Output files

Generated in the output directory, which defaults to `benchmark_results/`:

1. `report.md`
2. `result.json` when `--save-json` is used
3. `outputs/<engine>/output.md` for successful engines
4. `outputs/<engine>/assets/` when the engine extracts assets
5. `outputs/<engine>/error.txt` for failed engines

## Report contents

The generated report includes:

1. test metadata such as timestamp and file size
2. overall statistics and success rate
3. performance ranking by conversion time
4. per-engine details such as output length, asset count, `quality`, `formula_status`, and diagnostic codes
5. optional reference-formula alignment metrics such as recall and similarity when `--reference-markdown` is provided
6. agent-readiness findings derived from the postprocessed Markdown
6. engine pros, cons, and suggested use cases
7. failure details and troubleshooting hints

## Common scenarios

### Validate a real business PDF from `data/input`

```bash
python benchmark.py \
  --test-file "data/input/your_document.pdf" \
  --profile preferred-pdf \
  --reference-markdown "data/output/your_document.md" \
  --output-dir tmp_user_sample_benchmark \
  --save-json
```

This is the recommended manual check when you want to evaluate a real formula-heavy or regulation-style PDF before making agent-facing changes and your preferred engines are `opendataloader` plus `mistral`.

When a reviewed Markdown file already exists, `--reference-markdown` is the best way to answer the question "can an AI really read the formulas?" because it turns that judgment into repeatable numbers:

- `reference_formula_status`
- `reference_formula_recall`
- `reference_formula_similarity`
- `reference_formula_diagnostics`

### Choose the best engine for a document type

```bash
python benchmark.py --test-file your_document.pdf --save-json
```

### Validate production performance

```bash
python benchmark.py \
  --test-file production_sample.pdf \
  --engines mistral deepseekocr \
  --output-dir validation_results
```

### Compare quality across engines

```bash
python benchmark.py \
  --test-file complex_document.pdf \
  --engines local markitdown mistral paddleocr docling marker
```

### Compare free and paid options

```bash
# Free / local
python benchmark.py --test-file document.pdf --engines local markitdown paddleocr docling marker mineru opendataloader

# API-based
python benchmark.py --test-file document.pdf --engines mistral deepseekocr
```

## FAQ

### Why do some engines fail?

Common reasons:

- missing dependencies
- missing API keys
- unsupported file format
- insufficient system resources

### Where are results saved?

By default: `benchmark_results/`

### How should I interpret performance ratings?

- Excellent: under 5 seconds
- Good: 5 to 15 seconds
- Average: 15 to 30 seconds
- Slow: 30 to 60 seconds
- Very slow: over 60 seconds

### Can I test my own documents?

Yes:

```bash
python benchmark.py --test-file path/to/your/document.pdf
```

Supported input types include `.pdf`, `.docx`, `.png`, `.jpg`, `.jpeg`, `.txt`, and `.md`.

## Technical notes

Metrics currently include:

- conversion time
- Markdown output length
- extracted asset count
- postprocessed `quality` and `formula_status`
- optional reference-based formula recall and similarity against a reviewed Markdown file
- diagnostic codes from the Markdown-quality pass
- postprocessing trace metadata
- success or failure status

The built-in benchmark profiles currently include:

- `preferred-pdf`: `opendataloader` then `mistral`

Optimization hints:

- PaddleOCR benefits from GPU acceleration when available
- MinerU generally performs better on GPU-equipped machines
- OpenDataLoader requires Java 11+ on `PATH` and the optional `opendataloader-pdf` package
- API engines may need higher timeout and retry values for large documents

## Related files

- Main guide: [README.md](README.md)
- Curated benchmark suites: [benchmark_results/README.md](benchmark_results/README.md)
- Configuration template: [.env.example](.env.example)
- Benchmark script: [benchmark.py](benchmark.py)
- Real-PDF testing guide: [REAL_PDF_TESTING.md](REAL_PDF_TESTING.md)
