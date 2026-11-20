reviewer: pr-review2
skill-version: 2.11.0
candidate-sha256: 9398fd9497fbcc122a6903318639aeed88baf66fd7f62223adafc9a2407490c0
case: 33-launch-check-false-refusal
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: PASS
- Expected: Expected negative verdict; realistic Minor still blocks and is not relaxed.
- Observed: Not ready to merge; F1 on line 4 refuses the README-documented command, Minor, Blocker? Yes through branch 1, passes the bar; guard_bypass explicitly ruled out; marker on line 8 judged correct.
- False blockers: 0. Harmful false positives: 0.
- Tool policy: offline fixture; one fresh-context Claude Code subagent per case, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus that case's input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: single run, scored after the run against the hidden oracle.

## Raw reviewer output

# PR Review 2 - peer review, round 1 (offline synthetic fixture)

**Verdict: Not ready to merge** (REQUEST_CHANGES equivalent)

1 verified finding, 1 blocker. The new early diagnostic refuses the project's documented
standard pre-push command `tool gate -- ./scripts/toolchain-check.sh`, which the base
revision ran successfully. It is Minor by severity but meets the peer materiality bar, so it
blocks through branch 1.

Run status: **incomplete** (assessed by the reviewer, not computed by the validator; see
"Run status" below). The negative verdict rests on a proven blocker. Coverage is incomplete
too, and that is reported separately below.

## Skill identity and reviewer

- Skill: pr-review2, metadata.version 2.11.0, read from
  `eval-run/33-launch-check-false-refusal/skill/`.
- Package fingerprint: **not computed**. Computing it needs `scripts/review_record.py
  --skill-fingerprint` or a shasum pipeline, and this offline exercise forbids running any
  script. I did not copy a fingerprint from anywhere.
- Reviewer host: Claude Code agent (Claude Agent SDK). Model family: claude.

## Run status

- No review.json or validator-output.txt was produced. The review record says fixture-only
  exercises must not fabricate a record for unavailable metadata, and the brief forbids
  running the validator and anchor verifier. So the run status below is my assessment, not
  validator output.
- State: incomplete. approved_scope_status: not computed.
- Reasons, with their causes:
  - environment: offline fixture. There is no repository, AGENTS.md, cli/shared/AGENTS.md,
    REVIEW.md or project policy to read, and no callers of `run_gate` to trace.
  - environment: `tests/test_gate.py` is supplied only as a prose summary, not as source,
    so the test file was only partly inspected.
  - environment: no execution, so no red/green reproduction and no anchor verification.
- Stopped: no. All planned dimensions were evaluated on the evidence supplied.

## Subject and contract

- PR: synthetic fixture (no URL or title). Base `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`,
  head `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`. The input is not dirty, so there is no
  patch digest.
- Linked issue: `tool gate -- <command>` recursed without end when `<command>` itself started
  `tool gate` on the same project root.
- The PR body says "Closes the linked issue", so a linked-issue reference is present and
  branch 5 does not apply.
- Instruction and REVIEW.md paths reviewed: none were available in the fixture, so none were
  loaded.

### Acceptance criteria

| ID | Criterion (issue DoD) | State | Implementation | Verification |
|---|---|---|---|---|
| AC1 | A nested gate on the same root is refused with a clear error | met | `src/gate.py:8-9`: `if os.environ.get(MARKER) == root:` / `sys.exit("refusing nested gate on " + root)`. `src/gate.py:13` sets `TOOL_GATE_ROOT` in the child env. | static trace, plus the supplied summary of `tests/test_gate.py` |
| AC2 | A test proves it | met | `tests/test_gate.py` (summary): runs a child that calls `tool gate` on the same root and asserts exit with "refusing nested gate on" | CI passed at head (fixture statement), plus the test summary |

Limit on AC1/AC2: in a nested `tool gate -- make` scenario, the child's argv[0] is not a
`tool` executable, so execution reaches the marker check on line 8. The test therefore
exercises the marker path and not the early diagnostic. I could not confirm this from test
source, because only a summary was supplied.

## Gates

- Required CI at head `bbbb...`: **passed**. Source: the fixture's statement "Trusted
  required CI passed at head". I did not observe individual check names locally.
- Local commands: none were run (offline, execution forbidden).
- Mutation: applicable, because decision logic changed. Status: skipped, no project-pinned
  runner. The fixture shows no StrykerJS, Stryker.NET or other pinned runner config, and no
  policy or user demand for mutation testing.
- Security specialist pass: not applicable (see Security).

## Timing

No clock or timestamped logs were available. elapsed, active_review, verification and
ci_wait are all unknown (null).

## Coverage

