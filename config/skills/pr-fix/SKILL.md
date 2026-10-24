---
name: pr-fix
description: Triage and fix review findings on a PR, verify CI green, request re-review. Use when the user asks to address PR review comments, resolve review findings, or drive a PR to green after review.
---

Given a PR number (`$ARGUMENTS`; if empty, resolve from the current branch with `gh pr list --head <branch> --json number --limit 1`):

1. `gh pr view <number> --comments` - enumerate every review finding. Also list inline review threads with `gh api repos/{owner}/{repo}/pulls/<number>/comments` so nothing is missed.
2. Triage every finding before changing code. Group findings that share one root cause or defect class, search the diff for further copies, and fix every instance of the class together. For an optional/style finding, or one you can show is wrong or out of scope, change no code: reply on its thread (`gh api repos/{owner}/{repo}/pulls/<number>/comments/<comment_id>/replies -f body=...`) with the evidence and leave the decision to the reviewer.
3. For each defect being fixed, write a FAILING regression test first, run it to confirm it fails, then fix it and confirm it passes.
4. Register any new test files in ALL `.github/workflows/*.yml` files in the same commit. Unregistered test files cause coverage-check CI failures.
5. Update docs and CHANGELOG.
6. Run lint and the full test suite locally. Commit (Conventional Commits, no trailers), push. Invoking this skill is the explicit push approval.
7. Poll `gh pr checks <number> --watch` until all 9 checks are green. If a check fails, re-run it once with `gh run rerun <run_id> --failed` to rule out flakiness before debugging.
8. Reply on the PR with `gh pr comment <number>` giving every finding one disposition: fixed (finding -> test -> change), answered with evidence, or deferred with reason. Then `gh pr edit <number> --body` to update the description, and request re-review with `gh pr edit <number> --add-reviewer <reviewer>` for each original reviewer.

## Boundaries

- Do not report completion until checks are 9/9 green. Show the final `gh pr checks` output.
- Do not commit unrelated local changes.
- Do not skip, delete, or weaken tests to make CI pass.
- Do not force-push.
