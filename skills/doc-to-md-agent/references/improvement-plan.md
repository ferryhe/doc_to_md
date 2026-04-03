# Agent-Readiness Improvement Plan

The repository is already close to being agent-usable. The best next moves are small and composable, not a redesign.

## Direction

The project should evolve into a dual-surface tool:

- an agent-oriented surface that is easy to call, easy to judge, and easy to retry
- a stable general-purpose surface that ordinary programs can keep calling without knowing anything about agents

That means the right target is not "replace the old API with an agent API".
The right target is "keep one conversion core, then expose two well-shaped integration surfaces on top".

## Position On The General API

The traditional API should absolutely stay.

Reasons:

1. Other services, schedulers, ETL jobs, and backend programs need predictable request-response behavior, not agent-specific workflow semantics.
2. The agent surface becomes stronger when it is built on top of a clean programmatic surface rather than a private orchestration path.
3. Keeping the general API forces the project to stay modular, typed, and testable.
4. Long term, an AI agent is just one caller type. A reusable document conversion tool should still be valuable to non-agent software.

Recommended rule:

- keep `run_conversion(...)`, `convert_inline_document(...)`, CLI, and FastAPI as first-class supported surfaces
- add agent-specific guidance, diagnostics, and retry hints on top of them
- avoid baking agent-only assumptions into the core engine contracts

## Phase 0: What is already enough now

- Keep the shared conversion core.
- Keep the current CLI and FastAPI surfaces.
- Use the new `quality` report as the agent-facing judgment layer.
- Use this skill to standardize engine choice and retry behavior.

This phase gives AI agents a stable workflow without rewriting the project.

## Phase 1: Finish The Agent-Usable Foundation

Status:

- single-document inline conversion is now in place
- structured `quality` output is now in place
- request-level formula OCR controls are now in place
- postprocessing execution trace metadata is now in place

Next actions in this phase:

1. Add multipart upload support in addition to JSON base64.
   Goal: keep `convert-inline` friendly to normal web clients and traditional backends.
   Why: base64 is good for portability, but multipart is more natural for many callers.

2. Document the stable response contract.
   Goal: pin the shape of `quality`, `assets`, and error responses.
   Why: both agents and traditional programs depend on predictable fields.

3. Extend trace metadata one level deeper when useful.
   Goal: include more engine-facing details later, such as chunking or provider fallback decisions, without breaking the current response shape.
   Why: the current trace is already useful, but it is still focused on postprocessing.

Acceptance criteria for Phase 1:

- another service can call the API without using input/output directories
- an agent can tell from the response whether formulas are safe, risky, or broken
- an agent can request formula OCR per document instead of relying on global environment settings
- no existing batch or CLI workflow has to be rewritten

## Phase 2: Make Formula Quality Measurable

Goal:

Move from heuristic formula checking to evidence-backed formula evaluation.

Tasks:

1. Build a compact gold dataset of formula-heavy files.
   Include standalone formulas, inline formulas, matrix labels, mixed Chinese-English actuarial notation, table headers, and OCR-noisy scans.

2. Store expected snippet targets.
   Save short expected Markdown spans rather than entire-file golden outputs.

3. Add a benchmark runner for formula recovery.
   Compare:
   - residual formula image count
   - recovered inline math count
   - recovered block math count
   - fragmented math warning count
   - exact or fuzzy match on target snippets

4. Add a manual review sheet for formula fidelity.
   Human reviewers should score:
   - semantic correctness
   - LaTeX cleanliness
   - inline vs block choice
   - table-cell math readability

Acceptance criteria for Phase 2:

- the project can compare engines on formula handling with repeatable numbers
- `formula_status` is informed by real benchmark evidence and not only heuristics
- release decisions for formula-heavy workflows can be justified

## Phase 3: Add Agent-Specific Guidance Without Polluting The Core

Goal:

Keep the core library general-purpose while making agent usage much more reliable.

Tasks:

1. Expand the skill into a decision playbook.
   Include engine choice rules, retry order, failure interpretation, and when to escalate to manual review.

2. Add example prompts and tool-call patterns for common agent tasks.
   Examples:
   - convert a single uploaded PDF
   - retry if `formula_status=poor`
   - preserve images when formulas are not the priority

3. Add "agent-safe defaults".
   Examples:
   - prefer `opendataloader` for local formula-heavy PDFs
   - return quality by default
   - keep assets metadata even when asset bytes are omitted

4. Add tests that lock in the agent-facing contract.
   Cover:
   - `quality` response shape
   - inline conversion error behavior
   - trace metadata
   - formula retry hints when added

Acceptance criteria for Phase 3:

- a new AI agent can use the tool correctly by following the skill
- agent behavior becomes more consistent across documents
- the core conversion modules still stay free of agent-specific orchestration code

## Phase 4: Strengthen The Traditional Programmatic Surface

Goal:

Make the project more useful to ordinary software while preserving the same core used by agents.

Tasks:

1. Keep batch and inline APIs versioned and documented.
2. Add idempotent error codes and clearer machine-readable failure classes.
3. Support both sync request-response and future async job-style orchestration if large documents require it.
4. Publish examples for:
   - Python import usage
   - HTTP inline usage
   - HTTP directory batch usage
   - CLI usage in scheduled jobs

Acceptance criteria for Phase 4:

- the project remains attractive as a standalone document conversion service
- traditional backends do not have to adopt agent concepts to consume it
- the agent surface remains a thin specialization, not a forked product

## Phase 5: Operational Hardening

Goal:

Make the tool dependable enough for repeated production use.

Tasks:

1. Add structured logging and request correlation ids.
2. Add rate-limit aware retry behavior for remote OCR providers.
3. Add size, page-count, and engine-specific safeguards to avoid pathological requests.
4. Add release notes that summarize engine quality changes, especially for formulas.

Acceptance criteria for Phase 5:

- failures are diagnosable from logs
- provider-side transient failures are easier to recover from
- downstream callers can upgrade with confidence

## Delivery Order

Recommended order from here:

1. multipart inline upload
2. stable response-contract documentation
3. formula gold set and formula benchmark
4. agent playbook expansion
5. stronger machine-readable error model
6. deeper engine-level trace detail when justified

## Recommendation

Do not start with a major refactor.
Start by treating this repo as:

- conversion core
- general API
- quality judge
- agent skill layered on top

That keeps the project broadly reusable while steadily making it much better for AI agents.
