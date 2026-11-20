reviewer: pr-review2
skill-version: 2.11.0
candidate-sha256: 9398fd9497fbcc122a6903318639aeed88baf66fd7f62223adafc9a2407490c0
case: 35-dev-seed-a
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: PASS against the oracle in force at the time; superseded
- Rescore note: an independent re-review found the fixture did not settle whether the new
  fixture POSTs made the base-rooted risk materially more severe (rule 4). The case now
  states that base already posted the local config to the same listener, and was rerun at
  2.11.1; this run does not establish the corrected case.
- Expected: Expected positive verdict with the pre-existing residual disclosed, not blocking.
- Observed: Ready to merge; F1 wrong-listener risk recorded as a disclosed residual rooted in untouched wait_ready (rule 4, origin base), Blocker? No, with an author-opened follow-up issue requested; no runtime.py demand.
- False blockers: 0. Harmful false positives: 0.
- Tool policy: offline fixture; one fresh-context Claude Code subagent per case, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus that case's input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: single run, scored after the run against the hidden oracle.

## Raw reviewer output

# PR Review 2 - offline fixture 35-dev-seed-a

**Verdict: Ready to merge** (peer mode, round one, full review)

1 verified finding, 0 blockers. The single finding (F1, Minor) is a disclosed residual rooted in
unchanged code (materiality rule 4, origin base) and does not block. Nothing must be fixed in this
PR; the author is asked to open a follow-up issue for F1.

This is a fixture-only evaluation of the skill, not a live AURA PR review (SKILL.md, Inputs and
boundaries). All repository state comes from the supplied trusted observation in `input.md`.

## Skill and reviewer identity

| Field | Value |
|---|---|
| Skill name | pr-review2 |
| metadata.version | 2.11.0 |
| Package fingerprint | not computed: script execution is not permitted in this exercise, and the fingerprint must be computed from the directory read, never copied |
| Reviewer host | Claude Code (Claude Agent SDK) |
| Reviewer model family | claude |

## Run status

- review.json and validator-output.txt: not produced. The fixture forbids inventing review.json,
  and the validator and anchor verifier (`scripts/review_record.py`, `scripts/verify_anchors.py`)
  could not be run (no program execution). Run status is therefore not validator-computed.
- What a validator run would see from the supplied evidence: no material verification gap, both
  changed files reviewed, contract resolved, all criteria met, both required checks passed at head,
  no stop. Expected state: complete; approved_scope_status: complete. This is a reviewer
  expectation, not validator output.
- Stopped: no.

## Subject

| Field | Value |
|---|---|
| PR | offline synthetic fixture; URL/title/author not supplied |
| Linked contract | linked issue present: "`tool dev --seed` loads local fixtures into the dev service after it starts" |
| Base | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |
| Head | bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb |
| Patch digest | not applicable (clean commit input) |
| Instruction / REVIEW.md paths | none supplied in the fixture (root AGENTS.md, cli/shared/AGENTS.md, REVIEW.md not available); no instruction file was read |

## Required gates at head

Requiredness source: trusted policy line in the fixture: "required checks are lint and tests; both
passed at head."

| Check | Required | Status at head | Attribution | Evidence |
|---|---|---|---|---|
| lint | yes | passed | not applicable | trusted policy line, input.md |
| tests | yes | passed | not applicable | trusted policy line, input.md |
| Security specialist pass | no | not applicable | - | no trust boundary changed (see Security) |

No command was run locally (execution not permitted). No gate was inferred green beyond the
supplied statement.

## Timing

No review timing clock was collected. elapsed, active review, verification and CI-wait time are
all unknown.

## Mutation testing

Applicable: the change adds decision logic (`if seed:` in src/dev.py) and a test exercising it.
Status: skipped: no project-pinned runner. No StrykerJS/Stryker.NET dependency, manifest entry or
config was supplied, no mutation tool is installed, and neither policy nor the user requires
mutation ("Mutation is optional"). Production scope src/dev.py, test scope tests/test_dev.py; no
outcome counts.

## Coverage

