reviewer: pr-review2
skill-version: 2.11.1
candidate-sha256: f79409f6f0e85c3aaeaaef8d089ae86847ad7b85ea9dbe26f220a95758b87609
case: 35-dev-seed-a
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: FAIL
- Observed: Review incomplete / NEEDS_REVIEW with 0 blockers. The residual is classified as the oracle expects (origin base, rule 4, explicitly not materially more severe because base line 8 already posted the config to the same listener), but a material gap GAP-1 keeps the verdict from Ready to merge: the new dev(seed) parameter has no default and no caller was supplied.
- Tool policy: offline fixture; one fresh-context Claude Code subagent per case, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus that case's input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: absolute workspace paths in the raw output are redacted to <case-workspace>/. Run 1 at 2.11.1, scored after the run against the hidden oracle. Fixture defect, not a skill defect: the input changed the dev() signature without showing its caller. The case was corrected (src/cli.py wiring, seed=False default) and rerun.

## Raw reviewer output

# PR Review 2 - `tool dev --seed` (offline synthetic fixture, peer mode)

**Verdict: Review incomplete / NEEDS_REVIEW**

0 blockers. 1 verified finding: a Minor non-blocking residual whose root is pre-existing behavior (origin base, materiality rule 4). 1 material verification gap is still open: the supplied evidence does not show how `tool dev` calls the changed `dev(seed)`. That gap is the only reason this is not "Ready to merge". The residual finding does not block the PR by itself.

Nothing in the diff needs a fix demand: 0 blockers, 0 in-PR fix demands. One follow-up issue is suggested (DEV-1), and one open question needs an answer (GAP-1).

---

## Skill identity and reviewer

| Field | Value |
|---|---|
| Skill name | pr-review2 |
| metadata.version | 2.11.1 (read from the SKILL.md frontmatter of the directory that was read) |
| Package fingerprint | **Not computed.** The brief forbids running programs, so `review_record.py --skill-fingerprint` and the `find ... \| shasum` equivalent were not run. No value was copied from anywhere. |
| Skill directory read | `<case-workspace>/skill/` |
| Reviewer host | Claude Code (Claude Agent SDK) |
| Reviewer model family | claude |

## Run status

- **No review.json and no validator-output.txt were produced.** The brief says: "Do not invent metadata or review.json". It also forbids running the validator. Run status therefore was **not computed by the validator**, and this report does not claim it is complete.
- Based on the review record rules, this run would be **incomplete**. Reasons:
  - GAP-1 (material, cause `environment`): the fixture does not include the caller or CLI wiring of `dev()`. See Verification gaps.
  - Context incomplete (cause `scope_limit`, authority: the brief, "Only read the assigned input, candidate skill and necessary references"). Root `AGENTS.md`, `cli/shared/AGENTS.md`, `REVIEW.md` files and `SECURITY.md` were not available.
  - Skill fingerprint and anchor verification were not run (cause `scope_limit`, same brief authority: "no ... program/test/validator execution").
- approved_scope_status: incomplete. The open reasons are not all `scope_limit`, because GAP-1 is `environment`.
- Stopped: no.
- Kept artifact paths: none. Only this report exists, at the path above.

## Subject

| Field | Value |
|---|---|
| PR URL / title | Not supplied in the fixture |
| Linked contract | The linked issue (reference is present: "Closes the linked issue") |
| Base | `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` |
| Head | `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb` |
| Patch digest | Not applicable (commit input, not dirty input) |
| Instruction / REVIEW.md paths reviewed | None available. The fixture does not supply root `AGENTS.md`, `cli/shared/AGENTS.md`, `src/REVIEW.md`, `tests/REVIEW.md` or `SECURITY.md`. Only the trusted policy line in the fixture was applied. |

## Required gates at head

| Check | Required? | Status at head | Attribution | Source |
|---|---|---|---|---|
| lint | yes (trusted policy) | passed | not_applicable | Fixture: "required checks are lint and tests; both passed at head" |
| tests | yes (trusted policy) | passed | not_applicable | same |
| Security specialist pass | not required | not run | - | No trust boundary is changed. See the security pass below. |

- No commands were run locally. The brief forbids execution.
- The gate states above were supplied as trusted observation. This review did not observe them itself.

