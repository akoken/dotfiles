reviewer: pr-review2
skill-version: 2.11.0
candidate-sha256: 9398fd9497fbcc122a6903318639aeed88baf66fd7f62223adafc9a2407490c0
case: 32-nested-launch-check
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: PASS
- Expected: Expected positive verdict with the contrived bypass as a non-blocking should-fix.
- Observed: Ready to merge, 0 blockers; F1 renamed-symlink bypass is a Minor should-fix, Blocker? No, basis guard_bypass, with the deciding guard-versus-boundary evidence; no security finding and no removal demand.
- False blockers: 0. Harmful false positives: 0.
- Tool policy: offline fixture; one fresh-context Claude Code subagent per case, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus that case's input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: single run, scored after the run against the hidden oracle.

## Raw reviewer output

# PR Review 2 report - nested gate refusal (synthetic fixture)

**Verdict: Ready to merge** (peer mode, round 1, full review of the fixture evidence).

0 blockers. 1 verified finding, a non-blocking Minor should-fix (F1, basis guard_bypass).
1 out-of-scope observation. 1 non-material verification question.

## Header

- Skill: pr-review2, metadata.version 2.11.0. Package fingerprint: not computed. Computing it
  needs `scripts/review_record.py --skill-fingerprint` or a shasum pipeline, and this fixture
  run allows no script or program execution. It is reported as unavailable, not copied.
- Reviewer: host Claude Code (agent CLI), model family claude.
- Mode: peer, round 1, full pass. No re-review baseline (first review).
- Subject: offline synthetic fixture (`input.md`). Base `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`,
  head `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`. Clean input, so there is no patch digest.
  No PR URL or number was supplied.
- Linked contract: the linked issue in the fixture. Trigger: `tool gate -- <command>` recursed
  without end when `<command>` itself started `tool gate` on the same project root. DoD: a
  nested gate on the same root is refused with a clear error, and a test proves it. The PR body
  says it "Closes the linked issue", so branch 5 does not apply.
- Instructions / REVIEW.md: the fixture includes no AGENTS.md, cli/shared/AGENTS.md or
  REVIEW.md. The only project policy used is the fixture's statement about project docs.
- Run status: not computed by the validator. This is a fixture-only exercise, so under the
  review record rules no review.json was created and no validator or anchor verifier was run
  (execution is not permitted). The verdict below comes from the supplied fixture evidence
  only. It is not a live AURA PR review.

## Gates

| Check | Required | State at head | Source |
|---|---|---|---|
| Trusted required CI | yes (fixture: "Trusted required CI passed at head") | passed | fixture statement; not observed locally |
| Local commands | n/a | none run (fixture forbids execution) | - |
| Mutation testing | applicable (new decision logic in `early_diagnostic`/`run_gate`) | skipped: the fixture shows no project-pinned runner, and neither policy nor the user requires one | fixture |
| Specialist security pass | not required (no trust boundary changed, see Security) | not applicable | fixture project docs |

Red/green: no local reproduction was possible. The required CI ran
`tests/test_gate.py` at head, and it includes the same-root nested child case. Red at
base was not observed. Static trace: without the line 8 check, nothing stops the child
`tool gate` from spawning again, which is the recursion the issue describes. Regression
verification is therefore static plus CI-green-at-head only.

Timing: no clock data available. Active review, verification and CI-wait times are unknown.

## Coverage

Reviewed 2 of 2 changed files.

- `src/gate.py`: read in full, lines 1-13, from the fixture.
- `tests/test_gate.py`: inspected only through the fixture's summary of its two tests. The
  fixture does not include the file text, so this is partial inspection.

Risk: Low. This is a new local developer-convenience module that runs commands the same
user typed, with that user's own privileges. It writes no persistent state and does not
touch credentials, CI or release. A revert rolls it back fully. Rollback is a code revert,
since no deployment behavior or irreversible state is involved.

## Contract traceability

| ID | Criterion | State | Implementation | Verification |
|---|---|---|---|---|
| R1 | A nested gate on the same root is refused with a clear error | met | `src/gate.py:8-9` (`if os.environ.get(MARKER) == root:` then `sys.exit("refusing nested gate on " + root)`), with the marker set for the child at line 13 | static trace, plus the CI-passed test that runs a child calling `tool gate` on the same root and asserts the exit message "refusing nested gate on" |
| R2 | A test proves it | met | `tests/test_gate.py` (fixture summary) | required CI passed at head (fixture) |

PR body claims checked against the diff:

- "a root marker that refuses any nested gate on the same root": implemented at lines 2, 8-9
  and 13. See observation O1 about cycles through a different root.
- "an early diagnostic that names the common direct self-invocation before the child
  starts": implemented at lines 3-6 and 10-12. Direct `tool gate` argv is caught.
- "Tests cover both": the fixture summary lists one test per mechanism.

## Findings

### Blockers

None.

### Should-fix (non-blocking under materiality rules)

**F1 `gate.early-diagnostic.renamed-launcher`** - Minor, Blocker? No, basis guard_bypass

- Location: `src/gate.py:4`
  - Quote: `    if os.path.basename(argv[0]) == "tool" and argv[1:2] == ["gate"]:`
- Trigger/path: the user creates a symlink `bin/runner` that points to the tool, then runs
  `tool gate -- bin/runner gate`. `os.path.basename("bin/runner")` is `"runner"`, not
  `"tool"`, so `early_diagnostic` returns `None` (line 6). The child starts.
