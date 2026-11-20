reviewer: pr-review2
skill-version: 2.11.1
candidate-sha256: f79409f6f0e85c3aaeaaef8d089ae86847ad7b85ea9dbe26f220a95758b87609
case: 37-archive-known-gaps
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: FAIL
- Observed: Not ready to merge; F-01 Critical stays blocking as expected, but F-02 is also Blocker? Yes: the reviewer read the wrong progress total as an unmet DoD (2) ('the progress line shows <done>/<total> files'), which rule 5 cannot defer.
- Tool policy: offline fixture; one fresh-context Claude Code subagent per case, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus that case's input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: run 1 at 2.11.1, scored after the run against the hidden oracle. Fixture defect, not a skill defect: DoD (2) made F-02 a branch-2 requirement failure, which the materiality rules correctly never relax. The 2.11.0 reviewer flagged the same ambiguity. The case was corrected (DoD no longer covers the progress line) and rerun.

## Raw reviewer output

# PR Review 2 - offline fixture 37-archive-known-gaps (peer mode, round 2)

**Verdict: Not ready to merge** (REQUEST_CHANGES)

2 verified findings, both open, both `Blocker? Yes` (F-01 Critical, F-02 Minor). 0 new
findings this round; 0 prior findings fixed. The "Known gaps" section and the follow-up issues
#71/#72 do not clear either blocker: a Critical blocker is never deferred, and both findings
also fail a linked-issue DoD item (branch 2), which the materiality rules never relax.

Run status: **incomplete** (computed by hand, not by the validator - see Run status). Coverage
of the source at head rests on the trusted byte-identity statement and the prior full pass;
this pass did not read source text.

---

## Skill and reviewer identity

| Field | Value |
|---|---|
| Skill name | pr-review2 |
| metadata.version | 2.11.1 |
| Package fingerprint | **not computed** - the fingerprint requires running `scripts/review_record.py --skill-fingerprint` or hashing the files; this exercise forbids program execution. Not copied from any earlier report. |
| Reviewer host | Claude Code (agent CLI) |
| Reviewer model family | claude |
| Previous (round 1) identity | Supplied by the fixture as the same skill package fingerprint and the same reviewer model family as this run; the literal values are not in the fixture. |
| baseline_identity | same (per the trusted fixture statement; not mechanically verified) |

## Target

- Mode: AURA peer, offline synthetic fixture (not a live AURA PR review).
- PR URL / title / number / author: not supplied by the fixture.
- Linked contract: issue for `tool archive <dir>` (issue number not supplied; the fixture states
  the linked issue reference is present in the PR body).
- Base: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- Head: `dddddddddddddddddddddddddddddddddddddddd`
- Previously reviewed head (round 1, published review commit_id):
  `cccccccccccccccccccccccccccccccccccccccc`
- Patch digest: not applicable (clean commit input).
- Instruction / REVIEW.md paths: none supplied; root AGENTS.md, cli/shared/AGENTS.md and any
  REVIEW.md were not available to this exercise.

## Required gates at head `ddddddd...`

| Check | Required | Status at head | Attribution | Evidence |
|---|---|---|---|---|
| lint | yes (trusted policy) | passed | not_applicable | Trusted fixture line: "required checks are lint and tests; both passed at current head." |
| tests | yes (trusted policy) | passed | not_applicable | Same trusted line. |
| Security specialist pass | no | not applicable | - | No trust-boundary change evidenced (see Security). |

No command was run locally (execution forbidden). The green gates do not address F-01/F-02:
the tests evidently do not exercise disk-full mid-run or the filtered progress total.

## Mutation

Applicable (the PR changes decision logic: age filter, removal ordering, progress counting).
**Skipped: no project-pinned runner.** The fixture states mutation is optional and no mutation
tool is installed; neither policy nor the user requires it. The mutation reference was not read
and no runner was installed. No survivors/score exist.

## Timing

No review clock was collected. Active review, verification and CI-wait time: unknown (null).

## Review round, mode and coverage

- Round: 2 (verified re-review).
- First-pass baseline: published complete first-pass report pinned by commit_id
  `cccccccccccccccccccccccccccccccccccccccc`; it reviewed 2/2 files and all dimensions. It is
  also the latest reviewed revision.
- Ancestry: head `d` descends from `c` (trusted fixture statement). Base unchanged.
- Delta since `c`: no code change. `src/archive.py` and the tests are byte-identical to `c`.
  The only change is the PR body ("Known gaps" section). Delta files: 0 of 2 changed files.
- Risk: **High**. The PR adds irreversible deletion of user files (originals are removed after
  archiving), and F-01 shows a reachable data-loss path on disk full. Blast radius: any user
  directory the tool is run on; reversibility: deleted originals cannot be recovered by
  reverting the PR. This needs explicit human scrutiny of the deletion ordering.
