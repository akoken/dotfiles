reviewer: pr-review2
skill-version: 2.11.1
candidate-sha256: f79409f6f0e85c3aaeaaef8d089ae86847ad7b85ea9dbe26f220a95758b87609
case: 36-dev-seed-b
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: PASS
- Observed: Not ready to merge; F1 Minor Blocker? Yes: the port move to 3000 makes the base-rooted risk materially more likely, so it is judged as change-introduced and meets the bar; F2 PR-body omission, Blocker? No.
- Tool policy: offline fixture; one fresh-context Claude Code subagent per case, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus that case's input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: run 2 at 2.11.1 on the corrected fixture (see the run 1 result for this case), scored after the run against the hidden oracle.

## Raw reviewer output

# PR Review 2 - offline fixture review (36-dev-seed-b)

**Verdict: Not ready to merge** (REQUEST_CHANGES)

2 verified findings, 1 blocker:

- F1 (Minor, **Blocker? Yes**): moving the dev service to port 3000 makes `tool dev` and
  `tool dev --seed` post their config and fixtures to the frontend dev server that the README
  tells developers to keep running on that port. The command then reports success, but
  nothing was configured or loaded.
- F2 (Minor, Blocker? No, should-fix): the PR moves the port without saying so in the PR
  body, and the move is outside the linked issue's scope.

## Skill and reviewer identity

- Skill: `pr-review2`, metadata.version `2.11.1`.
- Package fingerprint: **not computed**. The fixture allows no script or program execution,
  so `review_record.py --skill-fingerprint` (or the equivalent shasum pipeline) could not run
  on `skill/`. No value is copied from elsewhere.
- Reviewer host: Claude Code (agent CLI). Model family: `claude`.

## Run status

- No `review.json` was built and no validator ran. The fixture says not to invent metadata
  or review.json, and execution is not allowed. Run status therefore has no validator output,
  and this report does not claim one. No `review.json` or `validator-output.txt` paths exist.
- If a validator ran on this evidence, I would expect run status to be **incomplete**, for these
  reasons (not computed):
  - `environment`: root `AGENTS.md`, `cli/shared/AGENTS.md`, directory instructions and
    `REVIEW.md` files were not supplied, so context is incomplete.
  - `environment`: `tests/test_dev.py` and the unchanged parts of `src/cli.py` were known only
    from the fixture's trusted description, not from source text.
  - `environment`: the skill fingerprint was not computed.
- Stopped: no. The review covered every dimension planned for the supplied evidence.
- The proven blocker justifies the negative verdict even though coverage is incomplete.

## Subject

- Mode: AURA peer, offline synthetic fixture. This is not a live AURA PR review.
- PR URL/number/title: not supplied.
- Linked contract: the issue that the PR body closes ("Closes the linked issue"). Its text is
  in the requirements table below.
- Base: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- Head: `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`
- Patch digest: not applicable (commit input, not dirty).
- Instructions/REVIEW.md read: none supplied. The only instructions applied are the trusted
  policy line in `input.md`.

## Required gates

| Check | Required | Status at head | Attribution | Evidence |
|---|---|---|---|---|
| lint | yes (trusted policy) | passed | not applicable | `input.md`: "required checks are lint and tests; both passed at head" |
| tests | yes (trusted policy) | passed | not applicable | same line |
| mutation | no (optional per fixture) | applicable, skipped: no project-pinned runner | - | `input.md`: "Mutation is optional and no mutation tool is installed" |
| security specialist pass | not required | not triggered | - | No trust boundary changes (see Security) |

- Commands run locally: none (execution not allowed).
- Passing tests do not cover the port-collision scenario (see F1).

## Timing

No review clock was collected (fixture statement). Active review, verification and CI-wait
time are all **unknown**.

## Mutation

The changed decision logic (`if seed:` in `src/dev.py`) is in scope, so mutation applies.
It was **skipped: no project-pinned runner** (no StrykerJS/Stryker.NET or other runner shown
in the reviewed tree) and policy does not require it. I did not read the mutation reference
and did not install a runner. Outcome counts: none.

## Coverage

Reviewed 3 of 3 changed files. Mode: round one, full.

