# Project Status

- Project: `doc_to_md`
- Active branch: `codex/release-dependency-automation`
- Target release: `0.2.0`
- State: local implementation, release verification, and mandatory pre-PR review complete; PR pending
- Scope: converter dependency compatibility, PaddleOCR/Mistral adapter updates, dependency automation, release metadata
- Baseline: project `.venv` passed Ruff and 198 tests before changes
- Known decision: Marker is monitored but removed from install extras because its current Pillow requirement conflicts with the audited base runtime
- Review: the mandatory Codex review found one in-scope Mistral SDK 2.x import incompatibility in formula OCR; it was fixed and covered by a regression test
- Verification: clean-environment tests `194 passed, 3 skipped`; project environment `208 passed`; scoped Ruff, `pip check`, direct `pip-audit`, release metadata, five isolated extras, pinned CPU profile, wheel/sdist build, Twine, CLI help, and clean wheel install all passed
- Known limitation: the legacy CUDA snapshot was checked through wheel discovery, but a full dry-run was stopped when pip began downloading the 2.4 GB Torch CUDA wheel
- Next: commit, push, open the release PR, then evaluate GitHub checks and review feedback before tagging `v0.2.0`
