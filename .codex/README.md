# Codex Worker Notes for doc_to_md

This directory records the local Codex worker convention for this repo.

Start every worker run with:

```bash
git status --short --branch
```

Then read:

1. `AGENTS.md`
2. `.hermes/project-status.md`
3. The active plan under `docs/plans/`

Do not commit, push, or open PRs from a standalone Codex CLI worker without explicit approval. When this repo is being operated through Hermes/project-agent automation, follow `AGENTS.md` as the authoritative repo workflow policy.
