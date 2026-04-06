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
- `027d5b8` Document API response contract
- `7b4247b` Add agent quality signals to benchmark
- `6523281` Add preferred engine readiness endpoint
- `710b545` Add preferred PDF benchmark profile

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

### Step 3: representative PDF benchmark path

- Enhanced `benchmark.py` so successful engine results now include:
  - `quality_status`
  - `formula_status`
  - `diagnostic_codes`
  - full `quality`
  - full `trace`
- Added `tests/test_benchmark.py` using the tracked real PDF fixture.
- Added real-PDF evaluation guidance for manual `data/input/` checks, later consolidated into `PDF_ENGINE_EVALUATION.md`.

Verification:

- `.venv\Scripts\python -m pytest tests/test_benchmark.py tests/test_real_pdf_smoke.py tests/test_api_contract.py tests/test_api.py tests/test_conversion_logic.py -q`
- `.venv\Scripts\python benchmark.py --test-file "data/input/保险公司偿付能力监管规则第4号：保险风险最低资本（非寿险业务）.pdf" --engines local --output-dir tmp_user_sample_benchmark --save-json`

Observed result on the representative sample:

- `local` completed in about `0.50s`
- `quality_status=review`
- `formula_status=review`
- `diagnostic_codes=["formula_context_without_math"]`
- formulas were not recovered as math segments, but the prose remained readable enough for analysis

### Step 4: preferred engine routing for opendataloader and mistral

- Added a preferred-engine readiness helper and API surface for the two currently favored PDF engines:
  - `doc_to_md.apps.conversion.logic.list_preferred_engine_readiness(...)`
  - `GET /apps/conversion/engine-readiness`
- Added benchmark profile support:
  - `python benchmark.py --profile preferred-pdf`
- Updated benchmark and skill docs so the normal evaluation path now points at `opendataloader` plus `mistral`.

Verification:

- `.venv\Scripts\python -m pytest tests/test_engine_readiness.py tests/test_benchmark.py tests/test_real_pdf_smoke.py tests/test_api.py tests/test_conversion_logic.py -q`
- direct readiness probe from Python helper
- real representative PDF regression via inline conversion
- real representative PDF benchmark with `preferred-pdf`

Observed result on the current machine:

- `mistral` is ready
- `opendataloader` is blocked because Java 11+ is not on `PATH`
- `opendataloader` is also blocked because `opendataloader-pdf` is not installed
- the representative PDF still produces `review/review` on `local`, so it remains a good formula-quality regression sample
- running `preferred-pdf` on the representative PDF produced:
  - `opendataloader`: blocked immediately by missing Java
  - `mistral`: success in about `11.13s`
  - `mistral quality_status=review`
  - `mistral formula_status=review`
  - `mistral diagnostic_codes=["fragmented_math_tokens"]`

### Step 5: reference-aware formula benchmark

- Extended `benchmark.py` with `--reference-markdown` so a reviewed Markdown file can act as a gold reference for formula readability.
- Added `doc_to_md.formula_reference.evaluate_formula_reference(...)` to score:
  - recovered formula recall
  - average reference similarity
  - fragmented candidate formula count
  - reference-aware diagnostics
- Expanded `doc_to_md.quality` so fenced ````math` blocks count as explicit math segments.
- Added tests in:
  - `tests/test_formula_reference.py`
  - `tests/test_quality.py`
  - `tests/test_benchmark.py`

Verification:

- `.venv\Scripts\python -m pytest tests/test_formula_reference.py tests/test_quality.py tests/test_benchmark.py tests/test_real_pdf_smoke.py tests/test_api.py tests/test_conversion_logic.py -q`
- `.venv\Scripts\python benchmark.py --test-file "data/input/保险公司偿付能力监管规则第4号：保险风险最低资本（非寿险业务）.pdf" --profile preferred-pdf --reference-markdown "data/output/保险公司偿付能力监管规则第4号：保险风险最低资本（非寿险业务）.md" --output-dir tmp_user_reference_formula_benchmark --save-json`

Observed result on the representative sample:

- `opendataloader`
  - `quality_status=review`
  - `formula_status=review`
  - `reference_formula_status=poor`
  - `reference_formula_recall=0%`
  - formulas were not recovered as explicit math segments
- `mistral`
  - `quality_status=review`
  - `formula_status=review`
  - `reference_formula_status=review`
  - `reference_formula_recall=96%`
  - `reference_formula_similarity=96%`
  - the remaining gap is mostly fragmented math tokens plus a small number of missed formulas
