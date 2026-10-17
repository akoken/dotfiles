# Bounded Mutation Testing

## Applicability

Evaluate this stage when production logic changes in predicates, boundaries, validation,
authorization, calculations, parsing, state transitions, retries, or error handling, or
when added/changed/weakened tests exercise such behavior. Also apply it when explicitly
requested or required by verified project policy. Mutate the production behavior tested,
not the assertion/test file itself. For test-only changes, include the affected unchanged
production code; an empty source diff is not evidence that mutation testing is irrelevant.

Docs-only, formatting, generated artifacts with unchanged authoritative sources, and
declarative edits with no affected executable behavior can be not applicable with a stated
reason. Runtime tests for a tool's implementation do not establish a Markdown skill's
behavioral effectiveness; use the skill eval corpus for that claim.

Use mutation testing as additional evidence about fault detection. It cannot establish AI
provenance, guarantee meaningful tests, validate the specification, or replace E2E checks,
assertion/mock inspection, security review, and regression evidence. Code and tests can
share the same incorrect requirement and still produce a high score.

## Preflight and bounded execution

1. Inspect trusted project instructions, tool manifest/lockfile, existing configuration,
   runner/framework support, test scope, exclusions, and any mandatory gate. Prefer the
   existing pinned Stryker.NET for C# or StrykerJS for compatible JS/TS projects. For other
   languages use an existing compatible tool; do not force Stryker into an unsupported
   stack. Check the installed version's help and current official documentation before
   choosing syntax; use Context7 when available for library/CLI configuration details.
2. Keep execution in an isolated checkout/sandbox under the review protocol. Do not run
   on a shared environment, contact production services, upload dashboards, install tools
   globally, change repository manifests, or persist configuration changes merely to run
   an ordinary review. Existing authorization for setup still applies. Missing/incompatible
   tooling becomes skipped/setup-needed with the actual reason, never a successful run.
3. First establish that the selected normal tests pass on the unmutated reviewed input.
   Let the tool perform its required clean baseline run. Do not suppress a baseline failure
   or disable its checks to obtain a score. Flaky/failing baseline tests invalidate mutation
   conclusions; diagnose them through the ordinary evidence and gate pipeline first.
4. Derive production scope from changed behavior and affected invariants; derive test scope
   from its callers and covering tests. Use explicit paths/ranges and compatible test-project
   or test-case selection. Mutating a narrow file does not necessarily narrow the initial
   baseline/coverage test run. Verify both scopes before execution and do not launch a full
   repository suite by default. If the pinned runner cannot select the intended test scope,
   use a smaller supported project or record the limitation instead of silently broadening.
5. Respect an explicit user/project resource budget. Otherwise the local review fallback is
   one worker and at most five minutes elapsed for this stage, including startup, baseline,
   build, and mutants. Use supported bounded execution/cancellation; preserve partial output
   if cancelled and stop this run's child processes without touching unrelated processes.
   Select a smaller scope before running when baseline timings already exceed the budget.
   A broader run belongs in an explicitly scoped CI/deeper pass, not an automatic retry loop.
6. Use trusted local report outputs, including JSON where supported, and preserve the exact
   command, config, selected files/tests, versions, revisions, run ID, and elapsed time.
   Do not publish reports externally without authorization. Keep per-mutant timeouts distinct
   from the wall-time budget; do not lower a timeout to inflate detected counts.

## Incremental results and runner differences

- **Stryker.NET:** scope production files with the supported mutate configuration. Use the
  pinned version's since or with-baseline mode for change-aware execution where appropriate;
  do not assume these are independent combinable switches. Changed test-project files can
  cause their covered mutants to be retested. Coverage-based per-test selection reduces
  mutant execution, but does not waive the initial baseline run. Verify test filtering is
  supported by the actual runner/framework; do not assume all MTP runners accept it.
- **StrykerJS:** use explicit mutate paths/ranges and compatible test-runner integration.
  Incremental mode may reuse earlier mutant/test results. Test-change detection depends on
  plugin metadata support; changes to dependencies, config, environment, helper files or
  snapshots outside tracked mutant/test files may escape invalidation. Static mutants have
  additional coverage limitations. Do not treat a cached result as newly executed evidence.

