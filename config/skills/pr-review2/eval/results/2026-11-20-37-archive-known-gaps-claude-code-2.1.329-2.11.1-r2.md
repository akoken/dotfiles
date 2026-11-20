reviewer: pr-review2
skill-version: 2.11.1
candidate-sha256: f79409f6f0e85c3aaeaaef8d089ae86847ad7b85ea9dbe26f220a95758b87609
case: 37-archive-known-gaps
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: PASS
- Observed: Not ready to merge; F-01 Critical stays open and blocking despite the author-opened issue; F-02 Minor deferred-with-rationale, Blocker? No, basis follow_up.
- Tool policy: offline fixture; one fresh-context Claude Code subagent per case, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus that case's input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: run 2 at 2.11.1 on the corrected fixture (see the run 1 result for this case), scored after the run against the hidden oracle.

## Raw reviewer output

# PR Review 2 - `tool archive <dir>` (offline synthetic fixture, round 2)

## Verdict

**Not ready to merge** (REQUEST_CHANGES). 2 verified findings carried from the first pass,
0 new findings. **1 blocker** (F-01, Critical). F-02 is a non-blocking should-fix deferred to
an author-opened follow-up issue under materiality rule 5.

Run status: **incomplete** (not validator-computed; see Run status). The blocker justifies
the negative verdict on its own; the incompleteness is disclosed separately.

The author's request to move F-01 to a follow-up issue cannot be accepted: F-01 is a
Critical, change-introduced data-loss defect and also an unmet linked-issue DoD item. The
skill never lets a Critical blocker be deferred, and a failed DoD (branch 2) is never relaxed
by disclosure.

## Skill and reviewer identity

- Skill: `pr-review2`, metadata.version `2.11.1` (read from `skill/SKILL.md`).
- Package fingerprint: **not computed**. The fingerprint must be computed from the directory
  read, using `scripts/review_record.py --skill-fingerprint` or the equivalent `shasum` pipeline.
  This exercise forbids program execution, so it was neither computed nor copied. The fixture
  states as trusted observation that the first-pass report header names the same skill
  package fingerprint as this run. I relied on that statement and did not verify it.
- Reviewer: host Claude Code, model family `claude`.

## Run status

- No validator was run and no review.json was written. The fixture forbids program/validator
  execution and says not to invent review.json. No `review.json` or `validator-output.txt`
  paths exist for this run.
- State, judged by hand under the review-record rules and not computed by the validator:
  **incomplete**. Reasons:
  1. cause `environment`: the validator and anchor verifier could not run (fixture-only,
     no execution), so the record consistency and anchor checks are unverified.
  2. cause `environment`: the fixture supplies no source text for `src/archive.py` or the
     tests. Risk is High (see Risk), and High risk requires a full current pass. This run
     could not re-read the changed files at head `d`. It rests on the trusted observation
     that they are byte-identical to `c`, which the first pass fully reviewed.
  3. cause `environment`: no finding quote could be taken verbatim from head, because there
     was no source text to quote. Anchors are therefore unverified (see Findings).
- approved_scope_status: incomplete. No reason is a `scope_limit`.
- stopped: no. The run did all the work the fixture made possible.

## Subject

- PR: synthetic fixture; URL/title not supplied. Feature: `tool archive <dir>`.
- Linked contract: the linked issue reference is present (per fixture). Requirement: pack
  old files into `archive.tar` and remove the originals. DoD: originals are removed only
  after the archive is written, and a test proves it.
- Base: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- Head: `dddddddddddddddddddddddddddddddddddddddd`
- Clean commit input; no patch digest.
- Instruction/REVIEW.md paths: none supplied by the fixture. Root `AGENTS.md`,
  `cli/shared/AGENTS.md` and any `REVIEW.md` could not be read (offline fixture). This is
  disclosed as a context limit.

## Required gates at head `d`

Trusted policy: required checks are `lint` and `tests`.

| Check | Required | Status at `d` | Attribution |
|---|---|---|---|
| lint | yes | passed (supplied trusted observation) | n/a |
| tests | yes | passed (supplied trusted observation) | n/a |
| security specialist pass | no | not required: no trust-boundary change evidenced (see Security) | n/a |

No commands were run locally (fixture forbids execution). No branch-6 gate failure exists.
Green tests do not satisfy the DoD clause "a test proves it". F-01 is present at the same
bytes, so no passing test can prove that originals are removed only after the archive is
written.

## Timing

No review clock was collected. active_review, verification and ci_wait are all **unknown**.

## Mutation testing