- Mode consequence: the protocol requires a full pass for High risk. This exercise could not
  perform one: the fixture supplies no source text, so no file was read at head in this pass.
  Coverage this pass: 0 of 2 changed files read; the PR body delta, author replies and the two
  follow-up issue descriptions (as summarized by the fixture) were inspected. Prior full-pass
  coverage at `c`: 2 of 2 files, all dimensions (reused as evidence, not claimed as current
  reading). Because the code is byte-identical, the prior findings' evidence is not invalidated
  by any change, which is enough to keep both blockers open; it is not a current full pass.
- Callers / affected paths: not traced in this pass (no source available).

## Run status

- State: **incomplete** (validator not run; no review.json was created, per the fixture's
  instruction not to invent one. Status below is the reviewer's application of the rule, not
  validator output.)
- approved_scope_status: incomplete.
- Reasons:
  1. Required full pass not performed (High risk) - cause `environment`: the offline fixture
     supplies no source files for `src/archive.py` or the tests.
  2. Anchor verification not performed - cause `environment`: no checkout and no script
     execution; verbatim head-line quotes cannot be produced from the fixture.
- Stopped: no.
- Kept review.json / validator-output.txt: none (fixture-only exercise; not fabricated).

To finish: obtain the head `d` checkout, read `src/archive.py` and its tests in full, record
verbatim anchors, build review.json (profile aura-peer, schema 2, with rereview), compute the
skill fingerprint, then run `review_record.py` and `verify_anchors.py` against head `d`.

## Contract traceability

| ID | Criterion (exact text) | State | Implementation | Verification |
|---|---|---|---|---|
| DoD-1 | "originals are removed only after the archive is written" | **unmet** | `src/archive.py` removes each original before its tar member is flushed (round-1 F-01) | Static, prior full pass at `c`; code byte-identical at `d`. No current re-read. |
| DoD-2 | "the progress line shows \"<done>/<total> files\"" | **unmet** | Progress total counts every file in `<dir>`, including files the age filter skips (round-1 F-02) | Static, prior full pass at `c`; code byte-identical at `d`. |

Reading of DoD-2: `<total>` is the number of files the run archives. An ordinary run that
archives 40 of 120 files ends at "40/120 files", so the line does not show done/total of the
archive job; the format is present but the stated quantity is wrong. The PR body disclosure
does not amend the linked issue: no authorized scope change has removed DoD-1 or DoD-2 from
the issue, so both stay in the contract.

## Findings - blockers

### F-01 - Originals removed before archive member is written (Critical, `Blocker? Yes`)

- Location: `src/archive.py` (removal of each original relative to tar member flush). Exact
  line and verbatim quote not available in this fixture.
- Status: **open**. Author reply "Moved to follow-up issues as disclosed in the PR body" is not
  accepted as resolution.
- Trigger/path: `tool archive <dir>` on a volume that fills up mid-run.
- Expected: an original is removed only after its data is durably in archive.tar (DoD-1).
- Actual: the original is removed before its tar member is flushed; on disk full the original
  is gone and archive.tar is truncated - permanent user data loss.
- Blocking reasons: branch 1 (reachable data-loss defect introduced by the change) and branch 2
  (DoD-1 unmet). One root cause, recorded as one finding with both reasons.
- Why the known-gaps disclosure does not help: a Critical change-introduced defect always
  blocks and must be fixed in the PR where it was found; materiality rule 5 deferral is only
  for Minor findings, and deferral never clears a computed blocker. Independently, branch 2
  is never relaxed by the materiality rules. Branch 3 does not add a reason: the partial
  implementation is disclosed, not concealed.
- Present at previous head: prior finding (field not applicable).
- Security boundary: no (no untrusted-source path evidenced); irrelevant to the outcome since
  Critical semantics already block.
- Verification: prior full static trace at `c` (published round-1 report); current evidence
  is the trusted statement that `src/archive.py` and the tests are byte-identical at `d`. No
  runtime reproduction in this exercise.
- Remedy: in this PR, write and flush (and close/fsync) archive.tar, or at least each member,
  before removing any original; remove originals only after the archive write succeeded, and
  leave all originals in place on any write error. Add a regression test that simulates a
  write failure (for example ENOSPC from the tar writer) mid-run and asserts every original
  still exists. Issue #71 may stay as a tracking link but cannot substitute for the fix.

### F-02 - Progress total counts files the age filter skips (Minor, `Blocker? Yes`)

- Location: `src/archive.py` (progress total computation). Exact line and verbatim quote not
  available in this fixture.
