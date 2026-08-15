---
name: data-efcore-patterns
description: Apply Entity Framework Core patterns for tracking, migrations, retries, bulk operations, DbContext lifetime, query behavior, and database-backed tests. Use when implementing, reviewing, debugging, or optimizing EF Core data access and migration workflows.
---

# Entity Framework Core Patterns

## Workflow

1. Inspect the installed EF Core version, provider, tracking defaults, DbContext registration, migration ownership, and existing query patterns.
2. Classify the operation as read, tracked update, disconnected update, bulk mutation, migration, retryable transaction, or long-lived/background work.
3. Choose tracking and lifetime deliberately; never rely on an entity being tracked without verifying the query path.
4. Keep queries server-side, bounded, asynchronous, and free of N+1 behavior.
5. Use EF tooling for migrations and the application's production migration path for verification.
6. Run provider-realistic tests when behavior depends on SQL translation, constraints, transactions, or migrations.

Completion requires correct tracking semantics, a bounded server-side query or explicit mutation path, safe DbContext lifetime, and verification against the relevant provider behavior.

## Reference Routing

Read only the needed section of [references/full-guide.md](references/full-guide.md):

- no-tracking defaults and explicit updates;
- migration creation, removal, scripts, and application;
- dedicated migration service/Aspire;
- execution strategies and retryable transactions;
- `ExecuteUpdate` / `ExecuteDelete`;
- N+1, tracking conflicts, async, or loop queries;
- scoped contexts, background services, factories, or actors;
- in-memory versus Testcontainers-backed testing.

Use `rg -n '^## Pattern|^## Common|^## DbContext|^## Testing' references/full-guide.md` to locate the branch.

## Guardrails

- Do not edit generated migration files casually; use EF tooling and inspect the generated result.
- Do not use the in-memory provider as evidence for relational translation or constraint behavior.
- Do not hold a scoped DbContext in a singleton or long-lived actor.
- Do not wrap an execution strategy incorrectly around a transaction; the retry boundary must own the full unit of work.
- Do not use whole-entity `Update` for disconnected partial updates without considering overwritten columns and concurrency tokens.
- Use the `data-database-performance` skill for cross-ORM query-shape and batching decisions.
