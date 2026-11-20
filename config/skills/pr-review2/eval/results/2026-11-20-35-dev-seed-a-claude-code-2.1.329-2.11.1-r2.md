reviewer: pr-review2
skill-version: 2.11.1
candidate-sha256: f79409f6f0e85c3aaeaaef8d089ae86847ad7b85ea9dbe26f220a95758b87609
case: 35-dev-seed-a
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: PASS
- Observed: Ready to merge, 0 blockers; F1 wrong-listener risk is a disclosed residual (rule 4, origin base), not materially more likely or more severe because base line 8 already posted the local config to the same listener; follow-up issue requested.
- Tool policy: offline fixture; one fresh-context Claude Code subagent per case, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus that case's input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: run 2 at 2.11.1 on the corrected fixture (see the run 1 result for this case), scored after the run against the hidden oracle.

## Raw reviewer output

# PR Review 2 - `tool dev --seed` (offline synthetic fixture, peer mode)

**Verdict: Ready to merge** - 1 verified finding, 0 blockers.

Nothing to fix in this PR: 0 blocking findings. One Minor residual rooted in unchanged code
(`wait_ready` readiness semantics in untouched `src/runtime.py`) is recorded with origin base,
`Blocker? No`, and the author is asked to open a follow-up issue for it.

This is a fixture-only evaluation of the skill (`input.md`), not a live AURA PR review. The
verdict rests on the trusted observations the fixture supplies; the limits below apply.

## Skill and reviewer identity

| Field | Value |
|---|---|
| Skill name | pr-review2 |
| metadata.version | 2.11.1 (read from `skill/SKILL.md`) |
| Package fingerprint | Not computed - the fixture forbids script/program execution, so `review_record.py --skill-fingerprint` (or the equivalent shasum pipeline) could not run over `skill/`. Not copied from any other source. |
| Reviewer host | Claude Code (agent CLI) |
| Reviewer model family | claude |

## Run status

- No review.json or validator-output.txt exists: the fixture instructs "Do not invent
  metadata or review.json" and forbids validator execution, and SKILL.md section 5 says
  fixture-only exercises do not fabricate a record. Run status therefore was **not computed
  by the validator**; nothing here claims a validator-computed `complete`.
- Reviewer's assessment for the record that would be built: no material verification gap,
  all three changed files covered from supplied evidence, required gates passed at head,
  contract resolved, sole criterion met. If a record were built from this evidence the
  expected state is complete, approved_scope_status complete, not stopped - but this is an
  expectation, not validator output.
- Anchor verification (`verify_anchors.py`) not run (no git, no execution). The finding's
  anchor quote below is copied from the fixture's head listing of `src/dev.py`.
- Kept artifact paths: none (no record produced, by instruction).

## Subject

- PR: offline synthetic fixture; title/URL not supplied. Adds `--seed` to `tool dev`.
- Linked contract: present ("Closes the linked issue"). Issue: "`tool dev --seed` loads local
  fixtures into the dev service after it starts." DoD: "fixtures are posted only after
  `wait_ready` returns; a test proves the order."
- Base: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- Head: `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`
- Dirty input: no (commit range); no patch digest.
- Instruction / REVIEW.md files: none supplied by the fixture (no AGENTS.md, cli/shared/AGENTS.md,
  REVIEW.md or SECURITY.md content). Applied: the fixture's trusted policy line (required checks
  lint and tests) and the skill's own references (`skill/references/review-protocol.md`,
  `project-checks.md`, `focused-reviews.md`, `security-routing.md`, `review-record.md`).

## Required gates at head

| Check | Required | Status at head | Evidence |
|---|---|---|---|
| lint | yes (trusted policy) | passed | `input.md`: "required checks are lint and tests; both passed at head" |
| tests | yes (trusted policy) | passed | same line |
| Specialist security pass | not required | not applicable | No changed trust boundary (see Security below); no project requirement supplied |

Local commands executed: none (forbidden by the fixture). No green state was inferred beyond
the trusted policy statement.

## Timing

No review timing clock was collected (stated by the fixture). elapsed, active review,
verification and CI wait: all unknown.

## Mutation

Applicable (changed decision logic: the `if seed:` branch in `src/dev.py`), **skipped: no
project-pinned runner**. Mutation is optional per the fixture, no mutation tool is installed,
and no policy or user instruction requires it. The mutation reference was not read and no
runner was installed.

## Coverage and review mode

- Round one, full review (fixture: "Round one, full").
- Reviewed 3 of 3 changed files: `src/cli.py` (changed lines 21 and 34, plus the fixture's
  statement that it is the only caller of `dev()`), `src/dev.py` (complete head content,
  with base-vs-head line provenance), `tests/test_dev.py` (from the fixture's trusted
  description of its assertions; verbatim test source was not supplied).
