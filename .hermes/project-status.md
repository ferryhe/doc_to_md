# Project Status

- Project: `doc_to_md`
- Active branch: `codex/release-dependency-automation`
- Target release: `0.2.0`
- State: PR #15 open; all 13 GitHub checks passed; follow-up review handling in progress
- Scope: converter dependency compatibility, PaddleOCR/Mistral adapter updates, dependency automation, release metadata
- Baseline: project `.venv` passed Ruff and 198 tests before changes
- Known decision: Marker is monitored but removed from install extras because its current Pillow requirement conflicts with the audited base runtime
- Review: the mandatory Codex review found one in-scope Mistral SDK 2.x import incompatibility in formula OCR; it was fixed and covered by a regression test
- Remote review: rejected an inaccurate Mistral 1.9.11 import finding after testing the real wheel; accepted a test-maintainability finding and changed optional-extra assertions to parse TOML structurally
- Verification: clean-environment tests `194 passed, 3 skipped`; project environment `208 passed`; scoped Ruff, `pip check`, direct `pip-audit`, release metadata, five isolated extras, pinned CPU profile, wheel/sdist build, Twine, CLI help, and clean wheel install all passed
- Known limitation: the legacy CUDA snapshot was checked through wheel discovery, but a full dry-run was stopped when pip began downloading the 2.4 GB Torch CUDA wheel
- Next: push the narrow review fix, rerun GitHub checks, perform the final follow-up pass, then merge and tag `v0.2.0`
