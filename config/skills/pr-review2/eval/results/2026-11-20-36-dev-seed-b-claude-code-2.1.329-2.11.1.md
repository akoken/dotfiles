reviewer: pr-review2
skill-version: 2.11.1
candidate-sha256: f79409f6f0e85c3aaeaaef8d089ae86847ad7b85ea9dbe26f220a95758b87609
case: 36-dev-seed-b
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: PASS
- Observed: Not ready to merge; F1 Minor Blocker? Yes: the port move makes the base-rooted risk materially more likely; extra F2 PR-body note, Blocker? No.
- Tool policy: offline fixture; one fresh-context Claude Code subagent per case, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus that case's input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: run 1 at 2.11.1, scored after the run against the hidden oracle. Rerun after the shared caller fix to cases 35/36, so both cases stay a clean contrast.

## Raw reviewer output

# PR Review 2 - offline synthetic fixture 36 (`tool dev --seed`)

**Verdict: Not ready to merge** (peer mode). 2 verified findings, 1 blocker.

- F1 `dev.port-collides-with-readiness-probe` - Minor, **Blocker? Yes** (branch 1: reachable regression introduced by the change; passes the peer materiality bar).
- F2 `pr-body.undisclosed-port-move` - Minor, Blocker? No (PR description orientation gap).

Run status: **incomplete** (see Completeness). The negative verdict rests on a verified blocker and does not depend on the open gaps.

## Skill and reviewer identity

