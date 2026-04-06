# Printed vs Handwritten Formula Benchmark Summary

## Goal

This benchmark pass was designed to answer four practical routing questions for this repository:

1. For ordinary text-heavy PDFs, is `markitdown` the simplest useful option?
2. For printed formula PDFs, are `mistral` and `mathpix` the best current remote options?
3. For handwritten formulas, which engine is strongest?
4. Why is `opendataloader` fast but still risky for AI-facing formula workflows?

## Detailed procedure

### Step 1: Keep the existing general-text benchmark as the prose baseline

We reused the existing benchmark artifacts in:

- [../ait170_ai_bulletin_january_2026_sample/](../ait170_ai_bulletin_january_2026_sample/)

That sample is still the best current reference for ordinary prose-heavy PDF conversion.

### Step 2: Reuse a real printed-formula PDF with a reviewed reference Markdown

We reused:

- source PDF: [printed_formulas_regulatory_pdf/source_document.pdf](printed_formulas_regulatory_pdf/source_document.pdf)
- reviewed reference: [printed_formulas_regulatory_pdf/reviewed.md](printed_formulas_regulatory_pdf/reviewed.md)

Why this sample:

- it is a realistic formula-bearing regulatory PDF
- it contains printed formulas embedded in normal document prose
- it already has a reviewed Markdown reference, so formula recall and similarity can be scored instead of guessed

### Step 3: Build a separate handwritten-formula sample

We assembled a four-page PDF from official Mathpix example images:

- limit expression
- cosine ratio
- oscillatory integral
- log-likelihood expression

Sample inputs:

- handwritten sample PDF: [handwritten_formulas_mathpix_sample/mathpix_handwritten_formulas.pdf](handwritten_formulas_mathpix_sample/mathpix_handwritten_formulas.pdf)
- reviewed reference: [handwritten_formulas_mathpix_sample/reviewed.md](handwritten_formulas_mathpix_sample/reviewed.md)

### Step 4: Run the same five engines on both formula samples

Engines compared:

- `opendataloader`
- `local`
- `markitdown`
- `mistral`
- `mathpix`

Printed-formula run:

```bash
python benchmark.py \
  --test-file "benchmark_results/formula_printed_vs_handwritten_2026_04_06/printed_formulas_regulatory_pdf/source_document.pdf" \
  --engines opendataloader local markitdown mistral mathpix \
  --reference-markdown "benchmark_results/formula_printed_vs_handwritten_2026_04_06/printed_formulas_regulatory_pdf/reviewed.md" \
  --output-dir tmp_formula_printed_vs_handwritten/printed_formulas_regulatory_pdf \
  --save-json
```

Handwritten-formula run:

```bash
python benchmark.py \
  --test-file benchmark_results/formula_printed_vs_handwritten_2026_04_06/handwritten_formulas_mathpix_sample/mathpix_handwritten_formulas.pdf \
  --engines opendataloader local markitdown mistral mathpix \
  --reference-markdown benchmark_results/formula_printed_vs_handwritten_2026_04_06/handwritten_formulas_mathpix_sample/reviewed.md \
  --output-dir tmp_formula_printed_vs_handwritten/handwritten_formulas_mathpix_sample \
  --save-json
```

### Step 5: Read the actual Markdown outputs, not just the summary scores

This matters because generic quality heuristics can look acceptable while formula recall is actually zero.

That happened on the handwritten sample:

- `local`: `good/not_applicable` by heuristic, but `0%` formula recall
- `markitdown`: `good/not_applicable` by heuristic, but `0%` formula recall

## Results

### A. General text-heavy PDF baseline

Source:

- [../ait170_ai_bulletin_january_2026_sample/report.md](../ait170_ai_bulletin_january_2026_sample/report.md)

Practical reading:

- `markitdown` is still the easiest local extra to install and try.
- `opendataloader` is the better local default when Java is acceptable.
- `mistral` is the best managed OCR path when you want stronger quality without maintaining a heavy local stack.

### B. Printed formula PDF

Source:

- [printed_formulas_regulatory_pdf/report.md](printed_formulas_regulatory_pdf/report.md)

Key results:

| Engine | Time | Formula recall | Similarity | Reading |
| --- | ---: | ---: | ---: | --- |
| `mistral` | 11.59s | 96% | 96% | Best printed-formula recovery in this run |
| `mathpix` | 8.01s | 80% | 85% | Strong second place, cleaner heuristics but lower recall |
| `opendataloader` | 0.89s | 0% | 0% | No explicit math segments recovered |
| `local` | 0.50s | 0% | 0% | No explicit math segments recovered |
| `markitdown` | 1.46s | 0% | 0% | No explicit math segments recovered |

