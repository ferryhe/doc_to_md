# Doc to Markdown 输出规范化与 Markdown Corpus Contract Implementation Plan

> **For Hermes/Codex:** Use the project-isolated Codex worker pattern. Read `AGENTS.md` and `.hermes/project-status.md` before each run. Do not commit, push, or open PRs without explicit approval.

**Goal:** 把 doc_to_md 的批量转换结果规范成 markdown_manifest + documents + conversion evidence。

**Architecture:** 保留多引擎能力；新增统一输出目录、manifest schema、转换质量状态和 agent-readable JSON。

**Tech Stack:** Project-native stack plus CLI-first JSON/JSONL manifests. Python projects should use Typer/Pydantic where already present; TypeScript projects should preserve pnpm/OpenAPI workflow.

---

## Context

This repository is one module in the broader agent-operated knowledge pipeline:

```text
web_listening -> doc_to_md -> md_to_rag -> rag_to_agent/domain adapters -> ai_interface
```

Current project role: 文档转换 CLI，负责 PDF/Office/HTML/扫描件 -> Markdown，并保留转换证据。

Current planning scope: 规范化 Markdown corpus 输出，让 md_to_rag 可以直接按 manifest 增量构建。

## Non-Negotiable Contracts

1. CLI outputs must be machine-readable and stable (`--json` where applicable).
2. Artifacts must be path-portable and manifest-driven.
3. Reruns must be idempotent.
4. Every derived artifact must preserve provenance back to its input.
5. Secrets/API keys must never be written into manifests or committed files.
6. Cross-repo integration happens through files/manifests/tool specs, not hidden imports.

## Proposed Tasks

### Task 1: 盘点 CLI 与引擎输出

**Objective:** 阅读 README、src CLI、tests，列出当前 convert/batch 输出文件和 metadata。

**Files:**
- Modify/Create project-specific files identified during the task.
- Update tests or fixtures for the changed contract.

**Steps:**
1. Inspect the current implementation and write down exact files touched.
2. Add or update the smallest contract/test fixture first.
3. Implement the minimal change.
4. Run the focused verification command.
5. Update `.hermes/project-status.md` with result and next action.

**Verification:** 运行现有 pytest；记录当前 contract 缺口。

### Task 2: 定义 markdown manifest v1

**Objective:** 新增 docs/contracts/doc-to-md-markdown-manifest-v1.md，字段含 source_asset、markdown_path、engine、engine_version、quality_flags、hashes。

**Files:**
- Modify/Create project-specific files identified during the task.
- Update tests or fixtures for the changed contract.

**Steps:**
1. Inspect the current implementation and write down exact files touched.
2. Add or update the smallest contract/test fixture first.
3. Implement the minimal change.
4. Run the focused verification command.
5. Update `.hermes/project-status.md` with result and next action.

**Verification:** 示例覆盖 PDF、HTML、Office、OCR fallback。

### Task 3: 实现 batch 输出目录标准

**Objective:** 统一 `markdown/`、`assets/`、`conversion_manifest.jsonl`、`markdown_manifest.json`；旧输出兼容。

**Files:**
- Modify/Create project-specific files identified during the task.
- Update tests or fixtures for the changed contract.

**Steps:**
1. Inspect the current implementation and write down exact files touched.
2. Add or update the smallest contract/test fixture first.
3. Implement the minimal change.
4. Run the focused verification command.
5. Update `.hermes/project-status.md` with result and next action.

**Verification:** 测试相对路径、hash、失败项 status。

### Task 4: 质量标记规范

**Objective:** 标准化 formula/table/image_only/ocr_low_confidence/conversion_failed 等 flags。

**Files:**
- Modify/Create project-specific files identified during the task.
- Update tests or fixtures for the changed contract.

**Steps:**
1. Inspect the current implementation and write down exact files touched.
2. Add or update the smallest contract/test fixture first.
3. Implement the minimal change.
4. Run the focused verification command.
5. Update `.hermes/project-status.md` with result and next action.

**Verification:** 测试公式型 PDF fixture 至少能产生明确 flag。

### Task 5: 给 md_to_rag 的 handoff fixture

**Objective:** 新增 tests/fixtures/markdown_manifest/，作为 md_to_rag ingest 的 contract fixture。

**Files:**
- Modify/Create project-specific files identified during the task.
- Update tests or fixtures for the changed contract.

**Steps:**
1. Inspect the current implementation and write down exact files touched.
2. Add or update the smallest contract/test fixture first.
3. Implement the minimal change.
4. Run the focused verification command.
5. Update `.hermes/project-status.md` with result and next action.

**Verification:** 跨 repo 手工 smoke：md_to_rag ingest fixture。


---

## Acceptance Criteria

- A Codex worker can understand this repo's boundary from `AGENTS.md`.
- A future implementation branch can start from this plan without needing cross-chat context.
- The module's input/output contract is explicit enough for the next module in the chain.
- All new behavior is testable through CLI commands and fixture manifests.

## Recommended First PR

Start with documentation/contracts and fixture-only changes. Do not implement all runtime behavior in the first PR. The first PR should make the intended contract reviewable before code follows.
