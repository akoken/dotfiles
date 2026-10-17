# Pre-PR Self Review

Use the shared SKILL.md decision pipeline, dimensions, verification protocol, and self
verdict mapping. This reference changes inputs and output only; it does not add blockers.

## Input guards

Confirm a feature branch and actual base branch. On main/base or detached HEAD, explain
that self mode needs a feature branch and request a target without changing the checkout.
For uncommitted/untracked files, list them and ask whether they belong unless the user has
already identified the scope. Never stash or discard. While scope is unresolved, inspect
the committed change but keep the self verdict incomplete. If included, preserve the
working tree and record both committed changes and a digest of the full dirty input.

Resolve the issue from an explicit user reference or actual branch convention; verify the
issue content. If no reference can be established, ask for the requirement instead of
guessing from arbitrary digits. No PR exists yet, so the peer missing-PR-reference branch
does not apply; lack of a self contract remains an explicit completeness gap.

## Local evidence

Use current project-documented commands for targeted typecheck, lint, behavior tests, and
compliance checks. For AURA, inspect cli/package.json and instructions before choosing
the corresponding npm/npx commands; avoid downloading a missing tool as a side effect.
Run affected tests, not the full suite by default. Record each actual command and result.
The required local gates replace CI for self mode; pending remote CI is not a failed gate
for a PR that does not exist yet.

Apply [mutation testing](mutation-testing.md) to qualifying logic/test changes only after
the selected normal tests pass. Reuse the same scope, resource budget, survivor triage,
and required-vs-optional gate rules as peer review. Include actual mutation evidence or
the explicit skip/setup reason in the draft PR body's Testing and Known gaps sections.

Evaluate additional hygiene within the reviewed branch only: debug artifacts, untracked
TODO/debt, unintended file churn, and unreachable/dead new code. Verify intent and usage
before classifying a candidate. A tracked TODO is not a blanket exemption from a failed
requirement, and a console.error on a real error path is not automatically a debug leftover.
Route unanchored observations separately and apply the ordinary severity/blocker rules.

Self re-review can use a saved local report with full SHA/patch digest, scope and round as
baseline under the protocol. Without such an artifact, history is unavailable. Do not
invent a published baseline or import peer Carried status from chat memory.

## Draft PR body

Always draft from the branch as it exists, including on a no-go or incomplete result.
Validate truthfulness using the PR-description dimension; generate rather than evaluate
an existing body. Include:

- Summary: concrete problem, resulting behavior, and why the change is needed.
- Verified linked issue reference. If missing, explicitly mark contract unavailable.
- Scope: account for every changed file, grouping by responsibility when useful. Disclose
  unintended files and planned removal instead of concealing the current diff.
- Testing: exact commands actually observed and results, plus skipped checks and gaps.
- Risk: affected boundaries, human review needs, and uncertainty.
- How to revert: concrete rollback method, state consequences, or justified not applicable.
- Known gaps: all current blockers, self-disqualifying findings, and completeness limits.

If no-go/incomplete, add a note that the body must be regenerated after fixes. Never
forecast the intended fixed branch, invent tests, or claim that missing checks passed.
The report uses Ready to open a PR / Not ready to open a PR / Review incomplete
as defined in SKILL.md.
Do not open a PR unless the user explicitly authorizes creation in this session.
