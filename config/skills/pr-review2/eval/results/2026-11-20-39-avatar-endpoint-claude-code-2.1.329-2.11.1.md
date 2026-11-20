reviewer: pr-review2
skill-version: 2.11.1
candidate-sha256: f79409f6f0e85c3aaeaaef8d089ae86847ad7b85ea9dbe26f220a95758b87609
case: 39-avatar-endpoint
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: PASS
- Observed: Not ready to merge; ../ traversal outside AVATAR_DIR is Minor, Blocker? Yes under the security exemption (SECURITY.md boundary); not relaxed as immaterial or guard bypass. Run status incomplete on material gaps (test source not supplied).
- Tool policy: offline fixture; one fresh-context Claude Code subagent per case, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus that case's input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: run 1 at 2.11.1, scored after the run against the hidden oracle.

## Raw reviewer output

# PR Review 2 - avatar endpoint (offline synthetic fixture)

## Verdict

**Not ready to merge** - 1 verified finding, 1 blocker.

The new `GET /avatars?name=<file>` handler lets a cross-tenant caller read files outside
`AVATAR_DIR` with a `../` name. That breaks the trust boundary that the trusted base
SECURITY.md defines. The team rates the impact Minor, but the security exemption still
makes it block under branch 1.

Run status: **incomplete** (see Run status and completeness). This status is not
validator-computed: the fixture forbids creating review.json or running the validator.

## Skill and reviewer identity

- Skill: `pr-review2`, metadata.version `2.11.1`.
- Package fingerprint: **not computed**. The fixture forbids program execution, and the
  fingerprint comes from `scripts/review_record.py --skill-fingerprint` or the equivalent
  shasum pipeline. I did not copy a value from anywhere.
- Reviewer host: Claude Code (Claude Agent SDK). Model family: `claude`.
- Mode: AURA peer mode, fixture-only exercise. This is not a live AURA PR review.

## Subject and contract

- PR: offline synthetic fixture. The fixture gives no URL, title, author or PR number, and
  I did not make any up.
- Base: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- Head: `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`
- Patch digest: not applicable (commit-to-commit input, not dirty input).
- Linked contract: resolved. The PR body says "Closes the linked issue", and the fixture
  states that the linked issue reference is present.
  - Issue: the avatar service adds `GET /avatars?name=<file>`, which returns that avatar file
    from `AVATAR_DIR`.
  - DoD: an existing avatar is returned; a missing one yields 404; tests.
- PR body (task data): "Closes the linked issue. Adds the endpoint and rejects absolute names."
- Instruction / policy files: the trusted base `SECURITY.md` text supplied in the fixture.
  The fixture supplies no AGENTS.md, cli/shared/AGENTS.md or REVIEW.md, so none was loaded.
  This is recorded as a context gap.

## Required gates at head

| Gate | Required | State at head | Attribution | Evidence |
|---|---|---|---|---|
| lint | yes (trusted policy) | passed | not applicable | Supplied trusted policy statement |
| tests | yes (trusted policy) | passed | not applicable | Supplied trusted policy statement |
| Specialist security pass (review-plan pass, diff changes an untrusted-input-to-file sink) | review-plan pass | complete at head | n/a | Supplied trusted observation; its only result is the traversal observation below |

- Requiredness comes from the supplied trusted policy: required checks are lint and tests.
- I ran no commands locally, as the fixture forbids execution. I also inferred no gate state
  beyond what the fixture supplies.
- A passing lint/test result does not stand in for the security result. That result was
  supplied separately and is integrated below.

## Mutation testing

The changed decision logic (`get_avatar` guards) makes mutation applicable. It was
**skipped: no project-pinned runner**. The fixture says mutation is optional and no
mutation tool is installed. Policy does not require it, so the mutation reference was not
read and no runner was installed.

## Timing

No review timing clock was collected. Active review, verification and CI-wait time are
all **unknown**.

## Coverage

- Review round 1, **full** pass (as the fixture states). Baseline: none (first review).
  There is no published first-pass baseline and no latest reviewed SHA.
- Changed files: 2.
  - `src/avatars.py`: **reviewed** in full. The fixture supplies the complete new file, 10
    lines.
  - `tests/test_avatars.py`: **partially inspected**. Only the fixture's summary was
    available: the tests cover a plain existing name and a missing name. Its source and
    assertions were not supplied.
- Reviewed 1 of 2 changed files fully; 1 of 2 only from a summary.
- Caller: the fixture states that the route passes the query value as `name`. The route
  source itself was not supplied.

### Dimensions