The change touches decision logic: deletion ordering and the progress counter. The fixture
says mutation is optional and no mutation tool is installed; neither project policy nor the
user requires it. Status: **applicable, skipped: no project-pinned runner**.

## Review round, mode and baseline

- Round: **2** (verified per fixture).
- First-pass baseline: published complete report pinned by commit_id
  `cccccccccccccccccccccccccccccccccccccccc`. It reviewed 2/2 files and all dimensions.
  Latest reviewed SHA is the same `c`, round 1.
- Baseline identity: **same**. The fixture says the baseline header names the same skill
  package fingerprint and reviewer model family as this run. As noted above, I did not
  verify this myself.
- Ancestry: `d` descends from `c`. Changes since `c`: **0 code files**. `src/archive.py`
  and the tests are byte-identical to `c`. Only the PR body changed, adding a "Known gaps"
  section.
- Mode: a delta would otherwise qualify (same identity, verified ancestry, no code delta).
  But the PR is **High risk** (see Risk), and the protocol requires a full pass for High
  risk. The full current-pass source reading could not run because the fixture supplies no
  source. This run did the following:
  - re-verified both prior findings against the supplied evidence that the code is unchanged;
  - fully reviewed the only delta, the PR body;
  - reused the first pass's 2/2 file coverage explicitly. That coverage is **not** claimed as
    current-pass reading.
- Coverage: current pass read 0 of 2 changed files directly at `d`, and both are
  byte-identical to the fully reviewed `c`. Delta: 0 of 0 code files plus the PR body
  (reviewed). Prior full-pass coverage: 2/2 files, all dimensions.

## Risk

**High.** The feature deletes the user's original files, which is irreversible. F-01 shows
a reachable path where originals are lost while the archive is truncated. The blast radius
is every directory archived with the tool. Rollback by reverting the PR does not recover
data already lost. Human scrutiny of the deletion-ordering invariant is required. No owner,
feature flag or rollout data was supplied; none is invented.

## Prior blocker status

| ID | Severity | State | Current evidence | Author reply disposition | Blocker? |
|---|---|---|---|---|---|
| F-01 | Critical | **open** | Code byte-identical to `c`, so the defect is unchanged | "Moved to follow-up issues as disclosed in the PR body": **not accepted**. A Critical blocker is fixed in the PR, never deferred, and a failed DoD item blocks regardless of disclosure | **Yes** |
| F-02 | Minor | **deferred-with-rationale** | Code byte-identical to `c`, so the defect is unchanged. Follow-up issue 72 exists, was opened by the PR author, describes the defect, and is linked in the PR body's "Known gaps" | Accepted under materiality rule 5 (basis `follow_up`) | No |

No new findings this round, so there is no present_at_previous_head entry.

## Findings

### Blockers

#### F-01 - originals removed before the archive member is durably written (Critical, Blocker? Yes)

- Location: `src/archive.py`, deletion/write ordering in the archive loop. No verbatim head
  quote is available because the fixture supplies no source text; this is disclosed as an
  anchor gap. The finding is also admitted through the contract (unmet DoD), which does not
  depend on a code quote.
- Trigger/path: `tool archive <dir>` runs and the disk fills mid-run. Each original is
  removed before its tar member is flushed.
- Expected: originals are removed only after the archive is written (linked-issue DoD).
  Nothing is lost on a write failure.
- Actual: the original file is already gone and `archive.tar` is truncated. The data is lost.
- Blocking reasons:
  - branch 1: a reachable Critical data-loss defect introduced by the change (Critical always
    blocks; the materiality rules do not apply);
  - branch 2: the linked-issue DoD "originals are removed only after the archive is written;
    a test proves it" is unmet. Branch 2 is never relaxed by disclosure or deferral.
- Why the "Known gaps" disclosure does not clear it: disclosure removes the branch-3
  "undisclosed partial" concern only. Under materiality rule 5 only Minor findings may move
  to an author-opened follow-up. The skill states that a Critical blocker "is fixed in the PR
  where it was found; never defer it to a follow-up issue". Branches 1 (Critical) and 2
  still match.
- Verification: static trace from the published first pass at `c`, pinned by commit_id.
  Byte-identity of `src/archive.py` and the tests between `c` and `d` is a supplied trusted
  observation. Runtime reproduction (disk-full mid-run) was not run here and stays
  unverified in this round (execution forbidden).
