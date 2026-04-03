# Quality Rubric

## Read the structured fields first

Each converted document can expose:

- `quality.status`
- `quality.formula_status`
- `quality.diagnostics[]`

Use those fields before doing manual review.

## Interpreting `formula_status`

- `good`: the output contains usable math signals and no formula-specific hard failures were detected.
- `review`: the output might still be usable, but it needs a focused spot-check.
- `poor`: formulas should not be trusted yet.
- `not_applicable`: no formula-heavy signal was detected.

## Important diagnostic codes

- `formula_image_reference`
  Meaning: image references still look formula-like.
  Action: enable formula OCR or switch engines before trusting the result.

- `formula_context_without_math`
  Meaning: the document talks like a formula section, but no math segments were recovered.
  Action: inspect that section for flattened or lost formulas.

- `fragmented_math_tokens`
  Meaning: OCR likely inserted spacing into symbols or numbers.
  Action: inspect formulas before downstream use.

- `math_html_entity`
  Meaning: HTML entities remain inside math.
  Action: treat as review-worthy cleanup.

- `unbalanced_display_math`
  Meaning: display math delimiters look broken.
  Action: treat as a hard failure for formula trust.

- `ocr_placeholder`
  Meaning: the output still contains OCR fallback or failure placeholders.
  Action: do not treat the section as fully extracted.

## Suggested retry order for formula-heavy PDFs

1. `opendataloader`
2. `opendataloader` plus `FORMULA_OCR_ENABLED=true`
3. `mistral`
4. `mistral` plus formula OCR if residual images remain

If the result is still `poor`, stop auto-trusting formulas and escalate to manual review or a more specialized engine experiment.
