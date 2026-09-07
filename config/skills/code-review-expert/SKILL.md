---
name: code-review-expert
description: "Evidence-first review of a diff, branch, or PR with a senior engineer lens. Checks correctness, security, code quality, SOLID/design, test quality, and removal candidates; produces an evidence-cited verdict (APPROVE / REQUEST_CHANGES). Use when reviewing a diff, a branch, or a pull request."
---

# Code Review Expert

## Overview

Review the diff on its own terms, admit only evidence-anchored findings, and end with a verdict computed from blocker status — not from severity or vibes. Default to review-only output unless the user asks to implement changes.

## Scope and Diff Source

Determine the diff source and state it in the report:

1. **Branch vs base (default).** Run `git fetch origin`, detect the base via `git symbolic-ref refs/remotes/origin/HEAD` (fall back to `main` if unset), then `git diff origin/<base>...HEAD`.
2. **On the base branch, or no distinct branch to diff.** Review staged plus unstaged changes: `git diff HEAD` (add `git diff --stat` for an overview).
3. **User names a target.** A commit range (`git diff A..B`), or a PR number via `gh pr diff <number>` when `gh` is available and authenticated. When reviewing a PR number, also fetch `gh pr view <number> --json title,body,baseRefName,url` and `gh pr checks <number>` — the PR body feeds the Review Contract below, and CI status feeds Blocker Computation branch 4.

Never checkout, branch, stash, or delete anything — this skill is read-only against the working tree and refs.

**Edge cases:**
- **Empty diff**: tell the user and ask whether to review staged changes, a commit range, or a PR instead.
- **Large diff (>500 changed lines)**: triage per the Coverage Accounting section below instead of skimming everything equally.

## Review Contract

The review contract is whatever defines scope:

- A linked issue, PR body, or a requirement the user stated in this conversation.
- If none exists, say so explicitly in the report and review the diff on its own terms — do not invent a contract.

**Admissibility.** A finding earns a place in the findings table only through at least one of these anchors:

1. A line the diff adds or changes.
2. An unmet stated requirement (an issue acceptance criterion, DoD item, or explicit user ask), including a silent omission.
3. A claim in the PR body, commit message, or user's stated intent that the diff contradicts.

A real, useful concern with none of these anchors is not a review finding. Route it to **Out-of-scope observations** instead of manufacturing an in-diff fix demand. Cap that section at five items; summarize any overflow count.

## Blocker Computation

Compute `Blocker?` independently for every admitted finding, through exactly these branches:

1. A reachable correctness, security, or regression defect introduced by the diff.
2. A failed stated requirement (acceptance criterion, DoD item, explicit user ask).
3. An undisclosed partial implementation, or a claim the diff contradicts.
4. A failing required gate — CI, tests, typecheck, or lint — that is not pre-existing on the base branch. Before blaming the diff, check whether the failure already exists at the merge-base:
   ```bash
   BASE=$(git merge-base origin/<base> HEAD)
   git worktree add /tmp/review-base-check "$BASE"
   (cd /tmp/review-base-check && <test/typecheck/lint command>)
   git worktree remove --force /tmp/review-base-check
   ```
   A failure that reproduces at the merge-base is pre-existing — note it, but it is never this diff's blocker.

`Blocker?` is **Yes** only when at least one branch matches; otherwise **No**. Severity (below) is classified independently and never sets blocker status — a real Critical-severity finding can still be non-blocking, and a real Minor one can still block.

**No early stop.** A computed blocker does not end the review. Keep working the full planned pass across every check dimension before reporting.

**Defect-class propagation.** When one defect class appears in a changed file, check sibling implementations *within files the diff touches* for the same class of bug before finalizing findings. A defect found only by scanning an untouched file routes to Out-of-scope observations with `Blocker? No` — propagation into untouched files never creates a blocker.

## Check Dimensions

Run every dimension below on every review; state explicitly when a dimension doesn't apply (e.g. "no SQL/shell sinks touched").

### (a) Correctness

Read the changed code line by line. For each non-trivial changed function, ask: **what input makes this wrong?** Trace the 1-2 inputs most likely to break it. Check logic errors (wrong operator, inverted condition, off-by-one), null/undefined/empty handling, error handling (swallowed exceptions, unawaited rejections, error paths returning success), async correctness (missing `await`, races between read and write), boundary values, resource leaks, and unexpected state mutation. If you cannot point to the line that fails, it is not a finding.

**Severity calibration:** a defect on an input the stated requirement does not require handling *and* that no current caller can produce (e.g. an invalid-input guard for a brand-new utility with no callers yet) is Style, not Minor — reserve Minor and Critical for paths that are actually reachable today.

### (b) Security

Load `references/security-checklist.md`. Covers injection, SSRF, path traversal, prototype pollution, AuthN/AuthZ and IDOR, JWT/token security, secrets and PII, supply chain, CORS/headers, race conditions (TOCTOU, database concurrency, distributed systems), cryptography, and data integrity. Report exploitability and impact together.

### (c) Code Quality

Load `references/code-quality-checklist.md`. Covers error-handling anti-patterns, performance (N+1 queries, missing caching, CPU-hot paths, memory), and boundary conditions (null handling, empty collections, numeric/string edges).

### (d) SOLID and Design

Load `references/solid-checklist.md`. Covers SRP/OCP/LSP/ISP/DIP smells and common code smells beyond SOLID. Any refactor proposal must be an incremental, minimal-diff plan — never a large rewrite pitch.

### (e) Test Quality

Running the suite only tells you it passes; this asks whether the tests are worth running:

