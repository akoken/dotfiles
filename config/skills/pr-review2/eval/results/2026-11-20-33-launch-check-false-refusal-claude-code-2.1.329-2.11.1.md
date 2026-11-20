reviewer: pr-review2
skill-version: 2.11.1
candidate-sha256: f79409f6f0e85c3aaeaaef8d089ae86847ad7b85ea9dbe26f220a95758b87609
case: 33-launch-check-false-refusal
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: PASS
- Observed: Not ready to merge; F1 on line 4 refuses the README command, Minor, Blocker? Yes, passes the bar.
- Tool policy: offline fixture; one fresh-context Claude Code subagent per case, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus that case's input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: run 1 at 2.11.1, scored after the run against the hidden oracle.

## Raw reviewer output

# PR Review 2 - peer review, round 1 (offline synthetic fixture)

## Verdict

**Not ready to merge** (REQUEST_CHANGES). 1 verified finding, 1 blocker.

The new early diagnostic refuses the project's standard pre-push command
`tool gate -- ./scripts/toolchain-check.sh`, because it matches the substring `tool` in the command's
basename. The base revision ran that command successfully. This is a Minor regression that the change
introduced, and it passes the peer materiality bar, so it blocks under branch 1.

Run status: **incomplete**. This is a fixture-only exercise. No review.json was built, and the validator
and anchor verifier were not run, because the brief allowed no script execution. Project context files
were not available. The blocker is still proven by a complete static trace, so the negative verdict stands.

## Skill and reviewer identity

- Skill: `pr-review2`, metadata.version `2.11.1`.
- Package fingerprint: **not computed**. The brief forbids running scripts
  (`scripts/review_record.py --skill-fingerprint` or `shasum`). I did not copy it from anywhere.
- Reviewer: host Claude Code (Agent SDK subagent), model_family `claude`.

## Run status

- State: incomplete. No validator ran, so this comes from the fixture limits, not from validator output.
  approved_scope_status: not computed.
- Reasons:
  - environment: offline fixture with no repository, no AGENTS.md/REVIEW.md, and no gh metadata.
    Evidence: input.md line 3-4 ("Offline synthetic fixture: no live tools, execution, edits or publication").
  - other: no review.json, validator-output.txt or anchor verification. Script execution is forbidden
    by the review brief. Per the review record, fixture-only exercises do not fabricate a record.
- Stopped: no. All planned dimensions were evaluated against the supplied evidence.
- Kept artifacts: none (no review.json or validator-output.txt). This report is the only output.

## Subject

- PR: synthetic fixture. No URL or title was supplied.
- Base `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`, head `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`.
- Linked contract: resolved from the fixture. The issue is that `tool gate -- <command>` recursed without
  end when `<command>` started `tool gate` on the same project root. DoD: a nested gate on the same root
  is refused with a clear error, and a test proves it.
- PR body: "Closes the linked issue", so the issue reference is present and branch 5 does not apply.
- Instruction and REVIEW.md paths: none available in the fixture (root AGENTS.md, cli/shared/AGENTS.md
  and REVIEW.md not supplied). The project README content is quoted in the fixture.

## Gates

| Check | Required | Status at head | Attribution | Evidence |
|---|---|---|---|---|
| Trusted required CI | yes (fixture) | passed | not_applicable | input.md: "Trusted required CI passed at head." |
| Local targeted tests | - | not run | - | Execution forbidden by the brief |
| Mutation testing | not required | applicable, skipped: no project-pinned runner | - | The supplied evidence shows no StrykerJS/Stryker.NET or other pinned runner, and no policy requires one. The tree could not be inspected to confirm this. |
| Specialist security pass | not required | not applicable | - | The change does not touch a trust boundary (see Security) |

Commands run locally: none.

Green CI does not cover F1. The suite has no negative case for the early diagnostic (see Tests).

## Timing

Unknown. No clock or timestamped log was available. All categories are null.

## Coverage

