reviewer: pr-review2
skill-version: 2.11.1
candidate-sha256: f79409f6f0e85c3aaeaaef8d089ae86847ad7b85ea9dbe26f220a95758b87609
case: 34-sync-preview-docs
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: PASS
- Observed: Not ready to merge; F-docs Blocker? Yes (DoD 2, docs/sync.md:21); docs/sync.md:24 Minor should-fix, basis fix_surface, security_boundary false.
- Tool policy: offline fixture; one fresh-context Claude Code subagent per case, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus that case's input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: run 1 at 2.11.1, scored after the run against the hidden oracle.

## Raw reviewer output

# PR Review 2 - Round 2 (qualified delta) - `tool sync --dry-run` preview

## Verdict

**Not ready to merge** (REQUEST_CHANGES).

2 verified findings: 1 blocker (F-docs, still open), 1 non-blocking should-fix (F-docs-preview-stream, basis fix_surface). 0 prior findings verified fixed.

- F-docs stays open: the help text is now present, but the docs example added to close it (`tool sync --dryrun src/ backup/`) is rejected by argparse, so DoD 2 ("document the flag with a working example") is still unmet. Blocks through branch 2 (failed linked-issue requirement), which no materiality rule relaxes.
- F-docs-preview-stream: the new troubleshooting row says the plan goes to stderr and recommends `2>plan.txt`; the plan is printed to stdout, so the file stays empty. Minor, change-introduced, but located in text added only to address F-docs and not reopening F-docs' own failure, so it is a non-blocking should-fix under materiality rule 3 (fix_surface).

No Maintainer decision item is needed.

## Skill and reviewer identity

- Skill: `pr-review2`, metadata.version `2.11.1`.
- Package fingerprint: **not computed**. This fixture-only exercise forbids script execution, so `review_record.py --skill-fingerprint` could not be run on the directory read (`.../34-sync-preview-docs/skill/`). The fingerprint is not copied from the prior report.
- Reviewer host: Claude Code (agent CLI); model family: `claude`.

## Run status

- Fixture-only exercise: no review.json or validator-output.txt was produced (the fixture forbids inventing review.json and running the validator), so run status is **not validator-computed** and no kept record paths exist.
- Reviewer-side accounting against the supplied evidence (not a validator result): every changed file is accounted for (2 delta files reviewed now, 1 reused from the qualified baseline), both required gates are resolved (passed at head), the contract is resolved, and each criterion is resolved (DoD 1 met, DoD 2 unmet). No material verification gap was identified within the supplied evidence. Non-material limits: fingerprint not computed, anchors not mechanically verified, no timing clock. The run was not stopped.
- approved_scope_status: not applicable (no scope limit).

## Subject

- Target: offline synthetic fixture (no PR URL/title supplied), AURA peer mode.
- Linked contract: issue "`tool sync <src> <dst>` gains a preview flag" (reference present per fixture).
- Base: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- Head: `dddddddddddddddddddddddddddddddddddddddd`
- Previously reviewed head (round 1, published, pinned by commit_id): `cccccccccccccccccccccccccccccccccccccccc`
- Patch digest: not applicable (clean commit input).
- Instruction / REVIEW.md paths: none supplied by the fixture; no AGENTS.md or REVIEW.md content was available to load. Applied the skill's AURA peer profile and the trusted policy line in the fixture.

## Required gates

Trusted policy: required checks are `lint` and `tests`.

| Check | Required | Status at head d | Attribution | Evidence |
|---|---|---|---|---|
| lint | yes | passed | not_applicable | fixture trusted observation |
| tests | yes | passed | not_applicable | fixture trusted observation |
| Security specialist pass | no | not applicable | - | issue states no security boundary; baseline pass below finds no new untrusted-input path |

No commands were run locally (fixture forbids execution).

## Timing

No review timing clock was collected: elapsed, active review, verification and CI-wait are all unknown.

## Mutation

Applicable in principle (src/sync.py decision logic changed base-to-head; it is unchanged in the c..d delta). **Skipped: no project-pinned runner** (fixture: no mutation tool installed; mutation optional, not required by policy or user). No outcome counts.

## Review round, mode and baseline

