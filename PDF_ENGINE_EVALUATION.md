# PDF Engine Evaluation

## Why this document exists

This is now the canonical evaluation and testing document for PDF workflows in this repository.

Use the docs this way:

- [README.md](README.md): product overview, installation, configuration, and normal usage
- this file: benchmark methodology, engine tradeoffs, routing rules, and real-PDF evaluation workflow
- [benchmark_results/README.md](benchmark_results/README.md): archived benchmark artifacts and raw outputs

The goal is to keep one detailed evaluation document instead of splitting benchmark usage and real-PDF testing across multiple top-level guides.

## Executive summary

Current best choices by document type:

| Document type | First choice | Best backup | Why |
| --- | --- | --- | --- |
| General text-heavy PDF | `opendataloader` | `mistral` | Best current local default when Java is acceptable |
| General text-heavy PDF, easiest local extra | `markitdown` | `opendataloader` | Simplest install story |
| Printed formula PDF | `mistral` | `mathpix` | Best current tracked printed-formula recovery |
| Handwritten formula PDF | `mathpix` | `mistral` | Best current tracked handwritten-formula recovery |

Important caution:

- `opendataloader` is still fast and structurally useful, but formula-heavy AI workflows should not trust it blindly.
- When it cannot recover explicit math, it often leaves formula context without machine-readable formulas or preserves formulas mainly as images.
- That is why prose routing and formula routing should now be treated as separate decisions.

## Current tracked benchmark suites

This repository currently keeps three benchmark views that answer different questions.

| Suite | Main question | Engines compared | Primary artifacts |
| --- | --- | --- | --- |
| General text-heavy PDF baseline | What should ordinary users try first for prose-heavy PDFs? | `local`, `markitdown`, `opendataloader`, `docling`, `paddleocr`, `marker`, `mineru`, `mistral` | [benchmark_results/ait170_ai_bulletin_january_2026_sample/report.md](benchmark_results/ait170_ai_bulletin_january_2026_sample/report.md) |
| Printed formulas in a regulatory PDF | Can the engine recover explicit math inside a real actuarial-style document? | `opendataloader`, `local`, `markitdown`, `mistral`, `mathpix` | [benchmark_results/formula_printed_vs_handwritten_2026_04_06/printed_formulas_regulatory_pdf/report.md](benchmark_results/formula_printed_vs_handwritten_2026_04_06/printed_formulas_regulatory_pdf/report.md) |
| Handwritten formulas | Which engine is strongest when math appears as handwriting or image-like equations? | `opendataloader`, `local`, `markitdown`, `mistral`, `mathpix` | [benchmark_results/formula_printed_vs_handwritten_2026_04_06/handwritten_formulas_mathpix_sample/report.md](benchmark_results/formula_printed_vs_handwritten_2026_04_06/handwritten_formulas_mathpix_sample/report.md) |

Start with these index files:

- [benchmark_results/README.md](benchmark_results/README.md)
- [benchmark_results/ait170_ai_bulletin_january_2026_sample/README.md](benchmark_results/ait170_ai_bulletin_january_2026_sample/README.md)
- [benchmark_results/formula_printed_vs_handwritten_2026_04_06/summary.md](benchmark_results/formula_printed_vs_handwritten_2026_04_06/summary.md)

## How to rerun the benchmarks

### Quick baseline checks

```bash
python benchmark.py --test-file path/to/document.pdf
python benchmark.py --test-file path/to/document.pdf --profile preferred-pdf
python benchmark.py --test-file path/to/document.pdf --profile formula-pdf
python benchmark.py --test-file path/to/document.pdf --save-json
```

Profile meaning:

- `preferred-pdf`: `opendataloader` then `mistral`
- `formula-pdf`: `opendataloader`, `mistral`, then `mathpix`

### Compare a custom engine set

```bash
python benchmark.py \
  --test-file path/to/document.pdf \
  --engines opendataloader local markitdown mistral mathpix \
  --save-json
```