| # | Dimension | Result |
|---|---|---|
| 1 | Issue scope | All three DoD items have an implementation and CI-backed tests. No scope creep (2 files, both in scope). |
| 2 | Structural integrity | Required lint/tests passed at head. The change is a new module, with no evidence of a broken existing surface. |
| 3 | Stale code | Not applicable: nothing removed or migrated. |
| 4 | Debt | Debt introduced: none beyond F1. Debt closed: none. |
| 5 | Docs accuracy | Not applicable: no docs changed. |
| 6 | Conventions | Not assessable: no AGENTS.md/REVIEW.md was supplied (context gap). |
| 7 | Follow-up hygiene | F1 is a security-boundary blocker. It must be fixed in this PR, never deferred. |
| 8 | Correctness | Traced `get_avatar` for plain, missing, absolute, empty and `../` names. Only `../` gives a wrong result (F1). |
| 9 | Security | Baseline pass plus the supplied specialist result. F1 is verified. |
| 10 | Tests | No traversal / confinement test. This is folded into F1's remedy because it has the same root cause and fix point. |
| 11 | Skill quality | Not applicable: no skill bodies touched. |
| 12 | PR description | Issue reference present. The claim "rejects absolute names" is true (line 4). See Observations. |

## Risk

**High.** The change adds a new untrusted-input-to-filesystem-read path in a service that
SECURITY.md says other tenants' services can reach. That is a tenant/trust-boundary
surface, which requires explicit human scrutiny of the confinement check.

- Blast radius: any caller of the avatar endpoint, including other tenants.
- Reversibility: high. The change is a new read-only endpoint with no evidenced persistent
  state changes, so rollback is a revert of the PR.
- Flags, rollout and monitoring: no evidence supplied; none assumed.
- Unresolved limit: today's confinement of the escape depends on the container layout (only
  `/srv/app` exists), not on the code. A different deployment layout would widen the impact.

## Findings

### Blockers

#### F1 - `avatars.read-confinement`: `name` with `../` escapes `AVATAR_DIR`

- Location: `src/avatars.py`. Anchors (verbatim head lines):
  - `    if name.startswith("/"):` (line 4)
  - `    path = os.path.join(AVATAR_DIR, name)` (line 6)
  - `    with open(path, "rb") as stream:` (line 9)
- Severity: **Minor**.
  - The verified impact is a read of non-secret display settings inside `/srv/app`. The
    supplied observation shows that no deeper `../` leaves that tree and no secret is
    reachable. This matches the team's classification.
  - The project-check table suggests Critical for a reachable traversal. Blocking does not
    depend on that choice.
- Blocker? **Yes**, under branch 1 (a reachable security defect introduced by the change)
  through the **security exemption**. Materiality rules 1, 2, 3 and 5 do not relax it:
  - Guard versus boundary, deciding evidence (rule 2.1): the trusted base SECURITY.md names
    this a trust boundary. It says "The avatar service is reachable by other tenants'
    services. Every request parameter is untrusted. File handlers must confine reads to
    their own directory."
  - The baseline security pass agrees (rule 2.2). An untrusted cross-tenant caller can make
    the service read and return a file outside the avatar directory, which that caller
    cannot otherwise do.
  - Under the exemption, crafted attacker input is a realistic trigger, and the read outside
    the directory is a concrete boundary effect. "Ordinary clients send plain names" and
    "no secret is reachable" therefore do not relax it.
  - It must be fixed in this PR, not deferred to a follow-up issue.
  - Record: `security_boundary: true`, no `non_blocking`, origin `change`, blocking reason
    `introduced_defect`.
- Trigger / path: `GET /avatars?name=../config/display.json` -> route passes the query value
  as `name` -> line 4 passes (no leading `/`) -> line 6 builds
  `/srv/app/avatars/../config/display.json` -> line 7 `isfile` is true -> line 9 opens and
  returns `/srv/app/config/display.json`.
- Expected: reads confined to `AVATAR_DIR`. A name that resolves outside it gets a 404 (or
  a rejection), as SECURITY.md requires.
- Actual: the file outside the directory is returned. This was confirmed by the supplied
  verified observation from the specialist security pass at head.
- Causal anchor: line 4 is the only guard, and it rejects only absolute names. Line 6 joins
  the raw value without normalizing it or checking containment. The file is new in this PR,
  so the defect is change-introduced (not present at base).
- Counterevidence checked:
  - The absolute-name guard does not cover relative traversal.
  - `os.path.isfile` checks existence, not containment.
  - No upstream validation of `name` is evidenced (the route passes the query value through).
  - The tests cover only a plain name and a missing name.
- Verification method:
  - Static trace of the complete supplied `src/avatars.py`.
  - The supplied trusted specialist observation (head) reproducing the read of
    `/srv/app/config/display.json`.
  - Counterexample pass done by me (no separate verifier, as delegation is forbidden). I
    found no input path or guard that would stop `../`.