Interpretation:

- On printed formulas mixed with Chinese regulatory prose, `mistral` is the strongest engine today in this repo.
- `mathpix` is still good, but on this specific printed sample it underperformed `mistral` on formula recall.
- `opendataloader`, `local`, and `markitdown` all failed the “AI can really read the formulas” test here.

### C. Handwritten formula PDF

Source:

- [handwritten_formulas_mathpix_sample/report.md](handwritten_formulas_mathpix_sample/report.md)

Key results:

| Engine | Time | Formula recall | Similarity | Reading |
| --- | ---: | ---: | ---: | --- |
| `mathpix` | 5.66s | 100% | 96% | Best handwritten-formula recovery in this run |
| `mistral` | 3.41s | 75% | 80% | Good second place, missed the integral page |
| `opendataloader` | 1.81s | 0% | 0% | Turned all four pages into image references |
| `local` | 0.00s | 0% | 0% | Did not recover usable handwritten formula text |
| `markitdown` | 0.03s | 0% | 0% | Effectively empty output |

Interpretation:

- For handwritten formulas, `mathpix` is clearly the best current engine in this repository.
- `mistral` is usable as a backup, but not first choice for harder handwritten math.

## Cross-sample conclusions

### 1. Is `markitdown` the simplest useful engine for ordinary text PDFs?

Yes, if the question is “what is the easiest local extra to install and try?”

No, if the question is “what is the best overall local PDF engine?”

Best phrasing based on current evidence:

- `markitdown` is the simplest local extra and a reasonable first install for ordinary text-heavy PDFs.
- `opendataloader` is the better local default when you care more about structure quality than absolute install simplicity.

### 2. For formula-heavy PDFs, are `mistral` and `mathpix` the best current options?

Yes.

But they are best for different formula shapes:

- printed formulas inside real documents: `mistral` is currently stronger
- handwritten formulas or image-like formula pages: `mathpix` is currently stronger

So the practical answer is not “pick one forever.”  
It is:

- keep both `mistral` and `mathpix` available
- route by document type or fallback rules

### 3. Which engine is best for handwritten formulas?

`mathpix`

This is the clearest result in the whole comparison.

### 4. What is the real issue with `opendataloader`?

`opendataloader` is fast and often structurally useful, but for formula-sensitive AI workflows it has a recurring weakness:

- when it cannot turn a formula into explicit math, it often leaves either plain non-math context or image output instead
- that means the Markdown can still look “structured” while the actual math is no longer machine-readable

This is exactly the failure mode that hurts downstream AI understanding.

## Recommended routing rules

### Ordinary text-heavy PDF

- first choice if you want the easiest install story: `markitdown`
- first choice if you want the stronger local default and can accept Java: `opendataloader`
- first choice if you want the strongest managed OCR option: `mistral`

### Printed formula PDF

- first choice: `mistral`
- second choice: `mathpix`
- avoid relying on `local`, `markitdown`, or `opendataloader` alone when explicit formula recovery matters

### Handwritten formula PDF

- first choice: `mathpix`
- second choice: `mistral`
- avoid `local` and `markitdown`
- do not rely on `opendataloader` alone

## Recommended OpenDataLoader combination strategy

`opendataloader` still has value, but not as a standalone answer for formula-heavy PDFs.

Best current combination ideas:

1. Route prose-first PDFs to `opendataloader`, but send formula-heavy PDFs directly to `mistral` or `mathpix`.
2. Add a fallback rule: if the result shows `formula_context_without_math` or `formula_image_reference`, rerun the same document with `mistral` or `mathpix`.
3. Longer-term, the strongest hybrid path would be:
   `opendataloader` for layout and prose
   plus targeted formula OCR on extracted formula regions or images

Important current limitation:

- this repository already has a formula-image OCR postprocessor, but today it is built around `mistral` and `deepseekocr`
- `mathpix` is not yet wired into that formula-image postprocessing path

So today the practical workaround is routing or rerun fallback, not a true merged hybrid pipeline.

## Artifact map

- archived summary: [summary.md](summary.md)
- printed formulas: [printed_formulas_regulatory_pdf/](printed_formulas_regulatory_pdf/)
- handwritten formulas: [handwritten_formulas_mathpix_sample/](handwritten_formulas_mathpix_sample/)
- general text baseline: [../ait170_ai_bulletin_january_2026_sample/](../ait170_ai_bulletin_january_2026_sample/)
