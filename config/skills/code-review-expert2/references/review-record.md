# Revision-Bound Review Record

For a real review, keep review.json in the authorized review workspace, outside the
reviewed source tree by default, together with validator-output.txt holding the exact
validator command line and its full output. Link the readable report to both; they outlive
a disposable checkout only when kept with the report. Do not commit or publish them unless
requested. Resolve target/preflight guards before constructing a record.
For fixture-only exercises, use supplied evidence and report missing metadata instead of
fabricating revisions, gate outcomes or inspection.

## Contract traceability

Give every explicit acceptance criterion an ID and text, implementation locations and
verification references. Mark each met, unmet, partial or unverified. A met criterion needs
both implementation and verification evidence; verified static reasoning can be named as
static evidence when execution is unavailable. Do not pretend it is a passing test.
Unmet/partial requirements enter the ordinary blocker calculation; unverified requirements
prevent positive review. An explicitly authorized scope change must update the contract
with its evidence before treating an omitted requirement as out of scope.

A criterion can ask the author to perform a run and record its result, for example a billed,
live, credentialed or host-specific probe. Bind acceptance to the criterion's exact text:
"has run and its result is recorded" is satisfied by a recorded run whatever its outcome,
including a recorded error, while "passes" requires the recorded outcome to be a pass. Accept
the author's record as verification evidence, with verification_basis author-recorded, when
it names its identity (date, build or version, inputs, outcome and stated limits), its stated
result satisfies the criterion's own text, and no available evidence (diff, CI, another
record or reply) contradicts it. verification_basis makes the source visible; it does not
verify the evidence. Do not add evidence requirements the contract does not contain: absent
raw artifacts or independent re-execution block only when the criterion, the issue or a
project/user instruction explicitly requires them; otherwise name what was not inspected as
a non-material gap. The criterion stays unverified when the record is incomplete (missing
identity, ambiguous outcome), when later commits change the recorded behavior, or when a
free in-scope check could confirm it and was not run. It is unmet or partial when the record
is absent or does not satisfy the criterion's own text, and a contradicted claim when it
conflicts with the diff or another record. Author prose about current code behavior is never
an author-recorded observation; verify it against the code under the protocol.

For bug fixes capture red/green evidence under the review protocol. Evidence references
point to actual command output, source locations, reports or authorized requirements.
No score, row count, JSON field or validator output proves that those observations are true.

## Record fields

Use schema_version 2 and profile general, aura-peer or aura-self. Schema 1 is the legacy
shape without causes; the validator still accepts it and reads what it lacks as unknown
(see run status below). The record contains:

- skill: the identity of the skill that ran: name, version (its SKILL.md metadata.version,
  X.Y.Z) and fingerprint. Compute the fingerprint with
  `python3 scripts/review_record.py --skill-fingerprint <skill directory>` on the installed
  directory you read; never copy it from an earlier report. It is the SHA-256 of one line
  `<file sha256>  <path>` plus newline per file in SKILL.md, references/ and scripts/,
  sorted by path bytes (eval/, `__pycache__` and .DS_Store excluded; symlinks and paths
  containing a newline or other control character refused, since they could forge or hide
  a line). On a clean tree it equals `find SKILL.md references scripts -type f | LC_ALL=C
  sort | xargs shasum -a 256 | shasum -a 256`. Write the same three values in the report
  header. Schema 2 requires it. A schema 1 record without skill (or with null) stays valid
  and reads as identity unknown, never as the current version.
- rereview: include it on every re-review (any round after the first, full or delta) and
  omit it on a first review. previous_head is the full SHA of the previously reviewed head
  (in delta mode it equals coverage.baseline_head); prior_finding_ids lists the IDs already
  reported before this round, and each of them stays in findings with its current state.
  The validator can enforce presence only in delta mode for a record with skill identity
  or when --expected-previous-head is supplied; elsewhere it is the reviewer's duty.
- subject: base and head full commit IDs; patch_digest is null or the SHA-256 of the full
  reviewed dirty input, including included untracked files.
