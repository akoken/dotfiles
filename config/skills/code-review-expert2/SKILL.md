---
name: code-review-expert2
description: "Review a diff, branch, commit range, or PR using verified findings, explicit coverage, risk-based re-review, and an incomplete-review verdict. Use for general code reviews; use pr-review2 for AURA merge-readiness or pre-PR self-review."
metadata:
  version: "2.3.0"
  derived-from: code-review-expert
---

# Code Review Expert 2

Review code on its stated contract. Separate candidate concerns from verified findings;
compute blockers from evidence and report what was actually inspected. Review-only by
default. Existing authorization to implement fixes remains valid, but a review request
alone does not authorize implementation, publication, commits, or pushes.

## Scope and immutable input

1. Identify the repository, worktree status, requested diff, and actual base/head revisions.
   Prefer local evidence. Fetch remote refs only when needed and allowed; fetching changes
   refs, so do not describe it as a completely read-only operation.
2. For a feature branch, resolve its actual target base, then inspect the merge-base diff.
   For a PR, obtain metadata, base/head SHAs, body, linked requirements, and required CI
   results for that head. Do not silently default an unresolved base to main.
3. On the base branch, inspect staged and unstaged changes with `git diff HEAD`; list
   relevant untracked files separately because that command omits them. Record the HEAD
   and a digest of the reviewed patch, including reviewed untracked content.
4. For an explicit range, use the supplied revisions. An empty or unavailable diff has no
   reviewable target; state this and request the missing target without granting approval.

Never switch, reset, delete, or stash the user's branch. If execution requires another
revision, use a new isolated detached worktree and safe cleanup as described in
[review protocol](references/review-protocol.md). A dirty tree is reviewable when it is
the requested input; do not execute unrelated local changes as if they were PR evidence.

Load applicable project instructions and directory-level REVIEW.md files using the
protocol. State the review contract: linked issue, PR body, explicit user requirement,
or unavailable. Missing requirements do not license inventing them.

## Decision pipeline

Read [review protocol](references/review-protocol.md) before reviewing. It defines candidate
verification, evidence limits, risk, finding lifecycle, convergence, and completeness.

Admit a finding only through at least one anchor:

1. A changed or added line.
2. An unmet stated requirement, including an omission.
3. A claim about the change contradicted by the actual diff.

Useful concerns with no anchor go to Out-of-scope observations, capped at five with an
overflow count. An unchanged line can still be evidence for a regression caused by a
changed caller; show that causal link rather than dismissing it solely by line location.

For each verified, admitted item compute `Blocker?` independently of severity. Yes requires:

1. A reachable correctness, security, or regression defect introduced by the change.
2. A failed stated requirement.
3. An undisclosed partial implementation or contradicted claim.
4. A required gate failure introduced by the change. Compare the same failing check at
   the merge-base when feasible; if attribution cannot be established, report that limit
   and mark the gate unresolved rather than declaring a regression or a clean pass.

Only these branches create blockers. A reachable defect may block even when its impact
is Minor. A label alone cannot create a blocker. Missing new tests alone do not prove
a runtime defect; evaluate behavioral risk, existing coverage, and explicit requirements.

Complete the planned pass after finding a blocker. When one defect class appears, inspect
variants in changed files. Untouched sibling defects with no change-induced causal link
remain separate observations, with no in-diff fix demand.

## Check dimensions

Evaluate each dimension on the applicable review surface; state why a dimension is
not applicable. Re-review may narrow that surface under the protocol, not silently.

- **Correctness:** trace the most plausible breaking inputs through non-trivial changed
  functions and current callers. Check boundary/error paths, state, async behavior,
  resource lifetime, and compatibility. For a bug fix, distinguish the user-visible
  symptom from its cause and look for regression evidence exercising that cause.
- **Security:** read [security checklist](references/security-checklist.md) for touched
  trust boundaries, identity/authorization, input-to-sink paths, secrets, or dependencies.
  Demonstrate reachability and impact; no untrusted sink touched is a valid explicit result.
- **Quality/performance:** read [quality checklist](references/code-quality-checklist.md)
  for relevant error, allocation, query, or hot-path changes. Avoid unsupported performance
  claims and speculative caching demands.
- **Design:** read [design checklist](references/solid-checklist.md) for structural changes.
  Tie proposals to demonstrated defects or requirements; optional refactoring is separate.
