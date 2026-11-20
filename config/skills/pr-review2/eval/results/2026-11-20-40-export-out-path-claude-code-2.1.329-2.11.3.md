reviewer: pr-review2
skill-version: 2.11.3
candidate-sha256: 446b6ed9f56a7f193ae54c2bb4ab44e2a83c9e8408f9d33a45195f96af3227f5
case: 40-export-out-path
host: claude-code-2.1.329
model: claude-opus-5-5

## Scores

- Verdict against oracle: PASS
- Observed: Review incomplete / NEEDS_REVIEW, 1 verified finding, 0 blockers. F1 symlink escape is a proven change-introduced Minor whose boundary status is unresolved: neither relaxed nor a proven blocker, recorded as boundary_gap G1 with no security_boundary and no non_blocking.
- Tool policy: offline fixture; one fresh-context Claude Code subagent, given only an isolated copy of SKILL.md, references/ and scripts/ (fingerprint checked) plus the case input.md; no execution, git, gh, network, delegation or edits besides its own output.md; oracle, rubric, classes and results withheld.
- Notes: single run at 2.11.3 (boundary_gap state), oracle unchanged from 2.11.2, scored after the run against the hidden oracle.

## Raw reviewer output

# PR Review 2 report - `tool export --out` containment (offline synthetic fixture)

**Verdict: Review incomplete / NEEDS_REVIEW** - 1 verified finding, 0 blockers.

The single verified finding (F1, symlink escape from the `--out` containment check) is a
proven, change-introduced, reachable Minor defect whose security or trust-boundary status the
supplied evidence leaves unresolved. Under the skill's security exemption it is therefore
neither relaxed to a should-fix nor counted as a proven blocker: it is linked to a material
verification gap (G1, boundary question), and that gap keeps the review incomplete. No other
verified blocker exists, so the verdict is NEEDS_REVIEW, not Not ready to merge and not
Ready to merge.

## Run identity and status

| Item | Value |
|---|---|
| Skill | pr-review2, metadata.version 2.11.3 (read from `skill/SKILL.md`) |
| Skill fingerprint | Not computed: the brief forbids script/program execution, so `review_record.py --skill-fingerprint` could not run. Not copied from any other source. |
| Reviewer host / model family | Claude Code (Claude Agent SDK) / claude |
| Mode | AURA peer mode, fixture-only evaluation (not a live AURA PR review) |
| Review round / mode | Round one, full (supplied trusted policy) |
| Base | `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` |
| Head | `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb` |
| PR URL / title | Not supplied by the fixture; not invented |
| Linked contract | Linked issue for `tool export --out <path>` (reference present per fixture; issue number not supplied) |
| Patch digest | Not applicable (clean commit range per fixture) |
| review.json / validator-output.txt | Not produced: the fixture says not to invent metadata or review.json, and validator execution is not permitted. Run status below is the reviewer's own computation under the review-record rules, not validator output. |
| Anchor verification | `verify_anchors.py` not run (no execution, no git). Quotes below are copied verbatim from the complete `src/export.py` supplied in the fixture. |
| Timing | Unknown: no review clock was collected (all categories null). |

**Run status (reviewer-computed, validator unavailable): incomplete.**
approved_scope_status: incomplete (not every reason is a scope_limit). Stopped: no.

| Reason | Cause | Evidence |
|---|---|---|
| G1 - open boundary question linked to F1 (material) | environment | CI configuration was not supplied, so the evidence does not show where `--out` comes from in CI or whether a pull-request author can create a `reports/` symlink there. |
| Required review-plan security specialist pass (S1) not run | missing_specialist | Security routing requires a focused pass for a material unresolved exploitability question; delegation/subagents are forbidden by the brief and no specialist workflow is available. |
| Project context incomplete (G2) | environment | Root `AGENTS.md`, `cli/shared/AGENTS.md`, `REVIEW.md` and `SECURITY.md` were not supplied by the fixture. |

## Required gates at head `bbbbbbbb...`

| Gate | Required | Status | Attribution | Evidence |
|---|---|---|---|---|
| lint | yes (trusted policy) | passed | not_applicable | Supplied trusted observation: passed at head |
| tests | yes (trusted policy) | passed | not_applicable | Supplied trusted observation: passed at head |
| S1 focused security pass (review plan, security routing) | yes, review-plan pass (not a repository branch-protection gate) | unavailable | not_applicable | Cause missing_specialist; see G1 |