- Status: **open**. Author reply "Moved to follow-up issues as disclosed in the PR body" is not
  accepted as resolution while DoD-2 remains in the linked issue.
- Trigger/path: any ordinary `tool archive <dir>` run where some files are newer than the age
  threshold.
- Expected: progress shows "<done>/<total> files" with total = files to be archived (DoD-2).
- Actual: total counts every file in `<dir>`, so a complete run ends at e.g. "40/120 files"
  and looks unfinished.
- Blocking reason: branch 2 (DoD-2 unmet). The materiality rules, including rule 5 deferral,
  apply only to branch-1 defects and never relax branch 2, so the author-opened, disclosed
  follow-up issue #72 does not make this non-blocking.
- Counterfactual, stated for transparency: if a maintainer recorded in the linked issue that
  DoD-2 moves to issue #72 (an authorized scope change), F-02 would be judged only under
  branch 1. It would meet the materiality bar (ordinary use; a message that leads the user to
  think the run is incomplete) and, being Minor, disclosed in the PR body with an author-opened
  issue link, could then be `deferred-with-rationale` with basis `follow_up`. That has not
  happened; the reviewer does not defer on the author's behalf.
- Present at previous head: prior finding (field not applicable).
- Verification: prior full static trace at `c`; code byte-identical at `d`.
- Remedy: compute the total from the files that pass the age filter (the same list the loop
  archives), and add a test where some files are skipped asserting the final line reads
  "N/N files". Alternative remedy: have the maintainer amend the linked issue's DoD to move
  this item to #72, after which deferral under rule 5 can be recorded.

## Findings - should-fix (non-blocking)

None.

## Prior blocker status (re-review)

| ID | Severity | State | Current evidence | Author reply disposition | Reopen cause |
|---|---|---|---|---|---|
| F-01 | Critical | open | Code byte-identical to `c`; no fix commit | "Moved to follow-up issues" - rejected: Critical must be fixed in this PR | n/a (never closed) |
| F-02 | Minor | open | Code byte-identical to `c`; DoD-2 still in linked issue | "Moved to follow-up issues" - not accepted: branch 2 is not relaxable by deferral | n/a (never closed) |

No repeated finding is raised without new evidence; both are the same IDs carried forward with
their state updated.

## Twelve dimensions

| # | Dimension | This round |
|---|---|---|
| 1 | Issue scope | DoD-1 and DoD-2 unmet (F-01, F-02). Partial scope is disclosed in the PR body. |
| 2 | Structural integrity | lint and tests passed at head (trusted). No local run. |
| 3 | Stale code | Prior full pass at `c`; no code delta. Not re-read. |
| 4 | Debt | Debt introduced: the two known defects are now tracked as #71/#72, but tracking does not close them. Debt closed: none. |
| 5 | Docs | No doc change in the delta. Prior pass at `c`. |
| 6 | Conventions | No code delta; prior pass at `c`. |
| 7 | Follow-up hygiene | Applied: F-01 is a Critical blocker and cannot move to a follow-up; F-02 is a branch-2 blocker and cannot move while DoD-2 stays in the issue. Issues #71/#72 exist and describe the defects. |
| 8 | Correctness | F-01, F-02 (prior pass, unchanged code). |
| 9 | Security | Baseline: no new untrusted-input path or trust boundary evidenced (`<dir>` is an operator-supplied local path). Not re-traced in this pass; no specialist needed. |
| 10 | Tests | Tests pass but miss disk-full and filtered-total cases (covered by the F-01/F-02 remedies, not a separate finding). Mutation skipped, no pinned runner. |
| 11 | Skill quality | Not applicable: no skill bodies touched. |
| 12 | PR description | "Known gaps" section is truthful and discloses the partial implementation (branch 3 does not apply). Linked issue reference present (branch 5 does not apply). Disclosure does not convert blockers into non-blockers. |

## Out-of-scope observations

None.

## Carried

None.

## Propagation sweep

No recurring defect class (F-01 and F-02 have different invariants and fix points). No sweep
triggered.

## Human scrutiny and rollback

- Human scrutiny: the deletion-ordering logic in `src/archive.py` (irreversible user-file
  removal) needs explicit human review once fixed.
- Rollback: reverting the PR restores prior tool behavior but cannot restore originals already
  deleted by a run that hit F-01; until fixed, the defect causes irreversible state change.
- Owner / approvals / feature flags: not supplied; none invented.

## Limits

- Fixture-only exercise: no git, gh, network, script or test execution; no source files
  available. All code-level evidence comes from the trusted fixture summary of the published
  round-1 report and the byte-identity statement.
- No review.json, validator output, anchor verification or skill fingerprint was produced;
  none was fabricated.