### Evaluate a representative real PDF with a reviewed Markdown target

This is the most useful manual check before changing recommendations for formula-sensitive workflows.

```bash
python benchmark.py \
  --test-file "data/input/your_document.pdf" \
  --profile formula-pdf \
  --reference-markdown "data/output/your_document.md" \
  --output-dir tmp_user_sample_benchmark \
  --save-json
```

If the document is just a normal prose-heavy PDF and handwritten formulas are not plausible, `preferred-pdf` is enough.

### Environment checks before benchmarking

- `opendataloader` requires Java 11+ on `PATH` and `opendataloader-pdf`
- `mistral` requires `MISTRAL_API_KEY`
- `mathpix` requires `MATHPIX_APP_ID` and `MATHPIX_APP_KEY`

The readiness endpoint currently covers the default prose and printed-formula pair:

```bash
curl http://localhost:8000/apps/conversion/engine-readiness
```

That endpoint reports readiness for `opendataloader` and `mistral`.
`mathpix` is supported, but it is currently treated as a specialist fallback rather than part of the built-in readiness profile.

## What to read in a benchmark result

For ordinary PDFs, start with:

- `quality_status`
- `formula_status`
- `diagnostic_codes`

For formula-sensitive PDFs, the reference-aware fields matter more:

- `reference_formula_status`
- `reference_formula_recall`
- `reference_formula_similarity`
- `reference_formula_diagnostics`

The key diagnostic codes to watch:

- `formula_context_without_math`
- `formula_image_reference`
- `fragmented_math_tokens`
- `unbalanced_display_math`

Important interpretation rule:

- heuristic quality alone is not enough for handwritten or formula-heavy PDFs
- `local` and `markitdown` can look acceptable by generic quality heuristics while still scoring `0%` formula recall against a reviewed reference

## Engine inventory and install cost

| Engine | What must be installed | Clean-env package count | Approx payload | Current project installability | Current benchmark status | Notes |
| --- | --- | ---: | ---: | --- | --- | --- |
| `local` | Base install only | `0` extra | `0` extra | Works now | Benchmarked | Fastest possible baseline, but weak PDF quality on the general-text sample |
| `markitdown` | `pip install -e ".[markitdown]"` | `33` | `63.0 MiB` | Works now | Benchmarked | Simplest local extra after base install |
| `opendataloader` | Java `11+` and `pip install -e ".[opendataloader]"` | `1` Python package | `21.2 MiB` plus Java | Works now after Java setup | Benchmarked | Small Python payload, but Java is a real setup step |
| `docling` | `pip install -e ".[docling]"` | `95` | `293.3 MiB` | Works now | Benchmarked | Heavy dependency stack, CPU-slow on the tracked prose sample |
| `paddleocr` | `pip install -e ".[paddleocr]"`, plus a working Paddle runtime | `58` extra-only | `99.1 MiB` extra-only; about `1.9 GB` more for the working Windows GPU runtime used here | Works in the main env only after extra runtime setup | Benchmarked | Successful run required `paddlepaddle-gpu==3.3.0` and explicit CUDA DLL paths on Windows |
| `marker` | `pip install -e ".[marker]"` in an isolated env | `78` | `250.4 MiB` | Fails in the main env | Benchmarked in an isolated env | Strong output, but not honest to present as a drop-in extra in this repo |
| `mineru` | `pip install -e ".[mineru]"` in an isolated env, plus runtime repair | `82` | `214.0 MiB` | Fails in the main env | Benchmarked in an isolated env | Needed the most manual runtime repair before the benchmark would succeed |
| `mistral` | Base install plus `MISTRAL_API_KEY` | `0` extra | `0` extra | Works now | Benchmarked | Best current managed OCR path for general and printed-formula PDFs |
| `mathpix` | Base install plus `MATHPIX_APP_ID` and `MATHPIX_APP_KEY` | `0` extra | `0` extra | Works now | Benchmarked in the formula suites | Strongest current handwritten-formula specialist |
| `deepseekocr` | Base install plus `SILICONFLOW_API_KEY` | `0` extra | `0` extra | Works now | Intentionally skipped | Supported, but still outside the main recommendation focus |

