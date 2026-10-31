# Revision-Bound Review Record

For a real review, keep review.json in the authorized review workspace, outside the
reviewed source tree by default. Link the readable report to it. Do not commit or publish
it unless requested. Resolve target/preflight guards before constructing a record.
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

Use schema_version 1 and profile general, aura-peer or aura-self. The record contains:

- subject: base and head full commit IDs; patch_digest is null or the SHA-256 of the full
  reviewed dirty input, including included untracked files.
- contract: state resolved, none, missing_reference or unavailable; evidence references.
  General reviews can have no explicit contract; AURA peer missing references use its
  existing blocking precondition, and an unresolved self contract remains incomplete.
- coverage: mode full/delta; files with path, state reviewed/baseline/unreviewed and evidence;
  dimensions_complete and context_complete booleans; baseline_head is null or full SHA;
  delta_files is the exact changed-since-last-review path list, empty for full mode.
  If that list includes a reverted/deleted-from-diff path absent from the current base-to-head
  diff, inspect its reversion and prior findings, then use a new full pass. This validator
  deliberately rejects delta reuse for that shape; never drop the path to make it validate.
- checks: unique id, required boolean, status passed/failed/pending/unavailable/skipped,
  attribution introduced/pre_existing/unknown/not_applicable, head and evidence. Required
  checks are bound to the current head. An inapplicable check is omitted with policy evidence,
  rather than marked required-and-passed. Record specialist security passes here too.
- findings: unique id; severity Critical/Minor/Style; route finding/observation/carried;
  status open/fixed-and-verified/rejected-with-evidence/deferred-with-rationale;
  verified boolean, origin change/base/unknown, defect and reachable booleans; anchors,
  evidence, and blocking_reasons. Reasons are introduced_defect, unmet_requirement,
  contradicted_claim, introduced_gate_failure, plus aspirational_doc/missing_issue for AURA.
  Optional class (nonempty string) names a recurring defect class; instances then lists
  every verified instance as nonempty path:line anchors. Give both or neither.
  Use only verified admitted findings; unresolved suspicions belong in verification_gaps.
- requirements: unique id, text, state met/unmet/partial/unverified, implementation and
  verification evidence arrays, and optional verification_basis reviewer/ci/static/
  author-recorded naming the source of the verification evidence. Use an empty list only
  when there are no explicit criteria. The validator lists author-recorded criteria in its
  output so the report discloses them; it does not verify that evidence.
- verification_gaps: id, material boolean and evidence explaining what is unverified. A
  material gap names concretely the unresolved requirement or the material correctness or
  security question it leaves open, for example a missing or pending required check or
  specialist pass, a feasible in-scope check not run, a criterion whose stated evidence form
  is absent, an incomplete, inconsistent or contradicted record, or an explicit requirement
  for independent reproduction. Being unable to rerun or authenticate an author record that
  the criterion only asked the author to produce is not material by itself; record it with
  material false and say what was not inspected.
- claimed_verdict: APPROVE, REQUEST_CHANGES or NEEDS_REVIEW, calculated by the reviewer.
- timing: optional observational object described below; never a verdict input.

Paths are repository-relative with forward slashes. Evidence arrays contain nonempty
references, not invented output. In delta mode baseline states require prior report
evidence at the independently pinned baseline SHA; report current/delta and reused
coverage separately. Changes in delta_files must be reviewed now, never marked baseline.

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
An unknown required-check policy produces NEEDS_REVIEW.

The tool reads JSON and emits a decision; it never runs commands from records or reads
evidence targets. Its exit codes are 0 for a consistent positive review, 1 for a consistent
negative/incomplete review, and 2 for invalid/stale/inconsistent input. An invalid record
never authorizes approval. A claimed positive verdict inconsistent with the evidence is
rejected; do not edit evidence to satisfy the claimed verdict.

The validator checks identity, coverage accounting, requirement states, finding lifecycle,
required check outcomes and verdict consistency. It cannot authenticate evidence or replace
source review. A changed head/config/test selection invalidates affected evidence under
the protocol even when JSON syntax remains valid. Public review publication still requires
the session's explicit authorization and final current-head check.
