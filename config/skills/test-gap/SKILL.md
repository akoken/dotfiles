---
name: test-gap
description: Use after tests with coverage, during PR review, or when comparing changed git diff lines against coverage.xml, lcov.info, or coverage.json to find untested changed lines.
---

`CODEX_HOME` is set in `config/zsh/.zshenv`; all four harness skill dirs resolve to the shared `config/skills/test-gap`.

## Workflow

1. Ensure the relevant test suite has already produced a coverage report.
2. Run the gap check:

```bash
python3 "${CODEX_HOME:-$HOME/.config/codex}/skills/test-gap/scripts/gap.py" --format md
```

3. Use explicit base/report when needed:

```bash
python3 "${CODEX_HOME:-$HOME/.config/codex}/skills/test-gap/scripts/gap.py" --base main --report coverage.xml --format md
python3 "${CODEX_HOME:-$HOME/.config/codex}/skills/test-gap/scripts/gap.py" --base develop --report lcov.info --format md
```

4. If no coverage report exists, tell the user which coverage formats are supported:
   - Cobertura `coverage.xml`
   - `lcov.info`
   - `coverage.json`
5. Treat the report as a prioritization signal, not proof of test quality.
6. Recommend tests for high-risk uncovered changed lines first:
   - error handling
   - authorization
   - persistence
   - concurrency
   - parsing
   - business logic

## Output Shape

```markdown
## Test Gap Result

- Base:
- Coverage report:
- Result:

| file | changed lines | uncovered | priority |
|---|---:|---:|---|

### Recommended Coverage
- ...
```

## Boundaries

- Do not install coverage tools.
- Do not claim covered lines are semantically well-tested.
- Do not fail a docs-only or config-only change solely because no coverage report exists.
