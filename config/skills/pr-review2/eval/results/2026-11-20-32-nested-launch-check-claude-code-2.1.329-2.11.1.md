reviewer: pr-review2
skill-version: 2.11.1
candidate-sha256: f79409f6f0e85c3aaeaaef8d089ae86847ad7b85ea9dbe26f220a95758b87609
case: 32-nested-launch-check
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: PASS
- Observed: Ready to merge; renamed-symlink bypass is a Minor should-fix, Blocker? No, basis guard_bypass, security_boundary false; two non-material gaps (caller not supplied).
- Tool policy: offline fixture; one fresh-context Claude Code subagent per case, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus that case's input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: run 1 at 2.11.1, scored after the run against the hidden oracle.

## Raw reviewer output

# PR Review 2 - nested gate refusal (offline synthetic fixture)

**Verdict: Ready to merge** (peer mode, round one, full pass on supplied evidence).

0 blockers. 1 verified finding: a non-blocking Minor should-fix (materiality basis
`guard_bypass`). No in-PR fix is demanded.

This is a fixture-only evaluation of the skill, not a live AURA PR review. The verdict is
computed from the evidence the fixture supplies; it is not merge authorization and does
not replace any required human approval.

## Skill and reviewer identity

| Field | Value |
|---|---|
| Skill name | pr-review2 |
| metadata.version | 2.11.1 |
| Package fingerprint | not computed: the fixture forbids script/program execution, so `scripts/review_record.py --skill-fingerprint` could not run on the read directory. Not copied from any other source. |
| Reviewer host | Claude Code (Agent SDK subagent) |
| Reviewer model family | claude |

## Run status

- No review.json or validator-output.txt was produced. The review record says fixture-only
  exercises use supplied evidence and report missing metadata instead of fabricating a
  record; the validator and `verify_anchors.py` also could not run (no execution allowed).
- Run status is therefore not validator-computed. Reviewer assessment on supplied evidence:
  both changed files covered, all twelve dimensions addressed, the required gate reported
  passed at head, no material verification gap. Disclosed limits are listed under
  "Verification gaps" below; none of them is material.
- stopped: no. approved_scope_status: not applicable (no scope narrower than the PR).

## Subject

- PR: synthetic fixture (no URL/number). Title not supplied.
- Linked contract: the linked issue (reference present in body: "Closes the linked issue").
  Issue text: `tool gate -- <command>` recursed without end when `<command>` itself started
  `tool gate` on the same project root.
- Base: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- Head: `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`
- Patch digest: not applicable (commit input, not dirty input).
- Instruction / REVIEW.md paths: none supplied by the fixture. AGENTS.md, cli/shared/AGENTS.md
  and REVIEW.md files were not available; the supplied project docs statement (gate is a
  local developer convenience) was used as the trusted project context.

## Required gates

| Gate | Required | Status at head | Attribution | Evidence |
|---|---|---|---|---|
| Trusted required CI | yes (fixture: "Trusted required CI passed at head") | passed | not_applicable | fixture input line 28 |
| Specialist security pass | not required | not applicable | - | no trust boundary changed (see Security) |

Local commands executed: none (fixture forbids execution). Red/green reproduction was not
run by the reviewer; the regression test's behavior is taken from the supplied description
and the green required CI.

## Timing

active_review_seconds, verification_seconds, ci_wait_seconds, elapsed_seconds: unknown (no
clock data captured in this offline run).

## Mutation

Applicable (changed decision logic in `src/gate.py`), skipped: no project-pinned runner.
The fixture supplies no StrykerJS/Stryker.NET dependency, manifest entry or committed
config, and no policy or user instruction requires mutation testing. The mutation
reference was not read and no runner was installed.

## Coverage

- Reviewed 2 of 2 changed files:
  - `src/gate.py` (new, complete source supplied, all 13 lines read and traced).
  - `tests/test_gate.py` (contents supplied as a description, not verbatim source; reviewed
    at that level).
- Deprioritized groups: none.
- Partial inspection: the test file's literal code and the CLI entry point that calls
  `run_gate` (and derives `root`) were not supplied; see Verification gaps.

## Risk