- Reviewed 2 of 2 changed files: `src/gate.py` (all 13 lines, from the fixture) and `tests/test_gate.py`
  (from the fixture's description only; its source was not supplied).
- The caller that computes `root` and `argv` for `run_gate` is not in the fixture. Root normalization
  and empty-argv handling are recorded as verification gaps.
- Mode: full first pass, round 1. No published baseline exists. Latest reviewed SHA: none.

## Risk

Low to Medium. The change is limited to a developer-tool CLI gate and does not touch auth, credentials,
CI/release or data. Blast radius: every user who runs the README-documented standard pre-push command.
After merge that command is refused at every invocation. Reversible: reverting or patching
`early_diagnostic` restores it, and no persistent state changes. Rollback is a plain revert. No feature
flag was evidenced, and none is assumed.

## Findings

### F1 - `gate.early-diagnostic-false-refusal`: substring match refuses non-gate commands, including the documented pre-push command

- Location: `src/gate.py` `early_diagnostic`, with the refusal at `run_gate`.
- Anchors (verbatim head lines):
  - `src/gate.py:4`: `    if "tool" in os.path.basename(argv[0]):`
  - `src/gate.py:5`: `        return "refusing nested gate: the command starts tool gate again"`
  - `src/gate.py:12`: `        sys.exit(message)`
- Severity: **Minor**. No data is lost, and the check can still be run without the gate (team
  classification, input.md line 30-31). I accept that rationale. It is close to Critical as a break of a
  documented workflow, but the result is the same under either label.
- **Blocker? Yes.** Branch 1: a reachable regression introduced by the change. It passes the peer
  materiality bar (rule 1):
  - Realistic ordinary trigger: the project README documents `tool gate -- ./scripts/toolchain-check.sh`
    as the standard pre-push command. A normal user produces this input without crafting it.
  - Concrete user-visible consequence: the command fails, which is a failed command. The message also
    tells the user that their command "starts tool gate again", which is false and sends them looking
    for recursion that does not exist. That is a message leading the user to a wrong action.
  - Guard versus boundary (rule 2) does not apply. Rule 2 covers a *bypass* of a guard, and this is a
    false *refusal* of legitimate input in ordinary use, not a contrived input slipping through.
    `security_boundary`: false. The finding still blocks under rule 1.
  - Rule 4 does not apply. The base ran the command successfully (input.md line 29-30), and the
    heuristic on line 4 is new in this PR. Origin: change.
  - Rule 5 does not apply. The PR body discloses no follow-up issue.
- Trigger and path: `tool gate -- ./scripts/toolchain-check.sh` reaches `run_gate(root, argv, spawn)`
  with `argv[0] == "./scripts/toolchain-check.sh"`.
  1. Line 8: `TOOL_GATE_ROOT` is unset for a top-level run, so the marker check passes.
  2. Line 10: `early_diagnostic(argv)` runs, and `os.path.basename("./scripts/toolchain-check.sh")`
     returns `"toolchain-check.sh"`.
  3. Line 4: `"tool" in "toolchain-check.sh"` is True, so line 5 returns the refusal message.
  4. Lines 11-12: `sys.exit(message)` prints the message and exits with status 1. The check never runs.
- Expected: the command runs the toolchain check, as it does at base. Only an actual nested
  `tool gate` on the same root should be refused (DoD).
- Actual: the command is refused at every invocation with a false explanation.
- Variants, same root cause and same fix point: any command whose basename contains `tool` is refused.
  Examples are `tool lint ...` (a non-gate subcommand of the same CLI), `toolbox`, `pytool` and
  `mytools.sh`. They are all instances at `src/gate.py:4`, not separate findings.
- PR-body relation (supporting anchor, not a separate blocker): the body describes the diagnostic as
  naming "the common direct self-invocation". In the diff it also fires on commands that are not
  self-invocations.
- Verification: complete static trace of `src/gate.py` at head, using standard `os.path.basename` and
  `in` semantics, plus the fixture's statement that the base ran the README command successfully.
  Red/green regression execution is **unverified**: execution was forbidden in this run.
  - Reproduction for a recipient: on head, run `tool gate -- ./scripts/toolchain-check.sh` from the
    project root. Expected failure signature: exit 1 with
    `refusing nested gate: the command starts tool gate again`.
  - On base the same command runs the check.
  - Equivalent unit probe: `early_diagnostic(["./scripts/toolchain-check.sh"])` returns the refusal
    string instead of `None`.
- Remedy:
  1. Make the early diagnostic match only an actual direct self-invocation. Require
     `os.path.basename(argv[0]) == "tool"` (or the resolved CLI entry point), plus `argv[1] == "gate"`
     when present. Alternatively, drop the heuristic and rely on the root marker, which already refuses
     the nested gate with a clear error.
  2. Add negative tests asserting `early_diagnostic` returns `None` for
     `["./scripts/toolchain-check.sh"]` and for a non-gate `["tool", "lint"]`. Also add an end-to-end
     test that `tool gate -- ./scripts/toolchain-check.sh` (or a stub script with a `tool`-prefixed name)
     is not refused.
  3. After fixing line 4, search for further copies of substring-based command matching in the gate path.

## Should-fix (non-blocking)

None.

## Requirements traceability

| ID | Criterion (exact text) | State | Implementation | Verification |
|---|---|---|---|---|
| R1 | "a nested gate on the same root is refused with a clear error" | met (static) | `src/gate.py:8-9` marker check with `"refusing nested gate on " + root`; `src/gate.py:13` sets the marker for the child | static trace; CI-run test asserting "refusing nested gate on" (basis: ci, test source not supplied) |
| R2 | "a test proves it" | met | tests/test_gate.py same-root child test (per fixture) | CI passed at head (basis: ci) |

The DoD is met. The blocker comes from a regression that the change introduced (branch 1), not from an
unmet requirement.

## Dimensions

1. Issue scope: R1 and R2 met. The early diagnostic is extra scope beyond the DoD and introduced F1.
2. Structural integrity: required CI passed. The README-documented command surface regresses (F1).
3. Stale code: not applicable. New file, nothing removed or renamed.
4. Technical debt: introduced: a heuristic diagnostic that duplicates the marker's job (folded into the
   F1 remedy). Closed: unbounded nested-gate recursion on the same root.