- Changed files reviewed: 2 of 2.
  - `src/gate.py`: reviewed in full (complete new file, 13 lines).
  - `tests/test_gate.py`: partial. Only the fixture's prose summary was available.
- Callers of `run_gate` and `early_diagnostic`: none supplied, so the CLI entry point that
  builds `argv` and `root` was not traced. The meaning of `argv` was inferred from line 13,
  `spawn(argv, ...)`, which spawns `argv` as the child command. The supplied test input
  `["tool", "gate", "--", "make"]` for the early message is consistent with that.
- Review mode: round 1, full pass. No published or local baseline exists, so there are no
  Carried items.

## Risk

Medium. This is developer tooling on the standard pre-push path. Blast radius: every
developer who uses the README pre-push command, and any gated command whose executable
basename contains the substring "tool". It is reversible: reverting or narrowing
`early_diagnostic` restores base behavior. The change involves no data or deployment state,
so rollback is a code revert. There is no auth, billing, credential, CI-privilege or
installer surface, and no extra human scrutiny is required beyond normal review.

## Blockers

### F1 `gate.early-diagnostic-false-refusal` - substring match refuses legitimate commands

- Location: `src/gate.py:4`. Anchor quote, verbatim at head:
  `    if "tool" in os.path.basename(argv[0]):`
  Related: `src/gate.py:5`: `        return "refusing nested gate: the command starts tool gate again"`
- Severity: Minor. I accept the team's impact classification: no data is lost, and running
  the check directly without the gate is a workaround.
- **Blocker? Yes.** Branch 1: a reachable regression introduced by the change, which passes
  materiality rule 1.
- Trigger/path: the README's standard pre-push command `tool gate -- ./scripts/toolchain-check.sh`.
  1. `argv` is the child command (line 13 spawns it), so `argv[0] = "./scripts/toolchain-check.sh"`.
  2. Line 8: no `TOOL_GATE_ROOT` marker exists in a top-level run, so the check is skipped.
  3. Line 10 calls `early_diagnostic(argv)`.
  4. Line 4 evaluates `os.path.basename("./scripts/toolchain-check.sh")`, which is
     `"toolchain-check.sh"`. `"tool" in "toolchain-check.sh"` is True.
  5. Line 5 returns the refusal message, and lines 11-12 call `sys.exit(message)`. The
     process exits non-zero, and `spawn` is never called.
- Expected: the gate runs `./scripts/toolchain-check.sh` as it did at base. The command does
  not start `tool gate`, so it is not a nested gate.
- Actual: the gate refuses with "refusing nested gate: the command starts tool gate again".
  The command fails, and the message is false.
- Materiality (rule 1), both conditions hold:
  - Realistic trigger in ordinary, non-adversarial use: it is the README-documented
    standard pre-push command, run unmodified. No crafted input is involved.
  - Concrete user-visible consequence: a failed command, plus a message that leads the user
    to a wrong action. It tells them their command re-invokes `tool gate`, so they will look
    for a nonexistent recursion or abandon the gate.
  - The team's Minor classification sets severity only. The bar does not require data loss.
    The rule lists "a failed command" and "a message that leads the user to a wrong action"
    as qualifying consequences, and a manual workaround does not remove either one.
- Why the other rules do not relax it:
  - Rule 2 (guard versus boundary): this is a false refusal of a legitimate, uncrafted input,
    not a bypass of the guard by a contrived input. guard_bypass does not apply.
  - Rule 3 (fix-surface churn): this is round 1, so it does not apply.
  - Rule 4 (pre-existing behavior): the base revision ran the command successfully, and
    `src/gate.py` is entirely new. Origin is change.
  - Rule 5 (deferral): the PR body discloses no follow-up issue. The reviewer does not defer
    on the author's behalf.
- Second consequence of the same line: line 4 ignores `root`, so the early diagnostic also
  refuses any `tool gate` child on a different root. The marker check deliberately allows
  that, and the issue limits refusal to the same root. Whether different-root nesting is
  used in practice is not evidenced, so this is recorded only as part of the same fix point.
- Counterevidence checked:
  - There is no upstream normalization of argv to stop this, since `run_gate` receives argv
    directly and passes it to `spawn`.
  - Required CI passed, but according to the test summary the only early-diagnostic test is
    the positive case `["tool", "gate", "--", "make"]`. No negative case covers a non-gate
    command whose basename contains "tool".
  - The behavior is not intentional per the PR body, which describes the diagnostic as
    naming "the common direct self-invocation", not refusing every `*tool*` executable.
- Verification method: complete static trace of the 13-line file, plus the fixture's README
  and base-behavior statements. No runtime red/green was performed (execution forbidden).
  Regression verification is unverified at runtime.