- contract: state resolved, none, missing_reference or unavailable; evidence references.
  General reviews can have no explicit contract; AURA peer missing references use its
  existing blocking precondition, and an unresolved self contract remains incomplete; it
  then carries gap, the id of the material verification gap that explains it.
- coverage: mode full/delta; files with path, state reviewed/baseline/unreviewed and evidence;
  each unreviewed file carries gap naming its material verification gap; dimensions_complete
  and context_complete booleans, each false one explained by dimensions_gap or context_gap;
  baseline_head is null or full SHA;
  delta_files is the exact changed-since-last-review path list, empty for full mode.
  If that list includes a reverted/deleted-from-diff path absent from the current base-to-head
  diff, inspect its reversion and prior findings, then use a new full pass. This validator
  deliberately rejects delta reuse for that shape; never drop the path to make it validate.
- checks: unique id, required boolean, status passed/failed/pending/unavailable/skipped,
  attribution introduced/pre_existing/unknown/not_applicable, head and evidence. Required
  checks are bound to the current head. An inapplicable check is omitted with policy evidence,
  rather than marked required-and-passed. Record specialist security passes here too. A
  required check that stays open (not passed, and not a failure attributed to the change)
  carries cause, and authority when the cause is scope_limit. List every planned required
  check here even when it never ran; a required check absent from the record reads as
  cause unknown.
- findings: unique id; severity Critical/Minor/Style; route finding/observation/carried;
  status open/fixed-and-verified/rejected-with-evidence/deferred-with-rationale;
  verified boolean, origin change/base/unknown, defect and reachable booleans; anchors,
  evidence, and blocking_reasons. Reasons are introduced_defect, unmet_requirement,
  contradicted_claim, introduced_gate_failure, plus aspirational_doc/missing_issue for AURA.
  An anchor is a nonempty string or an object with path (repository-relative), optional line
  (1-based, at the reviewed head) and optional quote: one whole line copied verbatim from
  that file at the reviewed head, without a line break. Give every admitted finding an object
  anchor with a quote; the quote, not the line number, locates the finding, so it survives
  line drift and can be checked mechanically under anchor verification below.
  Optional class (nonempty string) names a recurring defect class; instances then lists
  every verified instance as nonempty path:line anchors. Give both or neither.
  On a re-review, every finding whose ID is not in rereview.prior_finding_ids records
  present_at_previous_head: yes when evidence (code at previous_head, a probe there) shows
  the defect already existed at the previously reviewed head, no when evidence shows a later
  commit introduced it, and unknown when neither is evidenced. Prior findings and first
  reviews omit the field. A new finding without a valid value makes the record invalid, but
  the value itself is never a verdict input: it measures cross-round recall, and a yes does
  not route a change-introduced defect away from blocking.
  Use only verified admitted findings; unresolved suspicions belong in verification_gaps.
- requirements: unique id, text, state met/unmet/partial/unverified, implementation and
  verification evidence arrays, and optional verification_basis reviewer/ci/static/
  author-recorded naming the source of the verification evidence. An unverified criterion
  carries gap naming its material verification gap. Use an empty list only
  when there are no explicit criteria. The validator lists author-recorded criteria in its
  output so the report discloses them; it does not verify that evidence.
- verification_gaps: id, material boolean, cause (authority with scope_limit) and evidence
  explaining what is unverified. One gap can explain several files, criteria and coverage
  flags; the gap is where their cause is written once. A
  material gap names concretely the unresolved requirement or the material correctness or
  security question it leaves open, for example a missing or pending required check or
  specialist pass, a feasible in-scope check not run, a criterion whose stated evidence form
  is absent, an incomplete, inconsistent or contradicted record, or an explicit requirement
  for independent reproduction. Being unable to rerun or authenticate an author record that
  the criterion only asked the author to produce is not material by itself; record it with
  material false and say what was not inspected.
- stopped: null, or an object with cause and evidence when the review run ended before its
  planned work (a platform refusal, an exhausted quota, a tool or environment failure).
  An approved scope limit is not a stop; it never uses this field.
- claimed_verdict: APPROVE, REQUEST_CHANGES or NEEDS_REVIEW, calculated by the reviewer.
- claimed_run_status: complete or incomplete, calculated by the reviewer under the run
  status rule below.