- **Tests:** assess whether assertions would catch the changed behavior breaking; inspect
  existing and new coverage, error/boundary cases, weakened tests, and introduced flakiness.
  Use focused tests or E2E evidence appropriate to the change, not a full suite by default.
  For changed decision logic or tests exercising it, apply the bounded
  [mutation-testing stage](references/mutation-testing.md) after normal tests pass. State
  applicability even when skipped; survivors and score alone never create a blocker.
- **Removal:** read [removal plan](references/removal-plan.md) when the diff leaves obsolete
  code or performs migration. Verify callers before proposing deletion; never delete during
  a review-only run.

Pure formatting, naming preferences, and cleanup suggestions are omitted by default.
When the user requests them, keep them optional and separate from actionable defects.
Documentation, config, and skill prose can cause real product failures; do not filter
them as style merely because they are not executable source.


Use the applicable lenses in [focused reviews](references/focused-reviews.md) for changed
error/fallback paths, type invariants, affected comments and test resilience. Integrate them
into the normal pass; do not launch an agent or a full-file reread for every lens.

Always perform the baseline security pass in [security routing](references/security-routing.md).
For a changed trust boundary, use its focused specialist handoff and explicit completion
state. An independent required security check remains unresolved until current evidence is
available; a normal code review or green mutation score cannot stand in for it.

## Severity, completeness, and verdict

| Severity | Meaning |
|---|---|
| Critical | Reachable serious correctness/security/data-loss defect, risky breaking contract, or serious required-gate regression |
| Minor | Lower-impact reachable defect, demonstrated test weakness, stale reference, or incomplete migration |
| Style | Optional preference or cosmetic cleanup; only when requested |

For every report show `reviewed N of M changed files`, prioritized/deprioritized groups,
and any partial file inspection. For delta re-review also show `reviewed N of M delta
files` and baseline coverage separately; prior coverage is not current-pass work.

| Evidence state | Verdict |
|---|---|
| At least one verified computed blocker | REQUEST_CHANGES; also disclose any incomplete coverage |
| No blocker, but review incomplete or required gate unresolved | INCOMPLETE / NEEDS_REVIEW |
| No blocker, planned coverage complete, required gates satisfied | APPROVE |

If no runnable gate applies, explain that with evidence rather than treating it as missing.
Approval is a review conclusion for one revision, not merge authorization or a substitute
for required human approval. Recheck the head/patch digest before reporting; a changed
input invalidates affected conclusions and may require INCOMPLETE.

## Evidence record and requirements

Use [review record](references/review-record.md) for a real review: map each explicit
acceptance criterion to implementation and verification evidence, record unresolved items,
and validate the revision-bound review.json before a positive verdict. The validator checks
consistency, not source-code truth. Fixture-only or target-resolution exercises must report
missing metadata honestly; never invent a record just to satisfy the schema.

## Report

Lead with the verdict and finding count. Include:

- Contract; base/head SHAs or working-patch digest; reviewed source and REVIEW.md scope.
- Coverage, risk tier with reasons, review round/mode, and baseline evidence or unavailable.
- Commands/checks actually run, outcomes, skipped work and unresolved verification.
  Include measured review/test/CI-wait timing under the review record; unknown stays unknown.
- Mutation applicability/status, exact production/test scope, tool/config/revision identity,
  mutant outcomes and incomplete scope, with classified survivor evidence when applicable.
- Findings table: stable ID, location, severity, Blocker?, trigger/call path, expected vs
  actual result, causal diff, verification method, and concrete remedy. Keep rows readable;
  longer evidence can follow below the table. Never claim execution from static reasoning.
- Prior finding states and new-commit attribution on re-review; independently capped
  Out-of-scope and Carried sections when applicable. Empty sections may simply say None.
- Risky behavior, required human review, rollback method, and remaining uncertainty.

A clean review names the implementation and behavior inspected and its relevant test or
other evidence. Do not manufacture an issue or a placeholder finding to fill a table.
On incomplete work state what remains and how to finish; do not bury that in a footnote.

Do not ask for implementation approval again if the user already authorized the fixes.
Do not publish to an external service unless the session explicitly authorizes it.

## Maintaining this skill

After prompt, model, tool, or protocol changes, use [evaluation guide](eval/RUBRIC.md).
The seed cases are synthetic checks, not production reliability evidence. Convert real
misses and harmful false positives into expert-confirmed, held-out regression cases;
never invent a real incident or transfer a v1 evaluation result to v2.