## Timing

No review clock was collected (fixture statement). Elapsed, active review, verification and CI-wait times are all **unknown**.

## Mutation testing

- Applicable: yes, because the PR changes decision logic (the `if seed:` branch and call ordering).
- Status: **skipped, no project-pinned runner.** The fixture says mutation is optional and no mutation tool is installed. Neither policy nor the user requires it. Per SKILL.md, the mutation reference was not read and no runner was installed.

## Coverage

- Review mode: round 1, full pass.
- Changed files reviewed: **2 of 2**.
  - `src/dev.py`: reviewed line by line from the complete head content supplied, plus the base/head line provenance.
  - `tests/test_dev.py`: **partial**. Its content was not supplied. It was assessed only through the trusted observation "The test asserts load_fixtures runs after wait_ready" and the passing `tests` gate.
- Affected untouched code:
  - `src/runtime.py` `wait_ready`: inspected through its supplied semantics only.
  - `seed.load_fixtures`, `config.post_dev_config` and `runtime.start_service`: not supplied. Their error behavior is unknown.
  - The `tool dev` CLI entry point: not supplied. This is GAP-1.
- Prioritized: the ordering contract and the readiness semantics. Deprioritized: none.

## Risk

- **Low.** This is a local development command only. `--seed` adds one new branch, and the existing behavior is unchanged except for the new `seed` parameter.
- Blast radius: developer machines that run `tool dev`.
- Reversible: yes, by reverting the commit. Nothing is persisted outside the local dev environment except whatever the seeded service stores.
- No auth, billing, credential, CI or release surface is touched.
- Rollback: revert the PR. There is no deployment behavior, so production rollback does not apply.
- Owner and human approval counts: not supplied. None were invented.

## Baselines and history

- First-pass published baseline: none. This is round 1.
- Latest reviewed SHA: none.
- Re-review fields: not applicable.

---

## Contract traceability

| ID | Criterion (exact text) | State | Implementation | Verification |
|---|---|---|---|---|
| R1 | "`tool dev --seed` loads local fixtures into the dev service after it starts." | met, with a residual | `src/dev.py` line 7 `wait_ready(port=PORT)` comes before line 10 `load_fixtures("http://127.0.0.1:%d" % PORT)`, which is guarded by line 9 `if seed:` | Static trace and the trusted test observation. The CLI flag wiring (`--seed` reaching `dev(seed)`) is **unverified**. See GAP-1. |
| R2 | DoD: "fixtures are posted only after `wait_ready` returns" | met | Same lines. `load_fixtures` is reachable only after `wait_ready` returns, and there is no other call site in the file. | Static trace, plus the supplied test observation and the passing `tests` gate |
| R3 | DoD: "a test proves the order" | met | `tests/test_dev.py` | Trusted observation: "The test asserts load_fixtures runs after wait_ready". Required `tests` passed at head. File content was not inspected. |

**Note on R1 and the foreign-listener case.** If another program already listens on 8080, the fixtures go to that program instead of the dev service. This does not fail R1, for two reasons:

- The issue's acceptance text (the DoD) defines the ordering as relative to `wait_ready` returning, and that ordering holds.
- In that state, base `tool dev` was already pointed at the foreign program: line 8 posts the config there, and the user's own requests reach it. So seeding cannot reach "the dev service" for a reason rooted in unchanged code.

This is handled as the DEV-1 residual, not as branch 2.

## Findings

### Blockers

None.

### Should-fix / residual (non-blocking)

#### DEV-1 - Seeding inherits a readiness check that accepts any listener on port 8080

| Field | Value |
|---|---|
| ID | `dev.seed-readiness-target-identity` |
| Location | `src/dev.py` line 10 (changed); root cause in `src/runtime.py` `wait_ready` (untouched) |
| Anchor (verbatim head line) | `        load_fixtures("http://127.0.0.1:%d" % PORT)` (whitespace-normalized: `load_fixtures("http://127.0.0.1:%d" % PORT)`) |
| Severity | Minor (the team also classifies it Minor: local development only) |
| Blocker? | **No.** Materiality rule 4 (pre-existing behavior). Origin: **base**. |
| security_boundary | false |

