reviewer: pr-review2
skill-version: 2.11.0
candidate-sha256: 9398fd9497fbcc122a6903318639aeed88baf66fd7f62223adafc9a2407490c0
case: 38-gate-third-round
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: INVALID (originally recorded as PASS; rescored after an independent re-review)
- Rescore reason: fixture defect. The input claimed `./via/../tool gate` misses line 4, but
  `os.path.basename('./via/../tool')` is `tool`, so the diagnostic fires. The reviewer noticed
  this contradiction in its F-03 verification note and the run still scored PASS. The case was
  corrected (F-03 is now a launcher copy named tool.real) and rerun at 2.11.1; this run
  establishes nothing about F-03.
- Expected: Expected negative verdict; contrived bypasses relaxed; reassessment tests remaining blocker and recommends converging only after F-05.
- Observed: Not ready to merge, full pass round 3; F-05 Blocker? Yes (branches 2 and 1); F-03 and F-04 Minor should-fixes, Blocker? No, basis guard_bypass; approach reassessment states blocker status per finding and recommends converging after the F-05 fix, with F-03/F-04 as suggestions.
- False blockers: 0. Harmful false positives: 0.
- Tool policy: offline fixture; one fresh-context Claude Code subagent per case, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus that case's input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: single run, scored after the run against the hidden oracle.

## Raw reviewer output

# PR Review 2 - round 3 (full pass), peer mode

**Verdict: Not ready to merge (REQUEST_CHANGES).** 3 verified findings: 1 blocker (F-05), 2 non-blocking should-fixes (F-03, F-04, reclassified under the peer materiality rules). Coverage is incomplete (see Coverage and Run status); the blocker justifies the negative verdict on its own.

Round three with an open blocker: human reassessment is requested and an approach reassessment is included below. Recommendation: fix F-05 (a one-line message fix plus one test assertion) and converge. Treat F-03 and F-04 as suggestions. Do not run another fix round for them.

## Identity and run status

- Skill: pr-review2, metadata.version 2.11.0. Package fingerprint: **not computed**. Computing it needs a hashing script or command, and this fixture does not allow program execution. No value is copied from elsewhere.
- Reviewer: host Claude Code (Claude Agent SDK), model family `claude`.
- review.json / validator-output.txt: **none**. This is a fixture-only exercise, and the fixture says not to fabricate metadata or review.json. Without execution, the validator (`scripts/review_record.py`) and anchor verifier (`scripts/verify_anchors.py`) were not run.
- Run status: **not validator-computed**. These incompleteness sources are present, so the run would read incomplete:
  - G1 (cause `environment`): the content of `tests/test_gate.py` was not supplied, only a one-line summary of what the tests prove.
  - G2 (cause `environment`): the PR body text, base-revision code, root `AGENTS.md`, `cli/shared/AGENTS.md`, REVIEW.md files and the caller that computes `root` for `run_gate` were not supplied.
  - G5 (cause `environment`): validator, anchor verifier and skill fingerprint were not executed (fixture forbids execution).
  - approved_scope_status: not applicable. No scope limit was approved, because the maintainer asked for a full pass.
  - stopped: no.
- Timing: no review clock was collected. active_review, verification and ci_wait are all unknown (null).

## Subject

- Linked contract: the issue says `tool gate -- <command>` recursed without end when `<command>` started `tool gate` again on the same root. DoD: "a nested gate on the same root is refused with an error that tells the user how to proceed; a test proves it." The fixture states the PR body has the issue reference. Nothing else from the body was supplied.
- Base: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- Head: `eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee`
- Patch digest: not applicable. Committed head, no dirty input.
- Changed files: `src/gate.py`, `tests/test_gate.py`.
- Instruction/REVIEW.md paths loaded: none. None were supplied, which is part of gap G2. AURA conventions checks that depend on them are therefore unverified.

## Required gates

| Check | Required | State at head eeee...eeee | Source |
|---|---|---|---|
| lint | yes (trusted policy) | passed | supplied trusted policy line |
| tests | yes (trusted policy) | passed | supplied trusted policy line |
| security specialist pass | not required | not applicable: no trust boundary changed (see Security) | security routing baseline |
| mutation | optional | applicable, skipped: no project-pinned runner (fixture: optional, no tool installed) | SKILL.md mutation precheck |

No commands were executed locally. The green states are supplied observations, not ones I reproduced. No branch-6 gate failure exists.

## Review round, mode and baseline

