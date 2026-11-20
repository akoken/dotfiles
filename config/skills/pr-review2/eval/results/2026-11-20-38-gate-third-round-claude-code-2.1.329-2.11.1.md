reviewer: pr-review2
skill-version: 2.11.1
candidate-sha256: f79409f6f0e85c3aaeaaef8d089ae86847ad7b85ea9dbe26f220a95758b87609
case: 38-gate-third-round
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: PASS
- Observed: Not ready to merge; F-05 Blocker? Yes (DoD and branch 1); F-03 (tool.real) and F-04 Minor should-fixes, basis guard_bypass; reassessment recommends converging after the F-05 fix.
- Tool policy: offline fixture; one fresh-context Claude Code subagent per case, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus that case's input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: run 1 at 2.11.1, scored after the run against the hidden oracle. The reviewer flagged a non-material fixture inconsistency (VG-1): a direct `tool gate -- tool gate` exits at line 5, not line 9 as the input claimed. The case was corrected and rerun.

## Raw reviewer output

# PR Review 2 - round 3 (full pass) - offline synthetic fixture

**Verdict: Not ready to merge** (peer mode).

3 verified findings carried from round two (no new findings this round). 1 computed blocker
(F-05). 2 findings are non-blocking should-fixes relaxed under the materiality rules
(F-03, F-04, basis guard_bypass). Coverage is partial (see Coverage); the blocker alone
justifies the negative verdict.

Fastest path to merge: fix the refusal message on src/gate.py:9 so it names the real marker
`TOOL_GATE_ROOT` and says where to clear it, and extend the test to assert that guidance.
F-03 and F-04 can land as suggestions.

## Skill and reviewer identity

| Field | Value |
|---|---|
| Skill name | pr-review2 |
| metadata.version | 2.11.1 (read from the SKILL.md actually loaded) |
| Package fingerprint | not computed: this fixture forbids program execution, so `review_record.py --skill-fingerprint` could not run. Not copied from any report. |
| Reviewer host | Claude Code (Claude Agent SDK) |
| Reviewer model family | claude |

## Run status

- No review.json or validator-output.txt exists: this is a fixture-only exercise, which the
  skill and the fixture both say must not fabricate a record. The validator was therefore not
  run and run status is **not validator-computed**.
- Reviewer's assessment of incompleteness sources (not a validator result):
  - `tests/test_gate.py` content was not supplied; its behavior is known only from the supplied
    observation. Cause: environment (fixture did not supply the file).
  - Project instructions (root AGENTS.md, cli/shared/AGENTS.md, REVIEW.md files) and the PR
    body were not supplied. Cause: environment.
  - Skill fingerprint not computed. Cause: environment (no execution permitted).
- Run stopped: no. approved_scope_status: not applicable (no scope limit; the maintainer
  asked for a full pass).
- On this evidence the run would be **incomplete**; the verdict is still decided by a verified
  blocker.

## Subject

| Field | Value |
|---|---|
| PR URL / title / author | not supplied by the fixture |
| Linked contract | Linked issue reference present (number not supplied). Issue: `tool gate -- <command>` recursed without end when `<command>` started `tool gate` again on the same root. |
| DoD | A nested gate on the same root is refused with an error that tells the user how to proceed; a test proves it. |
| Base | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |
| Head | eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee |
| Patch digest | not applicable (committed head) |
| Changed paths | src/gate.py, tests/test_gate.py |
| Instruction / REVIEW.md paths read | none supplied; only the fixture's trusted statements about project docs ("local convenience running the user's own commands") |

## Required gates at head eeee...eeee

| Check | Required? | Status | Attribution | Evidence |
|---|---|---|---|---|
| lint | yes (trusted policy) | passed | not_applicable | fixture trusted policy line |
| tests | yes (trusted policy) | passed | not_applicable | fixture trusted policy line |
| Security specialist pass | not required | not run | n/a | no trust boundary changed (see Security) |

No commands were executed locally (forbidden by the fixture). Branch 6 does not match.

## Timing

Unknown. No review clock was collected; active review, verification and CI-wait times are
all unmeasured (null), not zero.

## Mutation

Applicable (changed decision logic in `run_gate` / `early_diagnostic`), **skipped: no
project-pinned runner**. Mutation is optional per the fixture and no tool is installed; not
required by policy or user, so no gate is left open.

## Review round and baseline

