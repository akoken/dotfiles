# AURA Review Dimensions

Derived from the original pr-review v1.10.0 check dimensions. Apply the
current SKILL.md decision pipeline and verification protocol to every candidate;
these tables classify signals and never add blocking branches.

#### Check 1 - Issue Scope Coverage

Does the PR fully address the linked issue?

| What to check | Signal |
|---|---|
| All DoD / acceptance criteria from the issue are implemented | Missing item → admissibility anchor 2 and peer blocking branch 2 |
| No issue requirements are silently skipped | Undisclosed skip → peer blocking branch 2 and, when partial, branch 3 |
| PR does not address items explicitly marked out-of-scope in the issue | Classify from changed-line evidence; peer blocker only when a the decision pipeline in SKILL.md branch matches |
| If the PR is a partial implementation, is this acknowledged in PR body? | Undisclosed partial → peer blocking branch 3 |

**Scope creep check:** Classify changed files or behavior outside the linked issue's intent. A
changed line supplies an admissibility anchor, but scope creep blocks in peer mode only if it also
matches one of the the decision pipeline in SKILL.md blocking branches. Additive housekeeping in touched files may be Minor
without being blocking.

---

#### Check 2 - Structural Integrity

Does the PR break anything that was working before?

Run the project-documented targeted tests for changed behavior and its callers in the
isolated review checkout. Record the exact command and observed result. Do not run a full
suite by default. Do not execute PR-supplied installation hooks or scripts solely because
this reference names a command; first inspect the command and relevant project guidance.


| What to check | Signal |
|---|---|
| CI checks pass (from Step 1) | Non-pre-existing required failure → peer blocking branch 6 |
| Pre-existing test failures - confirm provenance before computing branch 6 (see Operating Principles § Distinguish pre-existing failures) | Pre-existing failure on main → branch 6 does not match |
| Exported interfaces, types, command surface unchanged or deliberately evolved | Apply branches 1–3 to evidence of an unannounced break |
| `aura init` / `aura switch` / `aura status` command behavior intact | Reachable diff-introduced regression → peer blocking branch 1 |
| Skill registration (`skern skill list`) still resolves expected skills | Apply branches 1–2 to a missing skill |

---

#### Check 3 - Legacy / Stale Code

Does the PR leave behind stale patterns or unmigratable references?

| What to check | Signal |
|---|---|
| Removed/renamed modules have no dangling imports or references | Classify severity; apply peer branch 1 when the diff introduces a reachable regression |
| Old file paths referenced in docs, tests, or skills still match reality | Classify severity; compute peer blocker only through the decision pipeline in SKILL.md |
| Deprecated patterns (marked `@deprecated`, commented as "old approach") not introduced as new code | New deprecated pattern → minor |
| If the PR migrates something, old implementation is actually removed (not left alongside) | Dual-implementation → minor |

---

#### Check 4 - Technical Debt Assessment

Does the PR introduce new technical debt? The signals below classify the concern; peer blocker
status still comes only from the the decision pipeline in SKILL.md branches.