| File | Inspection |
|---|---|
| `src/dev.py` | Full new file (lines 1-11) with the base comparison supplied |
| `src/cli.py` | Changed lines 21 and 34 plus the base form of line 34. The fixture states it is the only caller of `dev()`. Other lines were not supplied. |
| `tests/test_dev.py` | Only the fixture's description of its assertions was available, not its source |

- Affected untouched code traced: `src/runtime.py` `wait_ready`, from its supplied
  behavior. `seed.load_fixtures` and `config.post_dev_config` were not supplied. Only their
  observed effect (POST to the port, success reported after a 404) is known.
- Partial inspection: `src/cli.py` (outside the changed lines) and `tests/test_dev.py` (source).

## Risk

**Low.** The change affects only local development tooling, with no production deployment,
auth, billing, credentials, CI/release or migration surface. Blast radius: every developer who
runs `tool dev` or `tool dev --seed` with the README-documented frontend server running.
Reversible: reverting the PR restores port 8080 and the old call. Rollback is a code revert,
and no persistent production state is involved. No extra human scrutiny is required beyond
normal review. Unresolved limit: whether `start_service` itself fails or warns when port 3000
is already taken was not supplied (see Verification gaps).

## Review round

Round 1, full pass. There is no prior published baseline, so there are no carried items, no
re-review blocker statuses and no `present_at_previous_head` values.

## Requirements traceability

| ID | Criterion (exact text) | State | Implementation | Verification |
|---|---|---|---|---|
| R1 | "`tool dev --seed` loads local fixtures into the dev service after it starts." | **partial** | `src/cli.py:21`, `src/cli.py:34`, `src/dev.py:9-10` | Static trace plus the fixture's verified observation. It holds when port 3000 is free. In the README-documented setup (frontend dev server on 3000), the fixtures go to the frontend server, not the dev service. Same root cause as F1. |
| R2 | DoD: "fixtures are posted only after `wait_ready` returns" | met | `src/dev.py:7` precedes `src/dev.py:9-10` | Static (call order). The test asserts it (description) and the tests gate passed at head. |
| R3 | DoD: "a test proves the order" | met | `tests/test_dev.py` (described) | The test asserts `load_fixtures` runs after `wait_ready` (trusted description), and the tests gate passed at head. Source not inspected. |

R2 and R3 are met as written. Calling `load_fixtures` after `wait_ready` does not ensure
the dev service is the program that answered, and that gap is F1.

## Findings - blockers

### F1 - `src/dev.py` dev port collides with the documented frontend server; config and fixtures reach the wrong program

- **ID:** `dev.port-readiness-target` (stable: `src/dev.py`, readiness/target-identity invariant,
  `tool dev` config and seeding)
- **Location / causal anchor:** `src/dev.py:4`, quote `PORT = 3000` (was `PORT = 8080` at base).
  Supporting lines in the same file: `src/dev.py:7` `    wait_ready(port=PORT)` (unchanged) and
  `src/dev.py:10` `        load_fixtures("http://127.0.0.1:%d" % PORT)` (new).
- **Severity:** Minor (team classification: local development only).
- **Blocker? Yes.** Mainly branch 1: a reachable regression defect introduced by the change
  that passes the materiality bar. Supporting branch 2: R1 is only partially met. This is one
  finding with one blocker, because both reasons share one root cause.
- **Trigger / path:** The developer follows the README and keeps the frontend dev server
  running (it listens on port 3000 by default), then runs `tool dev` or `tool dev --seed`.
  `src/cli.py:34` calls `dev(seed=args.seed)`, then:
  1. `start_service(port=3000)` runs (`src/dev.py:6`).
  2. `wait_ready(port=3000)` (`src/runtime.py`, untouched) returns as soon as any TCP connect to
     127.0.0.1:3000 succeeds. The frontend server already accepts connections, so it returns at once.
  3. `post_dev_config("http://127.0.0.1:3000")` (`src/dev.py:8`) and, with `--seed`,
     `load_fixtures("http://127.0.0.1:3000")` (`src/dev.py:10`) POST to the frontend server.