- Reviewed 2 of 2 changed files.
  - src/dev.py: complete new file content read line by line (lines 1-9), plus the supplied base
    comparison (lines 1, 3, 5, 6, 9 identical at base; seed import, `seed` parameter and lines 7-8
    new).
  - tests/test_dev.py: inspected through the supplied trusted observation only ("The test asserts
    load_fixtures runs after wait_ready"). Its source text was not supplied, so the
    test-resilience lens (mocking, tautology) rests on that observation and the green tests gate.
- Affected untouched callee traced: src/runtime.py `wait_ready(port, timeout=30)`, from its supplied
  behavior (returns as soon as any TCP connect to 127.0.0.1:port succeeds).
- Callers of `dev()` were not supplied; the CLI wiring of `--seed` is described only by the PR body.
- Mode: full, round one. No prior baseline; first-pass and latest reviewed baseline: none (first
  review).

## Risk

Low. Opt-in local development command (`tool dev --seed`), no deployment, release, auth, billing,
credential or migration surface. Blast radius: one developer machine. Reversibility: revert the PR;
the only state change is fixtures posted to a local service. Rollback: not applicable beyond a
revert, since no deployed behavior changes. No extra human scrutiny area is triggered.

## Contract traceability

| ID | Criterion (exact text) | Implementation | Verification | State |
|---|---|---|---|---|
| R1 | `tool dev --seed` loads local fixtures into the dev service after it starts. | src/dev.py:7-8 after start_service (line 5) and wait_ready (line 6) | static trace + tests gate passed | met |
| R2 | fixtures are posted only after `wait_ready` returns | src/dev.py:6-8, sequential call, `load_fixtures` only reachable after `wait_ready(port=PORT)` returns | static trace | met |
| R3 | a test proves the order | tests/test_dev.py asserts load_fixtures runs after wait_ready (supplied observation) | ci (tests passed at head); test source not supplied | met |

Note on R1: when port 8080 is already held by another program, fixtures reach that program instead
of the dev service. That is F1 below; its root is unchanged base behavior, and the issue's own DoD
defines "after it starts" as "after `wait_ready` returns", which the code satisfies.

## Findings

### Blockers

None.

### Should-fix / disclosed residual (non-blocking)

#### F1 - dev.seed-target-identity: seeding trusts a readiness probe that cannot tell the dev service from any other listener

- Location: src/dev.py:8 (changed line), root in src/runtime.py `wait_ready` (untouched) and
  src/dev.py:3 (unchanged at base).
- Anchor (verbatim head line, src/dev.py:8): `        load_fixtures("http://127.0.0.1:%d" % PORT)`
- Severity: Minor. Blocker? **No**.
- Trigger/path: another local program already listens on 127.0.0.1:8080 when `tool dev --seed`
  starts -> `start_service(port=8080)` (line 5) -> `wait_ready(port=8080)` (line 6) returns at once
  because any TCP connect succeeds -> line 8 posts the fixtures to that other program.
- Expected: fixtures load into the dev service started on line 5.
- Actual: fixtures are posted to whichever program owns port 8080; the dev service is not seeded.
- Verification method: complete static trace of src/dev.py lines 4-9 against the supplied
  `wait_ready` semantics, plus the supplied verified observation of this exact scenario. No local
  reproduction (execution not permitted); runtime verification by the reviewer is unverified.
- Counterevidence / origin: the root is unchanged behavior. At base, `PORT = 8080`,
  `start_service(port=PORT)` and `wait_ready(port=PORT)` were identical, and src/runtime.py is
  untouched. Before this PR, the same trigger already sent the user's own requests to the foreign
  program. Origin: base.
- Why it does not block (materiality rule 4, pre-existing behavior; deciding evidence):
  - Likelihood unchanged: the trigger (port 8080 pre-occupied) and the probe that misses it are
    both unchanged; the PR changes neither PORT nor `wait_ready`.
  - Severity not materially increased: the failure is the same misrouting of requests intended for
    the dev service that already affected the user's requests; `--seed` adds requests of the same
    kind, only on explicit opt-in. The team classifies the impact Minor, local development only,
    and port 8080 is not used by any tool the project documents.
  - Therefore it is a disclosed residual, not a change-introduced defect; rule 4 records origin
    base (no non_blocking basis). It is not Critical, so no Maintainer decision item is needed.
- Remedy (follow-up issue the author opens): make readiness identify the started service, for
  example fail fast when the port is already bound before `start_service`, check that `proc` is
  still alive after `wait_ready`, or probe a service-specific health endpoint/token instead of a
  bare TCP connect. Add a test with a pre-occupied port. The reviewer does not open the issue.
- Security note: not a trust boundary. The other listener is a local process; fixtures are local
  development data. Guard-versus-boundary order: no policy, issue or comment names the readiness
  probe a security boundary (2.1); no untrusted source gains an effect it could not otherwise cause
  (2.2); the PR body claims readiness waiting, not resistance to a foreign listener (2.3).

### Optional suggestions

None.

## Verification gaps (non-material)

- G1: If `load_fixtures` raises, `dev()` propagates the exception without returning `proc`; whether
  the started service is then left running depends on `start_service` semantics and the caller,
  neither of which was supplied. Not a verified finding; the command still fails visibly. Material:
  no.
- G2: tests/test_dev.py source and the `dev()` CLI caller were not supplied; their behavior is taken
  from the trusted observation and the PR body. Material: no (fixture declares the observation
  trusted; tests gate passed at head).

## Dimension results

1. Issue scope: all three criteria met (table above); no scope creep (2 files, both in scope).
2. Structural integrity: required lint/tests passed at head; existing `dev()` behavior unchanged
   when `seed` is false (lines 5, 6, 9 identical to base). Note: `seed` is a new required positional
   parameter; existing callers of `dev()` were not supplied, but the green tests gate gives no sign
   of a broken caller.
3. Stale code: none; nothing removed or renamed.
4. Technical debt: introduced: F1 residual inherits the TCP-only readiness probe (tracked via the
   requested follow-up). Closed: none.
5. Documentation: no docs changed; no comments affected.
6. Conventions: project instruction files not supplied; nothing in the diff contradicts supplied
   conventions. Skill-registry rows not applicable (no skill files).
7. Follow-up hygiene: F1 -> author-opened follow-up issue; no in-PR fix demand.
8. Correctness: lines 7-8 traced for `seed` true/false and for a pre-occupied port (F1); no other
   input produces a wrong result on a changed line.
9. Security: baseline pass done. No untrusted input path: the URL is built from a constant, the
   fixtures are local, no new dependency, privilege or secret handling. No trust boundary changed,
   so no specialist pass was needed.
10. Tests: the ordering assertion protects a stated protocol (seed after readiness), so an
    interaction/order assertion is appropriate. No test for the pre-occupied port case (part of F1's
    follow-up remedy).
11. Skill quality: not applicable, no skill bodies touched.
12. PR description: linked issue reference present ("Closes the linked issue"). Claims match the
    diff: `--seed` added; seeding waits for `wait_ready`. Not contradicted.

## Out-of-scope observations

- O1: The PR body has no test plan; the changed paths name tests/test_dev.py, so the gap only costs
  reviewer orientation. Non-blocking.

## Carried

Not applicable: first review, no qualified first-pass baseline.

## Propagation sweep

Class `dev.seed-target-identity` (F1): searched the full reviewed diff (src/dev.py, tests/test_dev.py)
for other request sinks that rely on `wait_ready` alone. Instances: src/dev.py:8 only. Scope not
covered: other callers of `wait_ready` elsewhere in the repository (not supplied); they are untouched
base code and out of scope for this PR.

## Limits and how to finish in a live review

- Compute the skill fingerprint, write review.json (profile aura-peer, F1 with origin base), run the
  validator with trusted base/head/changed-files and `--require-check lint --require-check tests`,
  then run verify_anchors.py at head; report run status from validator output.
- Read root AGENTS.md, cli/shared/AGENTS.md and any REVIEW.md for the changed paths.
- Read tests/test_dev.py source to confirm the ordering assertion is not over-mocked.
