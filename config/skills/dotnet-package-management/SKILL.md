---
name: dotnet-package-management
description: Use when adding, removing, or upgrading NuGet packages, configuring Central Package Management and shared versions, managing feeds, or diagnosing dependency conflicts and restore failures.
---

# NuGet Package Management

## Workflow

1. Inspect the pinned SDK, target projects, package manifests, central version ownership, lock files, and configured sources.
2. Choose the existing package-management mode; consult CPM suitability before proposing a migration and identify related shared version variables.
3. Use dotnet add/remove/list commands for the requested change; inspect CLI help for the installed SDK and the resulting central/project diff.
4. Preserve shared version ownership and development-only, conditional, or override metadata; use repository tooling for changes the CLI cannot express.
5. For feed or restore failures, inspect sources and dependency paths before applying the relevant troubleshooting branch.
6. Restore, build the affected projects, and inspect resolved direct/transitive versions and lock-file changes.

Completion requires the requested package graph restored and built, one owner for each version, preserved package metadata, and reviewed project, central-version, and lock-file diffs.

## Reference Routing

Read only the needed branch of [references/full-guide.md](references/full-guide.md):

- `Golden Rule: Never Edit XML Directly`.
- `Central Package Management (CPM)`.
- `Shared Version Variables`.
- `When NOT to Use CPM`.
- `CLI Command Reference`.
- `Package Sources`.
- `Common Patterns`.
- `Troubleshooting`.
- `Anti-Patterns`.
- `Quick Reference`: command or decision lookup.
- `Resources`: external documentation.

Use `rg -n '^## ' references/full-guide.md` to locate the relevant section.

## Guardrails

- Do not edit XML directly; use dotnet CLI commands or the repository package-management tooling.
- Do not inline package versions when CPM owns them.
- Do not mix central and per-project version ownership accidentally.
- Do not replace shared version variables with independently drifting literals.
- Do not migrate working legacy projects to CPM without checking SDK support and intentional version differences.
- Do not commit feed credentials or clear caches as the first response to every restore failure.