- Round 2, **qualified delta** mode.
- First-pass baseline: published, complete, pinned by commit_id `cccc...cccc` (full SHA above); reviewed 3/3 files and all dimensions; same report is also the latest reviewed revision.
- Delta qualification evidence (supplied trusted observations): risk Low; head d descends from c; base, contract and callers unchanged; no force push; delta paths `src/cli.py`, `docs/sync.md` are both in the current base-to-head diff (no reverted path).
- Baseline identity: the pinned report header names the same skill package fingerprint and the same reviewer model family as this run (supplied observation), so baseline_identity reads `same`. Limit: this run's own fingerprint was not computed here, so the "same fingerprint" match rests on the fixture's statement, not on an independent hash. Previous skill: pr-review2, same fingerprint per fixture (version not stated); previous reviewer model family: same as this run (`claude`) per fixture.
- prior_finding_ids: `F-docs`.

## Coverage

- Delta files: reviewed **2 of 2** now (`src/cli.py` lines 12-13, `docs/sync.md` lines 20-24).
- Reused baseline coverage: `src/sync.py` (byte-identical to c; full-pass coverage reused, not claimed as current-pass reading; its 6 supplied lines were still re-traced for the DoD 1 and stream checks).
- Base-to-head accounting: 3 of 3 changed files accounted for (2 reviewed now, 1 baseline).
- Affected callers: unchanged per fixture; `run(src, dst, dry_run)` stdout behavior traced for the docs claims.
- Prior blocker F-docs re-verified against current code.

## Risk

Low. Delta is a help string and a docs section; the flag's runtime path (src/sync.py) is unchanged since the reviewed baseline. Blast radius: users reading `--help` / docs/sync.md. Fully reversible by reverting the commits; no persisted state, migration or deployment behavior change, so rollback is a plain revert. No auth, credential, CI/release or installer surface; no extra human scrutiny beyond normal review required.

## Published blocker status (re-review)

| ID | Prior state | Current state | Current evidence | Author reply disposition |
|---|---|---|---|---|
| F-docs | open, Blocker Yes (DoD 2) | **open**, Blocker Yes | Help text added (`src/cli.py:13`) satisfies discoverability in `--help`; docs example `docs/sync.md:21` uses `--dryrun`, which argparse rejects with "unrecognized arguments". DoD 2 working example still missing. | "Added the help text and a docs section only to address F-docs." Partially accepted: help part verified; docs part does not satisfy DoD 2. |

## Findings

### Blockers

#### F-docs - DoD 2 still unmet: docs example does not work

- Location: `docs/sync.md:21`
- Anchor (verbatim head line): `Run \`tool sync --dryrun src/ backup/\` to list planned copies without writing.`
- Severity: Minor. **Blocker? Yes** - branch 2 (failed linked-issue requirement: DoD 2 "`tool sync --help` and docs/sync.md document the flag with a working example").
- Trigger/path: a user copies the Preview example from docs/sync.md.
- Expected: the example runs a preview of planned copies.
- Actual: argparse rejects `--dryrun` with "unrecognized arguments" (verified observation). The parser defines only `--dry-run` (`src/cli.py:12`, `parser.add_argument("--dry-run", action="store_true",`); argparse prefix abbreviation cannot match `--dryrun` because it is not a prefix of `--dry-run`, and no abbreviation settings changed.
- Why not relaxed: materiality rules never relax branch 2. Rule 3 (fix_surface) also does not apply: this text was added only to address F-docs and it reopens F-docs' own failure (users following the docs cannot use the flag). It also would pass rule 1 independently (ordinary trigger, failed command).
- Present at previous head: not applicable (prior finding; docs/sync.md had no preview text at c).
- Verification: static trace of the argparse definition plus the supplied verified observation; not executed locally.
- Remedy: change line 21 to `tool sync --dry-run src/ backup/`. Optionally add an example line to the help epilog if `--help` is meant to carry an example too (DoD wording is ambiguous on that; the docs example fails regardless).

### Should-fix (non-blocking, relaxed by materiality rules)

#### F-docs-preview-stream - troubleshooting row names the wrong output stream