**Trigger and path.**
1. Another local program is already listening on 127.0.0.1:8080 when `tool dev --seed` starts.
2. `start_service(port=PORT)` runs (line 6).
3. `wait_ready(port=PORT)` (line 7) returns as soon as any TCP connect to 127.0.0.1:8080 succeeds, so it returns immediately because of the foreign listener.
4. Line 8 posts the dev config to that program.
5. Line 10 posts the fixtures to that program.

**Expected vs actual.**
- Expected: fixtures load into the dev service that was just started.
- Actual: the fixtures (synthetic sample records with no secrets) are POSTed to whatever program already owns port 8080. The dev service, if it started at all, is not seeded.

**Causal anchor.**
- The new line 10 adds one more POST behind the existing readiness check.
- The broken invariant ("ready" means "our spawned service is ready") lives in untouched `src/runtime.py` `wait_ready`, together with the unchanged `PORT = 8080` (line 4).

**Why rule 4 applies (deciding evidence).**
- The root is unchanged behavior in untouched code. At base, lines 1, 3, 4, 6-8 and 11 were identical. Base line 8 already posted the developer's local config, which holds their local settings, to the foreign listener, and the user's own requests already reached it.
- **Not materially more likely.** The trigger is the same (port 8080 already occupied) and needs the same precondition. The PR does not touch the port choice or the readiness check.
- **Not materially more severe.**
  - The added payload is synthetic, non-secret sample data. It is less sensitive than the config that base already sends to the same recipient.
  - The extra POSTs land on a program that already receives an unexpected POST from line 8.
  - The dev session was already misrouted at base, so the unseeded service is a symptom of the same pre-existing failure. It is not a new failure mode.
- It is not a changed caller making untouched code regress. `wait_ready` behaves exactly as it did, and line 10 only adds a consumer of that behavior.

**Security exemption check (rule 2 order).**
1. No project policy, security doc, issue text or code comment that was supplied names `wait_ready` or port 8080 a security or trust boundary.
2. Baseline pass: the untrusted source here is a foreign local listener. What the change adds is that this listener receives synthetic, non-secret fixture data. It already received more sensitive data (the config) at base, so the change gives it no effect it could not already get. No boundary is changed.
3. The PR body says "seeding waits for readiness". That does not claim resistance to a foreign listener, and seeding does wait for `wait_ready` as stated, so branch 3 is not triggered.
4. The fixture says port 8080 is used by no tool the project documents.

So this is not a trust-boundary defect, and the exemption does not apply.

**Verification method.**
- A complete static trace of the supplied `src/dev.py`, using the supplied `wait_ready` semantics and the supplied verified observation of the foreign-listener behavior.
- No runtime reproduction: the brief forbids execution.
- Counterexample pass, run by this reviewer because no separate verifier is allowed. "Could the PR have made this worse?" Answer: same trigger and same recipient. The added data is less sensitive than what base already sends.

**Remedy (follow-up, not in-PR).** Ask the author to open a follow-up issue so the readiness check confirms it is talking to the spawned service. Any one of these would work:
- Have `wait_ready` probe a service-identifying health endpoint instead of a bare TCP connect.
- Fail fast when port 8080 is already bound before `start_service`, or confirm that `proc` owns the listening socket.
- Use an ephemeral or configurable port reported by the service.

One fix in `wait_ready` / `dev` closes both the base config misroute and the new fixture misroute. Optionally, the PR body can mention the residual.

**Maintainer decision item:** not required. This is not a Critical residual.

### Optional suggestions

None. Style was not requested.

## Verification gaps