- **Expected:** The dev config is posted to the dev service, and with `--seed` the fixtures are
  loaded into the dev service after it is ready (linked issue). Plain `tool dev` keeps working as
  it did at base.
- **Actual:** Per the verified observation, the frontend server answers the POSTs with 404, and
  `tool dev --seed` reports success while nothing was configured or loaded. Plain `tool dev` is
  hit too: its config POST (`src/dev.py:8`, same line as base) now reaches the frontend server.
  At base the dev service used port 8080, which no documented tool uses, so this path was not hit.
- **Materiality (peer rules), deciding evidence:**
  - Security exemption: does not apply. No policy, issue or comment names this a security or
    trust boundary. The other listener is the developer's own frontend server, and the baseline
    security pass shows no untrusted source gaining an effect it could not otherwise cause.
    `security_boundary: false`.
  - Rule 4 (pre-existing behavior): not relaxed. The weak TCP-only readiness check in
    `src/runtime.py` is unchanged base behavior. But changing `PORT` from 8080 to 3000, the
    documented default port of a server that the README says runs alongside `tool dev`, turns a
    rare collision into the normal setup. The change makes the risk materially more likely, so it
    is change-introduced and judged normally. `src/dev.py:4` is the causal changed line.
  - Rule 1 (materiality bar): met.
    - Realistic trigger: the README tells developers to run this exact setup, with no crafted
      input.
    - Concrete consequence: a command that reports success while config and fixtures were not
      applied (wrong output, and a message that leads the user to a wrong action).
  - Rules 2, 3 and 5 do not apply. The changed line is not a guard. This is round one. The PR
    body discloses no follow-up issue.
- **Counterevidence checked:**
  - The `seed` flag defaults to `False`, but that does not protect plain `tool dev`. Line 8 runs
    whenever `dev()` is called.
  - `src/cli.py` is the only caller of `dev()`, so every invocation uses `PORT = 3000`.
  - No other documented tool uses 8080, so the base port did not collide in the documented setup.
  - The tests pass because they assert call order, not which program answers on the port.
- **Verification method:** Complete static trace over the supplied code plus the fixture's
  verified runtime observation. I did not reproduce it at runtime (execution not allowed).
  Reproduction for the author: start any listener on 127.0.0.1:3000 (for example the frontend
  dev server), run `tool dev --seed`, and observe the 404s from that listener and a success
  report with no fixtures in the dev service.
- **Remedy:**
  1. Keep the dev service on a port no documented tool uses (restore 8080, or choose another
     free port and update the README), or make the port configurable with a non-colliding default.
  2. Make readiness target the started service. For example, fail fast when the port is already
     in use before `start_service`, or check a dev-service-specific health response instead of a
     bare TCP connect.
  3. Add a regression test that occupies the port with a foreign listener and asserts that
     `tool dev` / `tool dev --seed` does not report success.

  Whichever fix is chosen must cover both the `src/dev.py:8` config POST and the
  `src/dev.py:10` fixtures POST.

## Findings - should-fix (non-blocking)

### F2 - Out-of-scope port move is not disclosed in the PR body

- **ID:** `pr-body.undisclosed-port-change`
- **Location / anchor:** `src/dev.py:4`, quote `PORT = 3000`. PR body: "Adds --seed to
  `tool dev`; seeding waits for readiness."
- **Severity:** Minor (Check 12 / Check 1 scope creep).
- **Blocker? No.** The body's claims are not contradicted: `--seed` is added and seeding is
  called after `wait_ready`. The port move is a significant change outside the issue (which
  covers only `--seed`) that the body does not mention. This is an orientation and scope gap,
  not a contradicted claim or an undisclosed partial (branch 3), so it is not a computed
  blocker. It is not a materiality relaxation either: branch 1 never applied.
- **Expected vs actual:** Reviewers should learn from the body that the dev service moves
  from 8080 to 3000, and why. The body is silent on it.
- **Remedy:** If the port move is kept after F1 is fixed, state it and its reason in the PR
  body (or split it into its own issue/PR). If F1 is fixed by restoring 8080, this finding
  closes too.

## Optional suggestions

None.

## Out-of-scope observations (non-blocking, max five)

