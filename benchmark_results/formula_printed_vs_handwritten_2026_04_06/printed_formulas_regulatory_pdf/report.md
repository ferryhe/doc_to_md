# Benchmark Report

## Sample

- Timestamp: `2026-04-06T19:26:07.403057+00:00`
- Test file: `data\input\保险公司偿付能力监管规则第4号：保险风险最低资本（非寿险业务）.pdf`
- File size: 475.34 KB
- Reference Markdown: `data\output\保险公司偿付能力监管规则第4号：保险风险最低资本（非寿险业务）.md`
- Engines tested: 5

## Summary

- Fastest successful engine: `local` at 0.50s.
- Longest Markdown output: `markitdown` with 61,614 characters.
- Fastest engine with acceptable formula judgment: `mathpix` (good).
- Strongest reference-aligned formula output: `mistral` (review, recall=96%).

## Successful engines ranked by runtime

1. `local` - 0.50s, 13,142 chars, 0 assets, quality=review/review
2. `opendataloader` - 0.89s, 14,957 chars, 0 assets, quality=review/review
3. `markitdown` - 1.46s, 61,614 chars, 0 assets, quality=review/review
4. `mathpix` - 8.01s, 30,421 chars, 0 assets, quality=good/good
5. `mistral` - 11.59s, 30,408 chars, 0 assets, quality=review/review

## Result table

| Engine | Model | Status | Time | Markdown chars | Assets | Quality | Formula | Diagnostics | Artifact |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- | --- |
| `opendataloader` | `opendataloader` | success | 0.89s | 14,957 | 0 | review | review | `formula_context_without_math` | `outputs\opendataloader\output.md` |
| `local` | `local-text-wrapper` | success | 0.50s | 13,142 | 0 | review | review | `formula_context_without_math` | `outputs\local\output.md` |
| `markitdown` | `markitdown` | success | 1.46s | 61,614 | 0 | review | review | `formula_context_without_math` | `outputs\markitdown\output.md` |
| `mistral` | `mistral-ocr-latest` | success | 11.59s | 30,408 | 0 | review | review | `fragmented_math_tokens` | `outputs\mistral\output.md` |
| `mathpix` | `mathpix-pdf` | success | 8.01s | 30,421 | 0 | good | good | - | `outputs\mathpix\output.md` |

## Agent-readiness findings

### `local`

- Overall quality: `review`
- Formula quality: `review`
- Diagnostic codes: `formula_context_without_math`
- Reference formula alignment: `poor` (recall=0%, similarity=0%)
- Reference diagnostics: `reference_formula_missing_all`, `reference_formula_low_similarity`
- Trace highlights: formula_ocr_enabled=`False`, formula_ocr_attempted=`False`, postprocess_changed=`True`

### `opendataloader`

- Overall quality: `review`
- Formula quality: `review`
- Diagnostic codes: `formula_context_without_math`
- Reference formula alignment: `poor` (recall=0%, similarity=0%)
- Reference diagnostics: `reference_formula_missing_all`, `reference_formula_low_similarity`
- Trace highlights: formula_ocr_enabled=`False`, formula_ocr_attempted=`False`, postprocess_changed=`True`

### `markitdown`

- Overall quality: `review`
- Formula quality: `review`
- Diagnostic codes: `formula_context_without_math`
- Reference formula alignment: `poor` (recall=0%, similarity=0%)
- Reference diagnostics: `reference_formula_missing_all`, `reference_formula_low_similarity`
- Trace highlights: formula_ocr_enabled=`False`, formula_ocr_attempted=`False`, postprocess_changed=`False`

### `mathpix`

- Overall quality: `good`
- Formula quality: `good`
- Diagnostic codes: none
- Reference formula alignment: `review` (recall=80%, similarity=85%)
- Reference diagnostics: `reference_formula_missing`
- Trace highlights: formula_ocr_enabled=`False`, formula_ocr_attempted=`False`, postprocess_changed=`True`

### `mistral`

- Overall quality: `review`
- Formula quality: `review`
- Diagnostic codes: `fragmented_math_tokens`
- Reference formula alignment: `review` (recall=96%, similarity=96%)
- Reference diagnostics: `reference_formula_missing`, `reference_formula_fragmented_tokens`
- Trace highlights: formula_ocr_enabled=`False`, formula_ocr_attempted=`False`, postprocess_changed=`True`

## Engine notes

### OpenDataLoader (`opendataloader`)

- Best for: PDF-heavy workflows where you can maintain the Java runtime and optional package.
- Pros:
  - Purpose-built PDF pipeline with Java-backed layout analysis.
  - Supports hybrid mode for harder pages.
  - Can be a strong local option once prerequisites are satisfied.
- Cons:
  - Requires both Java 11+ and the optional Python package.
  - Current environment readiness is a hard prerequisite.
  - PDF-only, so it is not a general document engine.
- Measured on this sample: 0.89s, 14,957 Markdown chars, 0 assets.

### Mistral OCR (`mistral`)

- Best for: Production OCR when quality and convenience matter more than avoiding API usage.
- Pros:
  - Usually the easiest way to get high-quality OCR on difficult PDFs.
  - No local OCR model installation required.
  - Often the best speed-to-quality tradeoff when the API is available.
- Cons:
  - Requires a working API key and outbound network access.
  - Usage is not free.
  - Remote latency and service availability affect runtime.
- Measured on this sample: 11.59s, 30,408 Markdown chars, 0 assets.