- Round 3, **full pass**. The maintainer explicitly asked for a full pass, which overrides the delta option.
- Baseline: rounds 1 and 2 were published by pr-review2 at an earlier metadata.version. The exact version and fingerprint were not supplied, but the fingerprint differs from this run. The model family is the same (`claude`). baseline_identity: **skill_differs**. The previous skill identity is "pr-review2, earlier version, different fingerprint (values not supplied)". The previous reviewer is the same model family, with host not supplied. That baseline may not have checked what this version now checks. In particular, the round-2 "Minor, blocking" labels predate this version's peer materiality rules.
- Previous reviewed head: the fixture says there has been no commit since round two, so the previously reviewed head is the current head `eeee...eeee`. That SHA is derived from this statement, not from a supplied pin.
- Coverage this pass: `src/gate.py` was reviewed in full (all 13 lines). `tests/test_gate.py` was **not inspected**: only its summary was supplied (G1). That makes 1 of 2 changed files reviewed. No prior coverage is reused.

## Published blocker status (re-review)

| ID | Prior state | Current state | Blocker? now | Evidence | Author disposition |
|---|---|---|---|---|---|
| F-03 | open, "Minor, blocking" | open, should-fix | **No** (guard_bypass) | see F-03 | asked for reassessment, no fix |
| F-04 | open, "Minor, blocking" | open, should-fix | **No** (guard_bypass) | see F-04 | asked for reassessment, no fix |
| F-05 | open, "Minor, blocking" | open | **Yes** (branches 2 and 1) | see F-05 | asked for reassessment, no fix |

The code has not changed since round two. F-03 and F-04 are reclassified because this skill version applies the materiality rules to the existing evidence. Their state is not changed and no claim of new evidence is made. No new findings were added this round, so no present_at_previous_head values are needed.

## Blockers

### F-05 - refusal message names the wrong environment variable

- Location: `src/gate.py:9`
- Anchor (verbatim head line, not mechanically verified): `        sys.exit("refusing nested gate on " + root + "; unset TOOL_GATE to override")`
- Class: `gate.refusal-guidance-marker-name`. Instances: `src/gate.py:9`.
- Severity: Minor. **Blocker? Yes.**
  - Branch 2: the DoD requires an error "that tells the user how to proceed". The message tells the user to do something that does not work, so that DoD part fails.
  - Branch 1: the defect also passes the materiality bar. The trigger is ordinary use: every same-root nesting, the exact scenario in the issue, prints this message. The consequence is concrete: the message leads the user to a wrong action.
  - Materiality rules 1-5 cannot relax branch 2. Rule 3 (fix_surface) does not apply: F-05 is not a new round-3 finding, and nothing shows line 9 was added only to address another finding. Rule 5 (deferral) does not apply because no disclosed author-opened follow-up issue was supplied, and deferral cannot clear a branch-2 failure anyway.
- Trigger/path: run `tool gate -- <command>` where `<command>` re-enters `tool gate` on the same root.
  1. In the child, `os.environ.get(MARKER) == root` at line 8 is true.
  2. Line 9 exits with "...; unset TOOL_GATE to override".
- Expected: the guidance names the variable that actually controls the refusal. That variable is `MARKER = "TOOL_GATE_ROOT"` (`src/gate.py:2`).
- Actual: the guidance names `TOOL_GATE`, which nothing reads. Line 8 reads only `TOOL_GATE_ROOT`, and line 13 sets only `TOOL_GATE_ROOT`. A user who unsets `TOOL_GATE` as told gets the same refusal again. That outcome is a supplied, verified observation and agrees with the static trace: `TOOL_GATE` appears nowhere except inside the line-9 string literal.
- DoD test clause: the tests are summarized as proving only that a same-root nested gate exits with "refusing nested gate on". The guidance text is not asserted, so "a test proves it" holds for the refusal but not for the how-to-proceed part. This is the same root cause and stays on this finding.
- Verification: complete static trace of `src/gate.py` plus the supplied observation. No local execution.
- Remedy:
  1. Build the guidance from the constant, for example `"; unset " + MARKER + " to override"`. Then the message cannot drift from the marker again.
  2. Add a test assertion that the refusal message names `TOOL_GATE_ROOT`. Ideally, also assert that running with that variable removed is no longer refused at line 8.
  3. Search for further hard-coded copies of the variable name in tests and docs. I could not inspect `tests/test_gate.py`.

## Should-fix (non-blocking, materiality rules)

Both findings belong to one class: **`gate.early-diagnostic-launcher-identity`**. The early diagnostic identifies a nested gate from the spelled basename of `argv[0]`. One fix point closes both: `src/gate.py:4`. This is the second same-class finding, so a sweep was run (see Propagation sweep). The third-instance design-note rule is not triggered: there are two instances, and no test guards this class.