No local commands were executed (brief forbids it). No gate was inferred green.

Mutation testing: applicable (changed decision logic in `safe_out`), **skipped: no
project-pinned runner** evidenced in the supplied tree and neither policy nor the user
requires it (fixture: mutation optional, no mutation tool installed). Mutation reference not
read, no runner installed. No outcome counts.

## Contract traceability

Linked issue DoD: "an --out value with a `..` segment or an absolute path that points
outside the project root is rejected with a clear error; a test proves it."

| ID | Criterion | State | Implementation | Verification |
|---|---|---|---|---|
| R1 | `..` segment pointing outside root is rejected with a clear error | met | `src/export.py:3` collapses `..` lexically via `normpath`; `:4-5` rejects with `refusing to write outside the project: <out>` | static trace + test `../x.html` (supplied trusted observation) + required `tests` passed at head |
| R2 | absolute path outside root is rejected with a clear error | met | `os.path.join(root, out)` discards `root` for an absolute `out`; `:4` rejects `/tmp/x.html` | static trace + test `/tmp/x.html` + `tests` passed at head |
| R3 | a test proves it | met | `tests/test_export.py` | Supplied trusted observation that the tests cover `../x.html`, `/tmp/x.html` and `reports/x.html`, and `tests` passed at head. Limit: the test source was not supplied, so assertion text was not inspected (non-material given the trusted observation). |

Note on R1/R2 and F1: the DoD names two lexical forms (`..` segments and absolute paths).
A symlinked directory is a third mechanism the criterion text does not name, so F1 is not
counted as a failed DoD (branch 2). The `..`-through-symlink variant was also traced: for
`--out reports/../x.html` with `reports/` symlinked outside, `normpath` collapses to
`<root>/x.html` and the caller writes to that returned, already-collapsed path, so the write
stays inside the root. That variant is not a defect.

## Findings

### Unresolved-boundary finding (not a blocker; linked to material gap G1)

#### F1 `export.out-path-containment` - symlinked directory inside the root escapes the `--out` containment check

| Field | Value |
|---|---|
| ID | F1 / `src/export.py:safe_out` / symlink-escape |
| Location | `src/export.py:3-4` |
| Severity | Minor |
| Blocker? | **No** - proven reachable change-introduced defect, but its security/trust-boundary status is unresolved, so it is neither relaxed nor a proven blocker; boundary_gap = G1 (record field would be `boundary_gap: G1`, with no `security_boundary` and no `non_blocking`). |
| Origin | change (`src/export.py` is a new file in this PR) |
| Reachable | yes - the only caller passes the project root and the raw `--out` value, then writes the report to the returned path |
| Verified | yes - supplied verified observation plus static trace below |

Causal anchors (verbatim, head `bbbbbbbb...`):

- `src/export.py:3`: `    path = os.path.normpath(os.path.join(root, out))`
- `src/export.py:4`: `    if not path.startswith(root + os.sep):`

Trigger / path: `reports/` inside the project is a symlink to a directory outside the root;
the user (or any caller) runs `tool export --out reports/x.html`.

Expected: per the function's own error text ("refusing to write outside the project") the
report is never written outside the project root.

Actual: `normpath` is purely lexical and does not resolve symlinks, so `path` is
`<root>/reports/x.html`, which passes the prefix check at line 4. The caller then opens that
path and the OS follows the symlink, writing the report outside the root (supplied verified
observation).

Counterevidence checked:
- Upstream validation: none; the caller passes the raw `--out` value.
- Intentional behavior: no document claims symlink handling; README describes the check as
  protection from mistyped paths.
- Base: the function is new, so the defect cannot pre-exist at base (materiality rule 4 does
  not apply).
- Counterexample pass (self-performed, no fresh verifier allowed): tried to disprove via
  `..` collapsing and absolute-path handling; neither closes the symlink path, because no
  `realpath`/`resolve` call exists anywhere in the changed code.

Materiality / boundary decision (SKILL.md materiality rule 2, in order):

