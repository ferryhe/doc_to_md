# Benchmark Results Index

This directory keeps curated benchmark artifacts that are useful for engine selection, QA, and agent-facing evaluation.

## Included benchmark suites

### 1. General text-heavy PDF baseline

Directory:

- [benchmark_results/ait170_ai_bulletin_january_2026_sample](c:/Project/doc_to_md/benchmark_results/ait170_ai_bulletin_january_2026_sample)

What it shows:

- a prose-heavy PDF benchmark for ordinary document conversion
- practical tradeoffs across local and remote engines
- why `markitdown` is the easiest local extra
- why `opendataloader` is still the stronger local default when Java is acceptable
- why `mistral` is the stronger managed OCR option
- why `mathpix` remains a formula-specialist path even after being tested on the prose baseline

Open here first:

- [README.md](c:/Project/doc_to_md/benchmark_results/ait170_ai_bulletin_january_2026_sample/README.md)
- [report.md](c:/Project/doc_to_md/benchmark_results/ait170_ai_bulletin_january_2026_sample/report.md)

### 2. Printed vs handwritten formula suite

Directory:

- [benchmark_results/formula_printed_vs_handwritten_2026_04_06](c:/Project/doc_to_md/benchmark_results/formula_printed_vs_handwritten_2026_04_06)

What it shows:

- printed formulas inside a real regulatory PDF
- handwritten formulas from official Mathpix example images
- direct comparison across `opendataloader`, `local`, `markitdown`, `mistral`, and `mathpix`
- why formula-aware routing should differ for printed versus handwritten math

Open here first:

- [README.md](c:/Project/doc_to_md/benchmark_results/formula_printed_vs_handwritten_2026_04_06/README.md)
- [summary.md](c:/Project/doc_to_md/benchmark_results/formula_printed_vs_handwritten_2026_04_06/summary.md)

## Quick routing summary

| Document type | Best first choice | Best backup | Important caution |
| --- | --- | --- | --- |
| General text-heavy PDF | `opendataloader` or `markitdown` depending on install tolerance | `mistral` | `markitdown` is easiest, but not the strongest |
| Printed formula PDF | `mistral` | `mathpix` | `opendataloader`, `local`, and `markitdown` did not recover explicit formulas in the current reference benchmark |
| Handwritten formula PDF | `mathpix` | `mistral` | `local` and `markitdown` are not usable for handwritten formula recovery in the current sample |

## OpenDataLoader note

`opendataloader` remains valuable because it is fast and often structurally strong, but formula-heavy AI workflows need extra care:

- when explicit math recovery fails, it can leave formula context without machine-readable math
- on handwritten-like pages it can preserve formulas mainly as images

That means the Markdown can still look organized while the actual formulas are not AI-readable.

Best current practice in this repository:

- use `opendataloader` for prose-first PDFs
- rerun with `mistral` or `mathpix` when the result shows `formula_context_without_math` or `formula_image_reference`
