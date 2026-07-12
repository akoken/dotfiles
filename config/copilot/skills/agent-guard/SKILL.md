---
name: agent-guard
description: Use for stronger secret leak prevention with Agent Guard and gitleaks: scan staged changes, working trees, or paths; install repo-local pre-commit hooks; mask command output; check PII; or compare/upgrade from lightweight secret scanning before commits, PRs, pushes, or agent runs.
---

## Binary

Use the vendored binary directly:

```bash
/Users/akoken/Developer/repos/dotfiles/config/codex/skills/agent-guard/bin/agent-guard check
```

Required tools: `sh`, `awk`, `git`, `jq`, and `gitleaks`.

## Workflow

1. Run dependency check first when using this skill in a new machine or shell:

```bash
/Users/akoken/Developer/repos/dotfiles/config/codex/skills/agent-guard/bin/agent-guard check
```

2. Prefer staged scans before commits:

```bash
/Users/akoken/Developer/repos/dotfiles/config/codex/skills/agent-guard/bin/agent-guard scan-staged
```

3. Use a working-tree scan after agent edits or before a PR:

```bash
/Users/akoken/Developer/repos/dotfiles/config/codex/skills/agent-guard/bin/agent-guard scan-working-tree
```

4. Use path scans for explicit directories or files:

```bash
/Users/akoken/Developer/repos/dotfiles/config/codex/skills/agent-guard/bin/agent-guard scan-path .
```

5. For commands that may print secrets, run through the redacting wrapper:

```bash
/Users/akoken/Developer/repos/dotfiles/config/codex/skills/agent-guard/bin/agent-guard exec -- printenv
```

6. For text that may contain PII:

```bash
printf '%s\n' "$TEXT" | /Users/akoken/Developer/repos/dotfiles/config/codex/skills/agent-guard/bin/agent-guard pii-filter
```

7. To install the stable native git pre-commit hook in the current repo, use the vendored installer from inside that repo:

```bash
/Users/akoken/Developer/repos/dotfiles/config/codex/skills/agent-guard/install.sh git-hooks
```

Only run hook installation when the user explicitly asks for it. It sets `core.hooksPath=githooks` and refuses to overwrite an incompatible existing hook setup.

## Interpretation

- Exit `0`: clean.
- Exit `1`: secret-like finding from scan commands.
- Exit `2`: dependency, policy, hook block, or usage failure.
- Never print raw secrets. Report file/path, rule type, command used, and the redacted Agent Guard output only.

## Boundaries

- Do not enable experimental Codex plugin hooks unless the user explicitly asks.
- Do not install or download dependencies unless the user explicitly asks.
- Do not treat this as a vault, DLP, or credential rotation system.
- Gitignored files are not covered by working-tree backstops; use `scan-path` for explicit ignored directories.
- Output masking is best-effort and heuristic; unusual secret formats can still slip through.