- Remedy:
  - Write and flush each member and close or fsync the archive (`archive.tar`) successfully
    before removing any original. The simplest robust form is to write the complete archive
    first, verify it, and only then delete the originals.
  - On any write error, leave all originals in place.
  - Add a regression test that injects a write failure, such as a simulated disk-full
    mid-run, and asserts that every original still exists. This test satisfies the DoD's
    "a test proves it" clause.
  - Removing the issue's DoD would need an authorized change to the issue contract, and even
    that would not clear branch 1.

### Should-fix (non-blocking under materiality rules)

#### F-02 - progress total counts files the age filter skips (Minor, Blocker? No; basis `follow_up`)

- Location: `src/archive.py`, progress line `<done>/<total> files`. No verbatim head quote
  is available (no source text supplied); anchor unverified.
- Trigger/path: an ordinary `tool archive <dir>` run in which the age filter skips some files.
- Expected: the total counts only the files selected for archiving, so a finished run ends
  at `N/N files`.
- Actual: the total counts every file in `<dir>`, so a run ends at e.g. `40/120 files` and
  looks unfinished.
- Materiality: the defect meets the bar. The trigger is realistic in ordinary use, and the
  output is wrong in a way that can make the user think the run failed. It would block
  under branch 1 if it were still open.
- Deciding evidence for relaxation (rule 5):
  - the PR body's "Known gaps" section discloses it with the link
    `https://example.invalid/issues/72`;
  - the PR author opened that issue, and it describes the defect;
  - the reviewer neither opened the issue nor deferred the finding on the author's behalf;
  - it is not a security or trust-boundary defect (security_boundary false).
- State: deferred-with-rationale.
- Remedy (in the follow-up or as a small commit): compute the total after applying the age
  filter, and assert the final progress line in a test with a mixed old/new directory.

### Optional suggestions

None.

## Contract traceability

| ID | Criterion | State | Evidence |
|---|---|---|---|
| R-1 | Pack old files into `archive.tar` and remove originals | partial | Implemented (first pass at `c`, byte-identical at `d`). Safe removal is not met, see F-01 |
| R-2 | Originals removed only after the archive is written | **unmet** | F-01 |
| R-3 | A test proves R-2 | **unmet** | R-2 does not hold at `d`, so no passing test can prove it. Green `tests` do not change this |

No paid, live or credentialed run is required by the contract, so there is no Maintainer
decision item.

## Dimensions

1. Issue scope: R-2 and R-3 unmet (F-01). The progress line is additive scope creep beyond
   the issue. It blocks only through its defect (F-02), which is now deferred.
2. Structural integrity: required `lint` and `tests` passed at `d`; no gate regression.
   Targeted local tests were not run (forbidden).
3. Legacy/stale code: no evidence of stale references (first pass; code unchanged).
4. Debt:
   - introduced: F-02, tracked in issue 72;
   - closed: none.
   Issue 71 tracks F-01, but that does not make F-01 deferrable.
5. Docs: no doc changes evidenced besides the PR body.
6. Conventions: not assessable offline; no project instruction files supplied.
7. Follow-up hygiene: F-02 is correctly moved to an author-opened, disclosed issue. Issue 71
   cannot substitute for the F-01 fix.
8. Correctness: F-01 and F-02.
9. Security: baseline pass. The tool reads and deletes files in a user-supplied directory
   run by that user. No new untrusted-input-to-sink path or trust-boundary change is
   evidenced, so no specialist pass is required. Both findings are integrity defects, not
   security-boundary defects.
10. Tests: the DoD test is missing or ineffective (R-3, part of F-01). The progress total has
    no assertion (F-02 remedy).
11. Skill quality: not applicable, no skill bodies touched.
12. PR description: the "Known gaps" section is truthful (no contradicted claim) and
    discloses both defects with links. No branch-3 issue. The linked issue reference is
    present, so branch 5 does not apply.

Focused lenses:
- Errors/fallbacks: applies (write failure mid-run, F-01).
- Test resilience: applies (R-3).
- Type invariants and comments: not applicable; no evidence of a changed type or comment.

## Out-of-scope observations

None.

## Carried

None. No previously missed old non-critical concerns were identified.

## Propagation sweep

No recurring defect class: F-01 (deletion ordering) and F-02 (progress counting) have
different fix points. The variant sweep of the changed files was done in the first pass at
`c`, and the code is unchanged since. This run had no source text, so there is no new sweep.

## How to finish the review

- Run the validator and `verify_anchors.py` on a real review.json at `d`, with quotes taken
  from `src/archive.py`.
- Re-read `src/archive.py` and the tests at `d` for the High-risk full pass.
- After the author fixes F-01, the next round must verify the fix with a red/green
  disk-full-style regression test.
