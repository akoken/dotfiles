reviewer: pr-review2
skill-version: 2.11.1
candidate-sha256: f79409f6f0e85c3aaeaaef8d089ae86847ad7b85ea9dbe26f220a95758b87609
case: 38-gate-third-round
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: PASS
- Observed: Not ready to merge; F-05 Blocker? Yes (branch 2 and meets the bar); F-03 (tool.real) and F-04 Minor should-fixes, basis guard_bypass; reassessment lists materiality per remaining finding and recommends converging after the single F-05 fix.
- Tool policy: offline fixture; one fresh-context Claude Code subagent per case, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus that case's input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: run 2 at 2.11.1 on the corrected fixture (see the run 1 result for this case), scored after the run against the hidden oracle.

## Raw reviewer output

# PR Review 2 - round three reassessment (offline synthetic fixture)

**Verdict: Not ready to merge.** 3 verified findings (all carried from round two, 0 new);
1 computed blocker (F-05). F-03 and F-04 no longer block: they are relaxed to non-blocking
should-fixes under materiality rule 2 (guard_bypass). Coverage is also incomplete (see
Coverage and Run status); the negative verdict rests on the proven blocker regardless.

## Skill and reviewer identity

- Skill: `pr-review2`, metadata.version `2.11.1`, read from `skill/` in this fixture
  directory.
- Package fingerprint: **not computed**. The fixture forbids program execution, so
  `scripts/review_record.py --skill-fingerprint skill` was not run and no value is copied
  from anywhere else.
- Reviewer: host Claude Code, model family `claude`.

## Run status

- No review.json was built and no validator was run (fixture forbids execution and asks not
  to invent review.json). Run status is therefore **not validator-computed**; by the record
  rules this run would be **incomplete** with these sources:
  - context: root AGENTS.md, cli/shared/AGENTS.md and REVIEW.md files were not supplied
    (cause environment);
  - file: `tests/test_gate.py` content not supplied, only a summary of what it proves
    (cause environment);
  - PR body text not supplied, so Check 12 claim-vs-diff could only use the supplied
    statement about project docs (cause environment);
  - callers of `run_gate`/CLI argv parsing not supplied (cause environment).
- approved_scope_status: not applicable (no scope limit; maintainer asked for a full pass).
- stopped: no.
- review.json / validator-output.txt: none kept (not produced, per fixture).

## Subject

- Offline fixture, AURA peer mode. PR URL/title: not supplied.
- Linked contract: issue "`tool gate -- <command>` recursed without end when <command>
  started `tool gate` again on the same root". DoD: (R1) a nested gate on the same root is
  refused, (R2) with an error that tells the user how to proceed, (R3) a test proves it.
- Base `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`, head
  `eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee`. Clean committed input, no patch digest.
- Instruction/REVIEW.md paths reviewed: none available (not supplied).

## Required gates

| Gate | Required | State at head eeee... | Source |
|---|---|---|---|
| lint | yes (trusted policy) | passed | supplied trusted observation |
| tests | yes (trusted policy) | passed | supplied trusted observation |
| security specialist pass | no (no trust boundary changed, see Security) | not applicable | baseline pass below |

No local commands were run (fixture forbids execution). Gates are taken from the supplied
trusted observation, not inferred.

- Timing: no review clock was collected; active review, verification and CI-wait time are
  unknown.
- Mutation: applicable (changed decision logic in `src/gate.py`), **skipped: no
  project-pinned runner**; mutation is optional by policy and no tool is installed. No
  counts.

## Review round, mode and baseline

- Round three, **full pass** (maintainer explicitly requested a full pass, which overrides
  delta).
- Baselines: rounds one and two published by pr-review2 at an earlier metadata.version
  (exact version not supplied), different package fingerprint (value not supplied), same
  model family `claude`. Baseline identity: **skill_differs**. Since this is a full pass, no
  prior coverage is reused.
- Latest reviewed SHA: per the supplied observation there is no commit since round two, so
  round two reviewed this same head; the round-two commit_id/Reviewed-at-HEAD SHA itself was
  not supplied, so this is not independently pinned.

## Published finding status (re-review)

| ID | State | Current evidence | Author disposition | Round-2 status -> now |
|---|---|---|---|---|
| F-03 | open | `src/gate.py:4` unchanged; child still refused at line 8 | asked for reassessment, no fix | Minor blocking -> Minor **non-blocking** (guard_bypass) |
| F-04 | open | `src/gate.py:4` unchanged; child still refused at line 8 | asked for reassessment, no fix | Minor blocking -> Minor **non-blocking** (guard_bypass) |
| F-05 | open | `src/gate.py:9` unchanged | asked for reassessment, no fix | Minor blocking -> Minor **blocking** |

No finding is reopened and none is repeated without evidence; the status change for F-03 and
F-04 comes from applying the materiality rules of this skill version to unchanged code, not
from new code. No new findings this round, so present_at_previous_head does not apply.

