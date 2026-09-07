---
name: testing-crap-analysis
description: Use when collecting .NET coverage, analyzing CRAP risk hotspots, prioritizing tests or refactoring by complexity, or configuring coverage reports and CI thresholds.
---

# CRAP Score Analysis

## Workflow

1. Preflight: check `command -v reportgenerator` and `dotnet tool list -g` for dotnet-reportgenerator-globaltool; prefer a manifest-pinned `dotnet tool restore` and `dotnet tool run reportgenerator -- <arguments>`. If neither local nor global tool exists, run `dotnet tool install --global dotnet-reportgenerator-globaltool`. Repair this shell PATH for an installed global tool instead of reinstalling; report install/restore scope and stop on failure.
2. Inspect test projects, collectors, runsettings, exclusions, existing thresholds, and baseline reports; identify the production code being assessed.
3. Configure OpenCover output with complexity metrics using the coverage setup branch; retain justified exclusions and separate current results from stale reports.
4. Run the relevant tests with coverage and generate the selected ReportGenerator outputs, including HTML Risk Hotspots.
5. Rank methods by reported CRAP, complexity, and uncovered behavior; map high-risk methods to concrete tests or refactoring work.
6. Compare new and legacy code with the threshold policy; record test failures, unavailable metrics, exceptions, and report paths.

Completion requires fresh coverage and Risk Hotspots for the stated scope, identified high-risk methods with actions, and explicit threshold results or documented collection blockers.

## Reference Routing

Read only the needed branch of [references/full-guide.md](references/full-guide.md):

- `What is CRAP?`.
- `Preflight`.
- `Coverage Collection Setup`.
- `ReportGenerator Installation`.
- `Collecting Coverage`.
- `Reading the Report`.
- `Coverage Thresholds`.
- `CI/CD Integration`.
- `Quick Reference`: command or decision lookup.
- `What Gets Excluded`.
- `When to Update Thresholds`.
- `Additional Resources`: external documentation.

Use `rg -n '^## ' references/full-guide.md` to locate the relevant section.

## Guardrails

- Do not substitute Cobertura-only input for OpenCover complexity data when calculating CRAP.
- Do not accept new code below 80% line or 60% branch coverage, or above CRAP 30, without an explicit documented policy exception.
- Do not silently lower legacy targets below 60% line and 40% branch coverage; document the improvement plan and CRAP exceptions.
- Do not change high-risk legacy methods without adding relevant tests.
- Do not lower thresholds because testing is hard, deferred, or part of a new feature.
- Do not exclude handwritten production behavior merely to improve scores.
- Do not report missing tool execution or failed test collection as a passing coverage gate.
