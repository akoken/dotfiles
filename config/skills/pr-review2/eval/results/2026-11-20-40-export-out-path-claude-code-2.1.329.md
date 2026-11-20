reviewer: pr-review2
skill-version: 2.11.2
candidate-sha256: c8818e97778fc68b973d276a0654393e8d2511d73781c07987d8766bdb841016
case: 40-export-out-path
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: PASS
- Observed: Review incomplete / NEEDS_REVIEW. F1 symlink escape verified; Blocker? neither Yes nor relaxed, because step 2 of the guard-versus-boundary test is unsettled (CI provenance of --out and the symlink not supplied); guard_bypass explicitly unavailable; open boundary question recorded as material gap G1; DoD judged met.
- Tool policy: offline fixture; one fresh-context Claude Code subagent, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus the case input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: single run, scored after the run against the hidden oracle.

## Raw reviewer output

# PR Review 2 - offline fixture 40-export-out-path

## Verdict

**Review incomplete / NEEDS_REVIEW** (peer mode, round 1, full).

1 verified finding, 0 computed blockers. The finding (F1, symlink escape through `safe_out`)
is neither a computed blocker nor a relaxed should-fix: whether the check is a convenience
guard or a trust boundary cannot be decided from the supplied evidence, so under the
materiality security exemption it stays unrelaxed and the open boundary question is recorded
as a material verification gap (G1). No other verified blocker exists, so the result is
NEEDS_REVIEW rather than Not ready to merge or Ready to merge.

This is a fixture-only exercise of the skill, not a live AURA PR review. No review.json or
validator-output.txt was produced (the brief forbids inventing metadata or a record and
forbids running scripts), so run status below is the reviewer's assessment, not validator
output.

## Identity and subject

| Item | Value |
|---|---|
| Skill | pr-review2, metadata.version 2.11.2 (read from `skill/SKILL.md`) |
| Skill fingerprint | not computed: `scripts/review_record.py --skill-fingerprint` could not be run (no program execution allowed); unknown, not copied from any earlier report |
| Reviewer host / model family | Claude Code (agent CLI) / claude |
| Mode / profile | AURA peer, round 1, full review (trusted policy: "Round one, full") |
| PR URL / title | not supplied in the fixture |
| Linked contract | linked issue present: `tool export --out <path>` writes an HTML report; DoD quoted below |
| Base | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |
| Head | bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb |
| Patch digest | not applicable (clean commit range) |
| Instruction / REVIEW.md / SECURITY.md files | none supplied; none loaded (see G3) |
| Baseline | first round; no published or local baseline; not applicable |

## Run status (reviewer assessment, no validator output)

- State: **incomplete**. approved_scope_status: incomplete (reasons are not scope limits). Stopped: no.
- Reasons:
  - G1 material verification gap, cause **environment**: the CI configuration was not supplied,
    so the baseline security pass cannot tell whether an untrusted source (a pull-request
    author) can reach `safe_out` with a planted `reports/` symlink. Evidence: input.md lines 33-37.
  - G2 required review-plan specialist security pass not run, cause **missing_specialist**:
    security routing asks for a focused pass on a material unresolved exploitability question
    (untrusted value reaching a file write); delegation is prohibited in this exercise
    (brief: "no subagents"; input.md line 6: "no ... delegation").
  - G3 context incomplete, cause **environment**: root AGENTS.md, cli/shared/AGENTS.md,
    REVIEW.md and SECURITY.md files and the CI workflow files were not supplied.
- review.json / validator-output.txt: not produced (fixture-only; brief forbids inventing them).
  Anchor verifier not run (no execution; no git checkout).

## Required gates at head

| Gate | Required | State at head bbbbbbb...b | Attribution | Evidence |
|---|---|---|---|---|
| lint | yes (trusted policy) | passed | not applicable | input.md line 14 |
| tests | yes (trusted policy) | passed | not applicable | input.md line 14 |
| Focused security specialist pass | yes (review plan, security routing: material unresolved exploitability question) | unavailable | not applicable | G2 |
| Mutation testing | not required | skipped: no project-pinned runner (none named; input says no mutation tool is installed and mutation is optional) | not applicable | input.md lines 9-10 |

No commands were executed locally. Gate states come from the supplied trusted observation;
nothing was inferred green.

Mutation: applicable (changed decision logic in `src/export.py` line 4 and tests exercising it),
skipped: no project-pinned runner. Production scope `src/export.py`, test scope
`tests/test_export.py`; no tool, config, revision or counts exist. The mutation reference was
not read, per SKILL.md.

## Timing

No review timing clock was collected (input.md line 9). active_review, verification and
ci_wait: unknown. elapsed: unknown.

## Contract traceability

Linked issue DoD (verbatim): "an --out value with a `..` segment or an absolute path that
points outside the project root is rejected with a clear error; a test proves it."