- timing: optional observational object described below; never a verdict input.

Paths are repository-relative with forward slashes. Evidence arrays contain nonempty
references, not invented output. In delta mode baseline states require prior report
evidence at the independently pinned baseline SHA; report current/delta and reused
coverage separately. Changes in delta_files must be reviewed now, never marked baseline.

## Run status and causes

Run status says whether the run delivered full-PR assurance; the verdict says what the
evidence shows. They are separate: a complete run can request changes and an incomplete
run can already carry a proven blocker. The validator computes both; a model's claim of
completion is never evidence of it.

The run is incomplete exactly when an incompleteness source exists: a material verification
gap, an unreviewed file, a false dimensions_complete or context_complete, an unresolved
contract, an unverified requirement, an open required check, a required check absent from
the record, an unresolved required-check policy, an empty changed-file set, or a stopped
run. Each source becomes one run_status reason with its cause, authority and evidence; a
linked source takes the cause and evidence of its gap. A schema 2 record that leaves any
record-side source without its cause or gap link, links to a missing or non-material gap,
or claims a run status other than the computed one, is invalid. Causes:

- platform_refusal: an explicit platform safety refusal of a model run; quote its text.
- quota: an account or usage quota ran out.
- tool_failure: a tool, fetch, API error or timeout; not a platform refusal.
- environment: a missing dependency, fixture, host, sandbox or credential.
- missing_specialist: a required specialist pass or agent was not available.
- pending: the evidence exists but is not available yet, such as a running CI check or a
  human gate still waiting.
- scope_limit: an approved scope narrower than the full PR excluded it. authority names the
  approval (the brief line, issue comment or user/maintainer decision) and is required.
- other: a known cause outside these classes; the evidence names it.
- unknown: the cause is not evidenced. Never pick a specific class without evidence.

A deliberately limited review is incomplete with cause scope_limit, never complete: full-PR
assurance is missing even when the approved task was done. approved_scope_status records
the approved task separately: complete when every reason is a scope_limit (the run did all
the approved scope asked), incomplete otherwise. A stopped run is never complete in either.
Sources the validator finds outside the record (policy not supplied, a required check
absent from the record, an empty changed-file set) read as cause unknown with a validator
evidence line.

A schema 1 record has no causes: every reason reads cause unknown, and stopped, claimed
status and approved_scope_status read unknown unless the run is complete. Schema 2 fields
inside a schema 1 record are rejected by key presence, even with a null value, rather than
half-read; migrate the whole record.

## Timing without weakening review

For new real reviews, include timing when an actual clock or timestamped logs are available:

```json
"timing": {
  "elapsed_seconds": 180,
  "active_review_seconds": 100,
  "verification_seconds": 90,
  "ci_wait_seconds": null,
  "evidence": ["review-clock.jsonl:1-12"]
}
```

Measure wall elapsed independently from active inspection/analysis, local tests/build/mutation,
and passive CI waiting. Use monotonic elapsed measurement where available; otherwise use
reliable timestamped logs and disclose precision. Verification includes baseline/build and
mutation, not just mutants. Record actual work, not suggested future commands. Specialist
work is included in elapsed time and identified in evidence; do not add concurrent agent
runtimes to elapsed. Never infer time from token counts or output length.

A number is nonnegative finite seconds; booleans are invalid. Unknown/unmeasured categories
are null, not guessed zero. Use all-null values and explain unavailable measurement when
no clock data exists. Any numeric measurement needs evidence. Each category is the union
of observed intervals for that category, so parallel tests are not counted twice within it.
Categories can overlap: the example's 100+90 does not imply 190 seconds elapsed. Never add
them into a total. Each known category cannot exceed a known elapsed total. Do not claim
precise exclusive attribution without interval evidence. Evidence is observational; the
validator checks its shape, not timing authenticity. Older records may omit timing.