- Round 3, mode: **full** (explicit maintainer request; this overrides any delta option).
- Rounds 1 and 2 were published by pr-review2 at an earlier metadata.version with a different
  package fingerprint and the same reviewer model family. The fixture does not supply the
  earlier version string, fingerprint value or published SHAs.
- baseline_identity: **skill_differs** (same model family, different skill fingerprint). Not
  relevant to scope because this is a full pass, but disclosed: the earlier rounds may not have
  applied this version's materiality rules.
- Previously reviewed head: no commit since round two, so the round-two head is the current
  head eeee...eeee (per the fixture; the round-two pinned SHA itself is not supplied).
- Author reply disposition: no fix; the author asked for a reassessment instead.

## Published blocker status (re-review)

| ID | Round-2 state | Current state | Current blocker? | Reason for change |
|---|---|---|---|---|
| F-03 | Minor, blocking | open, non-blocking should-fix | No | New evidence and this version's materiality rule 2: the bypass is a contrived launcher rename on a convenience guard, and the child is still refused at line 8; nothing loops. |
| F-04 | Minor, blocking | open, non-blocking should-fix | No | Same as F-03: case trick on a convenience guard; child still refused at line 8. |
| F-05 | Minor, blocking | open | **Yes** | Unchanged code; still fails the DoD (branch 2) and passes the branch-1 materiality bar. |

No finding is repeated without evidence; each is re-traced below at the current head.

## Blockers

### F-05 - Refusal message names the wrong marker, so its "how to proceed" guidance fails

- **Location:** src/gate.py:9 (`run_gate` same-root refusal)
- **Anchor (verbatim, head):** `    sys.exit("refusing nested gate on " + root + "; unset TOOL_GATE to override")`
- **Supporting anchor:** src/gate.py:2 `MARKER = "TOOL_GATE_ROOT"`
- **Severity:** Minor
- **Blocker?** Yes
  - Branch 2: DoD requires the refusal error to "tell the user how to proceed". The only
    instruction it gives (`unset TOOL_GATE`) names a variable the code never reads; the
    marker is `TOOL_GATE_ROOT` (line 2, read at line 8). The DoD item is unmet. Materiality
    rules never relax branch 2.
  - Branch 1 materiality bar also met: realistic trigger in ordinary use (every same-root
    nesting prints this message, per the supplied verified observation) and a concrete
    consequence (a message that leads the user to a wrong action: a user who unsets
    `TOOL_GATE` as told sees the same refusal again).
  - Not a security/trust-boundary defect (security_boundary false). Not fix-surface churn:
    F-05 is a prior finding, not a new round-3 finding, and rule 3 never relaxes branch 2.
    Not deferrable under rule 5, which covers only branch-1 Minors.
- **Trigger/path:** `tool gate -- <command>` where `<command>` starts `tool gate` again on
  the same root. Outer gate: line 8 false, line 13 spawns the command with
  `TOOL_GATE_ROOT=<root>`. Inner gate: line 8 `os.environ.get(MARKER) == root` true, line 9
  exits with the message above.
- **Expected:** an error that names the actual override mechanism.
- **Actual:** tells the user to unset `TOOL_GATE`; doing so changes nothing, and the refusal
  repeats.
- **Additional static observation for the remedy:** line 13 re-injects `TOOL_GATE_ROOT` into
  every child environment from the outer gate, so unsetting the marker in the user's own
  interactive shell before starting the outer gate would not help either. Correct guidance must
  say to clear it for the nested invocation (for example `env -u TOOL_GATE_ROOT tool gate ...`
  inside the command) or to run the inner command without the outer gate.
- **Test weakness (same root cause, same remedy):** per the supplied observation, the test
  asserts only that a same-root nested gate exits with the prefix `"refusing nested gate on"`.
  It does not assert the guidance, so it did not catch the wrong variable name, and the DoD's
  "a test proves it" is only partially met for the how-to-proceed part.
- **Verification:** complete static trace of src/gate.py lines 2, 8, 9, 13 at head, plus the
  fixture's supplied verified runtime observation. No local execution (forbidden).
- **Remedy:** change line 9 to name `TOOL_GATE_ROOT` (preferably by interpolating `MARKER`
  so the name cannot drift again) and say where to clear it; extend tests/test_gate.py to
  assert the message names the real marker and, ideally, that following the guidance lets
  the nested gate proceed.

