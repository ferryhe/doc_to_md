# Benchmark Report

## Sample

- Timestamp: `2026-04-06T19:27:04.824214+00:00`
- Test file: `mathpix_handwritten_formulas.pdf`
- File size: 278.09 KB
- Reference Markdown: `reviewed.md`
- Engines tested: 5

## Summary

- Fastest successful engine: `local` at 0.00s.
- Longest Markdown output: `mistral` with 316 characters.
- Fastest engine with acceptable formula judgment: `local` (not_applicable).
- Strongest reference-aligned formula output: `mathpix` (good, recall=100%).

## Successful engines ranked by runtime

1. `local` - 0.00s, 80 chars, 0 assets, quality=good/not_applicable
2. `markitdown` - 0.03s, 40 chars, 0 assets, quality=good/not_applicable
3. `opendataloader` - 1.81s, 254 chars, 4 assets, quality=poor/poor
4. `mistral` - 3.41s, 316 chars, 1 assets, quality=poor/poor
5. `mathpix` - 5.66s, 256 chars, 0 assets, quality=good/good

## Result table

| Engine | Model | Status | Time | Markdown chars | Assets | Quality | Formula | Diagnostics | Artifact |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- | --- |
| `opendataloader` | `opendataloader` | success | 1.81s | 254 | 4 | poor | poor | `formula_image_reference` | `outputs\opendataloader\output.md` |
| `local` | `local-text-wrapper` | success | 0.00s | 80 | 0 | good | not_applicable | - | `outputs\local\output.md` |
| `markitdown` | `markitdown` | success | 0.03s | 40 | 0 | good | not_applicable | - | `outputs\markitdown\output.md` |
| `mistral` | `mistral-ocr-latest` | success | 3.41s | 316 | 1 | poor | poor | `formula_image_reference` | `outputs\mistral\output.md` |
| `mathpix` | `mathpix` | success | 5.66s | 256 | 0 | good | good | - | `outputs\mathpix\output.md` |

## Agent-readiness findings

### `local`

- Overall quality: `good`
- Formula quality: `not_applicable`
- Diagnostic codes: none
- Reference formula alignment: `poor` (recall=0%, similarity=0%)
- Reference diagnostics: `reference_formula_missing_all`, `reference_formula_low_similarity`
- Trace highlights: formula_ocr_enabled=`False`, formula_ocr_attempted=`False`, postprocess_changed=`True`

### `markitdown`

- Overall quality: `good`
- Formula quality: `not_applicable`
- Diagnostic codes: none
- Reference formula alignment: `poor` (recall=0%, similarity=0%)
- Reference diagnostics: `reference_formula_missing_all`, `reference_formula_low_similarity`
- Trace highlights: formula_ocr_enabled=`False`, formula_ocr_attempted=`False`, postprocess_changed=`False`

### `opendataloader`

- Overall quality: `poor`
- Formula quality: `poor`
- Diagnostic codes: `formula_image_reference`
- Reference formula alignment: `poor` (recall=0%, similarity=0%)
- Reference diagnostics: `reference_formula_missing_all`, `reference_formula_low_similarity`
- Trace highlights: formula_ocr_enabled=`False`, formula_ocr_attempted=`False`, postprocess_changed=`True`

### `mistral`

- Overall quality: `poor`
- Formula quality: `poor`
- Diagnostic codes: `formula_image_reference`
- Reference formula alignment: `review` (recall=75%, similarity=80%)
- Reference diagnostics: `reference_formula_missing`, `reference_formula_low_similarity`
- Trace highlights: formula_ocr_enabled=`False`, formula_ocr_attempted=`False`, postprocess_changed=`True`

### `mathpix`

- Overall quality: `good`
- Formula quality: `good`
- Diagnostic codes: none
- Reference formula alignment: `good` (recall=100%, similarity=96%)
- Reference diagnostics: none
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
- Measured on this sample: 1.81s, 254 Markdown chars, 4 assets.

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
- Measured on this sample: 3.41s, 316 Markdown chars, 1 assets.
