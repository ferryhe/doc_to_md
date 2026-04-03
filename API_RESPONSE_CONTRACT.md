# API Response Contract

This document pins the public JSON response shape for the FastAPI conversion endpoints.

The goal is to keep the project usable for two caller types at the same time:

- traditional programs that need stable machine-readable fields
- AI agents that need the same fields plus enough diagnostics to judge result quality

## Stability rule

For the existing endpoints, these fields should be treated as stable:

- `POST /apps/conversion/convert`
- `POST /apps/conversion/convert-inline`

Compatible future changes should prefer:

- adding new optional fields
- adding new diagnostic codes inside `quality.diagnostics`
- adding new trace fields without renaming or removing the current ones

Avoid:

- renaming existing top-level keys
- changing a field from scalar to object
- removing `quality`, `trace`, `assets`, or the current batch metrics

## Inline response

`POST /apps/conversion/convert-inline` returns:

```json
{
  "status": "converted",
  "source_name": "real_smoke.pdf",
  "engine": "local",
  "model": null,
  "markdown": "# real_smoke\n\n...",
  "quality": {},
  "trace": {},
  "asset_count": 0,
  "assets": [],
  "duration_seconds": 0.0034
}
```

Field meanings:

- `status`: currently always `"converted"` for successful inline calls
- `source_name`: caller-supplied filename
- `engine`: engine that handled the document
- `model`: engine model when meaningful, otherwise `null`
- `markdown`: converted Markdown payload
- `quality`: heuristic Markdown-quality report for judging trustworthiness
- `trace`: postprocessing trace for debugging or retry decisions
- `asset_count`: number of generated sidecar assets
- `assets`: asset metadata list, optionally including `content_base64`
- `duration_seconds`: end-to-end inline conversion duration

## Batch response

`POST /apps/conversion/convert` returns:

```json
{
  "engine": "local",
  "model": null,
  "input_dir": "C:\\temp\\input",
  "output_dir": "C:\\temp\\output",
  "total_candidates": 1,
  "eligible": 1,
  "converted": 1,
  "failed": 0,
  "skipped_since": 0,
  "dry_run": 0,
  "duration_seconds": 0.0046,
  "results": [
    {
      "source_path": "C:\\temp\\input\\real_smoke.pdf",
      "status": "converted",
      "output_path": "C:\\temp\\output\\real_smoke.md",
      "error": null,
      "modified_at": "2026-04-03T12:38:36.602696",
      "quality": {},
      "trace": {}
    }
  ]
}
```

Field meanings:

- `engine` / `model`: request-level engine identity
- `input_dir` / `output_dir`: resolved directories used for the run
- `total_candidates`: documents found before filtering
- `eligible`: documents that were eligible to process
- `converted`: successful conversions
- `failed`: failed conversions
- `skipped_since`: files skipped by the `since` filter
- `dry_run`: count of documents reported but not converted
- `duration_seconds`: total batch run duration
- `results`: one entry per processed candidate

## Shared object: `quality`

Both inline and batch results use the same `quality` object:

```json
{
  "status": "good",
  "formula_status": "not_applicable",
  "headings": 1,
  "bullet_lines": 0,
  "table_lines": 0,
  "image_references": 0,
  "formula_image_references": 0,
  "inline_math_segments": 0,
  "block_math_segments": 0,
  "diagnostics": []
}
```

Contract notes:

- `status` is the overall Markdown judgment: `good`, `review`, or `poor`
- `formula_status` is the formula-specific judgment: `good`, `review`, `poor`, or `not_applicable`
- count fields are always integers
- `diagnostics` is always a list, even when empty

Each diagnostic entry contains:

- `code`
- `severity`
- `message`
- `count`

## Shared object: `trace`

Both inline and batch results use the same `trace` object:

```json
{
  "math_normalization_changed": false,
  "formula_ocr_enabled": false,
  "formula_ocr_provider": null,
  "formula_ocr_attempted": false,
  "formula_ocr_applied": false,
  "formula_image_references_before": 0,
  "formula_image_references_after": 0,
  "asset_count_before": 0,
  "asset_count_after": 0,
  "postprocess_changed": false
}
```

Contract notes:

- the current trace surface is postprocessing-focused
- `formula_ocr_provider` can be `null`
- count fields are always integers

## Shared object: `assets`

Inline responses always include `assets`, even when the list is empty.

Each asset entry uses this shape:

```json
{
  "filename": "a.png",
  "subdir": "assets",
  "media_type": "image/png",
  "content_base64": null
}
```

Contract notes:

- `content_base64` is `null` unless the caller requests `include_assets=true`
- `subdir` and `media_type` can be `null`

## Error responses

There are two public error shapes today.

Validation-style errors return a `detail` list:

```json
{
  "detail": [
    {
      "loc": ["body", "formula_ocr_enabled"],
      "msg": "Input should be a valid boolean",
      "type": "bool_parsing"
    }
  ]
}
```

Request or runtime errors return a `detail` string:

```json
{
  "detail": "Input document must contain valid base64 content."
}
```

Current status code usage:

- `400`: bad request payload after parsing, such as invalid base64
- `415`: unsupported content type
- `422`: validation or missing-field errors
- `500`: unexpected runtime failures

## Real-PDF verification source

The success contract in this document is backed by the repository smoke fixture:

- `tests/fixtures/real_smoke.pdf`

The response shape is locked by:

- `tests/test_real_pdf_smoke.py`
- `tests/test_api_contract.py`
- supporting serialization checks in `tests/test_api.py`
