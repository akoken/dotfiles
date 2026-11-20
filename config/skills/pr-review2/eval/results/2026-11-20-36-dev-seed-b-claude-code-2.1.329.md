reviewer: pr-review2
skill-version: 2.11.0
candidate-sha256: 9398fd9497fbcc122a6903318639aeed88baf66fd7f62223adafc9a2407490c0
case: 36-dev-seed-b
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: PASS
- Expected: Expected negative verdict; residual exception does not apply when the change makes the risk materially more likely.
- Observed: Not ready to merge; F1 Minor Blocker? Yes: root partly in unchanged wait_ready, but the port move makes the risk materially more likely and more severe, so judged normally and passes the bar. Extra F2 (PR body does not disclose the port move), Minor, Blocker? No.
- False blockers: 0. Harmful false positives: 0.
- Tool policy: offline fixture; one fresh-context Claude Code subagent per case, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus that case's input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: single run, scored after the run against the hidden oracle. Extra finding F2 is a plausible, non-blocking orientation gap (the PR body omits the port move); not a false blocker.

## Raw reviewer output

# PR Review 2 - offline fixture 36-dev-seed-b (peer mode)

## Verdict

**Not ready to merge.** 2 verified findings, 1 blocker.

- F1 (Minor, **Blocker? Yes**): with `PORT = 3000`, the README-recommended frontend dev server already listens on the dev port, `wait_ready` returns at once, and `tool dev --seed` posts the fixtures to the frontend (404) while reporting success. This passes the peer materiality bar.
- F2 (Minor, Blocker? No): the PR body does not disclose the dev-service port move from 8080 to 3000.

No Maintainer decision item applies.

## Skill and reviewer identity

- Skill: `pr-review2`, metadata.version `2.11.0`.
- Package fingerprint: **not computed**. The fixture rules forbid program execution, so `scripts/review_record.py --skill-fingerprint` could not run, and the value was not copied from anywhere.
- Reviewer host: Claude Code (agent CLI). Model family: `claude`.

## Run status

- Not computed. This is a fixture-only exercise: no review.json was built and the validator was not run, as the fixture instructs ("Do not invent metadata or review.json"). No review.json or validator-output.txt path exists.
- Without validator output I can't report a run state. The known incompleteness sources are listed under Coverage and Verification gaps.

## Subject

- PR: offline synthetic fixture. No URL, number or title was supplied.
- Linked contract: the linked issue reference is present. Issue text: "`tool dev --seed` loads local fixtures into the dev service after it starts." DoD: "fixtures are posted only after `wait_ready` returns; a test proves the order."
- PR body (untrusted task data): "Closes the linked issue. Adds --seed to `tool dev`; seeding waits for readiness."
- Base: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- Head: `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`
- Patch digest: not applicable (commit input).
- Instruction/REVIEW.md paths: none supplied. Root AGENTS.md, cli/shared/AGENTS.md and any REVIEW.md were not available in the fixture, so I could not load them.

## Required gates at head

| Check | Required | Status at head | Attribution | Evidence |
|---|---|---|---|---|
| lint | yes (trusted policy) | passed | not applicable | Trusted fixture statement: "required checks are lint and tests; both passed at head" |
| tests | yes (trusted policy) | passed | not applicable | Same statement |

- Commands run locally: none, because execution is forbidden for this exercise.
- Branch 6 (introduced required-gate failure) does not apply.
- A green `tests` run does not cover the occupied-port scenario in F1.

## Timing

No review timing clock was collected. Active review, verification and CI-wait times are unknown (null).

## Mutation

- Applicability: applicable, because the PR changes decision logic (`if seed:` and the readiness ordering).
- Status: **skipped: no project-pinned runner.** The fixture states mutation is optional and no mutation tool is installed. No StrykerJS or Stryker.NET dependency, manifest entry or config was supplied, and no policy or user requirement makes mutation mandatory.
- I did not read the mutation reference or install a runner. Outcome counts: none.

## Coverage and review mode

- Round 1, full review. The first-pass published baseline does not exist: this is the first round.
- Changed files reviewed: 2 of 2.
  - `src/dev.py`: reviewed in full from the supplied complete head content (lines 1-9), against the supplied base facts (lines 1, 5, 6 and 9 identical; line 3 was `PORT = 8080`).
  - `tests/test_dev.py`: **partially inspected.** Only the trusted summary was supplied ("asserts load_fixtures runs after wait_ready"); the test source was not available verbatim.
- Affected callees traced:
  - `runtime.wait_ready` (untouched): supplied contract `wait_ready(port, timeout=30)` returns on the first successful TCP connect to `127.0.0.1:port`.
  - `runtime.start_service` and `seed.load_fixtures` (untouched): bodies not supplied.