5. Documentation accuracy: the README is unchanged. The F1 regression makes its documented standard
   command fail. No diff-added docs.
6. Conventions: no AGENTS.md was supplied to check against. Nothing assessable beyond file placement
   (src/, tests/), which looks normal.
7. Follow-up hygiene: F1 is a blocker and must be fixed in this PR, or deferred by the author under
   rule 5 with a disclosed author-opened issue.
8. Correctness: F1. Variants and caller assumptions are covered in Verification gaps.
9. Security: no new untrusted-input path. `spawn` receives an argv list (no shell string), the command
   is the feature's user-supplied purpose, and the marker is an accident-prevention guard. No policy,
   issue or comment names it a security or trust boundary. No specialist pass is needed.
10. Tests: happy-path only for the early diagnostic. With no negative case, F1 passes CI. The gap is
    folded into the F1 remedy.
11. Skill quality: no skill bodies touched.
12. PR description: issue reference present, test plan stated. The diagnostic claim is broader in
    effect than described (supporting anchor on F1).

Focused lenses: error/fallback (refusal paths traced, see F1); test resilience (see Tests). Type
invariants and comments: not applicable, since no types or comments changed.

## Verification gaps

- G1 (non-material): root spelling. `os.environ.get(MARKER) == root` (`src/gate.py:8`) compares raw
  strings. Whether the caller normalizes `root` (absolute, symlink-resolved, no trailing slash) is not
  evidenced, because the caller is not in the fixture. If it does not, a differently spelled same root
  would bypass the guard. That would be an accident-prevention guard bypass by an odd path spelling:
  non-blocking (guard_bypass), and not a boundary.
- G2 (non-material): empty argv. `argv[0]` on `src/gate.py:4` raises IndexError if the caller can pass
  an empty command (`tool gate --`). Whether the CLI rejects an empty command upstream is not evidenced.
- G3: no execution. Red/green for F1 and local targeted tests were not run, and the skill fingerprint,
  review.json, validator and anchor verifier were not run (brief: no script execution).

## Out-of-scope observations

1. Indirect cross-root recursion. Line 13 overwrites the single `TOOL_GATE_ROOT` value. So a chain
   A -> gate on B -> gate on A is not refused: the inner A sees the marker `B`. Base also recursed here,
   and the issue's trigger is a command that starts `tool gate` on the *same* root, so this is not
   anchored as an unmet DoD. A follow-up could store the set of active roots, for example as a
   path-separated list. If the maintainer reads the DoD as covering indirect nesting, this becomes a
   branch-2 item.

## Carried

Unavailable: this is the first round, with no qualified baseline.

## Propagation sweep

- Class `gate.early-diagnostic-false-refusal`.
- Search: manual read of all 13 lines of `src/gate.py` for substring or heuristic command matching.
- Files covered: `src/gate.py`. `tests/test_gate.py` is covered by description only.
- Instances: `src/gate.py:4`. Only one instance, so no class-sweep trigger.
- Debt: see dimension 4. Net: the change fixes the issue's recursion but adds a regression in the
  standard workflow.

## How to finish

Fix F1 and add the negative tests. Then rerun with a repository checkout so that the following can run:
the skill fingerprint, review.json with the validator and anchor verifier at the new head, and local
targeted tests with red/green (base: README command passes; head: refused; fix: passes).
