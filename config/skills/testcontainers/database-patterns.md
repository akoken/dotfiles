# Database Testcontainers Patterns

## Contents

- Module selection
- SQL Server
- PostgreSQL
- Migration verification
- Isolation and reset strategies
- Failure diagnostics

## Module Selection

Prefer the official database module because it provides a typed builder, connection string, defaults, and service-aware behavior.

| Dependency | Package | Builder |
|---|---|---|
| SQL Server | `Testcontainers.MsSql` | `MsSqlBuilder` |
| PostgreSQL | `Testcontainers.PostgreSql` | `PostgreSqlBuilder` |

Use `dotnet add package` and let the repository's central package management or lock strategy pin the resolved version.

## SQL Server

```csharp
using Microsoft.Data.SqlClient;
using Testcontainers.MsSql;

await using var database = new MsSqlBuilder(
        "mcr.microsoft.com/mssql/server:2022-CU14-ubuntu-22.04")
    .Build();

await database.StartAsync(cancellationToken);

await using var connection = new SqlConnection(database.GetConnectionString());
await connection.OpenAsync(cancellationToken);
```

Use the connection string supplied by the module. Do not reconstruct hostnames, ports, credentials, or trust settings manually.

## PostgreSQL

```csharp
using Npgsql;
using Testcontainers.PostgreSql;

await using var database = new PostgreSqlBuilder("postgres:15.1")
    .Build();

await database.StartAsync(cancellationToken);

await using var connection = new NpgsqlConnection(database.GetConnectionString());
await connection.OpenAsync(cancellationToken);
```

Pin the image tag to the version family used in production unless the test explicitly checks an upgrade path.

## Migration Verification

Test migrations through the same entry point used by deployment or application startup:

1. Start an empty database container.
2. Run the production migration command/service.
3. Assert the expected schema or perform representative reads and writes.
4. When upgrade compatibility matters, initialize the prior schema/data, apply the new migration, and verify preserved data.
5. When rollback is supported, test it explicitly; do not imply rollback safety from an upgrade-only test.

Avoid hand-written test schemas that can drift from production migrations.

## Isolation and Reset Strategies

Choose one boundary and document it in the fixture:

- **Container per test:** strongest isolation, slowest startup.
- **Container per class/collection:** good default when startup is expensive; reset state before each test.
- **Transaction rollback:** fast but invalid for code that opens multiple connections, commits independently, or tests transaction behavior.
- **Respawn/truncation:** useful for shared relational containers when configured for the real schema.
- **Database/schema per test:** useful only when creation and cleanup are reliable and names are collision-free.

Parallel tests must never share mutable rows, queue names, schemas, or database names unless the test is intentionally about concurrency.

## Failure Diagnostics

On startup, migration, or readiness failure, capture:

- pinned image name;
- container state and exit code;
- stdout/stderr with secrets redacted;
- resolved host and mapped port;
- migration command and exit result;
- Docker/runtime availability.

Keep failure output bounded. Do not print connection-string passwords or tokens.
