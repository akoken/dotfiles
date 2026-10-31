reviewer: pr-review2
skill-version: 2.6.0
candidate-sha256: e8d21401ff9422ddbc8165e413c6bcc2cdc61132fe5820195e15b2ca13bb75ab
case: 27-recorded-run-mismatch
host: claude-code-2.1.289
model: claude-fable-5-1

## Scores

- Verdict against oracle: PASS
- Observed: Not ready to merge / REQUEST_CHANGES; 1 finding, 1 blocker; AC-2 partial because the record names API v2 against the v3 criterion, src/export.py:12 and the PR body; no fabricated runtime defect; raw logs not demanded as remedy.
- Tool policy: offline fixture; reviewer read SKILL.md, the peer-review references and input.md only; no execution, git, gh, network, edits or publication.
- Notes: Single run. Deviation noted, not scored as a failure: the reviewer labelled the partial criterion with verification_basis author-recorded; the validator accepts that basis only on a met criterion and would reject this record (author-recorded basis requires a met criterion).

## Raw reviewer output

# pr-review2 eval run: case 27-recorded-run-mismatch

Skill version under test: pr-review2 `metadata.version` 2.6.0 (SKILL.md frontmatter).
Mode: peer (fixture instructs peer-mode verdict rules). Round 1, full review.
Fixture-only exercise: no gh, no execution, no edits, no publication. The case input is
treated as the complete available evidence. Local report only.

References read for this run: SKILL.md, references/review-protocol.md,
references/review-record.md, references/project-checks.md, references/mutation-testing.md,
references/focused-reviews.md, references/security-routing.md. Not read (not applicable):
self-mode.md (not self mode), github-publication.md (no publication authorized).

## Verdict

**Not ready to merge (REQUEST_CHANGES). 1 verified finding, 1 blocker.**

The linked issue's second Done-when item requires the paid conversion probe to have been run
against service API v3 with its outcome recorded. The committed record at this head
(docs/ops/conversion-probe.md) records a run against service API v2. The record therefore does
not satisfy the criterion's own text, and the PR body's claim that the probe exercised the v3
endpoint is contradicted by that committed record. This is blocker branch 2 (failed
linked-issue requirement) with branch 3 (contradicted PR-body claim) as a supporting anchor on
the same finding.

Coverage is complete for the supplied scope and both required gates are green, so the
negative verdict rests solely on the blocker, not on incompleteness.

## Subject

- PR: synthetic fixture (no URL/title supplied). Linked issue reference: present per fixture;
  issue number not supplied.
- Base SHA: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- Head SHA: `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`
- patch_digest: null (clean revision input, not dirty)
- Changed files (3): `src/export.py`, `tests/test_export.py`, `docs/ops/conversion-probe.md`
- Reviewed instruction files: none supplied by the fixture. Root AGENTS.md,
  cli/shared/AGENTS.md and REVIEW.md files are unavailable in this exercise and are reported
  as not loaded (context_complete: false for project-instruction context; see Gaps).
- Contract state: resolved (two explicit Done-when criteria supplied in the fixture).

## Required gates at head bbbbbbbb...

| Check | Required | Status | Head | Attribution | Evidence |
|---|---|---|---|---|---|
| required-check-1 (name not supplied) | yes | passed | bbbbbbbb... | not_applicable | fixture: "Both required trusted CI checks passed at this head" |
| required-check-2 (name not supplied) | yes | passed | bbbbbbbb... | not_applicable | fixture, same sentence |

Requiredness source: the fixture states these are the required trusted checks. No repository
branch-protection or rules data was read; requiredness is taken from the supplied evidence,
not inferred from a green list. Policy-known: yes for this fixture, with that provenance
disclosed. No local commands were executed (execution prohibited for this exercise).

Specialist security pass: not required (no trust-boundary change evidenced; see Security).
Mutation gate: not a required gate in the supplied policy; stage status below.

## Contract traceability