### Recommended minimal retained setup

If the project keeps only the currently recommended PDF engines:

- `local`
- `markitdown`
- `opendataloader`
- `docling`
- `mistral`
- `mathpix`

the install target should remain:

```bash
pip install -r requirements-recommended-pdf.txt
```

Equivalent direct command:

```bash
pip install -e ".[markitdown,docling,opendataloader]"
```

Why this is enough:

- `local`, `mistral`, and `mathpix` are already in the base package
- `markitdown`, `docling`, and `opendataloader` are the only extras needed for that retained set
- `requirements-core.txt` is broader than the recommended PDF setup and should not be presented as the same thing

### Observed installed footprint for the retained setup

The `Approx payload` column above is only a download estimate.
Actual installed size is larger.

On the Windows / Python 3.12 machine used for the tracked evaluation:

- `.venv`: about `1.32 GB`
- JDK required by `opendataloader`: about `303 MB`
- practical total: about `1.62 GB`

Largest installed components in that retained setup:

- `torch`: about `447 MB`
- `scipy`: about `111 MB`
- `cv2`: about `109 MB`
- `transformers`: about `102 MB`
- `sympy`: about `66 MB`
- `pandas`: about `60 MB`
- `onnxruntime`: about `35 MB`
- `docling_parse`: about `29 MB`
- `opendataloader_pdf`: about `23 MB`

Interpretation:

- most of the retained footprint comes from the `docling` stack, not from `markitdown` or `opendataloader`
- `opendataloader` itself is relatively small on the Python side, but its Java requirement adds a separate system footprint
- `mathpix` adds no extra Python footprint inside this repo, but it does add an external service dependency

### Current dependency conflicts

These are real resolver conflicts in the current project.

| Engine | Conflict |
| --- | --- |
| `marker` | Project pins `click==8.1.7`, while `marker-pdf>=1.10.1` requires `click>=8.2.0,<9` |
| `mineru` | Project pins `pillow==10.4.0`, while `mineru>=2.6.4` requires `pillow>=11.0.0` |

### Runtime repair that was actually needed

- `paddleocr`: the Python extra alone was not enough for a working Windows GPU run. A successful benchmark needed `paddlepaddle-gpu==3.3.0` from Paddle's `cu130` index and a process-level `PATH` update pointing at the bundled `nvidia/cu13` and `nvidia/cudnn` DLL directories.
- `marker`: the benchmark worked only in an isolated environment so it could use `click>=8.2.0` without touching the repository pins.
- `mineru`: the benchmark worked only after an isolated environment plus additional runtime packages and version adjustments, including `torch==2.2.2`, `torchvision==0.17.2`, `doclayout-yolo`, `ultralytics`, `ftfy`, `pyclipper`, `omegaconf`, `rapidocr`, `shapely`, `dill`, and `numpy<2`.

## General text-heavy PDF baseline

Tracked suite:

- [benchmark_results/ait170_ai_bulletin_january_2026_sample/report.md](benchmark_results/ait170_ai_bulletin_january_2026_sample/report.md)
- [benchmark_results/ait170_ai_bulletin_january_2026_sample/result.json](benchmark_results/ait170_ai_bulletin_january_2026_sample/result.json)
- [benchmark_results/ait170_ai_bulletin_january_2026_sample/outputs/](benchmark_results/ait170_ai_bulletin_january_2026_sample/outputs/)

Sample:

- source PDF: `data/input/ait170-ai-bulletin-january-2026_1.pdf`
- sample size: `717,988` bytes

Scoring method for this suite:

- install cost: `25%`
- speed: `25%`
- quality: `50%`