- Untouched dependency traced: `src/runtime.py` `wait_ready(port, timeout=30)` semantics as
  supplied (returns on the first successful TCP connect to 127.0.0.1:port).
- Not inspected because not supplied: `runtime.start_service`, `seed.load_fixtures`,
  `config.post_dev_config` implementations. Their relevant behavior is covered by the
  supplied verified observation; no candidate depends on unsupplied detail (see
  Out-of-scope observation O1 for the one hardening question it leaves).
- Baseline: first round, no prior published or local baseline; no Carried items possible.

## Risk

**Low.** Blast radius: local developer CLI (`tool dev`) only; the new path runs only when a
developer passes `--seed`, and plain `tool dev` keeps its base behavior (`seed=False` default,
`store_true` default False). No deployment, data migration, auth, billing, credential, CI or
release surface changes. Reversibility: a plain revert restores base behavior; no
irreversible state. Rollback: not applicable to deployment (no deployed behavior changes).
No extra human scrutiny trigger from the protocol list applies. Owner/human reviewer: not
supplied.

## Contract traceability

| ID | Criterion | State | Implementation | Verification |
|---|---|---|---|---|
| R1 | Fixtures are posted only after `wait_ready` returns | met | `src/dev.py` line 7 `wait_ready(port=PORT)` precedes line 10 `load_fixtures(...)` inside `if seed:` (line 9); straight-line code, no other `load_fixtures` call | static trace + required `tests` check passed at head |
| R2 | A test proves the order | met | `tests/test_dev.py` asserts `load_fixtures` runs after `wait_ready` (trusted fixture description) | required `tests` check passed at head |

The issue's narrative ("loads local fixtures into the dev service after it starts") is met
whenever the dev service owns port 8080. The port-collision case is handled under finding
F1 below, whose root is the untouched readiness probe, not an unmet DoD item: the DoD's exact
text names `wait_ready` returning as the ordering point, and that holds.

## Findings

### Blockers

None.

### Should-fix / disclosed residuals (non-blocking)

#### F1 `dev.readiness-port-ownership` - seeding inherits a readiness probe that accepts any listener on 8080

| Field | Value |
|---|---|
| Location | `src/dev.py` line 10 (changed), relying on line 7 (unchanged) and `src/runtime.py` `wait_ready` (untouched) |
| Anchor quote (head) | `load_fixtures("http://127.0.0.1:%d" % PORT)` |
| Severity | Minor (team classification: local development only; agrees with the evidence) |
| Origin | base |
| Blocker? | **No** - materiality rule 4 (pre-existing behavior); recorded with origin base, not a non_blocking basis |
| security_boundary | false |

- **Trigger/path:** another local program already listens on 127.0.0.1:8080 when the developer
  runs `tool dev --seed`. `start_service(port=PORT)` (line 6) -> `wait_ready(port=PORT)`
  (line 7) connects to the foreign listener and returns at once -> `post_dev_config(...)`
  (line 8) -> `load_fixtures(...)` (line 10) posts fixtures to the foreign program.
- **Expected:** fixtures land in the dev service that `tool dev` started.
- **Actual:** fixtures are posted to whatever owns port 8080 (verified observation in the
  fixture).
- **Why it is pre-existing, not change-introduced (deciding evidence):**
  1. `wait_ready` lives in `src/runtime.py`, untouched by this PR; its "any TCP connect"
     semantics are the root cause.
  2. At base, `src/dev.py` lines 1, 3, 4, 6-8 and 11 were identical: `PORT` was already 8080,
     and line 8 already posted the developer's local config to the same foreign listener in
     the same situation, and the developer's own requests reached it too.
  3. The change does not make the risk materially more likely (same trigger, same port, same
     probe, opt-in flag) or more severe: the added payload is synthetic sample records with no
     secrets, strictly less sensitive than the local settings already sent at base.