## Should-fix (non-blocking, relaxed by materiality rules)

Defect class for both: **`gate.nested-detection-by-launcher-name`** - `early_diagnostic`
identifies a nested gate by comparing the literal basename of `argv[0]` with `"tool"`, so any
other spelling of the same launcher slips past it. One shared fix point (line 4) closes both,
so they are one class with two instances. They remain two IDs because they were published
separately and keep stable IDs.

### F-03 - Early diagnostic misses a renamed launcher copy (`./tool.real gate`)

- **Location / anchor:** src/gate.py:4 `    if os.path.basename(argv[0]) == "tool" and argv[1:2] == ["gate"]:`
- **Severity:** Minor. **Blocker?** No.
- **non_blocking basis:** guard_bypass (materiality rule 2.4); security_boundary false.
- **Deciding evidence (rule 2, in order):** (1) project docs call the gate a local convenience
  running the user's own commands and nothing names it a security or trust boundary;
  (2) baseline security pass: the gated command is the user's own, no untrusted source reaches
  an effect it could not otherwise cause; (3) neither docs nor issue claim the gate catches
  indirect or renamed launchers (PR body not supplied; see limits); (4) therefore a
  convenience/accident-prevention guard, and a renamed launcher copy is a contrived input.
- **Trigger/path:** `tool gate -- ./tool.real gate ...`: basename is `tool.real`, line 4 false,
  parent spawns. Child reaches line 8 with `TOOL_GATE_ROOT=<root>` and is refused (supplied
  verified observation). Nothing loops.
- **Expected/actual:** early in-parent refusal expected; actual refusal happens one process
  later via line 9 with that message.
- **Remedy (suggestion):** see the approach reassessment; either drop the name-based early check
  in favor of the marker or compare resolved file identity instead of a name string.

### F-04 - Early diagnostic misses `TOOL` on a case-insensitive filesystem

- **Location / anchor:** same line, src/gate.py:4 (quote above).
- **Severity:** Minor. **Blocker?** No.
- **non_blocking basis:** guard_bypass (rule 2.4, "case tricks"); security_boundary false.
  Deciding evidence identical to F-03.
- **Trigger/path:** `tool gate -- TOOL gate ...` on a case-insensitive filesystem: basename
  `TOOL` != `"tool"`, line 4 false; child refused at line 8 (supplied verified observation).
  Nothing loops.
- **Remedy (suggestion):** same as F-03; one fix closes both instances.

## Verification gaps