| ID | Material? | Cause | What is unverified |
|---|---|---|---|
| GAP-1 | **yes** | environment (caller not supplied in the fixture) | Changed `src/dev.py` line 5 is `def dev(seed):`. The `seed` parameter is new and has **no default**. The PR body claims "Adds --seed to `tool dev`", but the changed paths are only `src/dev.py` and `tests/test_dev.py`. No CLI or argument-parsing file changed. The supplied evidence does not show how `tool dev` calls `dev()`. So two things cannot be confirmed: (a) that `--seed` is actually exposed as an optional flag, and (b) that plain `tool dev` without `--seed` still works rather than failing with a missing-argument error. Weak counterevidence: the required `tests` gate passed at head, but whether it covers the no-flag CLI path is unknown. **To close:** show the `tool dev` entry point, or a CLI test invoking `tool dev` with and without `--seed`. If dispatch derives flags from the signature, confirm that `seed` gets a `False` default. If plain `tool dev` is shown to fail, this becomes a branch-1 blocker (a regression in ordinary use) and the PR-body claim would be contradicted (branch 3). |
| GAP-2 | no | scope_limit (brief) | `tests/test_dev.py` content was not read. Its assertion is accepted from the trusted observation. It is unknown whether the test also covers `seed=False` (no fixture load). |
| GAP-3 | no | scope_limit (brief) | Project instructions and REVIEW.md files were not available. Skill fingerprint, review record, validator and anchor verifier were not run. |

## Out-of-scope observations

1. The error behavior of `post_dev_config` / `load_fixtures` is not supplied. If they raise, `proc` is never returned to the caller and may outlive the command. This is unverified and was already present at base for line 8, so it is not admitted as a finding.

## Carried

Not applicable. Round 1, no qualified first-pass baseline.

## Propagation sweep

- Defect class: `dev.readiness-target-identity` ("ready" does not prove the spawned service owns the port).
- Search: every post-readiness network call in the complete supplied `src/dev.py`.
- Instances found:
  - `src/dev.py:8` (`post_dev_config`, origin base)
  - `src/dev.py:10` (`load_fixtures`, new consumer)
- Files covered: `src/dev.py` (complete). `tests/test_dev.py` was covered only by its supplied description.
- The sweep is limited to the supplied files. Other `wait_ready` callers in the repository were not available.
- Only one finding (DEV-1) is in this class, so the second-instance trigger rule does not apply.
- Debt introduced: none. Debt closed: none. Legacy left: the base readiness semantics (DEV-1 follow-up).

## Dimension results

| # | Dimension | Result |
|---|---|---|
| 1 | Issue scope | R1-R3 met. No scope creep. CLI flag wiring unverified (GAP-1). |
| 2 | Structural integrity | Required lint/tests passed at head (supplied). The possible break of plain `tool dev` from the required `seed` parameter is unresolved (GAP-1). |
| 3 | Stale code | Not applicable. Nothing was removed or renamed. |
| 4 | Debt | No new debt. Residual readiness semantics recorded (DEV-1). |
| 5 | Docs | No docs changed. Not applicable. |
| 6 | Conventions | Project AGENTS.md was not available, so it could not be checked against conventions. No skill or CI files changed. |
| 7 | Follow-up hygiene | DEV-1: the author opens a follow-up issue. The reviewer opens none. |
| 8 | Correctness | Ordering is correct. DEV-1 residual. GAP-1 open. |
| 9 | Security | Baseline pass done. No new untrusted-input-to-sink path. Payload is synthetic and non-secret. No trust boundary changed. No specialist needed. |
| 10 | Tests | The order assertion protects a stated contract (the DoD ordering), so the interaction/order check is valid. Coverage of `seed=False` is unknown (GAP-2). Mutation skipped, no pinned runner. |
| 11 | Skill quality | No skill bodies touched. Not applicable. |
| 12 | PR description | Linked issue present (branch 5 not triggered). Claims match the diff except that the `--seed` CLI exposure is unverified (GAP-1). |

## Clean-review inspection rows (not findings)

- `src/dev.py` lines 1-11:
  - The imports are used.
  - `wait_ready` comes before both POSTs.
  - The seed branch is gated by `if seed:`.
  - `proc` is returned on the success path.
- `tests/test_dev.py`: asserts `load_fixtures` runs after `wait_ready` (supplied).

## How to finish this review

1. Supply the `tool dev` entry point or a CLI-level test for both `tool dev` and `tool dev --seed` (closes GAP-1).
2. In a live run:
   - Read the project AGENTS.md and REVIEW.md files.
   - Compute the skill fingerprint.
   - Build review.json, then run the validator and `verify_anchors.py` against head `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`.

If GAP-1 resolves with `seed` optional and plain `tool dev` working, the computed verdict becomes **Ready to merge**, with DEV-1 as a non-blocking follow-up.