- The CLI caller that maps `tool dev --seed` to `dev(seed)` was not supplied. The verified E2E observation shows the flag reaches seeding.
- Dimensions (all twelve):
  1. Issue scope: R1 partial (F1). The port move is outside the issue's stated intent (F2).
  2. Structural integrity: required lint and tests passed at head. The `dev()` command behavior changed its port (F2). No targeted local run was possible.
  3. Stale code: no removed or renamed modules. The README and other references to the old port 8080 were not supplied, which is a gap.
  4. Debt: debt introduced is F1's readiness/identity gap. No debt closed.
  5. Docs: no docs changed in the diff. The README frontend-port statement is the trigger evidence for F1.
  6. Conventions: project AGENTS.md was not supplied. No convention violation is evidenced.
  7. Follow-up hygiene: F1 must be fixed in this PR or deferred under rule 5 by the author. F2 is a suggestion.
  8. Correctness: F1.
  9. Security: see the Security section.
  10. Tests: the order test is valid for the DoD ordering contract but misses the occupied-port case (part of the F1 remedy).
  11. Skill quality: not applicable, no skill bodies touched.
  12. PR description: linked issue present. Port move undisclosed (F2).
- Focused lenses:
  - Errors/fallbacks: applied (the success report after a 404, see F1 and the Out-of-scope observations).
  - Type invariants: not applicable, no type construction changes.
  - Comments/docs: applied, no comments in the diff. The PR-body readiness claim was checked.
  - Test resilience: applied. The order assertion protects a stated protocol (DoD), so it is valid.

## Risk

- **Low.** Local development tooling only; no auth, billing, credentials, CI/release or migration surface.
- Blast radius: developers who run `tool dev --seed` with the frontend dev server on its default port 3000. This is the workflow the README recommends.
- Reversible: revert the commit, or change `PORT`.
- No deployment behavior changes, so rollback evidence is not applicable.
- No extra human scrutiny is required beyond normal review. Approval counts and owner were not supplied.

## Findings

### Blockers

#### F1 - `dev.seed-target-identity`: seeding posts to whatever already listens on port 3000

- **Location:** `src/dev.py`
  - Causal changed line 3: `PORT = 3000`
  - Effect line 8: `        load_fixtures("http://127.0.0.1:%d" % PORT)`
- **Severity:** Minor (team impact classification: local development only; I verified the impact below).
- **Blocker?** **Yes.**
  - Branch 1: a reachable regression introduced by the change. It passes materiality rule 1.
  - Supporting reason, branch 2: issue requirement R1 is only partially met.
  - Both reasons are recorded on this one finding, as one root cause.
- **Trigger/path:**
  1. A developer follows the README and keeps the frontend dev server running. That server listens on port 3000 by default.
  2. They run `tool dev --seed`, which calls `dev(seed=True)`.
  3. `start_service(port=3000)` runs.
  4. `wait_ready(port=3000)` (untouched `src/runtime.py`) returns on the first successful TCP connect to `127.0.0.1:3000`. The frontend server satisfies that at once.
  5. `load_fixtures("http://127.0.0.1:3000")` posts the fixtures to the frontend server.
- **Expected:** fixtures are loaded into the dev service after it is ready (issue text). The PR body says "seeding waits for readiness".
- **Actual:**
  - The frontend server answers the fixture POSTs with 404.
  - `tool dev --seed` reports success.
  - No fixtures are loaded into the dev service.
  - Evidence: supplied verified observation.
- **Causal anchor:**
  - At base, `PORT = 8080` did not collide with the README-recommended frontend port, and base `dev()` posted no fixtures.
  - The PR adds seeding (lines 2, 7-8) and moves the port to 3000 (line 3).
  - Together these turn `wait_ready`'s any-listener check into a wrong-target data write.
- **Materiality (peer rules):**
  - Rule 1, bar met:
    - Realistic trigger in ordinary, non-adversarial use: the README itself tells developers to run the frontend server alongside `tool dev`, and that server takes port 3000 by default. No crafted input is needed.
    - Concrete consequence: the fixtures are not loaded (missing data), and the command reports success. That message leads the developer to a wrong action: working against an unseeded service while believing it is seeded.
  - Rule 2: not applicable. This is no contrived bypass of a convenience guard; the trigger is the documented default setup.
  - Rule 3: not applicable (round one).
  - Rule 4: does not relax it.
    - The root is partly the unchanged `wait_ready` readiness probe in untouched `src/runtime.py`. But the change makes the risk materially more likely and more severe.
    - More likely: the port move creates a collision in the documented default workflow.
    - More severe: the new seeding step turns an early return into misdirected writes plus a false success.
    - This is therefore change-introduced and judged normally.
  - Rule 5: no follow-up issue is disclosed in the PR body, so deferral does not apply.
- **Counterevidence checked:**
  - The DoD ordering is literally met: line 6 `wait_ready` precedes line 8 `load_fixtures`, and the test asserts that order. Ordering does not establish that the ready listener is the dev service.
  - Required lint and tests passed. Per the supplied test description, the test does not exercise a pre-occupied port.
  - Whether `start_service` fails or keeps running when port 3000 is taken is not supplied (gap G2). Either way, the verified observation shows the misdirected seeding and the false success.