| ID | Criterion | State | Implementation | Verification |
|---|---|---|---|---|
| R1 | `--out` with a `..` segment that points outside the root is rejected with a clear error | met | `src/export.py` lines 3-5: normpath collapses `..`; prefix check on line 4 raises `SystemExit("refusing to write outside the project: " + out)` | static trace: root `/p`, out `../x.html` -> `/x.html`, fails `startswith("/p/")`, exits with message; CI: tests cover `../x.html` and passed at head |
| R2 | absolute `--out` outside the root is rejected with a clear error | met | `src/export.py` line 3: `os.path.join(root, "/tmp/x.html")` returns the absolute operand; line 4 rejects it | static trace as above; CI: tests cover `/tmp/x.html` and passed at head |
| R3 | a test proves it | met (with limit) | `tests/test_export.py` | CI tests passed at head; the supplied trusted observation states the tests cover `../x.html`, `/tmp/x.html` and plain `reports/x.html`. Limit: the test source text was not supplied, so assertion strength (that rejection and message are asserted) was taken from the trusted observation, not read |

The symlink case in F1 is not a DoD failure: `reports/x.html` contains no `..` segment and is
not absolute, so neither DoD form covers it. Branch 2 does not apply.

## Findings

### F1 - `export.out-path-containment`: symlinked directory under the root escapes the check

| Field | Value |
|---|---|
| ID | F1 `src/export.py:safe_out symlink-escape` |
| Location | `src/export.py` lines 3-4 |
| Anchor (verbatim head lines) | `    path = os.path.normpath(os.path.join(root, out))` and `    if not path.startswith(root + os.sep):` |
| Severity | Minor provisionally; becomes a Critical-class reachable path traversal (Check 9) if G1 resolves as a trust boundary |
| Blocker? | **Not computed yet: neither Yes nor relaxed.** The boundary question (materiality rule 2, step 2) is unsettled, so the finding is never relaxed to a guard_bypass should-fix, and it is not yet proven a boundary defect that would block under branch 1 at any severity. The open question is recorded as material gap G1, which makes the review NEEDS_REVIEW. |
| Origin | change (new file `src/export.py`) |
| Trigger / path | `reports/` inside the project root is a symlink to a directory outside the root; run `tool export --out reports/x.html`. The only caller passes the project root and the raw `--out` value, then writes to the returned path. |
| Expected | the report is written inside the project root, or the command is refused |
| Actual | line 3 yields `<root>/reports/x.html` (normpath is purely lexical and does not resolve symlinks); line 4 passes; the caller writes through the symlink to a location outside the root |
| Verification | supplied verified observation (input.md lines 30-32) plus static trace of lines 3-4. No local execution. Counterexample pass (self-performed, no separate verifier available): no upstream realpath or symlink check exists in the supplied file; the caller passes the raw value; the DoD and PR body do not promise symlink handling, which removes branches 2 and 3 but does not disprove the reachable write outside the root. |
| Same-class variant | the final component itself as a symlink (`reports/x.html` -> outside file) is closed by the same fix point; inferred from the same lexical comparison, not separately observed. |

Guard versus boundary, in the rule-2 order:

1. Policy, security docs, issue or code comments naming it a security or trust boundary:
   none. The README calls the check protection "from mistyped paths"; no document names it a
   boundary or claims symlink handling (input.md lines 33-34). Step 1 does not apply.
2. Baseline security pass: **unsettled.** The README says project CI runs `tool export` on
   pull-request branches, but the CI configuration was not supplied, so it is unknown where
   `--out` comes from in CI and whether a pull-request author can create the `reports/`
   symlink there (input.md lines 34-37). If CI runs a trusted tool version against
   PR-controlled content with write access the PR author would not otherwise have (for
   example a privileged workflow), a planted symlink lets untrusted content write outside the
   checkout: a boundary bypass. If the same CI job already executes PR-authored code with the
   same privileges, the symlink adds no capability and the check is a convenience guard.
   The evidence does not distinguish these.
3. PR body or issue claim of resisting such input: none. The PR body claims rejection of `../`
   and absolute paths only, which the code does. No contradicted claim (branch 3 does not apply).
4. Guard classification (basis guard_bypass) is **not available** because step 2 is unsettled.

How to resolve: supply the CI workflow that runs `tool export`, showing the trigger
(pull_request vs. a privileged trigger), which tool revision runs, where `--out` comes from,
and the job's write permissions/secrets. Then:
- untrusted source can reach the write with new effect -> trust-boundary defect, blocks under
  branch 1 at any severity, fixed in this PR (no deferral); verdict Not ready to merge.
- not reachable by an untrusted source -> guard, F1 becomes a non-blocking Minor should-fix,
  basis guard_bypass, security_boundary false; with G2 resolved and no other gap, Ready to merge.