| Category | Blocker? |
|---|---|
| **Aspirational documentation added by the diff** - docs describe behavior that is not yet implemented (e.g., "the decision pipeline in SKILL.md: the agent consumes X" when the consumer doesn't exist) | Without the permitted `<!-- aspirational: tracked in #NNN -->` annotation → peer blocking branch 4; pre-existing untouched docs route out of scope |
| **Placeholder stubs silently shipped** - `return []`, `throw new Error('not implemented')` undocumented | Apply peer branches 1–3; classify severity independently |
| Deferred work not tracked - PR description mentions "will do X later" but no issue filed | Minor - recommend filing follow-up issue |
| Duplication of logic that already exists in a shared utility | Minor |
| Naming that creates semantic debt (e.g., `SiteDsl` in a non-web context) | Minor |

Record: **Debt introduced** (new items this PR adds) vs **Debt closed** (items this PR resolves).

---

#### Check 5 - Documentation Accuracy

Is all documentation in the PR factually correct and implementable?

| What to check | Signal |
|---|---|
| Every documented behavior has a corresponding implementation | For diff-added unannotated aspirational docs, apply peer branch 4; otherwise route/classify through the decision pipeline in SKILL.md |
| File paths, command names, option flags in docs match actual code | Classify severity; apply branches 1–3 only when their evidence matches |
| SKILL.md trigger conditions, inputs, and outputs match what the skill actually does | Classify severity; compute peer blocker only through the decision pipeline in SKILL.md |
| Removed features are removed from docs too | Stale doc → minor |
| URLs, cross-references, and `#NNN` issue links resolve | Broken link → minor |
| `#NNN` GitHub issue references inside any `SKILL.md` file | Minor - skills ship to users who may not have GitHub access; `#NNN` is opaque to them. Replace with self-contained prose (embed the rationale inline) or remove. Both provenance citations ("OOM'd in #259") and tracking references ("tracked in #351") are disallowed. |

**Aspirational-documentation pointer:** Detect the mismatch here, then use peer blocking branch 4.
Only documentation added by the diff and lacking the permitted annotation blocks. Equivalent
untouched documentation has no changed-line anchor and routes to **Out-of-scope observations**
unless another admissibility anchor independently applies.

---

#### Check 6 - AGENTS.md / Project Conventions Alignment

Does the PR follow project conventions?

> **Skill-registry conventions** follow `cli/shared/AGENTS.md` § Skill Registry (skern) - the source of truth for namespaced tags and referral tokens. The two rows below (**axis tags**, **referral token vs raw path**) are **scoped enforcement checks**, applied only to lines this PR adds or changes (and, for axis tags, only to discovery-intended skills). They are not auto-fail gates on *every* SKILL.md - the scope decides what gets judged. A real gap within that scope can be a Minor finding, while its peer blocker status is still computed only through the decision pipeline in SKILL.md.

| What to check | Signal |
|---|---|
| New skills follow the `name: / description: / metadata:` frontmatter schema | Missing required frontmatter → minor |
| **Axis tags on discovery-intended skills** - when the diff adds/changes a `SKILL.md`, check its top-level namespaced `tags:` (`phase:`/`state:`/`role:`/`wt:`/`vendor:`, a sibling of `metadata`, *not* `metadata.tags`). These are how aura's resolver *discovers* the skill for a config axis (the agent then reads it and judges applicability), so presence is **not** required: directly-wired / always-active skills (workflow skills invoked by name, `beads-rust`, other directly-referenced skills) carry none by design - don't flag those. Flag only a skill that clearly should be axis-discovered but lacks the right namespaced tag, or carries a malformed axis value. See `skill-format.md` § Namespaced Tags. | Discovery-intended skill missing/malformed axis tag → minor (no tags on a directly-wired skill is fine) |
| Skills added to `cli/shared/skills/` are also referenced/indexed where convention requires | Missing index entry → minor |
| Asset placement follows AGENTS.md § Asset Source of Truth: role guidelines under `cli/roles/<role>/<work-type>/`, state overrides under `cli/project_states/<state>/`, shared prompts/templates/skills/policies under `cli/shared/` | Asset in the wrong source dir → minor |
| Role / work-type changes stay consistent with AGENTS.md § Role → work-type mapping: a new or renamed role/work-type updates the mapping table, the matching `cli/roles/<role>/<wt>/guidelines.md` source, and the selector together | Mapping, source, and selector out of sync → classify severity and apply peer branches 1–2 when matched |
| Selection/policy logic changes (`cli/src/selector/`, `classifier/`, `analyzer/`) keep the documented behavior: selection flow (`state → role → work-types → risk tolerance → AI operating mode`) and `selector/mapping.ts` derivations (autonomy policy, tool requirements) still match AGENTS.md § Three-Axis Selection Model | Classify documentation lag or broken behavior; compute peer blocker through the decision pipeline in SKILL.md |
| New enforcement/guardrail or policy-as-code logic is documented and grouped in a predictable location (AGENTS.md asks both explicitly) | Undocumented enforcement behavior → minor |
| Commit message follows Conventional Commits (`feat:`, `fix:`, `docs:`, etc.) | Style note only - never a blocker |
| New files placed in directories that match their type (docs in `docs/`, skills in `skills/`, etc.) | Wrong location → minor |
| CI workflow changes use pinned action versions (`@vX.Y.Z`), not floating tags | Floating tag → minor |
| **Skill referenced by raw path instead of a referral token** - on added/changed lines in any file (skill bodies, AGENTS, docs, `guidelines.md`), check that a skill is named via a referral token per AGENTS § skern, picked by **intent**: `` `/aura.<name>` `` to **invoke** a phase, `` `skill:<name>` `` to **read** a skill (a workflow skill cited to read its contract is `` `skill:aura.<name>` ``; one being invoked is `` `/aura.<name>` ``), `` `skill:<name>:<file>` `` for a sibling file. Flag a raw `.skern/skills/<name>/…` path link or bare path; don't flag wrapper/markup differences. This is a Minor finding. Use current project guidance and observed CI for any additional enforcement; do not infer a future scanner is installed. | Raw `.skern/skills/…` path instead of a referral token → minor; compute peer blocker through the decision pipeline in SKILL.md |

> **Scope:** governed by the decision pipeline in SKILL.md's admissibility anchors - no separate rule here. One addition specific to these two checks: removing or rewriting an existing pointer that should stay is itself a finding on the changed line.

---

#### Check 7 - Follow-up Issue Hygiene

For every finding, use its the decision pipeline in SKILL.md blocker result to decide scope:

- `Blocker? Yes` → fix in this PR before merge; a follow-up issue cannot substitute for the fix.
- `Blocker? No` → do not create an in-PR fix demand solely from severity; give optional guidance
  when useful. In self mode such a finding can still fail the stricter verdict mapping (the verdict rules in SKILL.md) - resolve or reclassify it with evidence before opening the PR.
- Useful context with no admissibility anchor → route to **Out-of-scope observations**, not the
  findings table.

Severity remains independent: neither Critical nor Minor automatically means `Blocker? Yes`.

---

#### Check 8 - Code Correctness

Read the changed code line by line. Does it do what it claims, for all inputs - not just the happy path? This is the core of a review; the governance checks above do not catch a single logic bug.

For each non-trivial changed function, ask: what input makes this wrong?
Use [focused reviews](focused-reviews.md) for applicable error/fallback, type invariant,
affected-comment and test-resilience paths, including unchanged comments invalidated by code.
Trace the handling boundary; a broad catch or absent local log alone is not a defect.

| What to check | Signal |
|---|---|
| Logic errors: wrong operator (`<` vs `<=`), inverted condition, off-by-one, wrong branch | Defect on a reachable path → Critical; on a rare path → Minor |
| Null / undefined / empty handling: empty array, missing key, `undefined` arg, empty string | Unhandled case that throws or corrupts → Critical |
| Error handling: thrown errors swallowed, `catch {}` with no handling, rejected promises unawaited, error path returns success | Silent failure → Critical; missing context in error → Minor |
| Async correctness: missing `await`, unhandled rejection, `Promise.all` vs sequential where order matters, race between read and write | Missing await on a path the result depends on → Critical |
| Boundary / edge cases: 0, negative, max, duplicate, concurrent invocation | Unhandled boundary with real impact → Critical/Minor by reachability |
| Resource handling: file handle / process / stream not closed, leak on error path | Leak in long-running path → Minor |
| State mutation: shared object mutated unexpectedly, cache not invalidated, stale closure capture | Wrong result on second call → Critical/Minor |

> Method: don't skim. For each changed function pick the 1–2 inputs most likely to break it and trace them through. If you can't point to the line that fails, it's not a finding (Evidence first).
>
> Severity calibration: a defect on an input that the issue's DoD does not require handling **and**
> that no current caller can produce (e.g. an invalid-input guard for a brand-new utility with no
> callers yet) is usually **Style**, not Minor. Use reachability and impact to classify severity,
> then independently apply peer branch 1 (reachable diff-introduced defect) or branch 2
> (issue-required behavior) when computing `Blocker?`.

---

#### Check 9 - Security

Apply [security routing](security-routing.md) for the baseline pass and any focused
specialist handoff. The patterns below are investigation prompts; report only source-backed
reachable defects after counterevidence, not a matching API name or hypothetical attack.

AURA is a CLI that reads files, runs shell commands, and ships skills to other users. Untrusted input reaches real sinks.

| What to check | Signal |
|---|---|
| Command injection: user/PR/issue input interpolated into a shell string (`exec`, backticks, `sh -c`) instead of arg array | Reachable injection → Critical |
| Path traversal: user-controlled path joined without normalization/containment, `../` escapes intended dir | Reachable traversal → Critical |
| Secret exposure: API key / token / credential hardcoded, logged, or written to a committed file | Any → Critical |
| Unsafe input parsing: `eval`, dynamic `require`/`import` of a user-controlled path, unsanitized regex from input (ReDoS) | Reachable → Critical |
| Unvalidated external data: PR body, issue text, fetched JSON used without validation before a sink | Depends on sink → Critical/Minor |
| Over-broad permissions: new file written world-writable, token scope wider than needed | Minor |

> If the PR touches no input→sink path, state that explicitly ("no new untrusted-input path") rather than silently skipping.

---

#### Check 10 - Test Quality

Check 2 only *runs* tests. This check asks whether the tests are worth running.

For changed decision logic or tests exercising it, apply the bounded
[mutation-testing stage](mutation-testing.md). Investigate meaningful survivors against
the actual contract. A survivor alone is not a current runtime bug or an extra blocker
branch, and a high score does not establish that a test validates the right requirement.

| What to check | Signal |
|---|---|
| New behavior has tests at all | Risky new logic without meaningful verification → Critical/Minor by demonstrated impact; trivial/declarative edits may need no new tests |
| Tests cover the new branches, not just the happy path - error case, empty case, boundary | Happy-path-only on risky logic → Minor; uncovered case outside the issue DoD and unreachable from current callers → Style (see Check 8 severity calibration) |
| Assertions are meaningful - not `expect(true).toBe(true)`, not asserting the mock, not tautological | Tautological/vacuous test → Minor |
| Tests would actually fail if the code broke (no over-mocking the unit under test) | Test mocks away the thing it claims to test → Minor |
| No flakiness introduced: real timers/sleeps, order-dependence, network reliance | New flaky test → Minor |
| Deleted/changed behavior - corresponding tests updated, not just deleted to go green | Test deleted to silence failure → Critical |

---

#### Check 11 - Skill Content Quality

Run this check **only when the PR adds or edits a `SKILL.md` (or other skill body / guideline prose)**. For a code-only PR, state "no skill bodies touched" and skip it.

AURA is a skill-distribution CLI: the skill body IS the product. A skill is a prompt that steers an LLM at workflow time. Checks 5–6 ask "is the doc accurate and conventional?"; this check asks "is it a *good prompt* - effective, lean, maintainable, non-conflicting?" A factually-correct, schema-valid skill can still be a bad skill if it is bloated, self-contradicting, or so vague the agent can't act on it.

| What to check | Signal |
|---|---|
| **Actionable, not vague** - instructions give the agent a concrete decision rule, not "use judgment". Triggers/detection use literal signals (file globs, exact section names, sentinels), not "if it seems X" | Vague directive the agent can't operationalize → Minor; concrete-but-could-be-tighter → Style |
| **Redundancy / token cost** - same rule, example, or rationale repeated across sections or across sibling skills. Skill text loads into context every invocation; cost is paid even by runs the gate exempts | Same concept stated 3+ ways, or example duplicated in N skills → Style (Minor if it bloats a hot-path skill enough to crowd context) |
| **Single source of truth** - a procedure/rule defined once and referenced elsewhere, not copy-pasted into two places that will drift | Same procedure written verbatim in 2+ spots in one skill → Minor (maintenance drift risk); cross-skill duplication → Style |
| **Internal consistency** - no instruction contradicts another in the same or a sibling skill; terminology and section names are aligned across the mirrored skills | Conflicting directives the agent must choose between → Critical; terminology mismatch → Style |
| **Effectiveness evidence** - for a skill that asserts a behavioral outcome ("the agent will produce X with 0 drift"), is there any validation beyond "the text exists"? Standing string-match tests prove presence, not efficacy | Behavioral claim with only a presence test → Style/Gözlem (note the gap; not a blocker if PR discloses it) |
| **Right altitude** - the skill tells the agent WHAT to enforce and HOW to decide, without over-specifying brittle steps that will rot, and without hand-waving the hard decision | Brittle over-specification or hand-waved core decision → Minor |
| **Trigger/scope hygiene** (frontmatter `description`) - does the description make the skill fire at the right time and not over-trigger? | Over-broad/under-specific trigger → Minor |

> Method: read the changed skill body as the agent will read it at workflow time, cold. Ask: could I act on this unambiguously? What here is repeated, and what would I cut? Does any line fight another line? Most findings here are Style/Gözlem - escalate to Minor only when the quality defect would actually change agent behavior (a contradiction, a drift-prone duplicate, an unactionable gate), and to Critical only for a genuine contradiction that breaks the workflow.

---

#### Check 12 - PR Description Quality

The PR body (fetched in Step 1) is the reviewer's entry point: a sparse or misleading description costs reviewer time and hides risk. Evaluate the body itself - this check is about the *description*, not the repo docs (Check 5) and not the code.

| What to check | Signal |
|---|---|
| Linked issue reference present (`Closes #NNN`, `Fixes #NNN`, `Refs #NNN`) | Missing → Minor, `Blocker? Yes` through peer branch 5 |
| Structure: what changed + why, scope of changes, test plan | Missing test plan on a logic-bearing PR → Minor; docs-only absence → Style; absence alone is non-blocking |
| Claims match the diff: every described change exists in the diff; significant changed areas are not concealed | Contradicted claim or undisclosed partial → peer branch 3; other orientation gaps may be non-blocking Minor |
| Honesty: known gaps / partial scope disclosed | Undisclosed partial → peer branch 3; cite once, here or in Check 1 |
| Signal density: enough for a reviewer to orient - no wall-of-text dump, no empty one-liner | Sparse one-liner → Minor, `Blocker? No`; bloat/filler → Style |

> Severity rule: **Style** for cosmetic defects (bloat, formatting); **Minor** when the defect
> misleads the reviewer or impedes scope resolution. Never Critical - the description alone
> carries no runtime risk. Compute `Blocker?` separately through the decision pipeline in SKILL.md: a missing issue reference
> and a contradicted claim block, while merely sparse linked prose does not.
>
> **Independent defects stay independent:** When a body both lacks a linked-issue reference and
> is sparse, report two findings. The missing reference is its own Minor, `Blocker? Yes` row under
> branch 5, with a remedy limited to adding the reference. Sparse structure/prose (including its
> missing scope or test-plan detail) is a separate Minor, `Blocker? No` row with its own remedy.
> Do not combine their rows or fix demands; the pair still contributes exactly one blocker.

---