Compare matched review mode, risk, scope and tool configuration before claiming a speedup.
Separate active work from test and CI delays. A time budget can stop optional work with an
honest partial/skipped status; it never clears a required gate or hides an unresolved defect.
The delta qualification and coverage reuse are reviewed outside the JSON validator; the
validator checks revision/file accounting, not the truth of a qualifying prior review.

## Validate independently supplied identity and policy

Run the bundled [validator](../scripts/review_record.py) with review.json,
--expected-profile from the trusted invocation mode (never copied from the record),
--expected-base and --expected-head from a fresh trusted target read, and --changed-files
pointing to a JSON array of all current changed paths from the verified diff. Supply
--expected-patch-digest for dirty input, --baseline-head and --delta-files for delta reuse,
and repeat --require-check for each required gate/pass from trusted policy and the review
plan. Requiredness and completeness of that list must be resolved outside the artifact;
do not trust the record to define its own policy. Pass --policy-known only after that step.
An unknown required-check policy produces NEEDS_REVIEW. To bind the record to the skill
that should have run, pass --expected-skill-version and --expected-skill-fingerprint taken
from a trusted source, such as the pinned release commit hashed with a script copy outside
the installed package; a package's own script cannot vouch for that package. On a re-review
pass --expected-previous-head from the pinned prior report. Each supplied expectation must
match the record, and a legacy record lacking the field is rejected rather than assumed
current. Without them the identity is self-reported, and the previous head is verified only
through the delta baseline; the output says which (previous_head_verified).

The tool reads JSON and emits a decision; it never runs commands from records or reads
evidence targets. Its exit codes are 0 for a consistent positive review, 1 for a consistent
negative/incomplete review, and 2 for invalid/stale/inconsistent input. An invalid record
never authorizes approval. A claimed positive verdict inconsistent with the evidence is
rejected; do not edit evidence to satisfy the claimed verdict.

The validator checks identity, coverage accounting, requirement states, finding lifecycle,
required check outcomes, verdict and run-status consistency. Its output states the
schema_version, the reviewed subject (base, head, patch_digest), skill (name, version and
fingerprint, each unknown for a record without identity) with skill_identity verified (both
expected values supplied and matched), self_reported or unknown, run_status (state, claimed,
approved_scope_status, causes, authorities, stopped and one reason per incompleteness source)
and, on a re-review, the new finding IDs grouped by present_at_previous_head. An invalid
record prints valid false with run_status incomplete and cause unknown. Report run status
and approved scope status from this output, never from the run's own claim. It
cannot authenticate evidence or replace source review. A changed head/config/test selection
invalidates affected evidence under the protocol even when JSON syntax remains valid. Public review publication still requires
the session's explicit authorization and final current-head check.

## Verify anchors against the reviewed head

The validator checks anchor shape only. Locating anchors reads the reviewed files, so it is
a separate script, [verify_anchors.py](../scripts/verify_anchors.py), run after the
validator and before reporting or publishing:

```
python3 scripts/verify_anchors.py review.json --expected-head <head> \
  --changed-files changed.json --repo <checkout containing head>
```

Use the same trusted head and changed-file list as the validator. The script reads file
content from the head commit through git, never from the working tree, and checks that:

1. every finding with route finding and origin change has an object anchor whose path is a
   changed file, unless it was admitted through the contract or the PR body (blocking
   reasons unmet_requirement, contradicted_claim or missing_issue); a string anchor cannot
   be located and does not count;
2. every object anchor with a quote or line resolves at head: the path is a regular UTF-8
   file, the quote matches a whole line once each whitespace run is collapsed to one space
   and both ends are trimmed, and a given line number holds the quote (or exists, without
   a quote).

It exits 0 when every check passes, 1 when any anchor mismatches, with the finding ID,
anchor index, path and problem of each, and 2 for invalid input or a git failure. A
mismatch means the finding is not verified where the record says. Send it back to
verification at the head; correct the anchor only from that re-verification, never by
editing a quote until it matches, or move the concern to verification_gaps. Use the
resolved line numbers for the report and any published comment. A dirty-input record
(patch_digest set) is refused because its reviewed content is not a commit; say in the
report that its anchors were not mechanically verified. Keep the command line and output
with validator-output.txt.