Remedy (covers the listed instance and further copies of the lexical-containment pattern):
resolve both sides before comparing, e.g. `real_root = os.path.realpath(root)`,
`path = os.path.realpath(os.path.join(real_root, out))`, and check
`os.path.commonpath([real_root, path]) == real_root` (and `path != real_root`). Add a
regression test that creates `reports/` as a symlink to a temporary directory outside the
root and asserts the export is refused with the error message. If it is judged a boundary,
also consider opening the target with `O_NOFOLLOW` relative to a root directory fd to close the
check-then-write race; search other write sites for the same lexical-only containment.

## Should-fix (relaxed by materiality rules)

None. F1 is deliberately not relaxed (see above).

## Verification gaps

| ID | Material | Cause | What is unverified |
|---|---|---|---|
| G1 | yes | environment | Whether an untrusted source (PR author in CI) can reach `safe_out` with a planted symlink and cause an effect it could not otherwise cause; CI configuration not supplied. Decides F1's blocker status. |
| G2 | yes | missing_specialist | Required review-plan focused security pass on the untrusted-path-to-file-write surface and G1; delegation prohibited in this exercise. |
| G3 | yes | environment | Project context: AGENTS.md, cli/shared/AGENTS.md, REVIEW.md, SECURITY.md and CI workflows not supplied, so module rules and security policy could not be checked. |
| G4 | no | environment | The caller of `safe_out` is not in the changed paths nor in the supplied complete `src/export.py`; its behavior (passes the project root and raw `--out`, writes to the returned path) is taken from the trusted observation. How `root` is formed was not inspected: a non-normalized root (trailing separator, relative `.`) would make line 4 reject valid paths. The passing plain `reports/x.html` test is partial counterevidence. Not reported as a finding (no evidence of a non-normalized root). |
| G5 | no | environment | `tests/test_export.py` source not supplied; covered cases taken from the trusted observation (see R3). |

## Coverage

- Changed files: 2. `src/export.py`: reviewed in full (complete text supplied).
  `tests/test_export.py`: reviewed through the supplied trusted summary only (cases covered,
  CI pass); source text not supplied (G5). Treat as 1 of 2 fully read, 1 of 2 partial.
- Caller of `safe_out`: behavior from trusted observation, not inspected (G4).
- Dimensions:
  1. Issue scope: R1-R3 met; no scope creep in the two changed paths.
  2. Structural integrity: lint and tests passed at head; no exported surface removed (new file).
  3. Stale code: not applicable, new file, nothing removed or migrated.
  4. Debt: debt introduced - lexical-only containment (F1); debt closed - none.
  5. Docs: no docs changed; the README's "mistyped paths" description is consistent with the code.
  6. Conventions: not checkable, project instructions not supplied (G3).
  7. Follow-up hygiene: no deferrals claimed; F1 must not be deferred on the author's behalf.
  8. Correctness: lines 3-5 traced for `..`, absolute, plain relative, prefix-sibling
     (`/p2` vs `/p`, handled by `os.sep`), and symlink inputs; F1 found; root-form question in G4.
  9. Security: baseline pass done; untrusted-input-to-file-write surface identified;
     boundary reachability unresolved (G1); specialist pass unavailable (G2).
  10. Tests: cases match the DoD; no symlink test (part of F1's remedy); mutation skipped,
      no pinned runner.
  11. Skill quality: not applicable, no skill bodies touched.
  12. PR description: linked issue reference present; claims match the diff for `../` and
      absolute paths; no test plan text was supplied to assess (non-blocking, not a finding).
- Focused lenses: errors/fallbacks - the failure path raises `SystemExit` with a clear
  message, no swallowed error; type invariants - not applicable (no types); comments/docs -
  README claim checked, consistent; test resilience - see dimension 10.

## Risk

Medium. Affected behavior: where `tool export` writes a file. Blast radius: local file
writes for users, and potentially CI runners if G1 resolves as reachable, which would
require explicit human scrutiny of the CI boundary (CI privileges are a listed scrutiny area).
Reversibility: code change is revertable; files already written outside the root are not
undone by a revert. Rollback: revert the PR; no deployment, flag or migration evidence was
supplied. Owner/human reviewer: unknown. Approval counts: not supplied, none invented.

## Propagation sweep

Class `export.out-path-containment` (lexical containment check without symlink resolution).
Search: full read of the supplied complete `src/export.py` (6 lines). Instances:
`src/export.py:3-4`. Not covered: `tests/test_export.py` source, the caller's file and any
other write sites (not supplied). Single instance, so no class-sweep trigger (second
same-class finding) applies.

## Out-of-scope observations

None.

## Carried

Not applicable (first round, no baseline).

## How to finish this review

1. Obtain the CI workflow running `tool export` and settle G1 (see F1 "How to resolve").
2. Run the focused security specialist pass on the immutable head with the G1 question (G2).
3. Load AGENTS.md / REVIEW.md / SECURITY.md for the changed paths (G3); optionally inspect the
   caller and test source (G4, G5).
4. Build review.json, compute the skill fingerprint, run the validator and anchor verifier
   against head bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb, then recompute the verdict.