- Expected vs actual: the early diagnostic only catches the literal `tool` basename, not
  renamed launchers. Actual outcome (verified observation in the fixture): no early message.
  The child then reads the marker at line 8 and exits with "refusing nested gate on
  <root>". No loop occurs.
- Causal anchor: changed line 4, which matches by basename only.
- Guard vs boundary, deciding evidence in rule 2 order:
  1. Project docs call the gate "a local developer convenience that runs commands the same
     user typed, with that user's privileges". No document calls the diagnostic a security
     or trust boundary.
  2. Baseline security pass: the bypassing input (a symlink plus argv) comes from that same
     user. It reaches no effect the user could not already cause, so there is no untrusted
     source and no boundary.
  3. Nothing claims the diagnostic resists such inputs. The PR body limits it to "the common
     direct self-invocation", and nothing claims it detects renamed or indirect launchers. No
     claim is contradicted, so branch 3 does not apply.
  4. Therefore this is a convenience guard. A renamed symlink is a contrived bypass, which
     makes this a non-blocking Minor should-fix (basis guard_bypass). The consequence is also
     small: the user still gets a clear refusal and nothing recurses.
- Verification: complete static trace of lines 4-13 plus the fixture's verified observation.
  No local execution.
- Remedy (optional; can be a suggestion, a small follow-up commit, or an issue the author
  opens): resolve the launcher before comparing. For example, compare
  `os.path.realpath(shutil.which(argv[0]) or argv[0])` with the tool's own resolved
  executable path, and keep the marker as the authoritative backstop. Or keep the current
  check and add a test showing that the renamed-launcher path ends in the marker refusal.

### Optional suggestions

None beyond the remedy above.

## Out-of-scope observations (1 of max 5)

- **O1 Cross-root cycles are not detected.** Line 13 replaces the marker with the current
  root (`env=dict(os.environ, **{MARKER: root})`), so the marker only records the innermost
  gate. Static trace: gate on A runs a command that runs a gate on B, which runs a gate on A.
  At the third level the marker is `B`, which is not `A`, so the gate proceeds. The cycle
  A, B, A, B, ... then continues without end.
  - Not admitted as a finding, for three reasons:
    1. It is not change-introduced. Before this change no nesting was detected at all, so
       this cycle already recursed, and the change makes no case worse.
    2. The issue's trigger and DoD describe a command that itself starts `tool gate` on the
       same root, and that case is met and tested.
    3. The fixture gives no evidence that any real configuration has such a cycle.
  - Caveat: if the author or maintainers read the PR body's "refuses any nested gate on the
    same root" to include nesting through an intermediate gate on another root, that claim
    is contradicted (branch 3).
  - Follow-up options: narrow the wording to "directly nested", or carry every ancestor root
    in the marker (for example `os.pathsep`-joined) and check membership, with a test.

## Carried

Not applicable (first review, no baseline).

## Verification gaps

- **G1 (non-material) Empty argv.** `early_diagnostic` reads `argv[0]` at line 4, which
  raises IndexError if `argv` is empty, for example `tool gate --` with no command. The
  caller and CLI parser are not in the fixture, so I cannot tell whether an empty command
  can reach `run_gate`. The issue's syntax `tool gate -- <command>` requires a command, so
  I did not raise a finding. If the parser accepts an empty command, guard it, for example
  with `argv[:1]`, or reject it with a clear message.
- **G2 (non-material) Fixture limits.** No local execution or red-at-base run. The test file
  text was not supplied. No AGENTS.md or REVIEW.md text was supplied. No package
  fingerprint, review.json, validator output or anchor verification, because no execution
  is allowed and fixture runs must not fabricate a record.

## Dimensions

1. Issue scope: met (R1, R2). No scope creep.
2. Structural integrity: new module. Required CI passed at head (fixture). No local run.
3. Stale code: none. This is a new file.
4. Debt: none introduced or closed, apart from O1, which is a pre-existing limit and not new debt.
5. Docs: no docs changed. The body's description matches the code (see O1 caveat).
6. Conventions: no AURA convention surface (skills, roles, selector) touched. No project
   convention text was supplied.
7. Follow-up hygiene: F1 is optional. O1 can become an issue the author opens if wanted.
8. Correctness: traced the same-root marker, the direct-invocation diagnostic, the
   renamed-launcher path (F1), cross-root nesting (O1) and empty argv (G1). Error lens:
   `sys.exit(str)` exits with status 1 and writes the message to stderr, which is a clear
   error. `spawn`'s result is returned unchanged.
9. Security: no new untrusted-input path. Commands and the environment variable come from
   the same local user with the same privileges. The `TOOL_GATE_ROOT` marker is not a trust
   boundary (fixture project docs). No specialist pass is needed.
10. Tests: both mechanisms are covered (fixture summary). The renamed-launcher path is not
    tested; this is optional (F1 remedy). Mutation: skipped, no project-pinned runner.
11. Skill quality: not applicable, because no skill bodies are touched.
12. PR description: linked issue present, and the claims match the diff (O1 caveat on "any").

## Propagation sweep

Defect class `gate.early-diagnostic.renamed-launcher`. Search: every argv/launcher identity
comparison in the reviewed diff (`src/gate.py` lines 1-13). Instances: `src/gate.py:4` only.
The marker comparison at line 8 depends on the caller's root string, not on launcher
identity, so it is not an instance. Legacy left: none. Debt introduced: none. Net: no
recurring class.