Weighted formula:

`final_score = install_cost * 0.25 + speed * 0.25 + quality * 0.50`

Important scope note:

- this weighted table is only for the tracked general text-heavy PDF baseline
- `mathpix` is not scored here because its current value in this repo comes from formula-specialist work, not ordinary prose benchmarking

### Weighted results

| Engine | Time | Markdown chars | Assets | Install cost score | Speed score | Quality score | Final score | Stars | Working conclusion |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `mistral` | `29.19s` | `110,549` | `14` | `3.5` | `4.0` | `4.0` | `3.88` | `★★★★☆` | Best managed-service option if API use is acceptable |
| `opendataloader` | `21.19s` | `112,618` | `60` | `3.5` | `4.0` | `3.8` | `3.77` | `★★★★☆` | Best current local balance |
| `local` | `3.40s` | `115,965` | `0` | `5.0` | `5.0` | `1.4` | `3.20` | `★★★☆☆` | Fast zero-extra baseline only |
| `markitdown` | `20.44s` | `113,587` | `0` | `4.0` | `4.0` | `2.3` | `3.15` | `★★★☆☆` | Best "just add one local extra" option |
| `docling` | `276.35s` | `114,482` | `0` | `2.0` | `1.0` | `4.3` | `2.90` | `★★★☆☆` | Best current text fidelity, but too slow for default CPU use |
| `marker` | `5990.15s` | `124,355` | `59` | `1.5` | `1.0` | `4.1` | `2.67` | `★★★☆☆` | Strong output, worst runtime and high setup cost |
| `mineru` | `1935.67s` | `103,466` | `11` | `1.0` | `1.0` | `3.2` | `2.10` | `★★☆☆☆` | Works after major setup effort, but not worth the cost here |
| `paddleocr` | `179.20s` | `1,385` | `0` | `1.5` | `2.0` | `0.8` | `1.27` | `★☆☆☆☆` | Runtime success, but near-empty output on this sample |

### What this suite means

- `opendataloader` is still the best current local default when Java is acceptable
- `markitdown` is still the easiest true extra to recommend
- `mistral` is still the best current managed OCR path for ordinary PDFs
- `docling` has strong text quality, but is too slow on CPU to be the default
- `local` should be described as a fast baseline, not a quality recommendation

## Formula-focused benchmark suite

Master summary:

- [benchmark_results/formula_printed_vs_handwritten_2026_04_06/summary.md](benchmark_results/formula_printed_vs_handwritten_2026_04_06/summary.md)

### Printed formulas inside a real regulatory PDF

Tracked report:

- [benchmark_results/formula_printed_vs_handwritten_2026_04_06/printed_formulas_regulatory_pdf/report.md](benchmark_results/formula_printed_vs_handwritten_2026_04_06/printed_formulas_regulatory_pdf/report.md)

Sample:

- source PDF: `data/input/保险公司偿付能力监管规则第4号：保险风险最低资本（非寿险业务）.pdf`
- reviewed reference: `data/output/保险公司偿付能力监管规则第4号：保险风险最低资本（非寿险业务）.md`

Results:

| Engine | Time | Heuristic formula status | Reference recall | Reference similarity | Reading |
| --- | ---: | --- | ---: | ---: | --- |
| `mistral` | `11.59s` | `review` | `96%` | `96%` | Best printed-formula recovery in the tracked run |
| `mathpix` | `8.01s` | `good` | `80%` | `85%` | Strong second place, but lower recall than `mistral` |
| `opendataloader` | `0.89s` | `review` | `0%` | `0%` | No explicit math segments recovered |
| `local` | `0.50s` | `review` | `0%` | `0%` | No explicit math segments recovered |
| `markitdown` | `1.46s` | `review` | `0%` | `0%` | No explicit math segments recovered |

Interpretation:

- on printed formulas mixed with Chinese regulatory prose, `mistral` is the strongest engine today in this repo
- `mathpix` is still useful, but it should currently be described as the backup on printed formulas
- `opendataloader`, `local`, and `markitdown` all failed the "AI can really read the formulas" test on this sample

### Handwritten formulas

Tracked report:

- [benchmark_results/formula_printed_vs_handwritten_2026_04_06/handwritten_formulas_mathpix_sample/report.md](benchmark_results/formula_printed_vs_handwritten_2026_04_06/handwritten_formulas_mathpix_sample/report.md)

Sample:

- source PDF: `tmp_mathpix_handwritten_formula_benchmark/mathpix_handwritten_formulas.pdf`
- reviewed reference: `tmp_mathpix_handwritten_formula_benchmark/reviewed.md`
- source images were assembled from official Mathpix example material

Results:

| Engine | Time | Heuristic formula status | Reference recall | Reference similarity | Reading |
| --- | ---: | --- | ---: | ---: | --- |
| `mathpix` | `5.66s` | `good` | `100%` | `96%` | Best handwritten-formula recovery in the tracked run |
| `mistral` | `3.41s` | `poor` | `75%` | `80%` | Good backup, but missed one page |
| `opendataloader` | `1.81s` | `poor` | `0%` | `0%` | Turned formulas into image references |
| `local` | `0.00s` | `not_applicable` | `0%` | `0%` | Did not recover usable handwritten formula text |
| `markitdown` | `0.03s` | `not_applicable` | `0%` | `0%` | Effectively empty output |

Interpretation:

- for handwritten formulas, `mathpix` is clearly the best current engine in this repository
- `mistral` is usable as a backup, but not first choice for harder handwritten math
- generic heuristic quality can be misleading here, because `local` and `markitdown` can look "fine" while still having zero formula recall

## Cross-sample conclusions

### Ordinary text-heavy PDF

- `markitdown` is the simplest local extra to install and try
- `opendataloader` is the stronger local default when Java is acceptable
- `mistral` is the strongest managed OCR path

### Printed formula PDF

- first choice: `mistral`
- second choice: `mathpix`
- do not rely on `local`, `markitdown`, or `opendataloader` alone when explicit formula recovery matters

### Handwritten formula PDF

- first choice: `mathpix`
- second choice: `mistral`
- avoid `local` and `markitdown`
- do not rely on `opendataloader` alone

### OpenDataLoader combination strategy

`opendataloader` still has value, but not as a standalone answer for formula-heavy PDFs.

Best current practice:

1. Route prose-first PDFs to `opendataloader`.
2. Route printed formula-heavy PDFs directly to `mistral`.
3. Route handwritten formulas or image-like math pages directly to `mathpix`.
4. If an `opendataloader` result shows `formula_context_without_math` or `formula_image_reference`, rerun the same document with `mistral` or `mathpix`.

Important current limitation:

- this repository already has a formula-image OCR postprocessor, but today it is built around `mistral` and `deepseekocr`
- `mathpix` is not yet wired into that formula-image postprocessing path

So today the practical workaround is routing or rerun fallback, not a true merged hybrid pipeline.

## Coverage status

### Completed in the main project environment

- `local`
- `markitdown`
- `opendataloader`
- `docling`
- `mistral`
- `mathpix`

### Completed only after extra runtime work

- `paddleocr`

### Completed only in isolated environments

- `marker`
- `mineru`

### Still intentionally out of scope for recommendation work

- `deepseekocr`
- `auto`
- `html_local`

## Short conclusion to carry into README

If README stays concise, the summary should be:

- `opendataloader` is the best current local default for prose-heavy PDFs when Java is acceptable
- `markitdown` is the easiest local extra to try
- `mistral` is the best current managed OCR path for general PDFs and printed formulas
- `mathpix` is the strongest current tracked option for handwritten formulas
- `docling` has strong text quality, but is too slow on CPU to be the default
- `local` should be described as a fast baseline, not a quality recommendation