- **Verification method:**
  - Static trace of the supplied complete `src/dev.py` and the supplied `wait_ready` contract.
  - The supplied verified E2E observation.
  - No local reproduction (execution forbidden). Regression red/green is unverified.
- **Remedy (any of these closes the class; fix every instance):**
  1. Make readiness specific to the started service. For example, wait on a dev-service health endpoint that identifies the service, or tie readiness to `proc`. Alternatively, fail fast with a clear error when the port is already in use before `start_service`.
  2. Or keep a port that does not collide with the frontend default: revert to 8080 or make it configurable. This alone leaves the any-listener probe fragile.
  3. Make `tool dev --seed` report failure when fixture POSTs are not accepted (non-2xx), so a misdirected seed cannot report success.
  4. Add a regression test that pre-binds a listener on the dev port and asserts that seeding does not report success against it.
- **Class sweep:**
  - `dev.seed-target-identity`, one instance: `src/dev.py:3` with effect at `src/dev.py:8`.
  - Search: the full reviewed diff, 2 files. `tests/test_dev.py` was inspected only by summary.
  - The sweep is partial for callers whose source was not supplied (CLI wiring, `runtime`, `seed`).

### Should-fix (non-blocking)

None relaxed by the materiality rules.

### Other non-blocking findings

#### F2 - `pr-body.undisclosed-change`: port move from 8080 to 3000 not described

- **Location:**
  - `src/dev.py` line 3: `PORT = 3000`
  - PR body: "Adds --seed to `tool dev`; seeding waits for readiness."
- **Severity:** Minor (Check 12: a significant changed area not described; also outside the issue's seed-only intent).
- **Blocker? No.** The body makes no claim that the diff contradicts, and the issue reference is present. Scope creep and undisclosed orientation gaps block only through a pipeline branch, and none matches.
- **Expected:** the PR body discloses the user-visible change of the dev-service port and why.
- **Actual:** the body mentions only `--seed` and readiness.
- **Verification:** static comparison of the PR body with the supplied diff facts.
- **Remedy:** describe the port change and its reason in the PR body, or drop it from this PR. If F1 is fixed by reverting to 8080, this finding goes away.

## Requirements traceability

| ID | Text | State | Implementation | Verification |
|---|---|---|---|---|
| R1 | "`tool dev --seed` loads local fixtures into the dev service after it starts." | partial | `src/dev.py:7-8` | Static trace plus the supplied verified observation: met when port 3000 is free, unmet in the README-recommended setup (F1) |
| R2 | "fixtures are posted only after `wait_ready` returns" | met | `src/dev.py:6-8` | Static (line order) plus the required `tests` check passed at head |
| R3 | "a test proves the order" | met | `tests/test_dev.py` | Supplied trusted description of the test plus `tests` passed at head. Test source not inspected verbatim (G1) |

## Security

- Baseline pass:
  - No new untrusted-input path. Fixture data goes from the local repository to `127.0.0.1` only.
  - No auth, secret, dependency or privilege change.
- Misdirected local POSTs reach another process of the same developer. No trust boundary is named in the supplied evidence, so this is a correctness defect (F1), not a vulnerability.
- No specialist pass is required.
- SECURITY.md was not supplied.

## Verification gaps

- G1: the `tests/test_dev.py` source was not supplied. The test assertion is known only by summary. Material for full assurance of R3's evidence form.
- G2: `runtime.start_service` behavior on an occupied port, the `seed.load_fixtures` success/error handling, and the CLI wiring of `--seed` were not supplied. This does not change F1, which rests on the verified observation.
- G3: project AGENTS.md, REVIEW.md, SECURITY.md and README references to the old port were not supplied.
- G4: no execution was allowed:
  - no local reproduction or red/green regression evidence for F1;
  - the skill fingerprint was not computed;
  - no validator or anchor verifier was run;
  - the anchors above are quoted from the supplied head content but not mechanically verified.

## Out-of-scope observations

1. `src/runtime.py` `wait_ready` treats any TCP listener as readiness for every caller. This is base behavior. The author or maintainer may want a follow-up issue for an identity-aware readiness probe, beyond what F1 needs.
2. The component that reports `tool dev --seed` success after 404 responses lies in code not supplied for review. If it lives in untouched `seed.load_fixtures`, swallowing non-2xx responses is a pre-existing hardening gap worth a follow-up issue.

## Carried

None. This is the first round, so there is no qualified baseline.

## Propagation sweep

- `dev.seed-target-identity`: searched the 2 changed files and found 1 instance (`src/dev.py:3`, effect at `:8`). Untouched callees were checked only through supplied contracts.
- Legacy left: the `wait_ready` any-listener probe.
- Debt introduced: seeding depends on that probe.
- Debt closed: none.
