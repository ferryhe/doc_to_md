# Agent Worklog

## 2026-04-03

### Current branch

- `feature/agent-readiness-foundation`

### Recent completed commits

- `19e0368` Add agent-ready quality checks and inline conversion API
- `27b18e5` Add formula OCR request overrides and postprocess trace
- `09214a2` Add multipart support for inline API
- `8bb2c7d` Document multipart inline usage and update roadmap
- `3b1b1c3` Add real PDF smoke fixture and tests

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

### Step 2: stable response contract

- Added `API_RESPONSE_CONTRACT.md` as the public JSON field contract for:
  - `POST /apps/conversion/convert`
  - `POST /apps/conversion/convert-inline`
- Added `tests/test_api_contract.py` to lock the success response shape against the real PDF fixture.
- Linked the contract from `README.md` and skill references.

Verification:

- Real response samples captured from the live FastAPI app using `tests/fixtures/real_smoke.pdf`
- `.venv\Scripts\python -m pytest tests/test_real_pdf_smoke.py tests/test_api_contract.py tests/test_api.py tests/test_conversion_logic.py -q`
- `.venv\Scripts\python -m pytest tests/test_quality.py tests/test_formula_ocr.py tests/test_settings.py tests/test_postprocessor_entities.py -q`

Observed result:

- Traditional callers can rely on the documented fields.
- AI agents can rely on the same fields plus `quality` and `trace` for decision-making.
- Real-PDF smoke and contract coverage passed together with broader postprocessing regressions.
