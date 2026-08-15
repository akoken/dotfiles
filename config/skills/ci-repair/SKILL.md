---
name: ci-repair
description: Use when the user asks to fix a failing GitHub Actions CI run, repair a PR branch, inspect failed CI logs, or rerun a focused failure-fix loop from CI evidence.
---

## Boundaries

- GitHub Actions only.
- One repair cycle per invocation.
- Do not push unless local verification passes or the user explicitly approves an unverified push.
- Do not commit unrelated local changes.
- Do not empty-commit.
- Keep the fix scoped to the failing check.

## Workflow

1. Resolve the PR or branch:
   - If the user gives a PR number: `gh pr view <number> --json number,url,headRefName,headRefOid`
   - If the user gives nothing: use current branch, then `gh pr list --head <branch> --json number,url,headRefName,headRefOid --limit 1`
2. Check the latest run for the PR head commit:
   - `gh run list --commit <head_sha> --limit 5 --json status,conclusion,databaseId,name,createdAt`
3. Stop if CI is passing, queued, in progress, or missing.
4. Fetch bounded failure context:
   - `gh run view <run_id> --json jobs`
   - `gh run view <run_id> --log-failed`
   - Include at most 3 failed jobs, 100 lines per failed step, and 400 lines total.
5. Preflight git:
   - confirm a git repo
   - confirm not detached
   - confirm no unrelated dirty worktree changes
   - if dirty, stop and explain what must be committed/stashed first
6. Checkout/update the PR branch only after preflight.
7. Record the repair baseline with `git rev-parse HEAD`.
8. Diagnose from the CI evidence:
   - reproduce locally when feasible
   - identify root cause
   - make the smallest focused fix
9. Verify locally using the repo's relevant command. Prefer existing project commands, nearby tests, or the command that failed in CI.
10. If verification fails, stop and report the remaining failure.
11. If verification passes and the user asked to push, stage only files changed since the repair baseline, commit, and push.

## Failure Summary Shape

```markdown
## CI Failure Summary

**PR:** #<number> (<branch>)
**Run:** <run-url or id>
**Commit:** <head_sha>
**Status:** failure

### Failed Job: <job-name>
**Failed Step:** <step-name> (exit code <N>)

```text
<bounded log excerpt>
```
```

## Final Report Shape

```markdown
## CI Repair Result

- PR:
- Branch:
- Root cause:
- Files changed:
- Local verification:
- Pushed: yes/no
- Remaining risk:
```

## Escalation Notes

`gh` commands may require network and authentication. If sandboxed network fails, rerun the same command with escalation and a clear approval question.