- Location: `docs/sync.md:24`
- Anchor (verbatim head line): `| Preview prints nothing | The plan goes to stderr; run \`tool sync --dry-run src/ backup/ 2>plan.txt\` |`
- Severity: Minor. **Blocker? No** - basis `fix_surface` (materiality rule 3), security_boundary false.
- Trigger/path: a user hits the "Preview prints nothing" row and runs the suggested command.
- Expected: docs correctly state where the plan is written; the suggested capture contains the plan.
- Actual: `src/sync.py:4` `print("copy", plan.src, "->", plan.dst)` writes to stdout, so `2>plan.txt` captures nothing (verified observation); the user is led to an empty file and a wrong diagnosis.
- Deciding evidence for the basis: round 2; the row lives in docs text the author added only to address F-docs (author reply; fixture: docs/sync.md had no preview text before c..d); it does not reopen F-docs' failure (flag discoverability / working example) - it is an independent wrong-stream claim. Not a security or trust boundary (issue: "no security boundary"; no untrusted-input path). Earlier finding named: F-docs.
- Present at previous head: **no** - fixture states docs/sync.md had no preview text at c; the row was added in c..d.
- Verification: static trace of `run()` print path plus supplied verified observation.
- Remedy: say the plan is printed to stdout and use `tool sync --dry-run src/ backup/ >plan.txt`; reconsider whether "Preview prints nothing" has a real cause (empty plan) and document that instead. May land as a suggestion, small follow-up commit, or author-opened issue.

### Optional suggestions

None.

## Linked-issue traceability

| ID | Criterion | State | Implementation | Verification |
|---|---|---|---|---|
| DoD-1 | `--dry-run` prints each planned copy without writing | met | `src/sync.py:3-6` (print per plan; `copy(plan)` only in else); `src/cli.py:12` flag | static trace (reused baseline coverage, file byte-identical to c); required `tests` passed at head |
| DoD-2 | `tool sync --help` and docs/sync.md document the flag with a working example | **unmet** | `src/cli.py:13` help text (present); `docs/sync.md:20-24` section (example broken) | static trace + verified argparse rejection of `--dryrun` |

## Dimensions

1. Issue scope: DoD 2 unmet (F-docs). No scope creep in delta.
2. Structural integrity: lint and tests passed at head; flag surface unchanged apart from help string.
3. Stale code: none in delta.
4. Debt: introduced - wrong docs stream claim (F-docs-preview-stream); closed - missing help text.
5. Docs accuracy: F-docs (`--dryrun`), F-docs-preview-stream (stderr claim). Help text matches behavior.
6. Conventions: no AGENTS.md/REVIEW.md content supplied; nothing beyond the docs findings.
7. Follow-up hygiene: F-docs must be fixed in this PR (branch 2); F-docs-preview-stream may land as suggestion/follow-up.
8. Correctness: no runtime code changed in delta; DoD 1 path re-traced.
9. Security: baseline pass - no new untrusted-input path (help string and docs only); issue states no security boundary; no specialist pass needed.
10. Tests: not applicable to delta (no logic change); mutation skipped as above.
11. Skill quality: not applicable - no skill bodies touched.
12. PR description: PR body not supplied beyond the linked issue reference being present; no contradicted claim identified. Limit: body text not available for a full Check 12 pass.

## Propagation sweep

- Search: every command example and stream/flag claim in the delta (`docs/sync.md:20-24`, `src/cli.py:12-13`), compared with the parser definition and `src/sync.py` output path.
- Instances: `--dryrun` at `docs/sync.md:21` (F-docs); stderr claim at `docs/sync.md:24` (F-docs-preview-stream). `docs/sync.md:24` uses the correct `--dry-run` spelling; `src/cli.py:13` help text is accurate.
- The two findings have different fix points, so they are not one recurring class; no class sweep triggered.
- Scope not covered: docs/sync.md lines outside 20-24 were not supplied (unchanged content).

## Out-of-scope observations

None.

## Carried

None.

## Limits

Offline synthetic fixture: no gh/git, no execution, no validator or anchor verifier run, no fingerprint computed, no timing. All repository facts come from the fixture's trusted observations. Anchors were checked by eye against the supplied head lines only.