Deciding evidence for guard versus boundary (rule 2), applied in order:

1. Project docs call the gate "a local convenience running the user's own commands". Nothing names it a security or trust boundary.
2. The security baseline pass finds no untrusted source. `argv` is the user's own command, and bypassing the diagnostic causes no effect the user could not already cause.
3. Nothing claims the diagnostic resists indirect launchers or path tricks, so there is no contradicted claim.
4. It is therefore a convenience guard.

Rule 1 (immaterial) also holds: the supplied observation shows that in both cases the child reaches line 8 and is refused, and nothing loops. The only user-visible difference is which refusal message prints.

### F-03 - early diagnostic and a symlinked `./via/../tool gate` spelling

- Location: `src/gate.py:4`. Anchor: `    if os.path.basename(argv[0]) == "tool" and argv[1:2] == ["gate"]:`
- Severity: Minor. **Blocker? No.** Basis `guard_bypass`, deciding evidence above. Origin: change.
- Trigger: `./via/../tool gate` where `via/` is a symlinked directory. That is an odd path spelling, which rule 2.4 names explicitly.
- Result: the supplied observation says the child still reaches line 8 and is refused, and no recursion occurs. The DoD behavior holds.
- Verification note (open discrepancy, non-material): a static trace of line 4 conflicts with the stated miss. `os.path.basename("./via/../tool")` splits strings and does not resolve symlinks, so it returns `"tool"`. The diagnostic should therefore fire for that exact argv. The supplied observation says the child reached line 8, which implies the diagnostic did not fire. The actual argv used in the observation was not supplied, so I cannot settle which is right. Either way, blocker status is No and the user-visible outcome is a refusal.
- Remedy (optional): see the approach reassessment. Prefer dropping or demoting the spelling check over adding more spelling cases.

### F-04 - early diagnostic and a binary named `TOOL` on a case-insensitive filesystem

- Location: `src/gate.py:4`, same anchor as F-03.
- Severity: Minor. **Blocker? No.** Basis `guard_bypass` (a case trick, named in rule 2.4), deciding evidence above. Origin: change.
- Trigger: on a case-insensitive filesystem, a project binary literally named `TOOL`. `os.path.basename("TOOL") == "tool"` is false, so the diagnostic returns `None`.
- Result: the child is spawned, line 8 refuses it, and nothing loops (supplied observation). The user sees line 9's message instead of line 5's. Once F-05 is fixed, that message is correct too.
- Remedy (optional): same as F-03.

## Contract traceability

| ID | Criterion | State | Implementation | Verification |
|---|---|---|---|---|
| R1 | A nested gate on the same root is refused | met | `src/gate.py:8-9` (marker check), `:13` (marker set for child) | static trace; tests summarized as asserting "refusing nested gate on"; supplied observation that every same-root nesting is refused |
| R2 | The refusal error tells the user how to proceed | **unmet** | `src/gate.py:9` | static trace plus supplied observation (F-05) |
| R3 | A test proves it | partial | `tests/test_gate.py` (content not supplied) | the summary covers R1 only, not R2 guidance (folded into F-05) |

## Dimension coverage

1. Issue scope: R2 is unmet (F-05). No scope creep is visible in the two changed files. Whether early_diagnostic is broader than the DoD is listed under verification gaps (G3).
2. Structural integrity: required lint and tests passed at head (supplied). No local command was run. Base behavior was not supplied.
3. Legacy/stale code: no removals are visible. The base was not supplied, so this cannot be fully assessed.
4. Technical debt: debt introduced is two overlapping nested-gate detectors. The spelling-based diagnostic at line 4 duplicates the spelling-independent marker check at line 8 and is the source of F-03/F-04. Debt closed: the unbounded recursion from the issue.
5. Documentation: no docs changed. The user-facing message claim is F-05.
6. Conventions: not assessable. AGENTS.md and REVIEW.md were not supplied (G2).
7. Follow-up hygiene: F-05 is fixed in this PR. F-03 and F-04 can land as suggestions, a small commit, or an author-opened issue. The reviewer opens nothing.
8. Correctness: all 13 lines of `src/gate.py` were traced. Findings are F-03, F-04 and F-05. Open questions are G3 and G4.
9. Security: baseline pass done, not applicable. There is no new untrusted-input path. `spawn` takes an argv list with no shell string interpolation. The marker comes from the user's own environment. Docs define no trust boundary. No specialist pass is needed.
10. Tests: the refusal is covered per the summary. The guidance text is not asserted (F-05). Test file content was not inspected (G1). Mutation: applicable, skipped, no project-pinned runner.
11. Skill quality: not applicable, no skill bodies touched.
12. PR description: the issue reference is present. Body text was not supplied, so claim-versus-diff truthfulness cannot be checked (G2).

