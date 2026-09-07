---
name: csharp-api-design
description: Use when designing public C# APIs, reviewing library compatibility, planning NuGet versioning or deprecation, or changing distributed wire contracts.
---

# Public API Design and Compatibility

## Workflow

1. Inventory every changed public member, released signature, consumer, and supported version; identify source, binary, and wire compatibility obligations.
2. Classify each change as additive, behavioral, deprecated, or breaking using the compatibility and change-guideline branches.
3. Preserve released signatures and defaults; add overloads or opt-in behavior and document the migration and deprecation window.
4. For serialized contracts, use the `dotnet-serialization` skill to plan reader-first rollout and old/new payload checks.
5. Run API approval tests and inspect every changed verified snapshot; test affected consumers and record the release version and migration notes.

Completion requires no removed public members, changed existing signatures, or new required parameters in a compatible release; every API snapshot change reviewed, wire changes opt-in and reader-first, and any intentional breaking release documented with migration guidance.

## Reference Routing

Read only the needed branch of [references/full-guide.md](references/full-guide.md):

- `The Three Types of Compatibility`.
- `Extend-Only Design`.
- `API Change Guidelines`.
- `API Approval Testing`.
- `Wire Compatibility`.
- `Encapsulation Patterns`.
- `Versioning Strategy`.
- `Anti-Patterns`.
- `Resources`: external documentation.

Use `rg -n '^## ' references/full-guide.md` to locate the relevant section.

## Guardrails

- Do not replace released signatures with optional-parameter variants; preserve the original overload for binary callers.
- Do not silently change defaults or behavior under a bug-fix label.
- Do not remove obsolete APIs before the documented deprecation window and breaking release.
- Do not approve snapshot changes without reviewing the public surface diff.
- Do not expose implementation types or leave inheritance open accidentally.
- Do not embed CLR type names in wire contracts.