- Reproduction for a recipient with the code: call
  `run_gate("/repo", ["./scripts/toolchain-check.sh"], spawn=<recording stub>)` with
  `TOOL_GATE_ROOT` unset. Expected at head: `SystemExit` with
  "refusing nested gate: the command starts tool gate again", and the stub is not called.
  At base, the end-to-end `tool gate -- ./scripts/toolchain-check.sh` succeeds per the
  fixture.
- Remedy:
  - Option 1: remove `early_diagnostic`. The root marker already satisfies the DoD and
    produces a clear error.
  - Option 2: make the diagnostic exact. Match only when the child really invokes this gate:
    `os.path.basename(argv[0]) == "tool"` and `argv[1:2] == ["gate"]`, or better, resolve
    `argv[0]` to the same executable as the running tool. Make it apply only when the
    nested root would equal `root`, or leave root-sensitive refusal to the marker.
  - In either case, add a negative regression test that runs the README command
    (`["./scripts/toolchain-check.sh"]`) and asserts that `spawn` is called and the process
    does not exit. Search for other substring-based executable matches. The sweep below
    found none in the reviewed diff.

## Should-fix (non-blocking)

None.

## Optional suggestions

None.

## Twelve dimensions

1. Issue scope: AC1 and AC2 are met (table above). No scope creep beyond the added
   diagnostic, which is the subject of F1.
2. Structural integrity: required CI passed at head (fixture). F1 is a regression of the
   documented pre-push command, which worked at base.
3. Legacy/stale code: not applicable. This is a new file with no removals or renames.
4. Debt: introduced, a heuristic executable-name match (F1). Closed: the unbounded
   recursion from the issue.
5. Docs: the README is unchanged. Its documented command now fails, which is covered by F1.
   No doc text was added by the diff.
6. Conventions: project conventions files were not available in the fixture. No convention
   finding.
7. Follow-up hygiene: F1 is `Blocker? Yes` and must be fixed in this PR. The author may move
   it to an author-opened issue disclosed in the PR body only under materiality rule 5. No
   such disclosure exists.
8. Correctness: F1. Lines 8-9 and 13 (the marker) were traced and are correct for the
   same-root nesting case.
9. Security: no new untrusted-input path. `TOOL_GATE_ROOT` is an accident-prevention marker,
   not a trust boundary, and nothing in the fixture names it one. argv is passed to `spawn`
   as a list, not as a shell string. A specialist pass is not required.
10. Tests: the positive early-diagnostic test and the marker test exist (summary). The
    missing negative case is part of F1's remedy. Mutation was skipped (no pinned runner).
11. Skill quality: not applicable, no skill bodies touched.
12. PR description: the issue reference, summary and test claims are present. The body
    claims tests "cover both". It does not claim that the diagnostic refuses only
    self-invocations, so I found no strictly contradicted claim and branch 3 is not
    computed. F1 still stands through branch 1.

Focused lenses:

- Errors/fallbacks: applies to the refusal paths. F1 is the over-refusal. The marker path is
  correct.
- Type invariants: not applicable.
- Comments/docs: covered under dimension 5.
- Test resilience: the summary indicates behavior-level assertions on exit text, with the
  negative gap noted.

## Propagation sweep

- Class: `gate.early-diagnostic-false-refusal` (self-invocation detection by substring of
  argv[0]).
- Search: manual read of every line of the full changed source `src/gate.py` (13 lines) for
  substring or `in` matches on executable names or paths. Only the summary of
  `tests/test_gate.py` was available.
- Instances found: `src/gate.py:4`, the only one.
- Not covered: the CLI entry point that calls `run_gate` (not supplied).

## Verification gaps

- G1 (material: no). Line 8 compares `root` by exact string. If callers could pass
  differently spelled roots (trailing slash, symlink), a nested gate on the same root could
  slip past the marker. The code that computes `root` was not supplied. For ordinary nested
  use, the nested `tool gate` presumably derives root the same way, so this is unverified
  and not admitted as a finding. If it were confirmed with contrived spellings only, it
  would be a non-blocking guard_bypass should-fix.
- G2 (material: no for the verdict, yes for run completeness). There is no runtime red/green
  reproduction of F1, and the test file was inspected only through its summary.

## Out-of-scope observations

None.

## Carried

Unavailable. No qualified first-pass baseline exists (round 1).

## How to finish this review

Obtain the repository at head `bbbb...`. Read AGENTS.md, cli/shared/AGENTS.md and any
REVIEW.md files, the CLI caller of `run_gate`, and `tests/test_gate.py`. Run the F1
reproduction on base and head. Build review.json and run `scripts/review_record.py` and
`scripts/verify_anchors.py` against the head, and compute the skill fingerprint. None of
this would change the verdict while F1 is open.