- **VG-1 (non-material, unresolved suspicion, not a finding):** static reading suggests a
  direct `tool gate -- tool gate ...` takes the early path (line 4 true, exit at line 12 with
  line 5's message `refusing nested gate: the command starts tool gate again`), which gives no
  how-to-proceed guidance. The supplied verified observation says every same-root nesting
  prints line 9's message. The caller that builds `argv` is not supplied, so I cannot settle
  which applies. Ask the author to confirm; if line 5 is reachable, give it the same guidance
  when fixing F-05.
- **VG-2:** tests/test_gate.py content not supplied; reviewed only through the supplied
  observation. Cause: environment.
- **VG-3:** project instruction files, REVIEW.md files and the PR body not supplied; Check 6
  and Check 12 claim truthfulness could not be fully evaluated. Cause: environment.

## Contract traceability

| ID | Criterion | State | Implementation | Verification |
|---|---|---|---|---|
| R1 | Nested gate on the same root is refused (no endless recursion) | met | src/gate.py:8-9, :13 | static trace + supplied test observation ("exits with 'refusing nested gate on'") |
| R2 | Refusal error tells the user how to proceed | **unmet** (F-05) | src/gate.py:9 | static trace + supplied observation that following it fails |
| R3 | A test proves it | partial | tests/test_gate.py (not supplied) | proves refusal only, not the guidance (F-05) |

## Coverage

- Changed files: 2. Read in full at head: 1 of 2 (src/gate.py, all 13 lines, every function
  traced: `early_diagnostic`, `run_gate`). tests/test_gate.py: not read (not supplied),
  accounted for only by the supplied observation.
- Mode: full pass; no delta reuse, no prior coverage reused.
- Callers of `run_gate` / the argv builder: not supplied (see VG-1).

## Dimensions

1. Issue scope: R2 unmet, R3 partial (F-05). No scope creep observed in the supplied file.
2. Structural integrity: required lint/tests passed at head; no local run permitted.
3. Stale code: none found; `early_diagnostic` is redundant with the marker check but live.
4. Debt: introduced - two refusal paths with divergent messages and a name-based heuristic
   duplicating the marker check (see reassessment). Closed - the unbounded recursion.
5. Docs: no docs changed; supplied project docs ("local convenience") are consistent with code.
6. Conventions: project instruction files not supplied (VG-3).
7. Follow-up hygiene: F-05 must be fixed in this PR; F-03/F-04 may land as suggestions, a
   small follow-up commit or an author-opened issue.
8. Correctness: traced; F-05 and the F-03/F-04 class.
9. Security: baseline pass done. The gate runs the user's own commands; env marker only; no
   new untrusted-input-to-sink path, no auth, secrets or privilege change. Not a trust
   boundary per project docs; no specialist pass required.
10. Tests: prefix-only assertion misses the guidance (folded into F-05). Mutation skipped
    (no pinned runner).
11. Skill quality: not applicable, no skill bodies touched.
12. PR description: linked issue reference present (branch 5 does not match); body otherwise
    not supplied, so claim truthfulness is unverified (VG-3).

Focused lenses: errors/fallback - both refusal paths exit non-zero via `sys.exit`, no success
masking; type invariants - not applicable; comments/messages - F-05; test resilience - F-05
test weakness.

## Risk

Low. A local developer-convenience CLI guard; no deployment, persistent state, credentials or
trust boundary. Blast radius: users of `tool gate` who nest it. Fully reversible by revert;
rollback is a code revert, nothing irreversible. No special human scrutiny area triggered.
Owner/required approvals: not supplied.

## Propagation sweep

- Class `gate.nested-detection-by-launcher-name` (second same-class finding, so swept):
  search = read every line of src/gate.py for argv/launcher-name comparisons. Instances:
  src/gate.py:4 (F-03 and F-04 both rooted here). No other name-based detection in the file.
  **Partial sweep:** tests/test_gate.py and the argv-building caller were not available.
- Class for F-05 (`gate.refusal-message-marker-name`): searched src/gate.py for marker names in
  user-facing strings; one instance, src/gate.py:9. Line 5's message names no variable.
  Partial for the same reason.
- Third-instance design-note rule: not triggered (two instances, and no existing test guards
  the class).

## Approach reassessment (round 3 with open blockers)

- **Recurring class:** `gate.nested-detection-by-launcher-name` (F-03, F-04). Both round-two
  "blockers" patch symptoms of one design choice: detecting a nested gate by the spelling of
  `argv[0]`. Any name heuristic will keep missing symlinks, copies, case variants and wrapper
  scripts. F-05 is a separate one-off string defect, not a symptom of that design.
- **Alternative A (recommended):** treat the environment marker (lines 8 and 13) as the single
  authoritative mechanism and remove `early_diagnostic`, or keep it only as a best-effort hint
  with no promise of completeness. Trade-off: a direct nesting costs one extra process spawn
  before refusal; in exchange there is one refusal path, one message and no name heuristic to
  chase.
- **Alternative B:** compare resolved file identity (`os.path.realpath` / `os.path.samefile`
  against the running launcher) instead of the basename. Trade-off: closes copies only partly
  (a copy is a different file), handles symlinks and case, adds filesystem calls, and still
  misses wrapper scripts, so the marker remains necessary anyway.
- **Materiality test of each remaining finding:**
  - F-03: does not meet the bar (guard_bypass on a convenience guard; child still refused).
  - F-04: does not meet the bar (same).
  - F-05: **meets the bar** (ordinary trigger, misleading message) and also fails DoD branch 2.
- **Recommendation:** converge. Do not run more rounds on F-03/F-04; treat them as
  suggestions. Fix F-05 in this PR (a one-line message change plus one test assertion), then
  the PR is approvable on the current evidence. This cap does not grant approval: a human
  reassessment is requested before any further automated fix/review loop.

## Out-of-scope observations

None.

## Carried

Unavailable: the first-pass published report and its pinned SHA were not supplied, so no
qualified first-pass baseline exists for Carried attribution.

## Limits

Offline synthetic fixture: no network, git, gh, program, test or validator execution. All
gate outcomes, test behavior and runtime observations come from the fixture's trusted
statements; code analysis is static. Not a live AURA PR review; nothing was published.
