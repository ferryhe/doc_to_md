# Current Interfaces

## What already exists

This repository already has three usable integration surfaces:

- Python single-document inline: `doc_to_md.apps.conversion.logic.convert_inline_document(...)`
- Python: `doc_to_md.apps.conversion.logic.run_conversion(...)`
- CLI: `python -m doc_to_md.cli convert ...`
- FastAPI: `POST /apps/conversion/convert`
- FastAPI single-document inline: `POST /apps/conversion/convert-inline`

Those surfaces are good enough for agent use in the workspace and for server-side orchestration.

## Interface strategy

The project should keep both of these layers:

- core reusable programmatic interfaces for ordinary software
- guidance and diagnostics that make those same interfaces safe for AI agents

The key architectural rule is:

- do not create a separate hidden conversion path for agents
- build agent readiness on top of the same typed API that normal programs use

## Current strengths

- One shared conversion pipeline is reused by CLI and FastAPI.
- Engine selection is centralized and consistent.
- Formula-image postprocessing already exists behind `FORMULA_OCR_ENABLED`.
- Conversion results now include a structured `quality` report per converted document.
- Conversion results now include postprocessing `trace` metadata per converted document.
- Single-document inline conversion no longer requires input/output directories.
- The inline HTTP API now supports both JSON base64 and multipart upload on the same endpoint.
- The same core already serves both batch workflows and agent-style single-document calls.
- Batch and inline requests can now override formula OCR settings per request.

## Current limits

- Formula quality is still heuristic, not benchmark-backed against a gold dataset.
- The trace surface is postprocessing-focused and does not yet expose deeper per-engine runtime details.

## Recommended use today

- Local agent working in the same repo or machine:
  use CLI, `run_conversion(...)`, or `convert_inline_document(...)`, then inspect `quality`.
- Another backend service with shared filesystem access:
  use the FastAPI layer.
- If a caller needs one request in and one response out:
  use `POST /apps/conversion/convert-inline`, choosing JSON or multipart based on the client environment.

## Keep These Stable

These should remain first-class and documented:

- `run_conversion(...)`
- `convert_inline_document(...)`
- `POST /apps/conversion/convert`
- `POST /apps/conversion/convert-inline`

If new agent-specific behavior is added later, prefer:

- new response metadata
- optional request flags
- extra helper functions

Avoid:

- changing existing behavior in agent-only ways
- forcing non-agent callers to understand retry or review semantics just to get Markdown
