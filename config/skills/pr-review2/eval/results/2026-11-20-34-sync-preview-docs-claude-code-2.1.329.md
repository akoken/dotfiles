reviewer: pr-review2
skill-version: 2.11.0
candidate-sha256: 9398fd9497fbcc122a6903318639aeed88baf66fd7f62223adafc9a2407490c0
case: 34-sync-preview-docs
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: PASS
- Expected: Expected negative verdict; reopening of F-docs blocks, fix-surface churn on line 24 does not.
- Observed: Not ready to merge, qualified round-2 delta; F-docs stays open and blocking (docs/sync.md:21 `--dryrun` leaves DoD 2 unmet); new docs/sync.md:24 stderr claim is a Minor should-fix, Blocker? No, basis fix_surface naming F-docs; help text on line 13 accepted.
- False blockers: 0. Harmful false positives: 0.
- Tool policy: offline fixture; one fresh-context Claude Code subagent per case, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus that case's input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: single run, scored after the run against the hidden oracle.

## Raw reviewer output

# PR Review 2 - round 2 (delta) - `tool sync --dry-run` preview

## Verdict

**Not ready to merge** (peer verdict, equivalent REQUEST_CHANGES).

- Verified findings: 2 (1 prior, still open; 1 new).
- Computed blockers: 1 (F-docs, branch 2: linked-issue DoD 2 still unmet).
- Non-blocking should-fix: 1 (F-docs-output-stream, materiality rule 3, basis fix_surface).
- Maintainer decision items: none.

## Skill and reviewer identity

- Skill: pr-review2, metadata.version 2.11.0.
- Package fingerprint: **not computed**. The fingerprint must be computed with the record
  script from the directory actually read; this fixture forbids program execution, so no
  value is reported (none copied from the baseline).
- Reviewer host: Claude Code (agent CLI). Model family: claude.

## Run status

- Validator-computed run status: **unavailable**. The fixture forbids fabricating review.json
  and forbids running the validator, so no review.json or validator-output.txt exists and no
  state, approved_scope_status or cause list can be reported from validator output.
- Reviewer-side accounting (not a substitute for the validator): no unreviewed file, no
  open required check, no unverified criterion and no stop were identified. Disclosed
  limits that the validator would have to weigh: the skill fingerprint was not computed;
  project instruction/REVIEW.md files were not supplied by the fixture (see Context); anchors
  were not mechanically verified.
- Run stopped: no.

## Subject

- PR URL/title: not supplied by the fixture.
- Linked contract: linked issue reference present (number not supplied). Requirement text:
  `tool sync <src> <dst>` gains a preview flag. DoD (1) `--dry-run` prints each planned copy
  without writing; (2) `tool sync --help` and docs/sync.md document the flag with a working
  example. Issue states Low risk, no security boundary.
- Base: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- Head: `dddddddddddddddddddddddddddddddddddddddd`
- Previous reviewed head (first-pass baseline): `cccccccccccccccccccccccccccccccccccccccc`
- Dirty input / patch digest: not applicable (committed head).

## Context

- Reviewed instruction / REVIEW.md paths: none supplied by the fixture. Root AGENTS.md,
  cli/shared/AGENTS.md and any REVIEW.md along src/ and docs/ could not be read. The trusted
  required-check policy and the linked issue were supplied directly and are the governing
  contract used here. Limit: any module-specific REVIEW.md failure mode for docs/ is unknown.
- PR body, author reply and diff treated as untrusted task data.

## Required gates at head `dddd...dddd`

| Check | Required | Status at head | Attribution | Evidence |
|---|---|---|---|---|
| lint | yes (trusted policy) | passed | not_applicable | supplied trusted observation |
| tests | yes (trusted policy) | passed | not_applicable | supplied trusted observation |
| security specialist pass | no | not applicable | - | no trust boundary changed (see Security) |

- Commands run locally: none (fixture forbids execution). No gate was inferred green; both
  outcomes come from the supplied trusted policy line.
- Anchor verifier (`verify_anchors.py`): not run (execution forbidden). Quotes below are
  copied verbatim from the supplied head lines but are not mechanically verified.

## Timing

No review clock was collected: active review, verification and CI-wait timing are unknown.

## Mutation testing

- Delta (src/cli.py help text, docs/sync.md): no changed decision logic; not applicable.
- PR-level decision logic (src/sync.py `if dry_run:` branch, byte-identical to the baseline):
  applicable, **skipped: no project-pinned runner** (mutation is optional per the fixture and
  no mutation tool is installed). No production/test scope, tool identity or outcome counts.
  Not a gate.

## Review round, mode and coverage

