---
name: dotnet-serialization
description: Use when choosing .NET serialization formats, implementing JSON source generation or binary contracts, migrating Newtonsoft.Json, handling polymorphism, evolving wire formats, or measuring serialization performance.
---

# Serialization in .NET

## Workflow

1. Inventory producers, consumers, persisted payloads, format constraints, installed serializer versions, and trimming or Native AOT requirements.
2. Choose the format using Format Recommendations; distinguish schema contracts from runtime implementation choices.
3. Define explicit field names, numbers, or keys and source-generation coverage for every serialized root and collection type.
4. For migration or polymorphism, read the separate branch and preserve naming, null/default handling, and explicit discriminators.
5. Plan tolerant readers and deploy new read support before enabling new writers; preserve old persisted data and rolling-upgrade compatibility.
6. Run representative round trips and old/new reader-writer tests; verify the publish path for AOT and benchmark actual payloads for performance work.

Completion requires every changed contract tested with supported readers and writers, migration semantics preserved, and any AOT or performance claim backed by the relevant publish or benchmark result.

## Reference Routing

Read only the needed branch of [references/full-guide.md](references/full-guide.md):

- `Schema-Based vs Reflection-Based`.
- `Format Recommendations`.
- `System.Text.Json with Source Generators`.
- `Protocol Buffers (Protobuf)`.
- `MessagePack`.
- `Migrating from Newtonsoft.Json`.
- `Polymorphism with Discriminators`.
- `Wire Compatibility Patterns`.
- `Performance Comparison`.
- `Best Practices`.
- `Resources`: external documentation.
- `API Wire Rollout Example`.

Use `rg -n '^## ' references/full-guide.md` to locate the relevant section.

## Guardrails

- Do not use BinaryFormatter.
- Do not embed assembly-qualified CLR type names as wire discriminators.
- Do not reuse removed Protobuf field numbers or MessagePack keys.
- Do not enable new writers before supported readers understand the new format.
- Do not assume source generation alone proves Native AOT compatibility; verify the published application.
- Do not treat approximate performance rankings as measurements of the application.