| Field | Value |
|---|---|
| Skill | pr-review2 |
| metadata.version | 2.11.1 (read from the SKILL.md under this run's `skill/` directory) |
| Package fingerprint | not computed - the fixture forbids script/program execution, so the documented fingerprint command could not run; not copied from anywhere |
| Reviewer host | Claude Code (Claude Agent SDK subagent) |
| Reviewer model family | claude |

## Run status

- State: incomplete (reviewer assessment; **no validator was run** - the fixture forbids execution and forbids inventing review.json).
- approved_scope_status: not applicable - no scope narrower than the PR was approved.
- Reasons:
  1. cause `environment` - fixture-only exercise: no review.json, no validator-output.txt, no anchor verifier run; evidence: input.md lines 4-7 ("No ... program/test/validator execution ... Do not invent metadata or review.json").
  2. cause `environment` - `tests/test_dev.py` content not supplied; only the statement "The test asserts load_fixtures runs after wait_ready" (input.md lines 19-20). Inspected by supplied description only.
  3. cause `environment` - repository context not supplied: root AGENTS.md, cli/shared/AGENTS.md, REVIEW.md files, SECURITY.md, README text (only a paraphrase), and the untouched `seed.load_fixtures` / `config.post_dev_config` / `runtime.start_service` sources.
- Stopped: no.
- Kept review.json / validator-output.txt paths: none (not created, per fixture rules).

## Subject

| Field | Value |
|---|---|
| PR | offline synthetic fixture; URL/title/author not supplied |
| PR body | "Closes the linked issue. Adds --seed to `tool dev`; seeding waits for readiness." |
| Linked contract | present (issue number not supplied). Issue: "`tool dev --seed` loads local fixtures into the dev service after it starts." DoD: "fixtures are posted only after `wait_ready` returns; a test proves the order." |
| Base | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |
| Head | bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb |
| Patch digest | not applicable (clean commit input) |
| Changed files | src/dev.py, tests/test_dev.py |
| Instruction / REVIEW.md paths read | none available in the fixture; only the trusted policy line in input.md |

## Required gates

| Check | Required | Status at head | Attribution | Evidence |
|---|---|---|---|---|
| lint | yes (trusted policy) | passed | not_applicable | input.md line 14 (supplied trusted observation) |
| tests | yes (trusted policy) | passed | not_applicable | input.md line 14 (supplied trusted observation) |
| Specialist security pass | not required | not applicable | - | no trust boundary changed (see Security) |

Local commands executed: none (execution forbidden by the fixture). Green gates are taken from the supplied trusted observation, not inferred.

## Mutation

Applicable (changed decision logic: the new `if seed:` branch and its test). **Skipped: no project-pinned runner** - the fixture states mutation is optional and no mutation tool is installed; no StrykerJS/Stryker.NET config or manifest is in the supplied tree, and neither policy nor user requires it. The mutation reference was not read and nothing was installed.

## Timing

No review timing clock was collected (input.md line 9). elapsed, active review, verification and CI-wait: all unknown.

## Coverage and review mode

- Round 1, **full** review. No published or local baseline; Carried: unavailable.
- Reviewed 2 of 2 changed files:
  - src/dev.py - fully inspected (complete head content supplied, lines 1-11, with base diff description).
  - tests/test_dev.py - partial: only the supplied description of its assertion.
- Affected callees traced from supplied descriptions: `runtime.wait_ready` (untouched; behavior supplied), `post_dev_config`, `load_fixtures` (sources not supplied; their observed effect is supplied).
- Dimensions: all twelve evaluated below; skill quality not applicable (no skill body touched).

## Risk

**Low-Medium.** Local development tooling only; no deployment, credentials, CI/release or data migration change. Blast radius: every developer running `tool dev` (with or without `--seed`) alongside the frontend dev server, which the README recommends. Reversible: revert or change one constant; no irreversible state. Rollback: revert the PR; rollback of deployed behavior is not applicable because no deployed behavior changes. No extra human-scrutiny category from the protocol applies. Owner/human approver: not supplied.

## Requirements traceability

| ID | Criterion (exact text) | State | Implementation | Verification |
|---|---|---|---|---|
| R1 | "`tool dev --seed` loads local fixtures into the dev service after it starts." | partial | src/dev.py:9-10 | static trace + supplied verified observation: when port 3000 is already held (the README-recommended frontend server), fixtures go to that program, not the dev service. Supporting reason on F1, same root cause. |
| R2 | "fixtures are posted only after `wait_ready` returns" | met (literal) | src/dev.py:7 precedes 9-10 in a straight-line function | static evidence; note F1: `wait_ready` can return before the dev service is ready |
| R3 | "a test proves the order" | met (by supplied description) | tests/test_dev.py | supplied statement that the test asserts load_fixtures after wait_ready; tests passed at head. Test source not inspected. |

## Findings - blockers

### F1 `dev.port-collides-with-readiness-probe` - Minor - Blocker? Yes

- **Location / causal anchor:** `src/dev.py:4` at head bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb (changed from `PORT = 8080` at base) - verbatim head line:
  `PORT = 3000`
  Affected lines (unchanged text, now aimed at the colliding port):
  - `src/dev.py:7` `    wait_ready(port=PORT)`
  - `src/dev.py:8` `    post_dev_config("http://127.0.0.1:%d" % PORT)`
  - `src/dev.py:10` `        load_fixtures("http://127.0.0.1:%d" % PORT)` (new line)
- **Trigger / path:** Developer follows the README and keeps the frontend dev server running (default port 3000), then runs `tool dev --seed` (or plain `tool dev`). `start_service(port=3000)` is called; `wait_ready(port=3000)` succeeds immediately because `runtime.wait_ready` "returns as soon as any TCP connect to 127.0.0.1:port succeeds" and the frontend server already accepts connections; `post_dev_config` and `load_fixtures` then POST to the frontend server.
- **Expected:** config posted to and fixtures loaded into the started dev service, only once it is ready (issue + PR body "seeding waits for readiness").
- **Actual:** frontend server answers both POSTs with 404; `tool dev --seed` reports success while nothing was configured or loaded (supplied verified observation, input.md lines 36-42). Plain `tool dev` also posts its config to the wrong program - this is a regression of existing behavior, not only of the new flag.
- **Why change-introduced (rule 4 analysis):** `wait_ready`'s connect-only probe is untouched, pre-existing behavior. At base the service used 8080, which no documented tool uses, so the collision was not an ordinary-use risk. The PR moves the service to 3000, the frontend server's documented default port in the README-recommended setup, making the risk materially more likely; a changed caller makes untouched code regress, so it is admitted as a change-introduced regression and judged normally, not as a disclosed residual.
- **Severity:** Minor (team classification: local development only).
- **Materiality (peer):**
  - Security exemption: does not apply. No policy, issue or comment names this a security/trust boundary, and the baseline security pass found no untrusted source; the other listener is the developer's own frontend server. security_boundary: false.
  - Rule 2 (guard vs boundary): not a guard bypass. The trigger is not a contrived or obfuscated input; it is the README-documented default setup.
  - Rule 1 (bar): **met.** Realistic trigger in ordinary non-adversarial use - the README tells developers to run the frontend server alongside `tool dev`, and it listens on 3000 by default. Concrete consequence - dev config and fixtures are not applied (wrong output) and the command reports success (a message that leads the user to a wrong action).
  - Rule 3: not applicable (round one). Rule 5: no deferral disclosed in the PR body.
  - Result: **blocks under branch 1.** Supporting reason: R1 is only partially met (branch 2) by the same root cause; recorded on this finding, not as a second blocker. The PR-body claim "seeding waits for readiness" is not literally contradicted by the diff (`wait_ready` is called first), so branch 3 is not claimed.
- **Verification method:** complete static trace of src/dev.py at head against the supplied untouched `wait_ready` contract, plus the supplied verified observation of the misdirected POSTs and 404 responses. Counterexample pass (self, no separate verifier available/authorized): checked whether `start_service` or `wait_ready` could detect the foreign listener - the supplied contract says `wait_ready` accepts any TCP connect, and nothing in src/dev.py checks the process or the POST responses; checked whether 3000 is optional - it is hard-coded on line 4. Not executed locally (forbidden); no red/green run.
- **Reproduction steps (for the author):** at head, start any listener on 127.0.0.1:3000 (e.g. the frontend dev server), run `tool dev --seed`; observe success output while the dev service has no config/fixtures and the listener logs two 404 POSTs. Repeat at base (8080): no collision in the documented setup.
- **Remedy:** keep the dev service on a port no documented tool uses (revert to 8080 or another non-conflicting port), or, if 3000 is required, make startup fail fast when the port is already bound before `start_service`. Add a regression test that pre-binds the chosen port and asserts `tool dev --seed` fails or targets the started service. Recommended hardening (may be a follow-up since it touches untouched code): make readiness confirm the spawned service (e.g. a service-specific health response or a live `proc` check) and make `post_dev_config`/`load_fixtures` treat non-2xx responses as failure instead of reporting success. As a Minor, this may instead move to an author-opened follow-up issue only if the PR body discloses it with the issue link (rule 5); the reviewer does not open it.

## Should-fix / non-blocking findings

### F2 `pr-body.undisclosed-port-move` - Minor - Blocker? No

- **Anchor:** `src/dev.py:4` `PORT = 3000` (base: `PORT = 8080`).
- **Issue:** the PR body describes only `--seed` and readiness; the move of the dev service from 8080 to 3000 is a behavior change outside the linked issue's scope and is not mentioned, which hid the F1 risk from reviewers.
- **Why not blocking:** not a partial implementation and no PR-body claim is contradicted (branch 3 does not match); scope creep blocks only through a pipeline branch, and its runtime effect is already blocked as F1. Not a materiality-relaxed finding (description defect, not a branch-1 defect).
- **Remedy:** state the port change and its rationale in the PR body, or drop it from this PR (which also closes F1 if 8080 is restored). Independent of F1's remedy when 3000 is kept deliberately.

## Dimension results

1. Issue scope: R2/R3 met as written; R1 partial via F1. Port move is out-of-issue scope (F2).
2. Structural integrity: required lint and tests passed at head (supplied). Plain `tool dev` regresses in the documented setup (F1).
3. Stale code: whether docs/scripts reference the old dev-service port 8080 could not be checked (README text not supplied); see verification gaps.
4. Debt: introduced - hard-coded port colliding with documented tooling (F1). Closed - none.
5. Docs: no docs changed in the diff; README interaction considered in F1.
6. Conventions: no AGENTS.md/REVIEW.md supplied; nothing evaluable beyond file placement (src/, tests/ - fine).
7. Follow-up hygiene: F1 must be fixed in the PR or deferred by the author under rule 5; F2 is guidance.
8. Correctness: F1. `if seed:` branch and call order otherwise correct by static trace.
9. Security: baseline pass - no new untrusted-input path; the new code posts to a fixed 127.0.0.1 URL with no PR/user-controlled sink; no auth, secret, dependency or privilege change visible. Not a trust boundary under supplied evidence. Specialist pass not triggered.
10. Tests: order assertion is a valid interaction assertion for the DoD protocol, but no test covers an occupied port or a foreign listener (folded into F1 remedy). Mutation skipped: no project-pinned runner.
11. Skill quality: not applicable - no skill bodies touched.
12. PR description: linked issue reference present; F2.

Focused lenses: errors/fallbacks applied (success reported despite 404 - part of F1); type invariants not applicable (no type changes); comments not applicable (no comments in changed code); test resilience applied (dimension 10).

## Propagation sweep

Class `dev.port-collides-with-readiness-probe` (one finding, one fix point: the port choice / readiness identity). Search: full read of src/dev.py at head for every use of `PORT` and every POST to the dev URL. Instances: src/dev.py:7, src/dev.py:8, src/dev.py:10 (all driven by src/dev.py:4). tests/test_dev.py not searchable (content not supplied) - sweep is **partial** for that file. Untouched callers of `wait_ready` elsewhere in the repository were not supplied and are outside this change's causal path.

## Verification gaps

- G1 (non-material): `wait_ready` timeout behavior (raise vs silent return after 30 s) not supplied; R2 holds literally either way.
- G2 (non-material for the verdict): README text, docs referencing port 8080, and `post_dev_config` payload contents not supplied; whether the misdirected config carries anything sensitive was not verified (hypothesis only, not a finding).
- G3: tests/test_dev.py source not inspected; R3 rests on the supplied description.
- G4: no review.json, validator, anchor verifier or skill fingerprint (execution forbidden). Anchors above were checked by hand against the supplied head content of src/dev.py only.

## Out-of-scope observations

- `runtime.wait_ready` treats any TCP connect as readiness (untouched code). Independent of this PR's port choice it can be fooled by any foreign listener; consider a follow-up issue to probe a service-specific health endpoint.

## Carried

Unavailable - round one, no qualified first-pass baseline.

## To finish the review

Supply tests/test_dev.py, the README and AGENTS/REVIEW.md context, then rerun with execution permitted to compute the skill fingerprint, build review.json, and run the validator and anchor verifier against head bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb.