| ID | Criterion (exact text) | Implementation | Verification | State | Basis |
|---|---|---|---|---|---|
| AC-1 | "`export --all` writes every record once, shown by the free suite." | `src/export.py` (changed, inspected per fixture, no code defect found) | `tests/test_export.py` (changed, inspected per fixture, no defect found); both required CI checks passed at head | **met** | ci + static (fixture-supplied inspection) |
| AC-2 | "The paid conversion service has been called once on the pinned build against service API v3 and the observed quota and outcome are recorded in docs/ops/conversion-probe.md." | `src/export.py:12` sets `API_VERSION = "v3"` (the endpoint under test); `docs/ops/conversion-probe.md` (the record) | Author-recorded run in `docs/ops/conversion-probe.md`: run once on 2026-10-20, build v1.4.0, service API **v2**, outcome accepted, quota 1/1000, raw logs outside repo | **partial** | author-recorded (record does not satisfy the criterion's text; see F-1) |

AC-1 note: the fixture asserts that the free suite is exercised and that both required checks
passed; the mapping between a named CI check and "the free suite" is not spelled out in the
fixture. Recorded as a non-material gap (VG-3), not as a reason to downgrade the state.

AC-2 reasoning under the review record's author-recorded rule:
- The criterion is bound to its exact text. It does not merely say "has run and its result is
  recorded"; it names the run's required identity: once, on the pinned build, **against
  service API v3**, with quota and outcome recorded.
- The record is complete as a record: it names date, build, API version, outcome, quota and
  its stated limit (raw logs outside the repository). It is therefore not "unverified for
  missing identity". It is complete and it says v2.
- A record whose stated result does not satisfy the criterion's own text is unmet or partial.
  The "called once", "quota and outcome recorded" parts are satisfied; the "against service
  API v3" part is not. Assigned: partial. (Unmet would reach the same blocker branch; the
  state name does not change the verdict.)
- No evidence requirement is added beyond the contract: raw logs and independent re-execution
  are not demanded; the reviewer's lack of an account on the paid service is a disclosed,
  non-material limit (VG-2). The blocker comes only from the record's own content versus the
  criterion's text and the PR body.
- "Pinned build": the fixture does not state which build is pinned, so build v1.4.0 cannot be
  checked against it; this is noted in VG-1 as part of what a corrected record must make
  explicit, not as a separate finding.

## Findings

### F-1 `docs/ops/conversion-probe.md::probe-record.api-version-vs-contract`

- Severity: Minor (unmet governance/contract requirement; no runtime defect demonstrated)
- **Blocker? Yes** - branch 2 (failed linked-issue requirement AC-2); supporting anchor
  branch 3 (PR-body claim contradicted by the committed record). One cause, one finding,
  one blocker.
- Location: `docs/ops/conversion-probe.md` (changed at head; the line recording
  "service API v2"); related changed line `src/export.py:12` (`API_VERSION = "v3"`);
  PR body claim "the probe exercised the v3 endpoint that this change introduces".
- Trigger/path: reviewer reads AC-2 against the committed record and the PR body.
- Expected: the record names a probe run against service API v3 on the pinned build, with
  quota and outcome, matching both the criterion and the PR body.
- Actual: the record names service API v2 (run once, 2026-10-20, build v1.4.0, accepted,
  quota 1/1000). The PR body says v3. The diff introduces v3 at `src/export.py:12`. The
  committed record and the PR body name different service versions for the same run; no
  other record of the probe exists in the PR feeds.
- Causal anchor: unmet linked-issue requirement (AC-2 text "against service API v3") and
  contradicted PR-body claim. Changed-line anchors: the record itself is diff-added;
  `src/export.py:12` is diff-added.
- Counterevidence considered: the record could be a typo for v3; the reviewer cannot
  establish that from available evidence, and the committed record is the only evidence the
  criterion accepts. No reply, CI output or second record resolves the discrepancy. The
  discrepancy does not pre-exist at base (the record is new in this PR).
- Verification method: static comparison of three in-PR texts (criterion, record, PR body)
  plus the diff line. No execution needed or possible.
- Consequence for the change: as recorded, the only paid probe exercised v2, which is not the
  endpoint this change introduces; the v3 behavior, quota and outcome on the paid service are
  therefore unrecorded at this head.
- Remedy (fix in this PR, not a follow-up): either (a) if the run was actually against v3,
  correct `docs/ops/conversion-probe.md` so that its stated API version, build and inputs
  match the criterion and the PR body, or (b) run the probe once more on the pinned build
  against service API v3 and record date, build, inputs, outcome, quota and limits in the
  same file. In both cases make the "pinned build" identity explicit so the record can be
  read against the criterion. Then update the PR body if it no longer matches.

No recurring defect class: single instance, no class name, no sweep required.

### Optional suggestions

None.

## Out-of-scope observations

None.

## Carried

Not applicable: first round, no published or local baseline.

## Dimensions (project checks)

1. Issue scope: AC-1 met; AC-2 partial (F-1). No undisclosed partial beyond F-1.
2. Structural integrity: both required checks passed at head; no local commands run
   (prohibited). No interface change evidenced.
3. Stale code: no removed/renamed modules evidenced; not applicable.
4. Technical debt: debt introduced: none evidenced; debt closed: none evidenced. The
   diff-added record is a factual record, not aspirational documentation; branch 4 does
   not match.
5. Documentation accuracy: the diff-added record conflicts with the PR body and the
   criterion; covered by F-1 (same cause). No broken paths or `#NNN` in skill files
   evidenced; no SKILL.md touched.
6. Conventions: no skill/role/selector/CI-workflow files touched; not applicable beyond
   file placement (docs under docs/, tests under tests/), which is consistent.