Focused lenses:

- Errors/fallback: applied. Both refusal paths exit non-zero through `sys.exit(str)`, and no error becomes a success.
- Type invariants: not applicable, no types changed.
- Comments/claims: applied to the user-facing message (F-05).
- Test resilience: applied as far as the summary allows (F-05, G1).

## Verification gaps

- G1 (material, `environment`): `tests/test_gate.py` was not inspected.
- G2 (material, `environment`): PR body, base code, instruction/REVIEW.md files and the `run_gate` caller were not supplied.
- G3 (open question to the author): line 4 refuses any command that starts with `tool gate`, whatever its root. The DoD only asks for same-root refusal. If direct nesting with a different root is a supported use, this would be a regression. It is not a finding because no evidence shows such use is supported or was allowed at base. It was present at the previously reviewed head, since the code has not changed.
- G4 (non-material): line 4 reads `argv[0]` without a length check, so an empty `<command>` would raise `IndexError`. Whether the CLI rejects an empty command upstream was not supplied.
- G5 (material, `environment`): validator, anchor verifier and fingerprint were not run, so the anchors above are not mechanically verified.
- G6 (non-material): the static-trace versus observation discrepancy for F-03's exact argv.

## Propagation sweep

- `gate.early-diagnostic-launcher-identity`: I read all 13 lines of `src/gate.py` looking for identification by spelled command name. The only instance is `src/gate.py:4`. The sweep is **partial**: `tests/test_gate.py` was not inspected.
- `gate.refusal-guidance-marker-name`: I searched `src/gate.py` for literal environment-variable names versus the `MARKER` constant. Lines 8 and 13 use `MARKER`; line 9 hard-codes `TOOL_GATE`. The only instance is `src/gate.py:9`. The sweep is **partial** because tests and docs were not inspected.
- Net: the PR closes the recursion bug. One user-facing guidance defect remains, plus an avoidable duplicate detector.

## Approach reassessment (round three, open blocker)

- Recurring classes across rounds:
  - `gate.early-diagnostic-launcher-identity` (F-03, F-04).
  - `gate.refusal-guidance-marker-name` (F-05), a single instance and not recurring.
- Pattern: F-03 and F-04 patch symptoms of one design choice. They detect nesting from how the command is spelled (line 4). Every new spelling, whether a symlink, a `..` path, a case variant or an indirect launcher, produces another instance. Meanwhile the environment marker (lines 8 and 13) already refuses all of them independently of spelling. That is the reason nothing loops.
- Alternative A: drop `early_diagnostic` and rely only on the marker.
  - For: one detector, no spelling cases, and F-03/F-04 disappear.
  - Against: one child process starts before the refusal, and the friendlier "command starts tool gate again" wording is lost unless it moves into the line-9 message.
- Alternative B: keep the diagnostic as an explicitly best-effort hint and resolve identity instead of spelling. For example, use `shutil.which` with `os.path.realpath`/`os.path.samefile` against the running executable.
  - For: earlier refusal in common cases.
  - Against: more filesystem logic, and indirect launchers are still missed. The marker stays the real guard, so this complexity buys little.
- Remaining blockers against the materiality bar:
  - F-03: does not meet it (guard_bypass, immaterial).
  - F-04: does not meet it (guard_bypass, immaterial).
  - F-05: **meets** it (ordinary trigger, misleading guidance) and also fails DoD branch 2.
- Recommendation: converge after F-05. Fix line 9 to use `MARKER` and add the guidance assertion. Then approve, with F-03 and F-04 kept as suggestions, preferably via Alternative A. Do not run further fix rounds for spelling variants.

## Risk

Low. The change is a local developer-CLI convenience guard: two files, no persistent state, no deploy, auth or CI surface. Blast radius is limited to users nesting `tool gate`. Rollback is a plain revert, with no irreversible state. No special human-scrutiny category applies. Human reassessment is requested only because of the round-three cap.

## Out-of-scope observations

None. Concerns anchored on changed lines but not verified are listed under Verification gaps.

## Carried

None. No previously missed non-critical base concern was identified.

## How to finish this review

1. Supply `tests/test_gate.py` content, the PR body and the instruction files.
2. Run the validator and anchor verifier on a real review.json at head `eeee...eeee`, and compute the skill fingerprint.
3. Answer G3.
4. After the F-05 fix, refresh the lint and tests gates at the new head.
