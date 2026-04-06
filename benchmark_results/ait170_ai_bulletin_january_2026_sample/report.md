# Benchmark Report

## Sample

- Timestamp: `2026-04-06T21:37:41.123820+00:00`
- Test file: `data\input\ait170-ai-bulletin-january-2026_1.pdf`
- File size: 701.16 KB
- Engines tested: 9

## Summary

- Fastest successful engine: `local` at 3.40s.
- Longest Markdown output: `marker` with 124,355 characters.
- Fastest engine with acceptable formula judgment: `local` (good).

## Successful engines ranked by runtime

1. `local` - 3.40s, 115,965 chars, 0 assets, quality=good/good
2. `mathpix` - 16.32s, 112,203 chars, 0 assets, quality=poor/poor
3. `markitdown` - 20.44s, 113,587 chars, 0 assets, quality=good/good
4. `opendataloader` - 21.19s, 112,618 chars, 60 assets, quality=poor/poor
5. `mistral` - 29.19s, 110,549 chars, 14 assets, quality=poor/poor
6. `paddleocr` - 179.20s, 1,385 chars, 0 assets, quality=review/not_applicable
7. `docling` - 276.35s, 114,482 chars, 0 assets, quality=good/good
8. `mineru` - 1935.67s, 103,466 chars, 11 assets, quality=poor/poor
9. `marker` - 5990.15s, 124,355 chars, 59 assets, quality=poor/poor

## Result table

| Engine | Model | Status | Time | Markdown chars | Assets | Quality | Formula | Diagnostics | Artifact |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- | --- |
| `local` | `local-text-wrapper` | success | 3.40s | 115,965 | 0 | good | good | - | `outputs\local\output.md` |
| `markitdown` | `markitdown` | success | 20.44s | 113,587 | 0 | good | good | - | `outputs\markitdown\output.md` |
| `paddleocr` | `paddleocr-en` | success | 179.20s | 1,385 | 0 | review | not_applicable | `ocr_placeholder` | `outputs\paddleocr\output.md` |
| `docling` | `docling` | success | 276.35s | 114,482 | 0 | good | good | - | `outputs\docling\output.md` |
| `marker` | `marker` | success | 5990.15s | 124,355 | 59 | poor | poor | `formula_image_reference` | `outputs\marker\output.md` |
| `mineru` | `pipeline:auto` | success | 1935.67s | 103,466 | 11 | poor | poor | `formula_image_reference`, `fragmented_math_tokens` | `outputs\mineru\output.md` |
| `mistral` | `mistral-ocr-latest` | success | 29.19s | 110,549 | 14 | poor | poor | `formula_image_reference` | `outputs\mistral\output.md` |
| `mathpix` | `mathpix-pdf` | success | 16.32s | 112,203 | 0 | poor | poor | `formula_image_reference`, `fragmented_math_tokens` | `outputs\mathpix\output.md` |
| `opendataloader` | `opendataloader` | success | 21.19s | 112,618 | 60 | poor | poor | `formula_image_reference` | `outputs\opendataloader\output.md` |

## Agent-readiness findings

### `local`

- Overall quality: `good`
- Formula quality: `good`
- Diagnostic codes: none

### `mathpix`

- Overall quality: `poor`
- Formula quality: `poor`
- Diagnostic codes: `formula_image_reference`, `fragmented_math_tokens`
- Trace highlights: formula_ocr_enabled=`False`, formula_ocr_attempted=`False`, postprocess_changed=`True`

### `markitdown`

- Overall quality: `good`
- Formula quality: `good`
- Diagnostic codes: none

### `opendataloader`

- Overall quality: `poor`
- Formula quality: `poor`
- Diagnostic codes: `formula_image_reference`

### `mistral`

- Overall quality: `poor`
- Formula quality: `poor`
- Diagnostic codes: `formula_image_reference`

### `paddleocr`

- Overall quality: `review`
- Formula quality: `not_applicable`
- Diagnostic codes: `ocr_placeholder`

### `docling`

- Overall quality: `good`
- Formula quality: `good`
- Diagnostic codes: none

### `mineru`

- Overall quality: `poor`
- Formula quality: `poor`
- Diagnostic codes: `formula_image_reference`, `fragmented_math_tokens`

### `marker`

- Overall quality: `poor`
- Formula quality: `poor`
- Diagnostic codes: `formula_image_reference`

## Engine notes

### PaddleOCR (`paddleocr`)

- Best for: Cases where you specifically want Paddle's OCR stack and are willing to manage the runtime.
- Pros:
  - Can use a local GPU-backed OCR stack when Paddle is configured correctly.
  - Works without an external OCR API.
  - Useful when you want a pure OCR-oriented path instead of a full layout pipeline.
- Cons:
  - Runtime setup is heavier than the Python extra alone suggests.
  - Windows GPU runs may require explicit CUDA DLL paths for the bundled Paddle runtime.
  - This sample produced very little usable text despite a successful run.
- Measured on this sample: 179.20s, 1,385 Markdown chars, 0 assets.

### Docling (`docling`)

- Best for: Complex PDFs where local structured extraction matters more than raw speed.
- Pros:
  - Strong document structure recovery on complex PDFs.
  - Good fit for enterprise reports and long-form documents.
  - Runs locally once dependencies are installed.
- Cons:
  - Heavy dependency stack and slower startup.
  - Runtime is usually much higher than API OCR on the same sample.
  - Environment setup is less lightweight than core engines.
- Measured on this sample: 276.35s, 114,482 Markdown chars, 0 assets.

### Marker (`marker`)

- Best for: One-off or high-fidelity local conversions where heavy setup and long runtime are acceptable.
- Pros:
  - Produced the longest Markdown output in this benchmark.
  - Recovered rich structure and extracted many page assets.
  - Can be very strong when quality matters more than install simplicity.
- Cons:
  - Requires an isolated environment in this project because of dependency conflicts.
  - Runtime on this sample was extremely high.
  - Still shows OCR and punctuation artifacts in the output.
- Measured on this sample: 5990.15s, 124,355 Markdown chars, 59 assets.

### MinerU (`mineru`)

- Best for: Research or specialized evaluation work where you explicitly want to test MinerU despite its setup overhead.
- Pros:
  - Recovered a usable long-form Markdown document after isolated-environment setup.
  - Includes its own layout and OCR pipeline rather than relying on a remote API.
  - Extracted a smaller, more restrained asset set than some other local engines.
- Cons:
  - Needed the most manual runtime repair to get working in this repository.
  - Runtime was still very high on this sample.
  - Output quality did not justify the setup cost compared with the better local alternatives.
- Measured on this sample: 1935.67s, 103,466 Markdown chars, 11 assets.

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
- Measured on this sample: 29.19s, 110,549 Markdown chars, 14 assets.

### Mathpix OCR (`mathpix`)

- Best for: Handwritten formulas, image-heavy math pages, and formula-sensitive fallback workflows.
- Pros:
  - Strongest current tracked option for handwritten-formula PDFs.
  - Good fallback for image-like math pages and formula screenshots.
  - Uses the base install only; no extra Python package is required in this repository.
- Cons:
  - Requires working Mathpix credentials and outbound network access.
  - PDF conversion is asynchronous, so small jobs can still incur polling latency.
  - Not the best default for ordinary prose-heavy PDFs where cheaper local paths are enough.
- Measured on this sample: 16.32s, 112,203 Markdown chars, 0 assets.

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
- Measured on this sample: 21.19s, 112,618 Markdown chars, 60 assets.
