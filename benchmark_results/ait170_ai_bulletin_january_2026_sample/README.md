# General Text-Heavy PDF Benchmark

This directory preserves the benchmark artifacts for a prose-heavy PDF sample used to compare the repository's major PDF engines.

## Why this sample matters

Use this suite when the question is:

- which engine is the easiest local option for ordinary PDFs?
- which local engine gives the best balance of quality and setup cost?
- when is a managed OCR path worth it for non-formula-heavy documents?

## Practical reading

- `markitdown` is the simplest local extra to install and try.
- `opendataloader` is the stronger local default when Java is acceptable.
- `mistral` is the stronger managed OCR path when you want better output quality without maintaining a heavy local stack.
- `mathpix` is now included in this baseline too, but it did not improve the recommendation for ordinary prose-heavy PDFs.
- Keep `mathpix` as a formula-specialist engine, not the default choice for general text-heavy PDFs.
- The archived `mineru` artifact predates the current MinerU2.5-Pro integration. Use `mineru_pro` and the `mineru-pro` benchmark profile for a new Pro-specific rerun.

## Main artifacts

- [report.md](report.md)
- [result.json](result.json)
- [outputs](outputs/)

## Note about the original input PDF

The original source PDF for this benchmark was evaluated from a local working `data/` directory during the benchmark run and is not re-archived inside this suite.