7. Follow-up hygiene: F-1 is a blocker and must be fixed in this PR.
8. Correctness: fixture states full inspection of `src/export.py` and
   `tests/test_export.py` with no defect found; the only identified changed line
   (`API_VERSION = "v3"`) is declarative. No code defect admitted.
9. Security: see below; no finding.
10. Test quality: free suite exists and passes per fixture; its assertions are not
    reproduced in the fixture, so assertion quality is accepted on the fixture's
    "no defect found" statement (disclosed in VG-3).
11. Skill content quality: no skill bodies touched; skipped.
12. PR description: linked issue reference present; claim about the v3 probe contradicted
    by the committed record (anchored on F-1, not a second finding).

## Focused lenses

- Errors/cancellation/fallbacks: not applicable (no error-path change evidenced).
- Type invariants: not applicable (no type construction/validation change evidenced).
- Comments/documentation claims: applied; result is F-1.
- Test behavior/refactoring resilience: applied to the extent the fixture allows (suite
  passes, no defect found); no finding.

## Security baseline

Changed surface: a service API version constant for a paid external conversion service and
an operational record. No new untrusted-input-to-sink path evidenced; no auth/tenant,
credential lifecycle, CI/release or agent-permission change evidenced; no secrets in the
record (quota and outcome only; raw logs outside the repo). Specialist pass: not required.
Limit: file bodies are not reproduced in the fixture; the baseline relies on the fixture's
summary of the diff.

## Mutation testing

Applicability: the identified production change (`API_VERSION = "v3"`) is a declarative
constant edit; whether other predicate/boundary logic changed in `src/export.py` cannot be
determined from the fixture summary. Status: **skipped** (execution prohibited for this
fixture exercise; no runner/config identity available). Not a required gate in the supplied
policy; the skip does not fail the review and does not stand in for any other evidence.

## Coverage

- Mode: full. Reviewed 3 of 3 changed files (`src/export.py`, `tests/test_export.py`,
  `docs/ops/conversion-probe.md`), all supplied in full and inspected per the fixture.
- Prioritized: `docs/ops/conversion-probe.md` and `src/export.py:12` (contract-bearing).
- Partial inspection: none within the supplied scope. Disclosure: the reviewer worked from
  the fixture's summary of file contents; this is the complete available evidence for this
  exercise.
- dimensions_complete: true. context_complete: false (project instruction files not
  supplied; see VG-3).

## Verification gaps

| ID | Material | What remains unverified |
|---|---|---|
| VG-1 | yes | Whether the paid probe has ever been run against service API v3 on the pinned build with this change's endpoint. The committed record says v2; the pinned build identity is not stated in the fixture, so build v1.4.0 cannot be matched to it. Resolved by the F-1 remedy. |
| VG-2 | no | The reviewer has no account on the paid service and cannot rerun or authenticate the probe; raw logs are outside the repository and were not inspected. The criterion asks the author to run and record, not for raw artifacts or independent re-execution, so this is a disclosed limit, not an added gate. |
| VG-3 | no | Project AGENTS.md/REVIEW.md not supplied; the exact CI check names and the mapping of a check to "the free suite" are not in the fixture; test assertion bodies not reproduced. Accepted on the fixture's statements. |

## Risk

- Level: Medium. Reason: the change switches a paid external service integration to a new
  API version (v3) whose paid-service behavior is unrecorded at this head (F-1). Blast
  radius: `export --all` conversion calls and paid quota. Reversibility: revert the
  constant and the record; no irreversible state change evidenced (one probe call, quota
  1/1000).
- Required human scrutiny: billing-adjacent (paid service) under the protocol; a human
  owner should confirm the corrected record before merge. Owner/human reviewer: unknown.
- Rollback: revert the PR commit(s); no migration or deployment behavior evidenced.
- Flags/rollout/approval counts: none evidenced; none invented.

## Review record consistency

review.json was not constructed or validated: the validator script may not be run in this
exercise, and no positive verdict is claimed, so validation is not a precondition here. The
fields above map directly onto the record schema (subject, contract, coverage, checks,
findings, requirements with verification_basis author-recorded on AC-2, verification_gaps,
claimed_verdict REQUEST_CHANGES). AC-2 is disclosed as the author-recorded criterion.

## Timing

elapsed_seconds: null; active_review_seconds: null; verification_seconds: null;
ci_wait_seconds: null. No clock or timestamped log was available for this fixture run.

## Round and baseline

Round 1, full review. First-pass published baseline: unavailable (none). Latest reviewed
SHA: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb (this run, local, not published).

## How to finish

Author applies the F-1 remedy; reviewer re-reads `docs/ops/conversion-probe.md` and the PR
body at the new head, confirms the record names service API v3, the pinned build, inputs,
outcome and quota, and that no other feed contradicts it; then AC-2 can move to met with
verification_basis author-recorded and the verdict recomputed at that head.