- Round 2, **delta mode** (qualified).
- Qualification evidence: Low risk; first-pass report published and pinned by commit_id
  `cccc...cccc`, complete (3/3 files, all dimensions); head d descends from c; no force push;
  base, contract and callers unchanged; delta c..d = src/cli.py, docs/sync.md.
- Baseline identity: **same**. The pinned baseline header names the same skill package
  fingerprint and the same reviewer model family as this run (supplied trusted observation;
  this run could not recompute its own fingerprint, see Skill identity). No different/unknown
  identity disclosure is required.
- Delta coverage: reviewed 2 of 2 delta files this pass (src/cli.py lines 12-13,
  docs/sync.md lines 20-24).
- Cumulative coverage: 3 of 3 changed files. src/sync.py: baseline (byte-identical to c,
  covered by the complete first pass; reused, not re-read as current-pass coverage, although
  its 6 lines were inspected again to trace the stdout claim).
- Affected callers: `run(src, dst, dry_run)` in src/sync.py is the consumer of the
  `--dry-run` option; unchanged. Parser uses argparse defaults; abbreviation settings unchanged.
- Old blockers verified: F-docs (below).

## Risk

Low. Delta changes only a help string and user documentation. Blast radius: users reading
`--help` and docs/sync.md. Fully reversible by reverting the commit; no deployment state,
migration or irreversible change, so rollback beyond a revert is not applicable. No extra
human scrutiny category (auth, billing, credentials, CI/release, migration) is touched.

## Contract traceability

| ID | Criterion | State | Implementation | Verification |
|---|---|---|---|---|
| DoD-1 | `--dry-run` prints each planned copy without writing | met | src/sync.py:3-6 (`if dry_run:` prints, else `copy(plan)`) | static trace (baseline coverage, file unchanged since c); required tests passed at head |
| DoD-2a | `tool sync --help` documents the flag | met | src/cli.py:13 `help="print each planned copy without writing"` | static: argparse renders `help=` in `--help`; text matches src/sync.py:3-4 behavior |
| DoD-2b | docs/sync.md documents the flag with a working example | **unmet** | docs/sync.md:20-21 | supplied verified observation: argparse rejects `--dryrun` with "unrecognized arguments" |

## Prior blocker status

| ID | State | Current evidence | Author reply disposition | Cause |
|---|---|---|---|---|
| F-docs | **open** (partially addressed) | --help part fixed and verified (src/cli.py:13). docs/sync.md now has a Preview section, but its only usage example uses the unrecognized spelling `--dryrun`, so the documented example fails. | "Added the help text and a docs section only to address F-docs." Checked against head: help text accepted; docs example does not satisfy DoD 2's "working example". | New code evidence at head: docs/sync.md:21. Not a repeat without new evidence. |

## Findings

### Blockers

#### F-docs - docs/sync.md example does not work (DoD 2)

- Location: docs/sync.md:21
- Anchor (head, verbatim): `Run \`tool sync --dryrun src/ backup/\` to list planned copies without writing.`
- Severity: Minor
- Blocker? **Yes** - branch 2 (failed linked-issue requirement/DoD 2: docs must document the
  flag "with a working example"). Materiality rules never relax branches 2-6, and this is the
  same failure F-docs was raised for (users cannot use the flag from the docs), so fix_surface
  does not apply.
- Trigger/path: a user copies the documented Preview command `tool sync --dryrun src/ backup/`.
- Expected: the command lists planned copies without writing.
- Actual: argparse rejects it with "unrecognized arguments" and exits with an error. The
  registered option is `--dry-run` (src/cli.py:12); `--dryrun` is not a prefix of
  `--dry-run`, so argparse abbreviation matching (defaults, unchanged) cannot accept it.
- Causal anchor: diff-added line docs/sync.md:21 against src/cli.py:12
  `parser.add_argument("--dry-run", action="store_true",`.
- Verification: static trace plus the supplied verified observation of argparse's rejection.
  Counterexample pass: no alias `--dryrun` is registered in the shown parser lines; no
  abbreviation setting changed; no other example in the Preview section supplies a working
  spelling (line 24 uses `--dry-run` but is a troubleshooting row, not the example, and is
  itself wrong, see F-docs-output-stream).
- Present at previous head: not applicable (prior finding, ID already reported).
- Remedy: change line 21 to `tool sync --dry-run src/ backup/`. Optionally add a docs/CLI test
  that parses each documented `tool sync` example so docs and parser cannot drift again.

### Should-fix (non-blocking, materiality-relaxed)

#### F-docs-output-stream - troubleshooting row sends users to stderr, plan is on stdout