## Blockers

### F-05 - refusal message names the wrong variable (`src/gate.py`)

- Severity: Minor. **Blocker? Yes** - branch 2 (DoD R2 unmet on the main refusal path) and
  branch 1 (reachable defect introduced by the change that passes the materiality bar).
  security_boundary: false (not relevant to blocking here).
- Anchor (head line 9):
  `        sys.exit("refusing nested gate on " + root + "; unset TOOL_GATE to override")`
  Marker definition (line 2): `MARKER = "TOOL_GATE_ROOT"`
- Trigger/path: any same-root nesting other than the literal direct form, for example the
  project's documented build script that itself runs `tool gate`. The child reaches line 8,
  `os.environ.get(MARKER) == root` is true, and line 9 prints the message.
- Expected: per DoD R2, the error tells the user how to proceed.
- Actual: it tells the user to unset `TOOL_GATE`, a variable the code never reads; the
  marker is `TOOL_GATE_ROOT`. A user who unsets `TOOL_GATE` as told sees the same refusal
  again (supplied verified observation).
- Materiality bar: realistic trigger in ordinary use (the project's own documented build
  script) and a concrete consequence (a message that leads the user to a wrong action).
  Both hold, so rule 1 does not relax it; branch 2 is not relaxable in any case.
- Test gap (same root cause): the test asserts only that the exit contains
  `"refusing nested gate on"`; nothing asserts the guidance, so DoD R3 does not cover R2.
- Verification: complete static trace of lines 2, 8-9 plus the supplied observation; no
  local execution (fixture limit).
- Remedy: make line 9 give guidance that actually works (at minimum name `MARKER`, e.g.
  build the text from `MARKER` instead of a literal, and state where it must be unset or
  that the inner command should be run directly), and extend `tests/test_gate.py` to assert
  the guidance names the real marker and that following it changes the outcome.
- Deferral: none disclosed; this Minor meets the bar, so it could move to an author-opened
  follow-up issue only under rule 5 (disclosed in the PR body with the link). However the
  branch-2 DoD failure is not relaxable by rule 5, so it must be fixed in this PR.

## Should-fix (non-blocking, relaxed by materiality rules)

Class `gate.nested-detection-by-launcher-name` (one shared fix point: the name test in
`early_diagnostic`). Second same-class finding, so the class was swept (see Propagation
sweep).

### F-03 - early diagnostic misses a renamed launcher copy

- Severity: Minor. **Blocker? No** - basis **guard_bypass** (rule 2), security_boundary
  false.
- Anchor (head line 4):
  `    if os.path.basename(argv[0]) == "tool" and argv[1:2] == ["gate"]:`
- Trigger: `tool gate -- ./tool.real gate ...` (copy of the launcher named `tool.real`).
  basename is `tool.real`, so line 4 is false and the early refusal is skipped.
- Actual effect: the child is spawned, reaches line 8 and is refused; nothing loops
  (supplied verified observation). DoD R1 still holds.
- Deciding evidence (rule 2 order): (1) project docs call the gate a local convenience
  running the user's own commands and nothing names it a security or trust boundary;
  (2) baseline security pass: the launcher name comes from the user's own command line, no
  untrusted source gains an effect it could not otherwise cause; (3) per the supplied
  observation nothing claims it catches indirect launchers (PR body text itself not
  supplied); (4) therefore a convenience guard, and a renamed launcher copy is a contrived
  input.
- Remedy (optional): see approach reassessment; preferably remove reliance on the launcher
  name rather than adding name variants.

### F-04 - early diagnostic misses `TOOL` on a case-insensitive filesystem

- Severity: Minor. **Blocker? No** - basis **guard_bypass** (rule 2), security_boundary
  false.
- Anchor: same line 4 as F-03 (`== "tool"` is case-sensitive).
- Trigger: a project binary literally named `TOOL` resolving to the launcher on a
  case-insensitive filesystem.
- Actual effect: as F-03, the child is refused at line 8; nothing loops.
- Deciding evidence: same as F-03; a case-variant name is a case trick under rule 2.4.
- Remedy (optional): same as F-03.

## Coverage

- Changed files: reviewed 1 of 2 in full.
  - `src/gate.py`: complete current content read, every function traced.
  - `tests/test_gate.py`: content not supplied; only the supplied summary of what it proves
    was used. Unreviewed.