**Low.** A local developer convenience tool (project docs: runs commands the same user typed,
with that user's privileges). Behavior affected: `tool gate` now refuses a nested gate on the
same root, via an inherited environment marker and an early argv diagnostic. Blast radius:
users of `tool gate` who intentionally nest gates on the same root (the issue defines that
as the bug). No persistent state, migration, credential or release surface changes.
Reversibility: plain revert of `src/gate.py`; nothing irreversible. Rollback: revert the
commit; no deployment behavior beyond the local CLI. No extra human scrutiny trigger
(auth, billing, credentials, CI/release, destructive migration, new architectural pattern)
applies.

## Review round

Round one, full pass. No prior published or local baseline; no re-review fields apply.

## Acceptance criteria

| ID | Criterion (issue DoD) | State | Implementation | Verification |
|---|---|---|---|---|
| R1 | A nested gate on the same root is refused with a clear error | met | `src/gate.py:8-9` `if os.environ.get(MARKER) == root:` / `sys.exit("refusing nested gate on " + root)`; marker set for the child at line 13 | static trace below + supplied test; required CI passed (basis: ci/static) |
| R2 | A test proves it | met | `tests/test_gate.py`: child calls `tool gate` on the same root, asserts exit with "refusing nested gate on" | required CI passed at head (basis: ci) |

Static trace for R1: parent `run_gate(root, argv, spawn)` with no marker passes line 8,
passes line 10-12 for an indirect child, and spawns with `TOOL_GATE_ROOT=root` (line 13).
The nested `tool gate` on the same root reads the inherited marker at line 8, equal to
`root`, and exits with "refusing nested gate on <root>". The test's asserted text
("refusing nested gate on") differs from the early message ("refusing nested gate: ..."),
so the test genuinely exercises the marker path, not the early diagnostic.

## PR-body claims

| Claim | Diff evidence | Result |
|---|---|---|
| Closes the linked issue | R1, R2 met | consistent |
| Root marker refuses any nested gate on the same root | lines 8-9, 13 | consistent |
| Early diagnostic names the common direct self-invocation before the child starts | lines 3-6, 10-12 | consistent; the claim is scoped to direct self-invocation and does not claim renamed or indirect launchers |
| Tests cover both | marker test + early-message test for `["tool", "gate", "--", "make"]` | consistent |

## Findings

### Blockers

None.

### Should-fix (non-blocking, relaxed by the materiality rules)

#### F1 `gate.early-diagnostic-launcher-identity` - renamed launcher skips the early diagnostic

- Location: `src/gate.py:4`
- Causal anchor (verbatim head line):
  `    if os.path.basename(argv[0]) == "tool" and argv[1:2] == ["gate"]:`
- Severity: Minor. **Blocker? No.** security_boundary: false.
- Materiality basis: `guard_bypass` (rule 2, step 4).
- Trigger/path: user creates a symlink `bin/runner` pointing at the tool and runs
  `tool gate -- bin/runner gate`. `os.path.basename("bin/runner")` is `"runner"`, so line 4
  is false and `early_diagnostic` returns `None`; line 13 spawns the child.
- Expected (per the diagnostic's purpose): self-invocation named before the child starts.
- Actual (verified observation supplied by the fixture): no early message; the child starts,
  reads the marker at line 8 and exits with "refusing nested gate on <root>". No loop occurs,
  so the issue's recursion is still prevented and R1 still holds.
- Deciding evidence, in rule order:
  1. Policy/docs/issue/comments: project docs call the gate "a local developer convenience
     that runs commands the same user typed, with that user's privileges"; no document calls
     the diagnostic a security or trust boundary. Not a boundary by step 1.
  2. Baseline security pass: the bypassing input is typed by the same local user, who can
     already run any command with the same privileges; the bypass reaches no effect that user
     could not otherwise cause. Not a boundary by step 2.
  3. Claims: the PR body claims only "the common direct self-invocation"; nothing claims
     detection of renamed or indirect launchers. No contradicted claim (branch 3 does not match).
  4. Therefore a convenience / accident-prevention guard. A renamed symlink is a contrived
     launcher spelling, so the bypass is a non-blocking Minor should-fix.
  Independently, the consequence is small: the user still gets a clear refusal from the
  marker, only after the child process starts.
- Verification method: static trace of lines 4, 8-13 plus the fixture's verified observation.
- Remedy (optional, may land as a suggestion or small follow-up commit): either compare the
  resolved launcher identity (for example `os.path.realpath(shutil.which(argv[0]) or argv[0])`
  against the tool's own resolved executable) instead of the basename, or document in the
  diagnostic's docstring/help that it matches only direct `tool gate` invocations and that the
  root marker is the authoritative refusal. If changed, add a test for a renamed launcher.
- Class: `gate.early-diagnostic-launcher-identity`; instances: `src/gate.py:4` (single
  instance; no second same-class finding, so no class-wide sweep was triggered).

### Optional suggestions

None.

## Dimensions

1. Issue scope: both DoD items met; no scope creep; no undisclosed partial.
2. Structural integrity: required CI passed at head. No targeted local commands could run
   (fixture forbids execution). New module; no existing exported interface changed in the diff.
3. Legacy/stale code: not applicable, nothing removed or renamed.
4. Debt: introduced - none beyond F1 (optional). Closed - the unbounded recursion of the issue.
5. Docs accuracy: no docs changed in the diff; supplied project docs do not conflict with
   the behavior.
6. Conventions: not assessable beyond the supplied files (no AGENTS.md supplied); no
   convention violation evidenced.
7. Follow-up hygiene: F1 is Blocker? No; it may land as a suggestion, a small follow-up
   commit or an author-opened issue. The reviewer opens nothing.
8. Correctness: traced `early_diagnostic` (direct `tool gate` argv, renamed launcher, full
   path such as `/usr/local/bin/tool`, which `basename` handles) and `run_gate` (no marker,
   same-root marker, different-root marker which is intentionally not refused per the issue's
   "same root" scope). Only F1 found.
9. Security: baseline pass done. Assets: local process environment and spawned command.
   Actor: the same local user. Entry point: CLI argv typed by that user. No new untrusted-input
   path, no privilege change, no secret handling, no new dependency. The marker is set as a
   dict entry passed to `spawn(..., env=...)`, not interpolated into a shell string. No
   specialist pass required.
10. Tests: both new behaviors have tests with meaningful, distinct assertions; the marker test
    goes through a real child. A renamed-launcher case is untested, which is consistent with
    the scoped claim (see F1 remedy).
11. Skill content quality: no skill bodies touched.
12. PR description: linked-issue reference present (branch 5 does not match); claims match
    the diff; test plan stated ("Tests cover both").

Focused lenses: errors/fallbacks - refusals use `sys.exit(message)` (non-zero exit, message on
stderr), no swallowed failure; type invariants - not applicable (no type construction);
comments/docs claims - none in the diff; test resilience - assertions target user-visible
exit text, not internals.

## Verification gaps

| ID | Material | Cause | Evidence / what is unverified |
|---|---|---|---|
| G1 | false | environment | The CLI entry that calls `run_gate` and derives `root` was not supplied. Whether two spellings of the same root (trailing slash, symlinked project path) could compare unequal at line 8 is not evidenced either way. The supplied test and observation show the ordinary same-root path is refused. |
| G2 | false | environment | `early_diagnostic([])` would raise `IndexError` at line 4; whether the caller can pass an empty command (for example `tool gate --`) is not evidenced, since argument parsing was not supplied. Not a verified finding. |
| G3 | false | environment | `tests/test_gate.py` supplied as a description, not verbatim code; the skill fingerprint, review.json validator and anchor verifier could not run (fixture forbids execution). |

## Out-of-scope observations

None beyond the unverified questions recorded as G1 and G2.

## Carried

Unavailable: round one, no qualifying first-pass baseline.

## Propagation sweep

- Class `gate.early-diagnostic-launcher-identity`: searched the full reviewed diff
  (`src/gate.py`, `tests/test_gate.py` as described) for other launcher-identity checks by
  argv basename. Instances found: `src/gate.py:4` only. Scope not covered: the CLI entry point
  (not supplied).
- Legacy left: none. Debt introduced: none required. Net: the change closes the issue's
  recursion with a robust marker plus a scoped convenience diagnostic.

## Reproduction (portable)

1. At head `bbbbbbbb...`, with the tool on PATH, run `tool gate -- tool gate -- make`: the
   parent prints "refusing nested gate: the command starts tool gate again" before spawning
   (lines 4-5, 10-12).
2. Create `bin/runner` as a symlink to the tool and run `tool gate -- bin/runner gate`:
   no early message; the child exits with "refusing nested gate on <root>" (line 8-9).
   No recursion. This is F1's observable behavior.
