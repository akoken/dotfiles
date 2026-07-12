---
name: secret-guard
description: Use before commits, PRs, pushes, or when checking staged diffs/files for leaked API keys, tokens, private keys, JWTs, credentials, or high-entropy secrets with redacted output.
---

## Rule

Never print secret values. Report rule names, file paths, line numbers, and redacted snippets only.

## Workflow

1. Prefer scanning the staged diff:

```bash
python3 /Users/akoken/Developer/repos/dotfiles/config/codex/skills/secret-guard/scripts/guard.py --format md
```

2. For explicit files:

```bash
python3 /Users/akoken/Developer/repos/dotfiles/config/codex/skills/secret-guard/scripts/guard.py --files path/to/file --format md
```

3. For known false positives:

```bash
python3 /Users/akoken/Developer/repos/dotfiles/config/codex/skills/secret-guard/scripts/guard.py --allowlist .secret-allowlist --format md
```

4. Interpret exit codes:
   - `0`: clean
   - `1`: finding present

5. Recommend one of:
   - remove the secret
   - replace with an env var or secret manager reference
   - rotate the exposed credential
   - allowlist only after confirming it is not a real secret

## Output Shape

```markdown
## Secret Guard Result

- Scope:
- Result: clean / findings
- Findings:
  - file:line rule redacted-snippet
- Required action:
- Follow-up:
```

## Boundaries

- Do not read `.env` values unless the user explicitly asks to scan that file; even then never repeat values.
- Do not install tools.
- Do not rewrite files unless the user separately asks for a fix.