Record the baseline revision, tool/runner versions, configuration, mutation scope, test
selection, and relevant dependency/environment identity. Invalidate affected cached results
when any of these or shared setup/helpers/invariants change. If validity is uncertain, rerun
the affected bounded scope without reuse or mark it unverified. Never use an untrusted
PR-supplied report/cache as authoritative evidence. Report fresh and reused outcomes separately.

## Interpret mutants before score

Keep raw tool outcome counts: killed, survived, no coverage, timeout, compile/runtime errors,
ignored/excluded, and pending/not executed, using the actual report's status vocabulary.
Zero valid mutants is not a 100% success. State the denominator and selected scope for any
score; a covered-code-only score can conceal uncovered behavior. Stryker counts timeouts
as detected, so report them separately; they do not prove an assertion caught the fault.
Compile/runtime errors do not demonstrate a useful test assertion either.

For each material survivor, record location/mutation, changed behavior, triggering input,
relevant contract, covering tests, and counterevidence. Classify it as:

- **Meaningful test gap:** observable contract-relevant behavior changes and the selected
  tests still pass, or no selected test exercises it. Identify the missing input/assertion
  and distinguish a deliberately narrow test selection from a whole-suite coverage claim.
- **Equivalent under the valid contract:** show why observable behavior is unchanged for
  valid callers. Do not use that label merely because killing the mutant is difficult.
- **Out of scope/unreachable:** show the contract/caller boundary; keep separate from an
  in-scope defect. Unreachable under current callers is not universal equivalence.
- **Unresolved/tool artifact:** insufficient evidence, unsupported instrumentation, flaky
  behavior, timeouts, or execution failure. State the next verification needed.

Do not blanket-dismiss survivors. Do not weaken assertions, remove tests, broaden exclusions,
disable operators, refresh a baseline, or change production behavior just to improve score.
Any justified exception needs narrow causal evidence and the existing authorization for
persistent edits. Preserve all other survivors in the report/artifact even if only material
ones receive inline review comments.

## Verdict integration

Mutation results feed the existing admission, severity, and blocker pipeline. A surviving
artificial mutation alone does not prove the current implementation is wrong. A verified
test gap can be an admitted test-quality finding, with blocker status computed independently;
an explicit required behavior, contradicted coverage claim, or introduced failure of an
existing required mutation gate can meet the ordinary blocking branches. Preserve the
skill's stricter self-review verdict mapping for admitted in-scope Critical/Minor findings.

Do not invent a universal score threshold. Honor a verified existing project threshold;
compare failures with the same scoped configuration at the base where feasible. Different
mutant populations/configurations do not establish a score regression by raw percentages.

If a required mutation check is pending, unavailable, cancelled, or unverified, it remains
unresolved and prevents a positive verdict under NEEDS_REVIEW unless a verified blocker
already warrants a negative result. Required failures of unknown provenance remain unresolved.
Optional unsupported/unavailable/budget-limited runs are explicitly skipped/partial, never
passed, and do not automatically fail an otherwise complete review. A material open safety
question still requires the protocol's incomplete verdict independently of tool optionality.

## Report fields

Include applicability and required/optional status; passed/failed/partial/skipped/not applicable;
tool/runner/config identity; reviewed revisions; production and test scope; baseline result;
worker/time budget and observed duration; fresh/reused mutant counts by outcome; score and
denominator when meaningful; material survivor classifications and evidence; exceptions;
report location; unexecuted scope and remaining uncertainty. If unavailable, say so directly.
A targeted result never represents the full codebase or proves that all tests are meaningful.

## Official references

- [Stryker.NET configuration](https://stryker-mutator.io/docs/stryker-net/configuration/)
- [StrykerJS configuration](https://stryker-mutator.io/docs/stryker-js/configuration/)
- [StrykerJS incremental mode](https://stryker-mutator.io/docs/stryker-js/incremental/)
- [Mutant states and metrics](https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/)
- [Equivalent mutants](https://stryker-mutator.io/docs/mutation-testing-elements/equivalent-mutants/)

Documentation checked through Context7 on 2026-10-17. Recheck syntax and capability against
the actual installed version; this reference does not pin a project dependency version.