1. `src/runtime.py` `wait_ready` treats any successful TCP connect as readiness of the
   intended service. This root is unchanged base behavior (origin base). The PR's port change
   made it reachable (F1). Beyond F1's in-PR fix, the author could open a follow-up issue to
   make readiness verify the service identity for all callers.
2. Per the verified observation, `tool dev --seed` reports success after the target answered
   404. That suggests `seed.load_fixtures` and/or `config.post_dev_config` (both untouched and
   not supplied) do not fail on non-2xx responses. I could not verify this from source. If
   confirmed, a follow-up issue to fail on non-success HTTP status would stop similar silent
   failures.

Overflow: 0.

## Carried

Unavailable: round one, no qualifying first-pass baseline.

## Dimensions

| # | Dimension | Result |
|---|---|---|
| 1 | Issue scope | R1 partial (F1). R2 and R3 met. The port move is scope creep (F2). |
| 2 | Structural integrity | Required lint/tests passed at head. Plain `tool dev` regresses in the documented setup (F1). The CLI surface adds `--seed` and the default stays unchanged. |
| 3 | Legacy/stale code | No removed modules or dangling references. The README's statement that the frontend runs on 3000 alongside `tool dev` now conflicts with the dev port (covered by F1). |
| 4 | Technical debt | Debt introduced: the hard-coded `PORT` collides with a documented tool (F1). Debt closed: none. |
| 5 | Documentation accuracy | No docs changed in the diff. The README is untouched. The conflict is covered by F1. |
| 6 | Conventions | Not assessable beyond the supplied files: AGENTS.md/REVIEW.md not supplied. Nothing flagged. |
| 7 | Follow-up hygiene | F1 is fixed in this PR (Blocker? Yes). F2 and the observations are optional or follow-up. |
| 8 | Correctness | F1. `dev(seed=False)` keeps the plain call compatible. Call order is correct. |
| 9 | Security | No new untrusted-input path. Local-only HTTP to 127.0.0.1. No secrets, auth or privilege changes. No trust boundary changed, so no specialist pass is required. Whether dev config content is sensitive when sent to another local program was not evidenced. Nothing indicates it is. |
| 10 | Tests | The order assertion is a valid contract test (the DoD requires it). Gap: no scenario with the port already occupied (remedy in F1). Mutation: applicable, skipped (no pinned runner). |
| 11 | Skill quality | Not applicable: no skill bodies touched. |
| 12 | PR description | Linked issue present. Port change undisclosed (F2). |

Focused lenses:
- Errors/fallbacks: applied. A failed config/seed becomes a success report. The cause traces
  to readiness targeting (F1) and possibly to untouched HTTP handling (observation 2).
- Type invariants: not applicable (no type construction changes).
- Comments/docs: applied to the README's unchanged frontend-port statement (F1).
- Test resilience: applied (dimension 10).

## Propagation sweep

There is no recurring class: one blocker finding. Search: every use of `PORT` and of
`http://127.0.0.1:%d` in the reviewed diff (`src/dev.py`, `src/cli.py`, test description).
Instances: `src/dev.py:6`, `src/dev.py:7`, `src/dev.py:8`, `src/dev.py:10`. All derive from
`src/dev.py:4` and are covered by F1's single fix point. Not covered: the repository outside
the supplied files (for example other code or docs that mention port 8080).

## Verification gaps

- V1 (environment, non-blocking for the verdict): project instruction files and REVIEW.md
  were not supplied.
- V2 (environment): `tests/test_dev.py` source and the rest of `src/cli.py` were not
  inspected.
- V3 (environment): `start_service` behavior when port 3000 is already bound is unknown.
  It does not change F1, which rests on the verified observation.
- V4 (environment): skill fingerprint not computed. No review.json, validator run or anchor
  verification, because the fixture forbids execution and fabricating a record. Anchors above
  are quoted from the supplied head text but were not mechanically verified.

To finish a full-assurance run: read the project instructions and REVIEW.md, read the test
and caller sources at head, compute the skill fingerprint, then build review.json and run the
validator and `verify_anchors.py` against the real head.

## Maintainer decision items

None.
