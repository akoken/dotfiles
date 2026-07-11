---
name: dotnet-project-structure
description: Structure or modernize .NET solutions using .slnx, global.json, Directory.Build.props, Central Package Management, SourceLink, NuGet configuration, release metadata, and reproducible build conventions. Use for new solution setup, repository-wide build configuration, SDK pinning, or project-layout migrations.
---

# .NET Project Structure

## Workflow

1. Inspect the current SDK, target frameworks, solution format, repository layout, shared build files, package-management mode, CI commands, and release conventions.
2. Preserve working repository conventions unless the requested modernization has a measurable benefit.
3. Change one ownership layer at a time: solution membership, SDK selection, shared build properties, package versions, release metadata, then CI.
4. Use the .NET CLI for solution and package operations when it supports the change.
5. Verify restore and build from a clean-enough state using the repository's pinned SDK and normal entry point.

Completion requires every project to remain reachable from the intended solution/build entry point, package versions to have one owner, and the documented build command to pass or have a clearly identified baseline blocker.

## Reference Routing

Read [references/full-guide.md](references/full-guide.md) only for the branch being changed:

- `.slnx` creation or migration;
- `Directory.Build.props` and common package metadata;
- `Directory.Packages.props` and Central Package Management;
- `global.json` roll-forward policy;
- release-note/version scripts;
- `NuGet.Config`, SourceLink, CI, or complete layout examples.

Use `rg -n '^## |^### ' references/full-guide.md` to locate the relevant section instead of loading unrelated examples.

## Guardrails

- Do not introduce a second source of truth for package or version data.
- Do not hand-edit generated solution state when the CLI provides the operation.
- Do not upgrade SDKs, target frameworks, analyzers, and packages in one undifferentiated change.
- Do not assume every repository needs the full reference layout.
- Preserve public package metadata, deterministic builds, and SourceLink when publishing libraries.