- Dimensions:
  1. Issue scope: R1 met (static trace lines 8-9, 10-12; tests pass); R2 unmet on the
     line-9 path (F-05); R3 partial (test proves refusal, not the guidance).
  2. Structural integrity: required lint/tests passed at head; no local runs.
  3. Stale code: nothing found in `src/gate.py`.
  4. Debt: introduced - two overlapping nested-gate detectors (name heuristic and env
     marker); closed - the unbounded recursion.
  5. Docs: no changed docs supplied; F-05 is the user-facing text defect.
  6. Conventions: AGENTS.md not supplied; not assessable.
  7. Follow-up hygiene: F-03/F-04 may land as suggestions, a follow-up commit or an
     author-opened issue; F-05 is fixed in this PR.
  8. Correctness: traced; see findings and verification gaps.
  9. Security: baseline pass done, no trust boundary changed (below).
  10. Tests: see F-05 test gap; test file itself not read.
  11. Skill quality: not applicable, no skill bodies touched.
  12. PR description: linked issue reference present; body text not supplied, so claims
      could not be compared with the diff.
- Focused lenses: errors/fallbacks applied (refusal paths at lines 9 and 12); type
  invariants not applicable (no type changes); comments/docs applied to user-facing
  messages; test resilience limited by the unread test file.

## Security (baseline pass)

Assets/actors: a local developer CLI running the user's own commands. Entry points: argv
and the `TOOL_GATE_ROOT` environment variable, both controlled by the same local user. No
auth, tenant, secret, dependency or privilege change. No new untrusted-input path reaches a
sink beyond what the user can already run. No specialist pass needed.

## Risk

Low. Local convenience guard; blast radius is a developer's own invocation (wrong refusal
hint, or the early diagnostic skipped in favour of the child-side refusal). Fully reversible
by reverting the commit; no deployment, data or irreversible state. No special human
scrutiny area touched.

## Verification gaps

- G1 (not material to the verdict, but unresolved): `early_diagnostic` indexes `argv[0]`
  (line 4) without a length check; if `run_gate` can receive an empty argv (e.g.
  `tool gate --` with no command) it would raise IndexError. The argv parsing caller was
  not supplied, so reachability is unverified; not admitted as a finding.
- G2: how `root` is derived (normalisation, symlinks) is not supplied; the supplied
  observation that every other same-root nesting reaches line 9 is accepted as trusted.
- G3: `tests/test_gate.py`, AGENTS.md/REVIEW.md and the PR body were not supplied.

## Propagation sweep

- Class `gate.nested-detection-by-launcher-name`: searched the full reviewed diff content
  available (`src/gate.py`) for launcher-identity tests (`basename`, `argv[0]`, literal
  `"tool"`). Instances: `src/gate.py:4` (F-03 and F-04 are two inputs through this one
  line). `tests/test_gate.py` not covered (content unavailable), so the sweep is
  **partial**. No test guards this class, so the third-instance design-note rule is not
  triggered.
- Class for F-05 (`gate.refusal-hint-names-marker`): `src/gate.py:9` is the only message
  naming a variable; line 5's message gives no variable. Same partial coverage for tests.
- Net: debt introduced (duplicate detection) is small; closed debt (recursion) is the
  issue's goal.

## Approach reassessment (round three, open findings)

- Recurring class: `gate.nested-detection-by-launcher-name` - F-03 (round two), F-04 (round
  two). Both are symptoms of one design choice: a name-based pre-spawn heuristic layered
  over the env marker, which already refuses every same-root nesting regardless of launcher
  name. Further name variants (symlinks, wrappers, other case spellings) would keep
  producing the same class.
- Alternative 1: drop the name heuristic (lines 3-6, 10-12) and rely only on the marker,
  moving the actionable guidance into the marker refusal. Trade-off: the direct
  `tool gate -- tool gate ...` case spawns one child before refusing instead of refusing
  up front; in exchange the whole bypass class disappears and there is one message to keep
  correct.
- Alternative 2: keep the early check but compare resolved file identity
  (`os.path.realpath`/`os.stat` of the resolved argv[0] against the running launcher)
  instead of the basename. Trade-off: closes F-03/F-04 for copies resolving to the same
  file only partly (a true copy is a different inode), adds filesystem lookups, and still
  misses scripts that call the tool indirectly; less robust than Alternative 1.
- Materiality per remaining finding:
  - F-03: does not meet the bar (contrived guard bypass, child still refused).
  - F-04: does not meet the bar (case trick, child still refused).
  - F-05: **meets** the bar (ordinary documented build script, misleading message) and is
    also a branch-2 DoD failure.
- Recommendation: converge on F-03 and F-04 - treat them as suggestions and stop iterating
  on them. Not ready to approve until F-05 is fixed with a test asserting the guidance;
  after that single fix, with F-03/F-04 as suggestions and gates green at the new head, the
  PR should be ready to merge without another name-variant round. Human reassessment of
  the loop is requested as this is round three with an open blocker.

## Out-of-scope observations

None.

## Carried

None (no previously missed old non-critical concerns identified).

## How to finish

Fix F-05 and its test, then re-review the new head: read `tests/test_gate.py`, AGENTS.md
and REVIEW.md, the PR body and the `run_gate` caller (resolving G1/G2), refresh lint/tests
at the new head, and build review.json, run the validator and the anchor verifier, and
compute the skill fingerprint in an environment where execution is permitted.