- **Security exemption check:** no project policy, security doc, issue text or code comment
  names `wait_ready` or the dev port a trust boundary (none supplied). Baseline security pass:
  the only "untrusted" party is a local listener on an undocumented port; with this change it
  gains no effect it could not already cause at base (it already receives the config and the
  user's requests). The exemption does not apply, and in any case rule 4 governs a residual
  rooted in untouched code.
- **Branch 3 check:** the PR body says "seeding waits for readiness". The code does call the
  project's readiness primitive before seeding, so the claim is not contradicted by the diff;
  what "readiness" means is the base definition in `wait_ready`.
- **Verification method:** complete static trace over the supplied head listing plus the
  fixture's verified runtime observation; no local reproduction (execution forbidden).
- **Remedy (follow-up issue the author opens; reviewer does not open it):** make readiness
  prove ownership of the port before any post - for example have `start_service` fail when
  8080 is already bound, check the child `proc` is still alive after `wait_ready`, or probe a
  service-identifying health endpoint instead of a bare TCP connect. Add a test with a
  pre-bound 8080 listener asserting neither the config nor the fixtures are posted to it.
  Fixing it in `wait_ready`/`start_service` covers both line 8 and line 10.

### Optional suggestions

None.

## Dimensions

| # | Dimension | Result |
|---|---|---|
| 1 | Issue scope | Both DoD items met (R1, R2). No out-of-scope changes; all three changed files serve the feature. |
| 2 | Structural integrity | Required lint/tests passed at head. Only caller `src/cli.py` passes `seed=args.seed`; `--seed` is `store_true`, so plain `tool dev` calls `dev(seed=False)` and keeps base behavior. Test covers both `tool dev` and `tool dev --seed` starting the service. Return value `proc` unchanged. |
| 3 | Stale code | None: no removals/renames; base `return dev()` replaced, no dangling reference. |
| 4 | Debt | Debt introduced: none. Debt closed: none. Pre-existing residual F1 disclosed for follow-up. |
| 5 | Docs | No documentation changed; no doc claim to verify. Not applicable. |
| 6 | Conventions | No project instruction files supplied; nothing to check against beyond the trusted policy. No skill registry/asset changes. |
| 7 | Follow-up hygiene | F1 -> author-opened follow-up issue; no blockers to keep in-PR. |
| 8 | Correctness | Traced `seed` False/True through `src/cli.py:34` -> `dev()`; ordering start -> wait -> config -> fixtures is straight-line; URL formatting uses int `PORT`. Error/fallback lens: see O1. Type-invariant lens: not applicable (no type construction/serialization changed). Comment lens: no comments changed or invalidated. |
| 9 | Security | Baseline pass done. Entry point: local CLI flag. Sink: HTTP POST to 127.0.0.1:8080 of synthetic, secret-free fixtures. No new untrusted-input path, no auth/secret/dependency/privilege change; the only exposure (foreign local listener) is the pre-existing F1. No changed trust boundary, so no specialist pass. |
| 10 | Tests | Order assertion protects a stated protocol (the DoD), so it is a valid interaction assertion, not brittle internals. Both flag modes covered. Gap: no pre-bound-port scenario, part of F1's follow-up. Mutation: skipped, no pinned runner. |
| 11 | Skill quality | No skill bodies touched. Not applicable. |
| 12 | PR description | Linked-issue reference present ("Closes the linked issue"). Claims ("Adds --seed", "seeding waits for readiness") match the diff. Body is brief with no explicit test plan; no admissibility anchor, see O2. |

## Out-of-scope observations (non-blocking, 2 of max 5)

- **O1 - failure after `start_service` leaves the process unreturned.** If `load_fixtures`
  (line 10) raises, `dev()` exits before `return proc`, so the caller cannot stop the
  started service. The same pattern already exists at base for `post_dev_config` (line 8),
  and `load_fixtures`'s error contract was not supplied, so no failing line is proven.
  Hardening suggestion: wrap post-start steps so `proc` is terminated or returned on failure.
- **O2 - PR body has no explicit test plan.** It is accurate and links the issue; adding one
  line naming the order test and both start-mode tests would help reviewers. Not a finding.

## Carried

Not available: first round, no qualifying baseline.

## Propagation sweep

Class `dev.readiness-port-ownership`: searched the full supplied diff (`src/cli.py`,
`src/dev.py`, `tests/test_dev.py`) and the one caller for posts that follow `wait_ready`.
Instances: `src/dev.py:8` (base, config post) and `src/dev.py:10` (new, fixture post) - one
shared fix point in `wait_ready`/`start_service`. Only one finding in this PR, so the
second-instance class trigger did not fire; no further copies in the reviewed scope. Files
outside the fixture were not available to search.

## Limits

- Fixture-only: no git/gh, no execution, no record or validator, no anchor verifier, no
  skill fingerprint. All repository facts come from `input.md` as trusted observation.
- `tests/test_dev.py` source and the implementations of `start_service`, `load_fixtures` and
  `post_dev_config` were not available verbatim; conclusions about them rest on the fixture's
  stated observations.
- No Maintainer decision item: F1 is not a Critical residual, and no criterion demands a
  paid/live/credentialed run.
- This verdict is not permission to merge and does not replace required human approval.