- New behavior has tests at all — zero tests on new logic is a defect, not a gap to note in passing.
- Tests cover non-happy-path branches: error case, empty case, boundary — not just the golden path.
- Assertions are meaningful — flag tautological assertions (`expect(true).toBe(true)`), tests that assert the mock instead of the behavior, and over-mocking that mocks away the exact thing under test.
- No test was deleted or weakened to make a failing suite pass instead of fixing the underlying code.
- No new flakiness: real timers/sleeps, order-dependence, or network reliance introduced by a new test.

### (f) Removal Candidates

Load `references/removal-plan.md`. Identify code the diff leaves unused, redundant, or feature-flagged off. Distinguish **safe delete now** from **defer with a plan**, and give the deferred ones a concrete follow-up plan with checkpoints.

### Common Findings Quick Reference

Default severity by category — always run through Blocker Computation independently; no row here creates a blocker on its own:

| Pattern | Default severity |
|---|---|
| Logic bug reachable on the happy path (unhandled null/empty/error case) | Critical |
| New behavior shipped with zero tests | Critical |
| Test deleted or weakened to silence a failure | Critical |
| Untrusted input reaching a shell, SQL, or path sink | Critical |
| Missing `await` / unhandled promise rejection | Critical |
| Tautological or over-mocked test | Minor |
| Happy-path-only test coverage on risky logic | Minor |
| Resource leak on an error path | Minor |
| Stale reference or incomplete migration | Minor |
| Deferred work with no follow-up filed | Minor |
| Naming or formatting inconsistency | Style |

## Coverage Accounting

Every report declares, unconditionally — including clean reviews and small diffs:

```
reviewed N of M changed files · prioritized: [...] · deprioritized: [... / none]
```

For a diff small enough to read in full, use `prioritized: all changed files; deprioritized: none`. For a large diff, prioritize logic-bearing source over docs, lockfiles, and generated output; run the full check-dimension pass on the highest-risk files first, then report the exact partial coverage honestly — never claim full coverage you didn't do, and never silently skip the declaration.

## Verdict

### Severity Scale

| Level | Meaning |
|---|---|
| **Critical** | Correctness/security defect on a reachable path, missing test for risky new behavior, test deleted to silence a failure, undocumented breaking change, non-pre-existing gate failure |
| **Minor** | Defect on a rare/unreachable path, weak or happy-path-only test coverage, resource leak, stale reference, incomplete migration, deferred debt with no follow-up filed |
| **Style** | Convention preference, optional improvement, cosmetic inconsistency |

Severity never determines `Blocker?` — that comes only from Blocker Computation above.

### Verdict Rules

| Condition | Verdict |
|---|---|
| One or more findings with `Blocker? Yes` | **REQUEST_CHANGES.** List each blocker. |
| No findings with `Blocker? Yes` | **APPROVE.** Non-blocking Critical/Minor findings and observations do not change this. |

### Output Template

Always render the findings table, even for a clean review. On a clean review, replace the placeholder row with one non-finding **inspection row**: `—` for number and severity, `No` for `Blocker?`, name the changed implementation and its corresponding test (or the highest-risk changed artifact if no test applies), and state what behavior was inspected. Never replace the table with bare "no findings" prose.

```markdown
## Code Review — [scope: branch/PR/diff description]

**Verdict:** APPROVE / REQUEST_CHANGES
**Scope contract:** [linked issue / PR body / user-stated intent / "none — reviewed diff on its own terms"]
**Diff source:** [git diff origin/<base>...HEAD / staged+unstaged / commit range / gh pr diff <N>]
**Coverage:** reviewed N of M changed files · prioritized: [...] · deprioritized: [... / none]

### Findings

| # | Location | Severity | Blocker? | Finding | Suggested fix |
|---|---|---|---|---|---|
| 1 | `path/to/file.ts:42` | Critical | Yes | Description | Concrete fix |
| 2 | `path/to/file.ts:88` | Style | No | Description | Optional |
[Clean review: render the inspection row here instead.]

### Out-of-scope observations (max 5)

| # | Context | Blocker? | Observation | Follow-up guidance |
|---|---|---|---|---|
| ... | ... | No | ... | Track separately; no change required in this review. |
[If none: "None."]

### Blockers

[If any: numbered list of every Blocker? Yes finding, each with its fix.]
[If none: "No computed blockers."]
```

### Next Steps

After presenting findings, ask how to proceed:

```markdown
---

## Next Steps

Found X issues (Critical: _, Minor: _, Style: _).

**How would you like to proceed?**

1. **Fix all** — implement every suggested fix
2. **Fix Critical only** — address blocking issues first
3. **Fix specific items** — tell me which to fix
4. **No changes** — review complete, no implementation needed
```

**Do not implement any changes until the user explicitly confirms.** This is a review-first workflow.

## Operating Principles

- **Evidence first.** Every finding cites a concrete `path:line` or diff excerpt. No line, no finding.
- **Never rubber-stamp.** Run every check; "CI is probably fine" is not evidence — read `gh pr checks` or the actual test output.
- **Blockers are not a stopping condition.** Finish the full pass before reporting, even after finding a blocker.
- **Distinguish pre-existing failures from regressions.** A gate failing on the base branch before the diff is not this diff's blocker.
- **Read code as code, not only as policy.** A diff can match every stated requirement and still ship a null-deref or a command injection — trace the riskiest changed paths by hand.

## Resources

### references/

| File | Purpose |
|------|---------|
| `security-checklist.md` | Web/app security, race conditions, JWT, and runtime risk checklist |
| `code-quality-checklist.md` | Error handling, performance, boundary conditions |
| `solid-checklist.md` | SOLID smell prompts and refactor heuristics |
| `removal-plan.md` | Template for deletion candidates and follow-up plan |
