# Agent Worklog

## 2026-04-03

### Current branch

- `feature/agent-readiness-foundation`

### Recent completed commits

- `19e0368` Add agent-ready quality checks and inline conversion API
- `27b18e5` Add formula OCR request overrides and postprocess trace
- `09214a2` Add multipart support for inline API
- `8bb2c7d` Document multipart inline usage and update roadmap

### Current focus

- Make real-PDF smoke testing a repeatable repository capability.
- Use that smoke path every time we extend the agent-facing API.

### Planned verification policy

- Run at least one real PDF smoke path for each implementation step.
- Prefer exercising both:
  - direct Python helper flow
  - FastAPI inline conversion flow

### Step 1: real PDF smoke baseline

- Add a deterministic real PDF fixture under `tests/fixtures/`.
- Add smoke tests that run the local engine against that fixture through:
  - `convert_inline_document(...)`
  - `POST /apps/conversion/convert-inline` with JSON
  - `POST /apps/conversion/convert-inline` with multipart
  - `run_conversion(...)` batch flow

Status:

- Implemented in `tools/generate_smoke_pdf.py`
- Implemented in `tests/test_real_pdf_smoke.py`
- Fixture generated at `tests/fixtures/real_smoke.pdf`

Verification:

- `.venv\Scripts\python tools/generate_smoke_pdf.py`
- `.venv\Scripts\python -m pytest tests/test_real_pdf_smoke.py -q`
- Direct extraction sanity check confirms the PDF text is readable by `pypdf`

Observed result:

- Real PDF smoke path passes for Python inline, HTTP inline JSON, HTTP inline multipart, and batch directory conversion.

### Next step

- Document the stable API response contract for both general callers and AI agents.
- Add response-contract tests that lock the external JSON shape using the same real PDF fixture.
