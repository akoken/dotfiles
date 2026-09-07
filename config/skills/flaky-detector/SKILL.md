---
name: flaky-detector
description: Use when diagnosing flaky tests, nondeterministic failures, intermittent CI failures, race-prone test suites, or when the user asks to run a test command repeatedly.
---

# Flaky Detector

Adapted from `mturac/pluginpool-flaky-detector`. Helper code is vendored under `scripts/` with its MIT license.

`CODEX_HOME` is set in `config/zsh/.zshenv`; all four harness skill dirs resolve to the shared `config/skills/flaky-detector`.

## Workflow

1. Ask for or infer the narrowest test command worth repeating.
2. Prefer a small run count first unless the user requests more:

```bash
python3 "${CODEX_HOME:-$HOME/.config/codex}/skills/flaky-detector/scripts/flaky.py" --cmd "pytest -v" --runs 10 --format md
```

3. Select parser when useful:

```bash
python3 "${CODEX_HOME:-$HOME/.config/codex}/skills/flaky-detector/scripts/flaky.py" --cmd "dotnet test" --runs 5 --format md
python3 "${CODEX_HOME:-$HOME/.config/codex}/skills/flaky-detector/scripts/flaky.py" --cmd "go test ./..." --parser gotest --runs 10 --format md
python3 "${CODEX_HOME:-$HOME/.config/codex}/skills/flaky-detector/scripts/flaky.py" --cmd "npm test -- --runInBand" --parser jest --runs 10 --format md
```

4. Use `--parallel N` only when the suite is known to be parallel-clean.
5. Interpret exit codes:
   - `0`: no flaky or always-failing tests parsed
   - `1`: flaky tests found
   - `2`: always-failing tests found
   - `3`: no tests parsed; rerun with a more verbose reporter
6. Recommend next action for the worst 1-3 offenders:
   - isolate shared state
   - remove time dependence
   - seed randomness
   - fix test order coupling
   - quarantine only with owner and expiry

## Output Shape

```markdown
## Flaky Test Report

- Command:
- Runs:
- Parser:
- Result:

### Worst Offenders
| test | pass | fail | flakiness % | next action |
|---|---:|---:|---:|---|

### Notes
- ...
```

## Boundaries

- Do not mark tests flaky without repeated evidence.
- Do not hide always-failing tests as flakes.
- Do not run expensive repeated commands without confirming the run count when cost is obviously high.
