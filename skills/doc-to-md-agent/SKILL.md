---
name: doc-to-md-agent
description: Use this skill when an AI agent needs to use doc_to_md as a core document-to-Markdown conversion capability, choose an engine, judge whether the output is reliable enough, and handle formula-heavy documents where Markdown math quality matters.
---

# doc-to-md-agent

Use this skill when the task is any of the following:

- Convert local documents into Markdown for downstream AI workflows.
- Call this repository from another project through Python, CLI, or FastAPI.
- Judge whether a conversion result is good enough to trust.
- Handle formula-heavy PDFs where residual formula images or broken math are important failure modes.
- Improve this repository's agent-readiness without immediately doing a large refactor.

## Quick workflow

1. Check preferred-engine readiness when the workflow is PDF-heavy.
   Call `GET /apps/conversion/engine-readiness` or use the Python helper `doc_to_md.apps.conversion.logic.list_preferred_engine_readiness()`.
   This tells the agent whether `opendataloader` and `mistral` are actually usable on the current machine.

2. Choose the narrowest integration surface that fits the task.
   For in-process single-document use `doc_to_md.apps.conversion.logic.convert_inline_document`.
   For in-process batch use `doc_to_md.apps.conversion.logic.run_conversion`.
   For service-style single-document orchestration use `POST /apps/conversion/convert-inline` with either JSON base64 or multipart upload.
   For service-style orchestration use `POST /apps/conversion/convert`.
   For workspace-local tasks use `python -m doc_to_md.cli convert`.

3. Treat conversion and evaluation as a pair.
   After each conversion, inspect the per-document `quality` payload from the API or run:

```powershell
python tools/evaluate_markdown_quality.py path\to\output.md --json
```

   When a reviewed Markdown reference already exists for the same document, also run:

```powershell
python benchmark.py --test-file path\to\document.pdf --profile preferred-pdf --reference-markdown path\to\reviewed.md --save-json
```

   Use the reference metrics when formula fidelity matters:
   `reference_formula_status`, `reference_formula_recall`, and `reference_formula_similarity`.

4. Use `formula_status` to decide whether to trust math-heavy output.
   `good`: safe to continue into chunking, indexing, or summarization.
   `review`: do a targeted spot-check on the formula-heavy sections before proceeding.
   `poor`: do not trust the formulas yet; retry with another engine or enable formula OCR.

5. For formula-heavy PDFs, prefer the stronger paths first.
   Start with `opendataloader` for the best current local balance.
   Use `mistral` when managed OCR is acceptable.
   If formula images remain, enable `FORMULA_OCR_ENABLED=true`.

## Decision rules

- If `quality.status=good` and `formula_status=not_applicable`, the document is probably fine for ordinary prose workflows.
- If `formula_status=good`, formulas are likely usable as-is.
- If `formula_status=review`, inspect the flagged regions and look for flattened formulas, fragmented OCR spacing, or missing math delimiters.
- If `formula_status=poor`, switch engines or OCR strategy before trusting the result.
- If the document is formula-heavy and `formula_context_without_math` appears, assume formulas may have been flattened into plain text and verify manually.

## Read These References

- Read [references/current-interfaces.md](references/current-interfaces.md) when deciding how another project should call this repo today.
- Read [../../API_RESPONSE_CONTRACT.md](../../API_RESPONSE_CONTRACT.md) when a caller depends on stable HTTP response fields or needs to parse errors safely.
- Read [references/quality-rubric.md](references/quality-rubric.md) when deciding whether a result is acceptable.
- Read [references/improvement-plan.md](references/improvement-plan.md) when the task is to make the project more agent-friendly over time.