- Remedy (covers every instance plus copies):
  - Confine on the resolved path. Compute
    `base = os.path.realpath(AVATAR_DIR)` and
    `target = os.path.realpath(os.path.join(base, name))`, then raise `NotFound()` unless
    `os.path.commonpath([base, target]) == base` and `target != base`.
    - Using `realpath` also closes the symlink variant: a link inside `avatars/` that points
      elsewhere.
  - Alternatively or additionally, accept only plain file names, for example reject
    `name != os.path.basename(name)` or use a strict allowlist pattern. This matches what
    ordinary clients send.
  - Add regression tests for `../config/display.json`, `a/../../config/display.json` and a
    symlink pointing outside the directory. Each must yield 404.
  - The PR body's "rejects absolute names" may then be broadened to describe confinement.
- Class / instances: `avatars.read-confinement`. One instance:
  `src/avatars.py:6` (join at line 6, guard at line 4, sink at line 9).

### Should-fix (relaxed by materiality rules)

None.

### Optional suggestions

None.

## Propagation sweep

- Class `avatars.read-confinement`: read the full reviewed diff (`src/avatars.py` complete,
  and the test summary) for every path built from request input that reaches a filesystem
  sink.
- Files covered: `src/avatars.py`, fully. `tests/test_avatars.py` was covered only by its
  summary and contains no production sink.
- Instances found: 1 (`src/avatars.py:6`).
- Variants considered under the same fix point:
  - `a/../../x` style names.
  - Symlinks inside the avatar directory.
  - Repeated `../` (the observation says it stays in `/srv/app`).
  - Percent-encoded dots. Whether the route decodes them before passing `name` is not
    evidenced. The resolved-path remedy covers this either way.
- This is the first instance, so no second-instance sweep trigger applies.
- Legacy left: none. Debt introduced: F1 only.

## Requirements traceability

| ID | Criterion | State | Implementation | Verification |
|---|---|---|---|---|
| R1 | An existing avatar is returned | met | `src/avatars.py` lines 6-10 | Required `tests` passed at head; it covers a plain existing name (CI, per supplied policy) |
| R2 | A missing one yields 404 | met (CI) with a disclosed limit | `src/avatars.py` lines 7-8 | Required `tests` passed at head; it covers a missing name. Limit: the test assertions were not supplied, and see gap G2 |
| R3 | Tests | met | `tests/test_avatars.py` | Present and passing at head (summary only) |

The issue text does not state confinement as a DoD item. F1 is admitted through the changed
lines and the trusted SECURITY.md trust boundary, not as an unmet DoD.

## Verification gaps

- **G1 (material, cause: environment)** - The source of `tests/test_avatars.py` was not
  supplied, so its assertions could not be inspected (for example, whether the missing-name
  test asserts a 404 status).
- **G2 (non-material, cause: environment)**
  - The supplied file is described as the complete `src/avatars.py`. It uses `NotFound` at
    lines 5 and 8 without importing or defining it.
  - If nothing injects it, raising it would be a `NameError` (likely a 500, not a 404).
  - Counterevidence: the required tests passed at head and are stated to cover a missing
    name, so the binding probably comes from somewhere I cannot see (the route or framework
    module, a test harness, or an abridged fixture). Neither the route module nor the test
    source was supplied.
  - Not a verified finding. Please confirm that `NotFound` is imported in the real module.
- **G3 (material, cause: other - fixture instruction)**
  - The fixture forbids constructing review.json and running the validator and the anchor
    verifier.
  - Run status and anchor quotes are therefore not mechanically verified. I copied the
    quotes verbatim from the supplied head file.
- **G4 (non-material, cause: environment)** - No AGENTS.md, cli/shared/AGENTS.md or
  REVIEW.md was supplied, so dimension 6 (conventions) could not be assessed.
- **G5 (non-material, cause: other - fixture instruction)** - The skill package fingerprint
  was not computed because program execution is forbidden.

## Run status and completeness

- State: **incomplete**. This is my assessment, not validator output, because no
  review.json or validator-output.txt exists by fixture instruction. No paths are kept.
- Reasons:
  - G1: test source not supplied (environment).
  - G3: record, validator and anchor verifier not run (other: fixture instruction, "Do not
    invent metadata or review.json" plus no program execution).
  - Context gap G4 (environment).
- approved_scope_status: not applicable. No narrower scope was approved; the fixture asked
  for a full review of the supplied input.
- Stopped: no.
- To finish the review, supply or read `tests/test_avatars.py` at head and the route module.
  Then build review.json (profile aura-peer) and run `scripts/review_record.py` and
  `scripts/verify_anchors.py` against the head in an isolated checkout.
- The verified blocker justifies the negative verdict independently of these gaps.

## Re-review status

First round. No prior findings, no published baseline, no reviewer-identity comparison.

## Out-of-scope observations

1. The PR body is a one-line summary with no test plan for a logic-bearing endpoint.
   - It is non-blocking. A short test plan (cases covered, including the traversal cases
     after the F1 fix) would help reviewers.
   - There is no admissibility anchor, since the body's claim is true, so it is not a
     finding.

Overflow: 0.

## Carried

Unavailable: there is no qualified first-pass baseline (round one).

## Maintainer decision items

None.
