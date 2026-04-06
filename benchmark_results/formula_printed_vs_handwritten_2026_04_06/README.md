# Formula Benchmark Suite

This suite compares two different kinds of formula-heavy PDFs:

1. a real printed-formula regulatory PDF
2. a compact handwritten-formula PDF assembled from official Mathpix example images

## Why this suite exists

The repository now needs different engine recommendations for:

- ordinary text-heavy PDFs
- printed formulas inside normal documents
- handwritten formulas or image-like math pages

This suite is the evidence behind that routing split.

## Start here

- [summary.md](c:/Project/doc_to_md/benchmark_results/formula_printed_vs_handwritten_2026_04_06/summary.md)

## Printed formulas

Directory:

- [printed_formulas_regulatory_pdf](c:/Project/doc_to_md/benchmark_results/formula_printed_vs_handwritten_2026_04_06/printed_formulas_regulatory_pdf)

Key reading:

- `mistral` was the best current engine on the printed-formula sample
- `mathpix` was a strong second place
- `opendataloader`, `local`, and `markitdown` did not recover explicit math segments in the reference comparison

## Handwritten formulas

Directory:

- [handwritten_formulas_mathpix_sample](c:/Project/doc_to_md/benchmark_results/formula_printed_vs_handwritten_2026_04_06/handwritten_formulas_mathpix_sample)

Key reading:

- `mathpix` was the best current engine on the handwritten-formula sample
- `mistral` was the best backup
- `opendataloader` mainly preserved handwritten formulas as images instead of explicit math

## Recommended reading order

1. [summary.md](c:/Project/doc_to_md/benchmark_results/formula_printed_vs_handwritten_2026_04_06/summary.md)
2. [printed report](c:/Project/doc_to_md/benchmark_results/formula_printed_vs_handwritten_2026_04_06/printed_formulas_regulatory_pdf/report.md)
3. [handwritten report](c:/Project/doc_to_md/benchmark_results/formula_printed_vs_handwritten_2026_04_06/handwritten_formulas_mathpix_sample/report.md)