1. Policy, security docs, linked issue or code comments name the check a security or trust
   boundary? **No** - the issue frames rejection as a DoD without security language, there
   are no code comments, and the README calls it protection from mistyped paths. (Note:
   project `SECURITY.md`/`AGENTS.md` were not supplied, see G2.)
2. Baseline security pass shows an untrusted source can reach it and cause an effect it
   could not otherwise cause? **Unsettled.** The README says CI runs `tool export` on
   pull-request branches. A pull-request author can plausibly commit a `reports/` symlink,
   and if CI passes a fixed in-repo `--out` such as `reports/x.html`, the CI job would write
   outside its workspace, an effect the PR author could not otherwise cause. But the CI
   configuration was not supplied, so neither the `--out` source in CI nor the author's
   ability to plant the symlink there is evidenced.
3. PR body/issue/changed docs claim resistance to such inputs? **No** - the PR body claims
   only "Rejects ../ and absolute --out paths outside the root", which the diff satisfies;
   no symlink claim exists, so branch 3 does not apply.
4. Convenience guard? **Cannot be concluded**: step 2 is unsettled, and the skill states an
   unsettled step 2 keeps the finding unrelaxed and "not a guard". It is therefore **not**
   relaxed as `guard_bypass` or `immaterial`, and is **not** a proven boundary defect either.

Result: Minor finding recorded with the open boundary question as material gap G1 under
security routing. If G1 resolves to "untrusted PR content reaches this path in CI", F1 becomes
a security/trust-boundary defect that blocks under branch 1 at any severity and must be fixed
in this PR (no follow-up deferral). If G1 resolves to "only the local user controls both the
symlink and `--out`", F1 becomes a non-blocking `guard_bypass` should-fix
(`security_boundary: false`).

Reproduction (static, runtime reproduction not permitted in this review):

```
mkdir -p /tmp/outside proj && ln -s /tmp/outside proj/reports
cd proj && tool export --out reports/x.html
# expected: "refusing to write outside the project: reports/x.html", non-zero exit
# actual (per supplied verified observation): report written to /tmp/outside/x.html
```

Verification method: complete static trace of `safe_out` and its single caller plus the
fixture's verified observation. Runtime regression verification: unverified (no execution).

Remedy (independent of how G1 resolves, recommended):
- Resolve symlinks before containment and compare by path components, not string prefix:
  `real_root = os.path.realpath(root)`, `path = os.path.realpath(os.path.join(real_root, out))`,
  reject unless `os.path.commonpath([real_root, path]) == real_root and path != real_root`;
  return the resolved `path` so the caller writes where the check looked.
- Add a regression test that creates `reports/` as a symlink to a `tmp_path` directory
  outside the root and asserts `SystemExit` for `--out reports/x.html`.
- If the check is ever declared a CI trust boundary, also consider opening the output with
  `O_NOFOLLOW` on the final component to close the check-then-write window (hardening, not
  required by the current evidence).

### Should-fix (relaxed by materiality rules)

None.

### Optional suggestions

None.

## Verification gaps

