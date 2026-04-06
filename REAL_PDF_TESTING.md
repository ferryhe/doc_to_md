# Real PDF Testing

This repository now uses two complementary real-PDF testing layers:

- a tracked deterministic smoke fixture for automated regression
- an optional representative business PDF in `data/input/` for manual evaluation

## Why both layers matter

The tracked fixture is small and stable, so it is safe for CI-style regression.

The representative PDF is closer to the real actuarial and regulatory documents this project needs to handle:

- long Chinese prose
- formulas mixed with explanatory text
- OCR-sensitive symbols
- regulatory layout patterns

That second layer is where agent-readiness decisions become meaningful.

## Automated real-PDF regression

Tracked fixture:

- `tests/fixtures/real_smoke.pdf`

Automated coverage:

- `tests/test_real_pdf_smoke.py`
- `tests/test_api_contract.py`
- `tests/test_benchmark.py`

Recommended command:

```powershell
.venv\Scripts\python -m pytest `
  tests/test_real_pdf_smoke.py `
  tests/test_api_contract.py `
  tests/test_benchmark.py `
  tests/test_api.py `
  tests/test_conversion_logic.py -q
```

## Manual representative PDF evaluation

Drop one or more real documents into:

- `data/input/`

Then run a focused benchmark:

```powershell
.venv\Scripts\python benchmark.py `
  --test-file "data/input/your_document.pdf" `
  --profile formula-pdf `
  --reference-markdown "data/output/your_document.md" `
  --output-dir tmp_user_sample_benchmark `
  --save-json
```

Artifacts:

- `tmp_user_sample_benchmark/report.md`
- `tmp_user_sample_benchmark/result.json`
- `tmp_user_sample_benchmark/outputs/<engine>/output.md`

## How to interpret the result

Look at:

- `quality_status`
- `formula_status`
- `reference_formula_status`
- `reference_formula_recall`
- `reference_formula_similarity`
- `reference_formula_diagnostics`
- `diagnostic_codes`
- `trace.formula_ocr_attempted`
- `trace.postprocess_changed`

Current interpretation rule:

- `good`: safe enough for normal downstream use
- `review`: readable, but an agent or human should spot-check important sections
- `poor`: not safe for formula-sensitive downstream work

Formula-specific warning signs:

- `formula_context_without_math`
- `formula_image_reference`
- `fragmented_math_tokens`
- `unbalanced_display_math`

## Current representative sample note

Sample used on `2026-04-03`:

- `data/input/保险公司偿付能力监管规则第4号：保险风险最低资本（非寿险业务）.pdf`
- `data/output/保险公司偿付能力监管规则第4号：保险风险最低资本（非寿险业务）.md`

Observed result with `preferred-pdf` plus the reviewed Markdown reference:

- `opendataloader`
  - overall quality: `review`
  - formula quality: `review`
  - reference formula alignment: `poor`
  - reference formula recall: `0%`
  - diagnostic codes: `formula_context_without_math`
- `mistral`
  - overall quality: `review`
  - formula quality: `review`
  - reference formula alignment: `review`
  - reference formula recall: `96%`
  - reference formula similarity: `96%`
  - diagnostic codes: `fragmented_math_tokens`

What this means:

- `opendataloader` is still fast, but it is not restoring formulas into explicit math segments on this sample
- `mistral` is already close to the reviewed target for AI-readable formulas
- the remaining gap on `mistral` is mostly fragmented math tokens and a small number of missed formulas
- this document is now a strong representative regression sample for future formula-quality work

Additional tracked suites added on `2026-04-06`:

- `benchmark_results/ait170_ai_bulletin_january_2026_sample/` for general text-heavy PDFs
- `benchmark_results/formula_printed_vs_handwritten_2026_04_06/printed_formulas_regulatory_pdf/` for printed formulas in a regulatory PDF
- `benchmark_results/formula_printed_vs_handwritten_2026_04_06/handwritten_formulas_mathpix_sample/` for handwritten formulas from official Mathpix sample material

Preferred-path note:

- if your normal workflow prefers `opendataloader` and `mistral`, use `--profile preferred-pdf`
- if the document may contain handwritten formulas or image-like math pages, use `--profile formula-pdf` so `mathpix` is included
- if you also have a reviewed Markdown sample, always add `--reference-markdown`
- before running that profile in a fresh shell, inspect `GET /apps/conversion/engine-readiness` or verify `java -version`

## Environment note

On the current machine:

- `opendataloader` can run once Java 17 is available on `PATH` in the current shell
- `mistral` can run when `MISTRAL_API_KEY` is present in `.env`
- `mathpix` can run when `MATHPIX_APP_ID` and `MATHPIX_APP_KEY` are present in `.env`
- `markitdown` and `docling` are blocked until their optional packages are installed

That means the current representative benchmark is most useful for:

- side-by-side `opendataloader`, `mistral`, and `mathpix` checks
- formula-reference checks against reviewed Markdown outputs