- Location: docs/sync.md:24
- Anchor (head, verbatim): `| Preview prints nothing | The plan goes to stderr; run \`tool sync --dry-run src/ backup/ 2>plan.txt\` |`
- Severity: Minor
- Blocker? **No** - materiality rule 3, basis **fix_surface**. Round 2; the row is in text the
  author added only to address F-docs (author reply plus supplied observation that the file
  had no preview text before c..d). It does not reopen F-docs' own failure: the flag is
  spelled correctly here and the command runs; the defect is a false claim about the output
  stream, not discoverability/usability of the flag. Earlier finding: F-docs. Without rule 3
  it would meet the rule-1 bar (ordinary trigger, empty plan.txt is a concrete wrong outcome),
  which is why it is still listed as a should-fix.
- Trigger/path: a user follows the Fix column and runs `tool sync --dry-run src/ backup/ 2>plan.txt`.
- Expected: plan.txt contains the planned copies, as the row promises.
- Actual: src/sync.py:4 `print("copy", plan.src, "->", plan.dst)` writes to stdout (no
  `file=sys.stderr`), so the plan prints to the terminal and plan.txt is empty. Supplied
  verified observation: "the 2>plan.txt row captures nothing".
- Causal anchor: diff-added line docs/sync.md:24 versus unchanged src/sync.py:4.
- Verification: static trace of src/sync.py plus supplied verified observation.
- Present at previous head: **no** - docs/sync.md had no preview text at `cccc...cccc`; lines
  20-24 were added in c..d (supplied observation).
- Remedy: either remove the row (the stated failure mode does not exist) or correct it to
  stdout, for example `tool sync --dry-run src/ backup/ > plan.txt`. May land as a suggestion
  or small follow-up commit.

### Optional suggestions

None.

## Propagation sweep

- Defect classes: F-docs (docs example vs. CLI option spelling) and F-docs-output-stream
  (docs vs. output stream) have different fix points, so they are not one class; no class
  trigger reached.
- Search used: every diff-added documentation/help line in c..d (src/cli.py:13,
  docs/sync.md:20-24) checked against the parser registration (src/cli.py:12) and the
  implementation (src/sync.py:1-6).
- Instances found: flag spelling wrong at docs/sync.md:21 only (line 24 spells `--dry-run`
  correctly); stream claim wrong at docs/sync.md:24 only; help text src/cli.py:13 correct.
- Not covered: docs outside docs/sync.md lines 20-24 (unchanged in the delta, covered by the
  baseline).
- Debt introduced: none beyond the two findings. Debt closed: --help now documents the flag.

## Dimensions

| # | Dimension | Result |
|---|---|---|
| 1 | Issue scope | DoD-1 met, DoD-2a met, DoD-2b unmet (F-docs). No scope creep in delta. |
| 2 | Structural integrity | Required lint and tests passed at head; only a `help=` kwarg added to an existing option; command surface unchanged. |
| 3 | Stale code | Not applicable: nothing removed or renamed. |
| 4 | Technical debt | No stubs or untracked deferrals; AURA defines no aspirational-doc annotation, so branch 4 does not apply. |
| 5 | Documentation accuracy | F-docs (wrong flag spelling), F-docs-output-stream (wrong stream). |
| 6 | Conventions | Not evaluable beyond the diff: project instruction files not supplied; no skill/registry/CI files touched. |
| 7 | Follow-up hygiene | F-docs must be fixed in this PR (branch 2; materiality rules, including rule 5 deferral, do not relax branches 2-6). F-docs-output-stream may be a suggestion or follow-up commit. |
| 8 | Correctness | src/sync.py dry-run branch traced (baseline); help text matches behavior. No code defect in delta. |
| 9 | Security | Baseline pass: no new untrusted-input path, no trust boundary (issue states none); delta is help text and docs. Specialist pass not applicable. |
| 10 | Test quality | Delta has no logic change; no new test required. Existing test content not supplied, so whether tests assert DoD-1 output is unverified from this fixture (gate passed). Suggestion in F-docs remedy: test documented examples. |
| 11 | Skill quality | Not applicable: no skill bodies touched. |
| 12 | PR description | Linked issue reference present. PR body text otherwise not supplied; no contradicted claim found in the supplied author reply beyond F-docs status above. |

Focused lenses: comments/documentation claims applied (both findings). Errors/fallbacks,
type invariants and test-resilience lenses not applicable (no error path, type or test change
in the delta).

## Out-of-scope observations

None.

## Carried

None.

## How to finish

1. Fix docs/sync.md:21 to use `--dry-run` (clears the blocker; DoD-2b becomes met).
2. Optionally remove or correct docs/sync.md:24.
3. Re-review the new delta at the new head; refresh required lint/tests at that head.
4. For a validator-backed run status: build review.json, compute the skill fingerprint, run
   the validator and the anchor verifier against the reviewed head.