| ID | Material | Cause | Open question / evidence |
|---|---|---|---|
| G1 | yes | environment | Boundary question for F1: does untrusted pull-request content reach `safe_out` in CI (source of `--out` in the CI job, and whether a PR author's committed `reports/` symlink is present when `tool export` runs)? README states CI runs `tool export` on PR branches; CI configuration not supplied. Linked to F1 and to the unavailable S1 pass. |
| G2 | yes | environment | Project instructions (`AGENTS.md`, `cli/shared/AGENTS.md`), `REVIEW.md` for `src/` and `tests/`, and `SECURITY.md` not supplied; a project security policy could settle materiality step 1 for F1. context_complete = false. |
| G3 | no | environment | `tests/test_export.py` source not supplied; assertion text not inspected. Covered cases and the passing `tests` gate come from supplied trusted observation. |
| G4 | no | other | Root form passed by the caller (absolute, normalized, trailing separator) not shown. `root + os.sep` misbehaves for a root of `/` or a root with a trailing separator; not a verified defect because the passing `reports/x.html` test indicates the actual caller form works. |

## How to finish this review

1. Supply the CI workflow that runs `tool export` on PR branches (or a maintainer statement
   of where `--out` comes from there and whether PR-authored files are checked out first).
2. Run the focused security pass (S1) on base/head with that configuration, the `safe_out`
   caller path, and the hypothesis "a PR-committed `reports/` symlink plus a fixed CI
   `--out` writes outside the CI workspace"; ask it to disprove the claim.
3. Supply root `AGENTS.md`, `cli/shared/AGENTS.md`, applicable `REVIEW.md` and `SECURITY.md`.
4. Re-apply materiality rule 2 to F1 with that evidence: boundary -> Not ready to merge until
   fixed; guard -> F1 becomes a `guard_bypass` should-fix and, with G1/G2 closed and gates
   still green, the review can reach Ready to merge.
   Simplest path for the author: apply the F1 remedy, which closes F1 under either outcome.

## Coverage

- Reviewed 2 of 2 changed files: `src/export.py` (complete new content, every line traced,
  plus its single caller as described in the fixture); `tests/test_export.py` (via supplied
  trusted summary only - partial inspection, G3).
- Instruction / REVIEW.md paths loaded: none available (G2).
- Dimensions (project checks 1-12):
  1. Issue scope: R1-R3 met; no scope creep (only the two expected files changed).
  2. Structural integrity: required lint/tests passed at head (trusted); no local commands
     run; no command surface change beyond the new validation.
  3. Stale code: not applicable - new file, nothing removed or renamed.
  4. Debt: debt introduced - lexical-only path containment (F1); debt closed - unbounded
     `--out` writes now rejected for `..` and absolute escapes.
  5. Docs: no docs changed; README "mistyped paths" description is consistent with the code.
  6. Conventions: not assessable against AGENTS.md (G2); nothing observable conflicts.
  7. Follow-up hygiene: F1 must not be deferred by the reviewer; any deferral is the
     author's under rule 5 and only if G1 resolves to a guard.
  8. Correctness: `safe_out` traced for `..`, absolute, plain relative, `..`-through-symlink
     and symlinked-directory inputs; F1 found; G4 noted.
  9. Security: baseline pass done - untrusted-input-to-file-write surface identified (`--out`
     -> file write); CI exposure unresolved (G1, S1). No secrets, dependencies or privilege
     changes.
  10. Tests: cover the DoD's lexical cases and the accepted plain path; no symlink case
      (part of F1 remedy).
  11. Skill content quality: not applicable - no skill bodies touched.
  12. PR description: linked issue present; the claim "Rejects ../ and absolute --out paths
      outside the root" matches the diff; not contradicted.
- Focused lenses: errors/fallbacks - applicable, the rejection path raises `SystemExit` with
  a clear message and no success-on-failure; type invariants - not applicable (no types);
  comments/docs claims - applicable, README claim consistent; test resilience - applicable,
  missing symlink scenario noted under F1.

## Risk

**Medium.** The change gates where a CLI writes files. Blast radius: the `tool export`
command and, per the README, CI jobs that run it on PR branches - CI is a boundary the
protocol requires explicit human scrutiny for. Reversibility: a code revert restores prior
behavior; files already written outside the root are not reverted automatically. No
deployment, migration or feature flag involved; rollback is reverting the commit. Owner /
human reviewer: not supplied. Unresolved limits: G1-G4.

## Propagation sweep

- Class `export.out-path-containment`: searched all six lines of `src/export.py` (the whole
  changed production code) and the described single caller for other containment or
  path-resolution sites; 1 instance found (`src/export.py:3-4`). `tests/test_export.py` not
  swept at source level (G3). One instance only, so no class-sweep trigger.
- Legacy left: none. Net: improves on unbounded writes; symlink gap remains.

## Out-of-scope observations

1. The PR body does not state the remaining limitation (symlinked directories are not
   resolved); disclosing it, or fixing F1, would make the scope explicit. Non-blocking.

## Carried

Unavailable - round one, no published baseline.

## Re-review data

Not applicable - first review round. Published blocker status: none (no prior review).

## Limits

Offline fixture: no network, git, gh, program, test, validator or anchor-verifier execution;
no subagents; no publication. All repository state comes from the fixture's supplied trusted
observation. PR number/URL/title, issue number, CI configuration and project instruction
files were not supplied and are not invented. This verdict is not merge permission.
