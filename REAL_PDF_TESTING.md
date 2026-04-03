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
  --profile preferred-pdf `
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

Observed result with `local`:

- overall quality: `review`
- formula quality: `review`
- diagnostic codes: `formula_context_without_math`
- trace: formula OCR was not attempted and postprocessing did not materially change the output

What this means:

- plain text extraction is usable enough to continue analysis
- formulas are being flattened into prose-like text instead of recovered as math segments
- this document is a good representative regression sample for future formula-quality work

Preferred-path note:

- if your normal workflow prefers `opendataloader` and `mistral`, use `--profile preferred-pdf`
- before running that profile, inspect `GET /apps/conversion/engine-readiness` to confirm whether the local machine is actually ready for both engines
- on the current machine, `preferred-pdf` currently means:
  - `opendataloader` is blocked until Java 11+ and `opendataloader-pdf` are installed
  - `mistral` is the only ready engine in that preferred pair

## Environment note

On the current machine:

- `opendataloader` is blocked because `java` is not installed on `PATH`
- `markitdown` and `docling` are blocked until their optional packages are installed

That means the current representative benchmark is most useful for:

- `local` baseline checks
- future verification after optional engine dependencies are installed
