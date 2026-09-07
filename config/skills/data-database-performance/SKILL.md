---
name: data-database-performance
description: Use when optimizing database queries, designing read/write stores, choosing EF Core versus Dapper, or diagnosing N+1 queries, excessive rows, tracking overhead, and join explosions.
---

# Database Performance Patterns

## Workflow

1. Inspect the provider, ORM, query SQL, round trips, result sizes, and read/write ownership; record the slow path and a measurable baseline.
2. Choose purpose-built read projections and write commands; use the EF Core versus Dapper branch for the workload decision.
3. Bound list reads with validated limits and deterministic pagination; project only the columns the consumer needs.
4. Move relational joins and filtering into SQL; batch related reads and choose projections or split queries when collection joins multiply rows.
5. Disable tracking for read-only entities, retain explicit tracking for updates, and constrain bounded string columns.
6. Verify results and query shape against the real provider; compare round trips, rows, and timing with the baseline.

Completion requires every changed query to have correct results, bounded rows, deliberate tracking, no per-row database calls, and recorded provider-level performance evidence.

## Reference Routing

Read only the needed branch of [references/full-guide.md](references/full-guide.md):

- `Core Principles`.
- `Read/Write Model Separation`.
- `Always Apply Row Limits`.
- `AsNoTracking for Read Queries`.
- `Avoid N+1 Queries`.
- `Never Do Application-Side Joins`.
- `Avoid Cartesian Explosions`.
- `Constrain Column Sizes`.
- `Don't Build Generic Repositories`.
- `Dapper for Read-Heavy Workloads`.
- `When to Use EF Core vs Dapper`.
- `Quick Reference`: command or decision lookup.
- `Resources`: external documentation.

Use `rg -n '^## ' references/full-guide.md` to locate the relevant section.

## Guardrails

- Do not return unbounded lists or use SELECT * for consumer projections.
- Do not issue related-data queries inside a per-row loop.
- Do not fetch whole tables to join them in application code; only assemble already bounded batch results in memory.
- Do not stack collection Includes without checking row multiplication; use projection or split queries.
- Do not track entities used only for reads.
- Do not hide query shape behind generic repositories; use purpose-built read/write stores.
- Do not leave bounded string columns without maximum lengths.
