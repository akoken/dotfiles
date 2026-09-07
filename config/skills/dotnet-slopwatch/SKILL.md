---
name: dotnet-slopwatch
description: Use after LLM changes to C# source, tests, project files, or shared props; when investigating Slopwatch detections; or when configuring its baseline, edit hooks, and CI gate.
---

# Slopwatch: LLM Anti-Cheat for .NET

## Workflow

1. Preflight: check `command -v slopwatch` and `dotnet tool list -g` for Slopwatch.Cmd; prefer a manifest-pinned `dotnet tool restore` and `dotnet tool run slopwatch -- <arguments>`. If neither local nor global tool exists, run `dotnet tool install --global Slopwatch.Cmd`. Repair this shell PATH for an installed global tool instead of reinstalling; report install/restore scope and stop on failure.
2. Inspect the changed files, existing baseline, exclusions, and severity policy before analysis; initialize a first baseline from pre-change legacy code only.
3. Run `slopwatch analyze --fail-on warning` after each relevant code modification, using the local invocation when pinned.
4. Map detections to Detection Rules; fix the underlying disabled test, suppression, swallowed error, timing workaround, or package-management bypass.
5. Rerun analysis after fixes; document the narrow reason for any justified baseline update or generated-code exclusion.
6. For hook or CI setup, use the integration branch and verify that a failing analysis propagates a failure to the caller.

Completion requires a successful analysis of the final changes, no unexplained new detections, and documented justification for every baseline or exclusion change.

## Reference Routing

Read only the needed branch of [references/full-guide.md](references/full-guide.md):

- `What is Slop?`.
- `Preflight`.
- `Installation`.
- `First-Time Setup: Establish a Baseline`.
- `Usage During LLM Sessions`.
- `Claude Code Hook Integration`.
- `CI/CD Integration`.
- `Detection Rules`.
- `Configuration`.
- `The Philosophy: Zero Tolerance for New Slop`.
- `Quick Reference`: command or decision lookup.
- `When to Override (Almost Never)`.

Use `rg -n '^## ' references/full-guide.md` to locate the relevant section.

## Guardrails

- Do not initialize or refresh a baseline over new defects to make analysis pass.
- Do not disable tests or suppress warnings instead of fixing their causes.
- Do not swallow exceptions or add arbitrary test delays to hide failures.
- Do not lower severity or disable rules merely because a detection is inconvenient.
- Do not reinstall a global tool that only needs its PATH repaired.
- Do not report analysis as passed when tool restore, installation, or execution failed.
