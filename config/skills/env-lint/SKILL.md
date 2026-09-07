---
name: env-lint
description: Use when checking .env, .env.local, .env.production, or other environment files against .env.example without printing environment variable values.
---

## Rule

Never print environment variable values. Report key names only.

`CODEX_HOME` is set in `config/zsh/.zshenv`; all four harness skill dirs resolve to the shared `config/skills/env-lint`.

## Workflow

1. Run the default key-parity check:

```bash
python3 "${CODEX_HOME:-$HOME/.config/codex}/skills/env-lint/scripts/envlint.py" --format md
```

2. For explicit files:

```bash
python3 "${CODEX_HOME:-$HOME/.config/codex}/skills/env-lint/scripts/envlint.py" --example .env.example --env .env.local --format md
```

3. Interpret exit codes:
   - `0`: all required keys present
   - `1`: required key missing

4. Triage results:
   - missing keys that block local/dev/prod startup
   - extra keys that look stale
   - empty keys that require user-provided values

## Output Shape

```markdown
## Env Lint Result

- Compared:
- Missing keys:
- Extra keys:
- Empty keys:
- Deployment blockers:
- Cleanup candidates:
```

## Boundaries

- Do not print values.
- Do not ask the user to paste secret values into chat.
- Do not modify env files unless the user explicitly asks.
